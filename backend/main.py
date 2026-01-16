"""
Email Classifier API - Entry Point

Aplicação FastAPI para classificação de emails usando IA.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import Settings
from interfaces.api.v1.email_controller import router as email_router


def create_app() -> FastAPI:
    """
    Factory function para criar a aplicação FastAPI.
    
    Returns:
        Instância configurada do FastAPI
    """
    settings = Settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="""
        API para classificação automática de emails usando Inteligência Artificial.
        
        ## Funcionalidades
        
        * **Classificar por texto**: Envie o conteúdo do email e receba a classificação
        * **Classificar por arquivo**: Faça upload de um arquivo .txt ou .pdf
        
        ## Categorias
        
        * **Produtivo**: Emails que requerem ação ou resposta
        * **Improdutivo**: Emails que não necessitam ação imediata
        """,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Registrar routers
    app.include_router(email_router, prefix="/api/v1")
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        return {
            "message": "Email Classifier API",
            "version": settings.app_version,
            "docs": "/docs"
        }
    
    return app


# Criar instância da aplicação
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
