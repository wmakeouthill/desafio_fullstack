"""
Leitor de arquivos PDF.

Implementação do LeitorArquivoPort para arquivos PDF.
"""

import io
import logging

from application.ports.leitor_arquivo_port import LeitorArquivoPort
from domain.exceptions import ArquivoInvalidoException

try:
    from PyPDF2 import PdfReader
    PYPDF2_DISPONIVEL = True
except ImportError:
    PYPDF2_DISPONIVEL = False


logger = logging.getLogger(__name__)


class LeitorPdf(LeitorArquivoPort):
    """
    Leitor para arquivos PDF.
    
    Utiliza PyPDF2 para extrair texto de documentos PDF.
    """
    
    EXTENSOES_SUPORTADAS = {'.pdf'}
    
    def __init__(self):
        """Inicializa o leitor e verifica dependências."""
        if not PYPDF2_DISPONIVEL:
            logger.warning(
                "PyPDF2 não está instalado. "
                "Instale com: pip install PyPDF2"
            )
    
    def ler(self, arquivo: bytes) -> str:
        """
        Extrai o texto de um arquivo PDF.
        
        Args:
            arquivo: Conteúdo do arquivo em bytes
            
        Returns:
            Texto extraído de todas as páginas do PDF
            
        Raises:
            ArquivoInvalidoException: Se não for possível ler o PDF
        """
        if not PYPDF2_DISPONIVEL:
            raise ArquivoInvalidoException(
                "Suporte a PDF não disponível. "
                "PyPDF2 não está instalado."
            )
        
        try:
            pdf_file = io.BytesIO(arquivo)
            reader = PdfReader(pdf_file)
            
            textos = []
            for pagina in reader.pages:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    textos.append(texto_pagina)
            
            if not textos:
                raise ArquivoInvalidoException(
                    "Não foi possível extrair texto do PDF. "
                    "O arquivo pode estar protegido ou conter apenas imagens."
                )
            
            return '\n\n'.join(textos)
        
        except ArquivoInvalidoException:
            raise
        except Exception as e:
            logger.error(f"Erro ao ler PDF: {e}")
            raise ArquivoInvalidoException(
                f"Erro ao processar PDF: {str(e)}"
            )
    
    def suporta_extensao(self, extensao: str) -> bool:
        """
        Verifica se a extensão é suportada.
        
        Args:
            extensao: Extensão do arquivo (ex: '.pdf')
            
        Returns:
            True se suportada, False caso contrário
        """
        return extensao.lower() in self.EXTENSOES_SUPORTADAS
