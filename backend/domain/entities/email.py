"""
Entidade Email - Representa um email a ser classificado.

Esta entidade faz parte da camada Domain e não possui dependências externas.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CategoriaEmail(Enum):
    """Categorias possíveis para classificação de email."""
    PRODUTIVO = "Produtivo"
    IMPRODUTIVO = "Improdutivo"


@dataclass(frozen=True)
class Email:
    """
    Entidade Email - representa um email a ser classificado.
    
    Atributos:
        conteudo: Texto do email a ser classificado
        categoria: Categoria atribuída após classificação (opcional)
        resposta_sugerida: Resposta automática sugerida (opcional)
    
    Raises:
        ValueError: Se o conteúdo estiver vazio ou apenas com espaços
    """
    conteudo: str
    categoria: Optional[CategoriaEmail] = None
    resposta_sugerida: Optional[str] = None
    
    def __post_init__(self):
        """Valida os dados da entidade após inicialização."""
        if not self.conteudo or not self.conteudo.strip():
            raise ValueError("Conteúdo do email não pode estar vazio")
    
    @property
    def esta_classificado(self) -> bool:
        """Retorna True se o email já foi classificado."""
        return self.categoria is not None
    
    @property
    def e_produtivo(self) -> bool:
        """Retorna True se o email é classificado como Produtivo."""
        return self.categoria == CategoriaEmail.PRODUTIVO
    
    @property
    def e_improdutivo(self) -> bool:
        """Retorna True se o email é classificado como Improdutivo."""
        return self.categoria == CategoriaEmail.IMPRODUTIVO
