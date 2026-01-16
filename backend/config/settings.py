"""
Configurações da Aplicação.

Gerencia configurações via variáveis de ambiente.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Configurações da aplicação carregadas de variáveis de ambiente.
    
    Variáveis de ambiente podem ser definidas em um arquivo .env
    ou diretamente no sistema operacional.
    """
    
    # API
    app_name: str = Field(
        default="Email Classifier API",
        description="Nome da aplicação"
    )
    app_version: str = Field(
        default="1.0.0",
        description="Versão da aplicação"
    )
    debug: bool = Field(
        default=False,
        description="Modo debug"
    )
    
    # CORS
    cors_origins: str = Field(
        default="http://localhost:4200,http://localhost:3000",
        description="Origens permitidas para CORS (separadas por vírgula)"
    )
    
    # AI Provider
    ai_provider: str = Field(
        default="openai",
        description="Provedor de IA: 'openai' ou 'gemini'"
    )
    
    # OpenAI
    openai_api_key: str = Field(
        default="",
        description="Chave de API da OpenAI"
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="Modelo da OpenAI a ser usado"
    )
    openai_max_tokens: int = Field(
        default=4000,
        description="Máximo de tokens para resposta da OpenAI"
    )
    
    # Google Gemini
    gemini_api_key: str = Field(
        default="",
        description="Chave de API do Google Gemini"
    )
    gemini_model: str = Field(
        default="gemini-2.5-flash-preview-05-20",
        description="Modelo do Gemini a ser usado"
    )
    gemini_max_tokens: int = Field(
        default=8192,
        description="Máximo de tokens para resposta do Gemini"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Retorna a lista de origens CORS."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
