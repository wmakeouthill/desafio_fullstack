"""
Testes unitários para a entidade Email.
"""

import pytest
from domain.entities.email import Email, CategoriaEmail


class TestEmail:
    """Testes para a entidade Email."""
    
    def test_criar_email_valido(self):
        """Deve criar um email com conteúdo válido."""
        email = Email(conteudo="Olá, preciso de suporte técnico.")
        
        assert email.conteudo == "Olá, preciso de suporte técnico."
        assert email.categoria is None
        assert email.resposta_sugerida is None
    
    def test_criar_email_com_categoria(self):
        """Deve criar um email com categoria definida."""
        email = Email(
            conteudo="Teste",
            categoria=CategoriaEmail.PRODUTIVO
        )
        
        assert email.categoria == CategoriaEmail.PRODUTIVO
        assert email.e_produtivo is True
        assert email.e_improdutivo is False
    
    def test_email_vazio_deve_lancar_erro(self):
        """Deve lançar erro ao criar email com conteúdo vazio."""
        with pytest.raises(ValueError, match="não pode estar vazio"):
            Email(conteudo="")
    
    def test_email_apenas_espacos_deve_lancar_erro(self):
        """Deve lançar erro ao criar email apenas com espaços."""
        with pytest.raises(ValueError, match="não pode estar vazio"):
            Email(conteudo="   ")
    
    def test_email_nao_classificado(self):
        """Deve retornar False para esta_classificado quando não há categoria."""
        email = Email(conteudo="Teste")
        
        assert email.esta_classificado is False
    
    def test_email_classificado(self):
        """Deve retornar True para esta_classificado quando há categoria."""
        email = Email(
            conteudo="Teste",
            categoria=CategoriaEmail.IMPRODUTIVO
        )
        
        assert email.esta_classificado is True


class TestCategoriaEmail:
    """Testes para o enum CategoriaEmail."""
    
    def test_categoria_produtivo(self):
        """Deve ter valor correto para PRODUTIVO."""
        assert CategoriaEmail.PRODUTIVO.value == "Produtivo"
    
    def test_categoria_improdutivo(self):
        """Deve ter valor correto para IMPRODUTIVO."""
        assert CategoriaEmail.IMPRODUTIVO.value == "Improdutivo"
