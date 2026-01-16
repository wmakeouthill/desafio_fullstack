"""
Testes unitários para o use case ClassificarEmailUseCase.
"""

import pytest
from unittest.mock import Mock

from application.use_cases.classificar_email_use_case import ClassificarEmailUseCase
from application.dtos.email_dto import ClassificarEmailRequest
from application.ports.classificador_port import ClassificadorPort
from domain.value_objects.classificacao_resultado import ClassificacaoResultado
from domain.entities.email import CategoriaEmail
from domain.exceptions import ConteudoInvalidoException, ClassificacaoException


class TestClassificarEmailUseCase:
    """Testes para o use case ClassificarEmailUseCase."""
    
    def setup_method(self):
        """Setup executado antes de cada teste."""
        self.mock_classificador = Mock(spec=ClassificadorPort)
        self.use_case = ClassificarEmailUseCase(
            classificador=self.mock_classificador
        )
    
    def test_classificar_email_produtivo(self):
        """Deve classificar email como produtivo corretamente."""
        # Arrange
        self.mock_classificador.classificar.return_value = ClassificacaoResultado(
            categoria=CategoriaEmail.PRODUTIVO,
            confianca=0.95,
            resposta_sugerida="Vamos analisar sua solicitação."
        )
        request = ClassificarEmailRequest(
            conteudo="Preciso de suporte técnico urgente."
        )
        
        # Act
        resultado = self.use_case.executar(request)
        
        # Assert
        assert resultado.categoria == "Produtivo"
        assert resultado.confianca == 0.95
        assert resultado.resposta_sugerida == "Vamos analisar sua solicitação."
        self.mock_classificador.classificar.assert_called_once()
    
    def test_classificar_email_improdutivo(self):
        """Deve classificar email como improdutivo corretamente."""
        # Arrange
        self.mock_classificador.classificar.return_value = ClassificacaoResultado(
            categoria=CategoriaEmail.IMPRODUTIVO,
            confianca=0.88,
            resposta_sugerida="Obrigado pela mensagem!"
        )
        request = ClassificarEmailRequest(
            conteudo="Feliz Natal! Desejo a todos boas festas."
        )
        
        # Act
        resultado = self.use_case.executar(request)
        
        # Assert
        assert resultado.categoria == "Improdutivo"
        assert resultado.confianca == 0.88
    
    def test_conteudo_vazio_deve_lancar_erro(self):
        """Deve lançar erro quando conteúdo está vazio."""
        # Arrange
        request = ClassificarEmailRequest(conteudo="   ")
        
        # Act & Assert
        with pytest.raises(ConteudoInvalidoException):
            self.use_case.executar(request)
    
    def test_erro_classificacao_deve_propagar(self):
        """Deve propagar erro quando classificador falha."""
        # Arrange
        self.mock_classificador.classificar.side_effect = ClassificacaoException(
            "Erro na API"
        )
        request = ClassificarEmailRequest(
            conteudo="Email para classificar"
        )
        
        # Act & Assert
        with pytest.raises(ClassificacaoException):
            self.use_case.executar(request)
