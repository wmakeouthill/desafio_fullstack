"""
Leitor de arquivos MSG.

Implementação do LeitorArquivoPort para arquivos de email no formato MSG (Microsoft Outlook).
"""

import struct
from typing import Optional

from application.ports.leitor_arquivo_port import LeitorArquivoPort
from domain.exceptions import ArquivoInvalidoException


class LeitorMsg(LeitorArquivoPort):
    """
    Leitor para arquivos de email MSG (.msg).
    
    Suporta o formato MSG proprietário do Microsoft Outlook.
    Usa uma implementação simplificada que extrai texto básico.
    """
    
    EXTENSOES_SUPORTADAS = {'.msg'}
    
    def ler(self, arquivo: bytes) -> str:
        """
        Extrai o texto de um arquivo MSG.
        
        Args:
            arquivo: Conteúdo do arquivo em bytes
            
        Returns:
            Texto extraído do arquivo
            
        Raises:
            ArquivoInvalidoException: Se não for possível ler o arquivo MSG
        """
        try:
            # Tentar usar a biblioteca extract-msg se disponível
            try:
                import extract_msg
                
                # Salvar temporariamente para processar
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.msg') as tmp:
                    tmp.write(arquivo)
                    tmp_path = tmp.name
                
                try:
                    msg = extract_msg.Message(tmp_path)
                    
                    partes = []
                    
                    # Extrair cabeçalhos
                    if msg.sender:
                        partes.append(f"De: {msg.sender}")
                    if msg.to:
                        partes.append(f"Para: {msg.to}")
                    if msg.subject:
                        partes.append(f"Assunto: {msg.subject}")
                    if msg.date:
                        partes.append(f"Data: {msg.date}")
                    
                    # Extrair corpo
                    corpo = msg.body or ""
                    
                    if partes:
                        return "\n".join(partes) + "\n\n" + corpo
                    return corpo
                    
                finally:
                    os.unlink(tmp_path)
                    
            except ImportError:
                # Fallback: extrair texto de forma simplificada
                return self._extrair_texto_simplificado(arquivo)
                
        except Exception as e:
            if isinstance(e, ArquivoInvalidoException):
                raise
            raise ArquivoInvalidoException(
                f"Não foi possível ler o arquivo MSG: {str(e)}"
            )
    
    def _extrair_texto_simplificado(self, arquivo: bytes) -> str:
        """
        Extração simplificada de texto de arquivo MSG.
        
        Tenta extrair strings legíveis do arquivo binário.
        """
        # Verificar assinatura do arquivo MSG (Compound File Binary)
        if not arquivo.startswith(b'\xD0\xCF\x11\xE0'):
            raise ArquivoInvalidoException(
                "O arquivo não parece ser um arquivo MSG válido."
            )
        
        # Extrair strings UTF-16 e ASCII do arquivo
        texto_partes = []
        
        # Tentar extrair texto UTF-16
        try:
            # Procurar por sequências de texto UTF-16
            i = 0
            while i < len(arquivo) - 2:
                if arquivo[i:i+2] == b'\xff\xfe':  # BOM UTF-16 LE
                    # Tentar decodificar
                    end = arquivo.find(b'\x00\x00', i + 2)
                    if end > i:
                        try:
                            texto = arquivo[i:end+2].decode('utf-16-le', errors='ignore')
                            if len(texto) > 10 and texto.isprintable():
                                texto_partes.append(texto)
                        except:
                            pass
                i += 1
        except:
            pass
        
        # Tentar extrair texto ASCII/UTF-8
        import re
        texto_ascii = arquivo.decode('utf-8', errors='ignore')
        # Encontrar sequências de texto legível
        matches = re.findall(r'[\w\s@.\-,!?:;()]{20,}', texto_ascii)
        texto_partes.extend(matches)
        
        if not texto_partes:
            raise ArquivoInvalidoException(
                "Não foi possível extrair texto do arquivo MSG. "
                "Considere instalar a biblioteca 'extract-msg' para melhor suporte."
            )
        
        return "\n".join(set(texto_partes))
    
    def suporta_extensao(self, extensao: str) -> bool:
        """
        Verifica se a extensão é suportada.
        
        Args:
            extensao: Extensão do arquivo (ex: '.msg')
            
        Returns:
            True se a extensão for suportada
        """
        return extensao.lower() in self.EXTENSOES_SUPORTADAS
