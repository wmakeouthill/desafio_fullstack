"""
Port (Interface) para o serviço de classificação.

Define o contrato que qualquer implementação de classificador deve seguir.
"""

from abc import ABC, abstractmethod

from domain.value_objects.classificacao_resultado import ClassificacaoResultado


class ClassificadorPort(ABC):
    """
    Interface para o serviço de classificação de emails.
    
    Esta abstração permite trocar a implementação do classificador
    (OpenAI, HuggingFace, etc.) sem alterar a lógica de negócio.
    """
    
    @abstractmethod
    def classificar(self, conteudo: str) -> ClassificacaoResultado:
        """
        Classifica o conteúdo do email e retorna o resultado.
        
        Args:
            conteudo: Texto do email a ser classificado
            
        Returns:
            ClassificacaoResultado com categoria, confiança e resposta sugerida
            
        Raises:
            ClassificacaoException: Se ocorrer erro na classificação
        """
        pass
