"""
Leitor de arquivos EML.

Implementação do LeitorArquivoPort para arquivos de email no formato EML (RFC 822).
"""

import email
from email import policy
from email.message import EmailMessage
from typing import Optional

from application.ports.leitor_arquivo_port import LeitorArquivoPort
from domain.exceptions import ArquivoInvalidoException


class LeitorEml(LeitorArquivoPort):
    """
    Leitor para arquivos de email (.eml).
    
    Suporta o formato EML (RFC 822) usado por Outlook, Thunderbird,
    e outros clientes de email.
    """
    
    EXTENSOES_SUPORTADAS = {'.eml'}
    ENCODINGS = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    def ler(self, arquivo: bytes) -> str:
        """
        Extrai o texto de um arquivo EML.
        
        Extrai cabeçalhos relevantes (De, Para, Assunto) e o corpo do email.
        
        Args:
            arquivo: Conteúdo do arquivo em bytes
            
        Returns:
            Texto extraído do arquivo incluindo metadados
            
        Raises:
            ArquivoInvalidoException: Se não for possível ler o arquivo EML
        """
        try:
            # Tentar parsear o email
            msg = email.message_from_bytes(arquivo, policy=policy.default)
            
            # Extrair cabeçalhos
            headers = self._extrair_cabecalhos(msg)
            
            # Extrair corpo
            corpo = self._extrair_corpo(msg)
            
            if not corpo:
                raise ArquivoInvalidoException(
                    "O arquivo EML não contém conteúdo de texto."
                )
            
            # Montar texto completo com cabeçalhos
            partes = []
            if headers:
                partes.append(headers)
            partes.append(corpo)
            
            return "\n\n".join(partes)
            
        except Exception as e:
            if isinstance(e, ArquivoInvalidoException):
                raise
            raise ArquivoInvalidoException(
                f"Não foi possível ler o arquivo EML: {str(e)}"
            )
    
    def _extrair_cabecalhos(self, msg: EmailMessage) -> str:
        """Extrai os cabeçalhos relevantes do email."""
        cabecalhos = []
        
        if msg.get('From'):
            cabecalhos.append(f"De: {msg.get('From')}")
        if msg.get('To'):
            cabecalhos.append(f"Para: {msg.get('To')}")
        if msg.get('Subject'):
            cabecalhos.append(f"Assunto: {msg.get('Subject')}")
        if msg.get('Date'):
            cabecalhos.append(f"Data: {msg.get('Date')}")
        
        return "\n".join(cabecalhos) if cabecalhos else ""
    
    def _extrair_corpo(self, msg: EmailMessage) -> Optional[str]:
        """Extrai o corpo do email, preferindo texto simples."""
        corpo = None
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                
                # Preferir texto simples
                if content_type == 'text/plain':
                    corpo = self._decode_payload(part)
                    if corpo:
                        break
                        
                # Usar HTML como fallback
                elif content_type == 'text/html' and not corpo:
                    html_content = self._decode_payload(part)
                    if html_content:
                        # Remover tags HTML de forma simples
                        corpo = self._limpar_html(html_content)
        else:
            corpo = self._decode_payload(msg)
            
            # Se for HTML, limpar
            if msg.get_content_type() == 'text/html' and corpo:
                corpo = self._limpar_html(corpo)
        
        return corpo
    
    def _decode_payload(self, part) -> Optional[str]:
        """Decodifica o payload de uma parte do email."""
        try:
            payload = part.get_payload(decode=True)
            if payload:
                # Tentar diferentes encodings
                charset = part.get_content_charset() or 'utf-8'
                try:
                    return payload.decode(charset)
                except (UnicodeDecodeError, LookupError):
                    for enc in self.ENCODINGS:
                        try:
                            return payload.decode(enc)
                        except UnicodeDecodeError:
                            continue
        except Exception:
            pass
        return None
    
    def _limpar_html(self, html: str) -> str:
        """Remove tags HTML de forma simples."""
        import re
        # Remover tags
        texto = re.sub(r'<[^>]+>', ' ', html)
        # Remover múltiplos espaços
        texto = re.sub(r'\s+', ' ', texto)
        # Remover espaços no início/fim de linhas
        texto = "\n".join(line.strip() for line in texto.split('\n'))
        return texto.strip()
    
    def suporta_extensao(self, extensao: str) -> bool:
        """
        Verifica se a extensão é suportada.
        
        Args:
            extensao: Extensão do arquivo (ex: '.eml')
            
        Returns:
            True se a extensão for suportada
        """
        return extensao.lower() in self.EXTENSOES_SUPORTADAS
