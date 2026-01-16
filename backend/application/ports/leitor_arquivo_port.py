"""
Port (Interface) para leitura de arquivos.

Define o contrato para leitores de diferentes formatos de arquivo.
"""

from abc import ABC, abstractmethod


class LeitorArquivoPort(ABC):
    """
    Interface para leitura de arquivos.
    
    Esta abstração permite adicionar novos formatos de arquivo
    sem alterar a lógica existente.
    """
    
    @abstractmethod
    def ler(self, arquivo: bytes) -> str:
        """
        Extrai o texto do arquivo.
        
        Args:
            arquivo: Conteúdo do arquivo em bytes
            
        Returns:
            Texto extraído do arquivo
            
        Raises:
            ArquivoInvalidoException: Se o arquivo não puder ser lido
        """
        pass
    
    @abstractmethod
    def suporta_extensao(self, extensao: str) -> bool:
        """
        Verifica se o leitor suporta a extensão do arquivo.
        
        Args:
            extensao: Extensão do arquivo (ex: '.txt', '.pdf')
            
        Returns:
            True se a extensão é suportada, False caso contrário
        """
        pass
