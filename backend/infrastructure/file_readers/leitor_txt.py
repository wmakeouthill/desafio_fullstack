"""
Leitor de arquivos TXT.

Implementação do LeitorArquivoPort para arquivos de texto simples.
"""

from application.ports.leitor_arquivo_port import LeitorArquivoPort
from domain.exceptions import ArquivoInvalidoException


class LeitorTxt(LeitorArquivoPort):
    """
    Leitor para arquivos de texto (.txt).
    
    Suporta diferentes encodings comuns em arquivos de texto.
    """
    
    EXTENSOES_SUPORTADAS = {'.txt', '.text'}
    ENCODINGS = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    def ler(self, arquivo: bytes) -> str:
        """
        Extrai o texto de um arquivo TXT.
        
        Args:
            arquivo: Conteúdo do arquivo em bytes
            
        Returns:
            Texto extraído do arquivo
            
        Raises:
            ArquivoInvalidoException: Se não for possível decodificar o arquivo
        """
        for encoding in self.ENCODINGS:
            try:
                return arquivo.decode(encoding)
            except UnicodeDecodeError:
                continue
        
        raise ArquivoInvalidoException(
            "Não foi possível decodificar o arquivo. "
            "Verifique se é um arquivo de texto válido."
        )
    
    def suporta_extensao(self, extensao: str) -> bool:
        """
        Verifica se a extensão é suportada.
        
        Args:
            extensao: Extensão do arquivo (ex: '.txt')
            
        Returns:
            True se suportada, False caso contrário
        """
        return extensao.lower() in self.EXTENSOES_SUPORTADAS
