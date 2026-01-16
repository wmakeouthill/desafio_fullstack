"""
Leitor de arquivos MBOX.

Implementação do LeitorArquivoPort para arquivos MBOX (múltiplos emails).
"""

import mailbox
import tempfile
import os
from typing import List

from application.ports.leitor_arquivo_port import LeitorArquivoPort
from domain.exceptions import ArquivoInvalidoException


class LeitorMbox(LeitorArquivoPort):
    """
    Leitor para arquivos MBOX (.mbox).
    
    Suporta o formato MBOX usado por Gmail (exportação), Thunderbird,
    e outros clientes de email para armazenar múltiplos emails.
    
    Nota: Extrai todos os emails concatenados em um único texto.
    """
    
    EXTENSOES_SUPORTADAS = {'.mbox'}
    ENCODINGS = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    MAX_EMAILS = 10  # Limitar quantidade de emails para não sobrecarregar
    
    def ler(self, arquivo: bytes) -> str:
        """
        Extrai o texto de um arquivo MBOX.
        
        Extrai até MAX_EMAILS emails do arquivo.
        
        Args:
            arquivo: Conteúdo do arquivo em bytes
            
        Returns:
            Texto extraído de todos os emails concatenados
            
        Raises:
            ArquivoInvalidoException: Se não for possível ler o arquivo MBOX
        """
        try:
            # Salvar em arquivo temporário para processar
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mbox') as tmp:
                tmp.write(arquivo)
                tmp_path = tmp.name
            
            try:
                mbox = mailbox.mbox(tmp_path)
                emails_texto = []
                
                for i, msg in enumerate(mbox):
                    if i >= self.MAX_EMAILS:
                        emails_texto.append(
                            f"\n[... Mais {len(mbox) - self.MAX_EMAILS} emails não exibidos ...]"
                        )
                        break
                    
                    email_texto = self._extrair_email(msg, i + 1)
                    if email_texto:
                        emails_texto.append(email_texto)
                
                mbox.close()
                
                if not emails_texto:
                    raise ArquivoInvalidoException(
                        "O arquivo MBOX não contém emails legíveis."
                    )
                
                return "\n\n".join(emails_texto)
                
            finally:
                os.unlink(tmp_path)
                
        except Exception as e:
            if isinstance(e, ArquivoInvalidoException):
                raise
            raise ArquivoInvalidoException(
                f"Não foi possível ler o arquivo MBOX: {str(e)}"
            )
    
    def _extrair_email(self, msg, numero: int) -> str:
        """Extrai texto de um email individual do MBOX."""
        partes = [f"=== Email {numero} ==="]
        
        # Cabeçalhos
        if msg.get('From'):
            partes.append(f"De: {msg.get('From')}")
        if msg.get('To'):
            partes.append(f"Para: {msg.get('To')}")
        if msg.get('Subject'):
            partes.append(f"Assunto: {msg.get('Subject')}")
        if msg.get('Date'):
            partes.append(f"Data: {msg.get('Date')}")
        
        partes.append("")  # Linha em branco
        
        # Corpo
        corpo = self._extrair_corpo(msg)
        if corpo:
            partes.append(corpo)
        
        return "\n".join(partes)
    
    def _extrair_corpo(self, msg) -> str:
        """Extrai o corpo do email."""
        corpo = None
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                
                if content_type == 'text/plain':
                    payload = part.get_payload(decode=True)
                    if payload:
                        corpo = self._decode_payload(payload, part)
                        if corpo:
                            break
                            
                elif content_type == 'text/html' and not corpo:
                    payload = part.get_payload(decode=True)
                    if payload:
                        html = self._decode_payload(payload, part)
                        if html:
                            corpo = self._limpar_html(html)
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                corpo = self._decode_payload(payload, msg)
                if msg.get_content_type() == 'text/html' and corpo:
                    corpo = self._limpar_html(corpo)
        
        return corpo or ""
    
    def _decode_payload(self, payload: bytes, part) -> str:
        """Decodifica o payload."""
        charset = part.get_content_charset() or 'utf-8'
        try:
            return payload.decode(charset)
        except (UnicodeDecodeError, LookupError):
            for enc in self.ENCODINGS:
                try:
                    return payload.decode(enc)
                except UnicodeDecodeError:
                    continue
        return ""
    
    def _limpar_html(self, html: str) -> str:
        """Remove tags HTML."""
        import re
        texto = re.sub(r'<[^>]+>', ' ', html)
        texto = re.sub(r'\s+', ' ', texto)
        return texto.strip()
    
    def suporta_extensao(self, extensao: str) -> bool:
        """
        Verifica se a extensão é suportada.
        
        Args:
            extensao: Extensão do arquivo (ex: '.mbox')
            
        Returns:
            True se a extensão for suportada
        """
        return extensao.lower() in self.EXTENSOES_SUPORTADAS
