"""
Injeção de Dependências para a API.

Configura e fornece as dependências necessárias para os controllers.
"""

from functools import lru_cache
from typing import Optional

from config.settings import Settings
from application.use_cases.classificar_email_use_case import ClassificarEmailUseCase
from application.use_cases.classificar_arquivo_use_case import ClassificarArquivoUseCase
from application.ports.classificador_port import ClassificadorPort
from infrastructure.ai.classificador_factory import ClassificadorFactory
from infrastructure.nlp.preprocessador import PreprocessadorTexto
from infrastructure.file_readers.leitor_txt import LeitorTxt
from infrastructure.file_readers.leitor_pdf import LeitorPdf
from infrastructure.file_readers.leitor_eml import LeitorEml
from infrastructure.file_readers.leitor_msg import LeitorMsg
from infrastructure.file_readers.leitor_mbox import LeitorMbox


@lru_cache
def get_settings() -> Settings:
    """Retorna as configurações da aplicação (cached)."""
    return Settings()


def get_preprocessador() -> PreprocessadorTexto:
    """Retorna uma instância do preprocessador de texto."""
    return PreprocessadorTexto(remover_stopwords=False)


def get_classificador(provider: Optional[str] = None) -> ClassificadorPort:
    """
    Retorna uma instância do classificador baseado no provider.
    
    Args:
        provider: 'openai' ou 'gemini'. Se None, usa o padrão do settings.
    """
    settings = get_settings()
    preprocessador = get_preprocessador()
    
    # Usar provider do request ou o padrão do settings
    provider_name = provider or settings.ai_provider
    
    # Selecionar API key, modelo e max_tokens baseado no provider
    if provider_name.lower() == "gemini":
        api_key = settings.gemini_api_key
        modelo = settings.gemini_model
        max_tokens = settings.gemini_max_tokens
    else:
        api_key = settings.openai_api_key
        modelo = settings.openai_model
        max_tokens = settings.openai_max_tokens
    
    return ClassificadorFactory.criar_por_nome(
        provider_name=provider_name,
        api_key=api_key,
        modelo=modelo,
        preprocessador=preprocessador,
        max_tokens=max_tokens
    )


def get_leitores():
    """Retorna a lista de leitores de arquivo disponíveis."""
    return [
        LeitorTxt(),
        LeitorPdf(),
        LeitorEml(),
        LeitorMsg(),
        LeitorMbox()
    ]


def get_classificar_email_use_case(provider: Optional[str] = None) -> ClassificarEmailUseCase:
    """Retorna o use case de classificação por texto."""
    classificador = get_classificador(provider)
    return ClassificarEmailUseCase(classificador=classificador)


def get_classificar_arquivo_use_case(provider: Optional[str] = None) -> ClassificarArquivoUseCase:
    """Retorna o use case de classificação por arquivo."""
    classificador = get_classificador(provider)
    leitores = get_leitores()
    
    return ClassificarArquivoUseCase(
        classificador=classificador,
        leitores=leitores
    )


def get_available_providers() -> dict:
    """Retorna os providers disponíveis e seus status."""
    settings = get_settings()
    return {
        "default": settings.ai_provider,
        "providers": {
            "openai": {
                "available": bool(settings.openai_api_key),
                "model": settings.openai_model
            },
            "gemini": {
                "available": bool(settings.gemini_api_key),
                "model": settings.gemini_model
            }
        }
    }
