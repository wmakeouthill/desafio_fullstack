#!/bin/bash
# ============================================
# Deploy para Google Cloud Run - Free Tier
# Projeto: classificador-email-desafio
# Região: São Paulo (southamerica-east1)
# ============================================

set -e

PROJECT_ID="classificador-email-desafio"
SERVICE_NAME="email-classifier-api"
REGION="southamerica-east1"  # São Paulo

echo "🚀 Deploy Email Classifier API para Cloud Run"
echo "Projeto: $PROJECT_ID"
echo "Região: $REGION (São Paulo)"

# 1. Configurar projeto
echo -e "\n📌 Configurando projeto..."
gcloud config set project $PROJECT_ID

# 2. Habilitar APIs necessárias
echo -e "\n🔧 Habilitando APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com

# 3. Deploy direto do source (sem Artifact Registry!)
echo -e "\n🚀 Fazendo deploy (isso pode levar 2-3 minutos)..."

gcloud run deploy $SERVICE_NAME \
    --source . \
    --project $PROJECT_ID \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 1 \
    --concurrency 80 \
    --timeout 60s \
    --set-env-vars "AI_PROVIDER=openai,DEBUG=false,OPENAI_MODEL=gpt-4o-mini,OPENAI_MODELS_FALLBACK=gpt-3.5-turbo,OPENAI_MAX_TOKENS=4000,GEMINI_MODEL=gemini-2.5-flash,GEMINI_MODELS_FALLBACK=gemini-2.0-flash;gemini-2.0-flash-lite,GEMINI_MAX_TOKENS=8192" \
    --set-secrets "OPENAI_API_KEY=openai-api-key:latest,GEMINI_API_KEY=gemini-api-key:latest"

echo -e "\n✅ Deploy concluído!"

# Obter URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)")
echo -e "\n📍 URL: $SERVICE_URL"
echo "📍 Health: $SERVICE_URL/api/v1/emails/health"
