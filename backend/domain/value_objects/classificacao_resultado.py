"""
Value Object para resultado da classificação.

Value Objects são imutáveis e definidos pelo seu valor, não por identidade.
"""

from dataclasses import dataclass, field
from typing import Optional

from domain.entities.email import CategoriaEmail


@dataclass(frozen=True)
class ClassificacaoResultado:
    """
    Value Object imutável para resultado da classificação.
    
    Atributos:
        categoria: Categoria atribuída ao email (Produtivo/Improdutivo)
        confianca: Nível de confiança da classificação (0.0 a 1.0)
        resposta_sugerida: Texto da resposta automática sugerida
        assunto: Assunto detectado do email original (opcional)
        remetente: Remetente detectado do email original (opcional)
        destinatario: Destinatário detectado do email original (opcional)
    
    Raises:
        ValueError: Se a confiança não estiver entre 0 e 1
    """
    categoria: CategoriaEmail
    confianca: float
    resposta_sugerida: str
    assunto: Optional[str] = field(default=None)
    remetente: Optional[str] = field(default=None)
    destinatario: Optional[str] = field(default=None)
    
    def __post_init__(self):
        """Valida os dados do value object após inicialização."""
        if not 0 <= self.confianca <= 1:
            raise ValueError("Confiança deve estar entre 0 e 1")
        
        if not self.resposta_sugerida or not self.resposta_sugerida.strip():
            raise ValueError("Resposta sugerida não pode estar vazia")
    
    @property
    def confianca_percentual(self) -> float:
        """Retorna a confiança em formato percentual (0-100)."""
        return self.confianca * 100
    
    @property
    def alta_confianca(self) -> bool:
        """Retorna True se a confiança é maior que 80%."""
        return self.confianca >= 0.8
