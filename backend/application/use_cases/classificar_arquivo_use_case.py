"""
Use Case: Classificar Email por Arquivo.

Caso de uso responsável por classificar um email a partir de um arquivo (.txt ou .pdf).
"""

from typing import List

from application.ports.classificador_port import ClassificadorPort
from application.ports.leitor_arquivo_port import LeitorArquivoPort
from application.dtos.email_dto import ClassificarArquivoResponse
from domain.entities.email import Email
from domain.exceptions import (
    ConteudoInvalidoException,
    ClassificacaoException,
    ArquivoInvalidoException,
    FormatoNaoSuportadoException,
)


class ClassificarArquivoUseCase:
    """
    Caso de uso para classificar emails a partir de arquivos.
    
    Este use case orquestra a leitura de um arquivo, extração
    do texto e classificação do conteúdo.
    """
    
    def __init__(
        self,
        classificador: ClassificadorPort,
        leitores: List[LeitorArquivoPort]
    ):
        """
        Inicializa o use case com suas dependências.
        
        Args:
            classificador: Implementação do serviço de classificação
            leitores: Lista de leitores de arquivo disponíveis
        """
        self._classificador = classificador
        self._leitores = leitores
    
    def executar(
        self,
        arquivo: bytes,
        nome_arquivo: str
    ) -> ClassificarArquivoResponse:
        """
        Executa a classificação do email a partir de um arquivo.
        
        Args:
            arquivo: Conteúdo do arquivo em bytes
            nome_arquivo: Nome original do arquivo
            
        Returns:
            ClassificarArquivoResponse com o resultado da classificação
            
        Raises:
            FormatoNaoSuportadoException: Se o formato não for suportado
            ArquivoInvalidoException: Se o arquivo não puder ser lido
            ConteudoInvalidoException: Se o conteúdo for inválido
            ClassificacaoException: Se ocorrer erro na classificação
        """
        # Extrair extensão do arquivo
        extensao = self._extrair_extensao(nome_arquivo)
        
        # Encontrar leitor apropriado
        leitor = self._encontrar_leitor(extensao)
        
        # Extrair texto do arquivo
        conteudo = leitor.ler(arquivo)
        
        if not conteudo or not conteudo.strip():
            raise ArquivoInvalidoException("Arquivo está vazio ou não contém texto")
        
        try:
            # Criar entidade de domínio
            email = Email(conteudo=conteudo)
            
            # Executar classificação
            resultado = self._classificador.classificar(email.conteudo)
            
            # Retornar resposta
            return ClassificarArquivoResponse(
                categoria=resultado.categoria.value,
                confianca=resultado.confianca,
                resposta_sugerida=resultado.resposta_sugerida,
                nome_arquivo=nome_arquivo,
                assunto=resultado.assunto,
                remetente=resultado.remetente,
                destinatario=resultado.destinatario
            )
        
        except ValueError as e:
            raise ConteudoInvalidoException(str(e))
    
    def _extrair_extensao(self, nome_arquivo: str) -> str:
        """Extrai a extensão do nome do arquivo."""
        if '.' not in nome_arquivo:
            raise FormatoNaoSuportadoException("sem extensão")
        return '.' + nome_arquivo.rsplit('.', 1)[-1].lower()
    
    def _encontrar_leitor(self, extensao: str) -> LeitorArquivoPort:
        """Encontra o leitor apropriado para a extensão."""
        for leitor in self._leitores:
            if leitor.suporta_extensao(extensao):
                return leitor
        raise FormatoNaoSuportadoException(extensao)
