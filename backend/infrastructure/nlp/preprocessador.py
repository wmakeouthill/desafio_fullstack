"""
Preprocessador de Texto para NLP.

Responsável pelo pré-processamento de texto antes da classificação.
"""

import re
from typing import List


class PreprocessadorTexto:
    """
    Responsável pelo pré-processamento de texto para análise de NLP.
    
    Realiza operações como:
    - Normalização de espaços
    - Remoção de caracteres especiais
    - Limpeza de formatação de email
    """
    
    def __init__(self, remover_stopwords: bool = False):
        """
        Inicializa o preprocessador.
        
        Args:
            remover_stopwords: Se deve remover stopwords (palavras comuns)
        """
        self._remover_stopwords = remover_stopwords
        self._stopwords_pt = self._carregar_stopwords()
    
    def processar(self, texto: str, preservar_headers: bool = True) -> str:
        """
        Realiza o pré-processamento completo do texto.
        
        Args:
            texto: Texto original a ser processado
            preservar_headers: Se True, mantém os headers do email (De, Para, Assunto)
                              para que a IA possa extrair metadados. Default: True
            
        Returns:
            Texto processado e normalizado
        """
        # NÃO remover headers por padrão - a IA precisa deles para extrair metadados
        if not preservar_headers:
            texto = self._limpar_headers_email(texto)
        
        texto = self._remover_urls(texto)
        # NÃO remover emails do corpo, apenas normalizar
        # texto = self._remover_emails(texto)
        texto = self._normalizar_espacos(texto)
        
        if self._remover_stopwords:
            texto = self._filtrar_stopwords(texto)
        
        return texto.strip()
    
    def _limpar_headers_email(self, texto: str) -> str:
        """Remove headers comuns de email (De:, Para:, Assunto:, etc.)."""
        padroes = [
            r'^(De|From|Para|To|Cc|Bcc|Assunto|Subject|Data|Date):.*$',
            r'^-{3,}.*$',
            r'^={3,}.*$',
        ]
        for padrao in padroes:
            texto = re.sub(padrao, '', texto, flags=re.MULTILINE | re.IGNORECASE)
        return texto
    
    def _remover_urls(self, texto: str) -> str:
        """Remove URLs do texto."""
        return re.sub(r'https?://\S+|www\.\S+', '', texto)
    
    def _remover_emails(self, texto: str) -> str:
        """Remove endereços de email do texto."""
        return re.sub(r'\S+@\S+\.\S+', '', texto)
    
    def _normalizar_espacos(self, texto: str) -> str:
        """Normaliza múltiplos espaços e quebras de linha."""
        texto = re.sub(r'\n+', '\n', texto)
        texto = re.sub(r'[ \t]+', ' ', texto)
        return texto
    
    def _filtrar_stopwords(self, texto: str) -> str:
        """Remove stopwords do texto."""
        palavras = texto.lower().split()
        palavras_filtradas = [p for p in palavras if p not in self._stopwords_pt]
        return ' '.join(palavras_filtradas)
    
    def _carregar_stopwords(self) -> set:
        """Carrega lista de stopwords em português."""
        return {
            'a', 'o', 'e', 'é', 'de', 'da', 'do', 'em', 'um', 'uma',
            'para', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por',
            'mais', 'as', 'dos', 'como', 'mas', 'foi', 'ao', 'ele', 'das',
            'tem', 'à', 'seu', 'sua', 'ou', 'ser', 'quando', 'muito', 'há',
            'nos', 'já', 'está', 'eu', 'também', 'só', 'pelo', 'pela', 'até',
            'isso', 'ela', 'entre', 'era', 'depois', 'sem', 'mesmo', 'aos',
            'ter', 'seus', 'quem', 'nas', 'me', 'esse', 'eles', 'estão',
            'você', 'tinha', 'foram', 'essa', 'num', 'nem', 'suas', 'meu',
            'às', 'minha', 'têm', 'numa', 'pelos', 'elas', 'havia', 'seja',
            'qual', 'será', 'nós', 'tenho', 'lhe', 'deles', 'essas', 'esses',
            'pelas', 'este', 'fosse', 'dele', 'tu', 'te', 'vocês', 'vos',
            'lhes', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'nosso',
            'nossa', 'nossos', 'nossas', 'dela', 'delas', 'esta', 'estes',
            'estas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'isto',
            'aquilo', 'estou', 'está', 'estamos', 'estão', 'estive',
            'esteve', 'estivemos', 'estiveram', 'estava', 'estávamos',
            'estavam', 'estivera', 'estivéramos', 'esteja', 'estejamos',
            'estejam', 'estivesse', 'estivéssemos', 'estivessem', 'estiver',
            'estivermos', 'estiverem', 'hei', 'há', 'havemos', 'hão',
            'houve', 'houvemos', 'houveram', 'houvera', 'houvéramos',
            'haja', 'hajamos', 'hajam', 'houvesse', 'houvéssemos',
            'houvessem', 'houver', 'houvermos', 'houverem', 'houverei',
            'houverá', 'houveremos', 'houverão', 'houveria', 'houveríamos',
            'houveriam', 'sou', 'somos', 'são', 'era', 'éramos', 'eram',
            'fui', 'foi', 'fomos', 'foram', 'fora', 'fôramos', 'seja',
            'sejamos', 'sejam', 'fosse', 'fôssemos', 'fossem', 'for',
            'formos', 'forem', 'serei', 'será', 'seremos', 'serão', 'seria',
            'seríamos', 'seriam', 'tenho', 'tem', 'temos', 'tém', 'tinha',
            'tínhamos', 'tinham', 'tive', 'teve', 'tivemos', 'tiveram',
            'tivera', 'tivéramos', 'tenha', 'tenhamos', 'tenham', 'tivesse',
            'tivéssemos', 'tivessem', 'tiver', 'tivermos', 'tiverem',
            'terei', 'terá', 'teremos', 'terão', 'teria', 'teríamos', 'teriam'
        }
