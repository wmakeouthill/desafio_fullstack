<#
.SYNOPSIS
    Configura Cloud Run como privado e cria Service Account para Vercel.

.DESCRIPTION
    Este script:
    1. Cria uma Service Account para o Vercel invocar o Cloud Run
    2. Dá permissão de invoker para a Service Account
    3. Remove acesso público do Cloud Run
    4. Gera arquivo JSON com credenciais

.PARAMETER ProjectId
    ID do projeto no Google Cloud

.PARAMETER ServiceName
    Nome do serviço no Cloud Run (padrão: email-classifier-api)

.PARAMETER Region
    Região do Cloud Run (padrão: southamerica-east1)

.EXAMPLE
    .\setup-private-cloudrun.ps1 -ProjectId "meu-projeto-123"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,
    
    [Parameter(Mandatory=$false)]
    [string]$ServiceName = "email-classifier-api",
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "southamerica-east1"
)

$ErrorActionPreference = "Stop"

Write-Host "🔧 Configurando Cloud Run Privado" -ForegroundColor Cyan
Write-Host "   Projeto: $ProjectId"
Write-Host "   Serviço: $ServiceName"
Write-Host "   Região:  $Region"
Write-Host ""

# Configurar projeto
Write-Host "📌 Configurando projeto no gcloud..." -ForegroundColor Yellow
gcloud config set project $ProjectId

$ServiceAccountName = "vercel-invoker"
$ServiceAccountEmail = "$ServiceAccountName@$ProjectId.iam.gserviceaccount.com"
$KeyFileName = "vercel-service-account-key.json"

# Verificar se Service Account já existe
Write-Host "🔍 Verificando Service Account existente..." -ForegroundColor Yellow
$existingSA = gcloud iam service-accounts list --filter="email:$ServiceAccountEmail" --format="value(email)" 2>$null

if ($existingSA) {
    Write-Host "   Service Account já existe: $ServiceAccountEmail" -ForegroundColor Green
} else {
    # Criar Service Account
    Write-Host "➕ Criando Service Account..." -ForegroundColor Yellow
    gcloud iam service-accounts create $ServiceAccountName `
        --display-name="Vercel Cloud Run Invoker" `
        --description="Service Account usada pelo Vercel para invocar Cloud Run"
    Write-Host "   ✅ Service Account criada: $ServiceAccountEmail" -ForegroundColor Green
}

# Dar permissão de invoker
Write-Host "🔐 Configurando permissão de invoker..." -ForegroundColor Yellow
gcloud run services add-iam-policy-binding $ServiceName `
    --member="serviceAccount:$ServiceAccountEmail" `
    --role="roles/run.invoker" `
    --region=$Region 2>&1 | Out-Null
Write-Host "   ✅ Permissão concedida" -ForegroundColor Green

# Verificar se já existe chave
if (Test-Path $KeyFileName) {
    Write-Host "⚠️  Arquivo $KeyFileName já existe. Sobrescrever? (s/n)" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -ne "s") {
        Write-Host "   Mantendo chave existente" -ForegroundColor Yellow
    } else {
        Remove-Item $KeyFileName -Force
        Write-Host "🔑 Gerando nova chave JSON..." -ForegroundColor Yellow
        gcloud iam service-accounts keys create $KeyFileName `
            --iam-account=$ServiceAccountEmail
        Write-Host "   ✅ Chave criada: $KeyFileName" -ForegroundColor Green
    }
} else {
    Write-Host "🔑 Gerando chave JSON..." -ForegroundColor Yellow
    gcloud iam service-accounts keys create $KeyFileName `
        --iam-account=$ServiceAccountEmail
    Write-Host "   ✅ Chave criada: $KeyFileName" -ForegroundColor Green
}

# Perguntar se quer remover acesso público
Write-Host ""
Write-Host "❓ Deseja remover o acesso público do Cloud Run agora? (s/n)" -ForegroundColor Cyan
$removePublic = Read-Host

if ($removePublic -eq "s") {
    Write-Host "🔒 Removendo acesso público..." -ForegroundColor Yellow
    
    # Verificar se allUsers tem acesso
    $policy = gcloud run services get-iam-policy $ServiceName --region=$Region --format=json 2>$null | ConvertFrom-Json
    $hasAllUsers = $policy.bindings | Where-Object { $_.members -contains "allUsers" }
    
    if ($hasAllUsers) {
        gcloud run services remove-iam-policy-binding $ServiceName `
            --member="allUsers" `
            --role="roles/run.invoker" `
            --region=$Region 2>&1 | Out-Null
        Write-Host "   ✅ Acesso público removido!" -ForegroundColor Green
    } else {
        Write-Host "   ℹ️  Cloud Run já não tem acesso público" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ⏭️  Mantendo Cloud Run público por enquanto" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "                    ✅ CONFIGURAÇÃO CONCLUÍDA!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Copie o conteúdo de '$KeyFileName'" -ForegroundColor White
Write-Host "2. Vá para: https://vercel.com/dashboard" -ForegroundColor White
Write-Host "3. Seu projeto → Settings → Environment Variables" -ForegroundColor White
Write-Host "4. Adicione:" -ForegroundColor White
Write-Host "   Nome:  GOOGLE_SERVICE_ACCOUNT_KEY" -ForegroundColor Cyan
Write-Host "   Valor: (cole o JSON inteiro)" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Faça deploy do frontend:" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Gray
Write-Host "   npm install" -ForegroundColor Gray
Write-Host "   vercel --prod" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  IMPORTANTE: Não commite o arquivo $KeyFileName no Git!" -ForegroundColor Red
Write-Host ""

# Mostrar conteúdo da chave para facilitar cópia
Write-Host "📄 Conteúdo da chave (para copiar no Vercel):" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────" -ForegroundColor Gray
$keyContent = Get-Content $KeyFileName -Raw
# Mostrar em uma linha só para facilitar cópia no Vercel
$keyOneLine = $keyContent -replace "`r`n", "" -replace "`n", "" -replace "  ", ""
Write-Host $keyOneLine -ForegroundColor DarkGray
Write-Host "─────────────────────────────────────────────" -ForegroundColor Gray
