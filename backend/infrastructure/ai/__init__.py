# AI - Integração com APIs de Inteligência Artificial
from infrastructure.ai.openai_classificador import OpenAIClassificador
from infrastructure.ai.gemini_classificador import GeminiClassificador
from infrastructure.ai.classificador_factory import ClassificadorFactory, AIProvider

__all__ = [
    "OpenAIClassificador",
    "GeminiClassificador", 
    "ClassificadorFactory",
    "AIProvider"
]
