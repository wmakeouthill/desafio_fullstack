"""
Testes unitários para o value object ClassificacaoResultado.
"""

import pytest
from domain.value_objects.classificacao_resultado import ClassificacaoResultado
from domain.entities.email import CategoriaEmail


class TestClassificacaoResultado:
    """Testes para o value object ClassificacaoResultado."""
    
    def test_criar_resultado_valido(self):
        """Deve criar um resultado com dados válidos."""
        resultado = ClassificacaoResultado(
            categoria=CategoriaEmail.PRODUTIVO,
            confianca=0.95,
            resposta_sugerida="Obrigado pelo contato."
        )
        
        assert resultado.categoria == CategoriaEmail.PRODUTIVO
        assert resultado.confianca == 0.95
        assert resultado.resposta_sugerida == "Obrigado pelo contato."
    
    def test_confianca_percentual(self):
        """Deve retornar confiança em formato percentual."""
        resultado = ClassificacaoResultado(
            categoria=CategoriaEmail.PRODUTIVO,
            confianca=0.85,
            resposta_sugerida="Teste"
        )
        
        assert resultado.confianca_percentual == 85.0
    
    def test_alta_confianca_verdadeiro(self):
        """Deve retornar True quando confiança >= 0.8."""
        resultado = ClassificacaoResultado(
            categoria=CategoriaEmail.PRODUTIVO,
            confianca=0.80,
            resposta_sugerida="Teste"
        )
        
        assert resultado.alta_confianca is True
    
    def test_alta_confianca_falso(self):
        """Deve retornar False quando confiança < 0.8."""
        resultado = ClassificacaoResultado(
            categoria=CategoriaEmail.PRODUTIVO,
            confianca=0.79,
            resposta_sugerida="Teste"
        )
        
        assert resultado.alta_confianca is False
    
    def test_confianca_menor_que_zero_deve_lancar_erro(self):
        """Deve lançar erro quando confiança < 0."""
        with pytest.raises(ValueError, match="entre 0 e 1"):
            ClassificacaoResultado(
                categoria=CategoriaEmail.PRODUTIVO,
                confianca=-0.1,
                resposta_sugerida="Teste"
            )
    
    def test_confianca_maior_que_um_deve_lancar_erro(self):
        """Deve lançar erro quando confiança > 1."""
        with pytest.raises(ValueError, match="entre 0 e 1"):
            ClassificacaoResultado(
                categoria=CategoriaEmail.PRODUTIVO,
                confianca=1.5,
                resposta_sugerida="Teste"
            )
    
    def test_resposta_vazia_deve_lancar_erro(self):
        """Deve lançar erro quando resposta está vazia."""
        with pytest.raises(ValueError, match="não pode estar vazia"):
            ClassificacaoResultado(
                categoria=CategoriaEmail.PRODUTIVO,
                confianca=0.9,
                resposta_sugerida=""
            )
