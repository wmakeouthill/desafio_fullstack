"""
Factory para criação de classificadores de IA.

Permite selecionar dinamicamente entre diferentes provedores de IA.
"""

from enum import Enum
from typing import Optional

from application.ports.classificador_port import ClassificadorPort
from infrastructure.ai.openai_classificador import OpenAIClassificador
from infrastructure.ai.gemini_classificador import GeminiClassificador
from infrastructure.nlp.preprocessador import PreprocessadorTexto


class AIProvider(Enum):
    """Provedores de IA disponíveis."""
    OPENAI = "openai"
    GEMINI = "gemini"


class ClassificadorFactory:
    """
    Factory para criar instâncias de classificadores.
    
    Permite trocar entre diferentes provedores de IA de forma transparente.
    """
    
    @staticmethod
    def criar(
        provider: AIProvider,
        api_key: str,
        modelo: Optional[str] = None,
        preprocessador: Optional[PreprocessadorTexto] = None,
        max_tokens: Optional[int] = None
    ) -> ClassificadorPort:
        """
        Cria uma instância do classificador baseado no provider.
        
        Args:
            provider: Provedor de IA (OPENAI ou GEMINI)
            api_key: Chave de API do provedor
            modelo: Modelo específico a ser usado (opcional)
            preprocessador: Preprocessador de texto (opcional)
            max_tokens: Máximo de tokens para resposta (opcional)
            
        Returns:
            Instância do classificador
            
        Raises:
            ValueError: Se o provider não for suportado
        """
        preprocessador = preprocessador or PreprocessadorTexto()
        
        if provider == AIProvider.OPENAI:
            return OpenAIClassificador(
                api_key=api_key,
                preprocessador=preprocessador,
                modelo=modelo or "gpt-4o-mini",
                max_tokens=max_tokens or 4000
            )
        
        elif provider == AIProvider.GEMINI:
            return GeminiClassificador(
                api_key=api_key,
                preprocessador=preprocessador,
                modelo=modelo or "gemini-2.5-flash-preview-05-20",
                max_tokens=max_tokens or 8192
            )
        
        else:
            raise ValueError(f"Provider não suportado: {provider}")
    
    @staticmethod
    def criar_por_nome(
        provider_name: str,
        api_key: str,
        modelo: Optional[str] = None,
        preprocessador: Optional[PreprocessadorTexto] = None,
        max_tokens: Optional[int] = None
    ) -> ClassificadorPort:
        """
        Cria classificador pelo nome do provider (string).
        
        Args:
            provider_name: Nome do provider ("openai" ou "gemini")
            api_key: Chave de API
            modelo: Modelo específico (opcional)
            preprocessador: Preprocessador (opcional)
            max_tokens: Máximo de tokens para resposta (opcional)
            
        Returns:
            Instância do classificador
        """
        try:
            provider = AIProvider(provider_name.lower())
        except ValueError:
            raise ValueError(
                f"Provider '{provider_name}' não suportado. "
                f"Use: {[p.value for p in AIProvider]}"
            )
        
        return ClassificadorFactory.criar(
            provider=provider,
            api_key=api_key,
            modelo=modelo,
            preprocessador=preprocessador,
            max_tokens=max_tokens
        )
