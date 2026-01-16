# ============================================
# Deploy para Google Cloud Run - Free Tier
# BUILD LOCAL + Push para Artifact Registry
# Projeto: classificador-email-desafio
# Regiao: Sao Paulo (southamerica-east1)
# ============================================

# Configuracoes
$PROJECT_ID = "classificador-email-desafio"
$SERVICE_NAME = "email-classifier-api"
$REGION = "southamerica-east1"
$IMAGE_NAME = "$REGION-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/$SERVICE_NAME"

Write-Host ""
Write-Host "=== Deploy Email Classifier API para Cloud Run ===" -ForegroundColor Cyan
Write-Host "Projeto: $PROJECT_ID" -ForegroundColor Yellow
Write-Host "Regiao: $REGION (Sao Paulo)" -ForegroundColor Yellow
Write-Host "Build: LOCAL (Docker)" -ForegroundColor Yellow

# 1. Configurar projeto
Write-Host ""
Write-Host "[1/6] Configurando projeto..." -ForegroundColor Green
gcloud config set project $PROJECT_ID --quiet

# 2. Habilitar APIs necessarias
Write-Host ""
Write-Host "[2/6] Habilitando APIs..." -ForegroundColor Green
gcloud services enable run.googleapis.com --quiet
gcloud services enable artifactregistry.googleapis.com --quiet
gcloud services enable secretmanager.googleapis.com --quiet

# 3. Criar repositorio no Artifact Registry se nao existir
Write-Host ""
Write-Host "[3/6] Configurando Artifact Registry..." -ForegroundColor Green
$repoExists = gcloud artifacts repositories describe cloud-run-source-deploy --location=$REGION 2>$null
if (-not $repoExists) {
    Write-Host "Criando repositorio no Artifact Registry..." -ForegroundColor Yellow
    gcloud artifacts repositories create cloud-run-source-deploy `
        --repository-format=docker `
        --location=$REGION `
        --description="Docker images for Cloud Run" `
        --quiet
}
Write-Host "Artifact Registry configurado." -ForegroundColor Green

# Configurar Docker para autenticar com GCP
gcloud auth configure-docker $REGION-docker.pkg.dev --quiet

# 4. Criar secrets se nao existirem
Write-Host ""
Write-Host "[4/6] Configurando secrets..." -ForegroundColor Green

# Verificar e criar openai-api-key
$openaiExists = gcloud secrets describe openai-api-key 2>$null
if (-not $openaiExists) {
    Write-Host "Secret 'openai-api-key' nao existe. Criando..." -ForegroundColor Yellow
    $openaiKey = Read-Host "Digite sua OPENAI_API_KEY (sk-...)"
    if ($openaiKey) {
        $openaiKey | gcloud secrets create openai-api-key --data-file=- --quiet
        Write-Host "Secret 'openai-api-key' criado com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "ERRO: Chave OpenAI nao fornecida!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Secret 'openai-api-key' ja existe." -ForegroundColor Green
}

# Verificar e criar gemini-api-key
$geminiExists = gcloud secrets describe gemini-api-key 2>$null
if (-not $geminiExists) {
    Write-Host "Secret 'gemini-api-key' nao existe. Criando..." -ForegroundColor Yellow
    $geminiKey = Read-Host "Digite sua GEMINI_API_KEY (ou pressione Enter para pular)"
    if ($geminiKey) {
        $geminiKey | gcloud secrets create gemini-api-key --data-file=- --quiet
        Write-Host "Secret 'gemini-api-key' criado com sucesso!" -ForegroundColor Green
    } else {
        "placeholder" | gcloud secrets create gemini-api-key --data-file=- --quiet
        Write-Host "Secret 'gemini-api-key' criado com placeholder." -ForegroundColor Yellow
    }
} else {
    Write-Host "Secret 'gemini-api-key' ja existe." -ForegroundColor Green
}

# 5. Build LOCAL da imagem Docker
Write-Host ""
Write-Host "[5/6] Build LOCAL da imagem Docker..." -ForegroundColor Green
docker build -t $IMAGE_NAME .

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Falha no build da imagem Docker!" -ForegroundColor Red
    exit 1
}

# Push para Artifact Registry
Write-Host ""
Write-Host "[5/6] Push da imagem para Artifact Registry..." -ForegroundColor Green
docker push $IMAGE_NAME

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Falha no push da imagem!" -ForegroundColor Red
    exit 1
}

# 6. Deploy no Cloud Run usando a imagem
Write-Host ""
Write-Host "[6/6] Deploy no Cloud Run..." -ForegroundColor Green

gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_NAME `
    --project $PROJECT_ID `
    --region $REGION `
    --platform managed `
    --allow-unauthenticated `
    --port 8000 `
    --memory 512Mi `
    --cpu 1 `
    --min-instances 0 `
    --max-instances 1 `
    --concurrency 80 `
    --timeout 60s `
    --set-env-vars "AI_PROVIDER=openai,DEBUG=false,OPENAI_MODEL=gpt-4o-mini,OPENAI_MODELS_FALLBACK=gpt-3.5-turbo,OPENAI_MAX_TOKENS=4000,GEMINI_MODEL=gemini-2.5-flash,GEMINI_MODELS_FALLBACK=gemini-2.0-flash;gemini-2.0-flash-lite,GEMINI_MAX_TOKENS=8192" `
    --set-secrets "OPENAI_API_KEY=openai-api-key:latest,GEMINI_API_KEY=gemini-api-key:latest" `
    --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== Deploy concluido com sucesso! ===" -ForegroundColor Green
    
    $SERVICE_URL = gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)"
    
    Write-Host ""
    Write-Host "URL do servico: $SERVICE_URL" -ForegroundColor Cyan
    Write-Host "Health check: $SERVICE_URL/api/v1/emails/health" -ForegroundColor Cyan
    
    Write-Host ""
    Write-Host "LEMBRETE: Atualize CORS_ORIGINS apos deploy do frontend!" -ForegroundColor Yellow
    Write-Host "gcloud run services update $SERVICE_NAME --region $REGION --set-env-vars CORS_ORIGINS=https://seu-frontend.vercel.app" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "=== ERRO no deploy! ===" -ForegroundColor Red
}
