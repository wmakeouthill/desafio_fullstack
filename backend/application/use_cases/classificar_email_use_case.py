"""
Use Case: Classificar Email por Texto.

Caso de uso responsável por classificar um email a partir do seu conteúdo textual.
"""

from application.ports.classificador_port import ClassificadorPort
from application.dtos.email_dto import ClassificarEmailRequest, ClassificarEmailResponse
from domain.entities.email import Email
from domain.exceptions import ConteudoInvalidoException, ClassificacaoException


class ClassificarEmailUseCase:
    """
    Caso de uso para classificar emails a partir de texto.
    
    Este use case orquestra a classificação de um email, validando
    o conteúdo e delegando a classificação para o serviço apropriado.
    """
    
    def __init__(self, classificador: ClassificadorPort):
        """
        Inicializa o use case com suas dependências.
        
        Args:
            classificador: Implementação do serviço de classificação
        """
        self._classificador = classificador
    
    def executar(self, request: ClassificarEmailRequest) -> ClassificarEmailResponse:
        """
        Executa a classificação do email.
        
        Args:
            request: DTO com o conteúdo do email
            
        Returns:
            ClassificarEmailResponse com o resultado da classificação
            
        Raises:
            ConteudoInvalidoException: Se o conteúdo for inválido
            ClassificacaoException: Se ocorrer erro na classificação
        """
        try:
            # Criar entidade de domínio (valida regras de negócio)
            email = Email(conteudo=request.conteudo)
            
            # Executar classificação via porta (abstração)
            resultado = self._classificador.classificar(email.conteudo)
            
            # Retornar DTO de resposta
            return ClassificarEmailResponse(
                categoria=resultado.categoria.value,
                confianca=resultado.confianca,
                resposta_sugerida=resultado.resposta_sugerida
            )
        
        except ValueError as e:
            raise ConteudoInvalidoException(str(e))
        except Exception as e:
            if isinstance(e, (ConteudoInvalidoException, ClassificacaoException)):
                raise
            raise ClassificacaoException(f"Erro inesperado: {str(e)}")
