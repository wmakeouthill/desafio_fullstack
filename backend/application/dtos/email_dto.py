"""
DTOs (Data Transfer Objects) para operações com emails.

DTOs são usados para transferir dados entre camadas da aplicação.
"""

from pydantic import BaseModel, Field


from typing import Optional, Literal


class ClassificarEmailRequest(BaseModel):
    """Request para classificação de email via texto."""
    
    conteudo: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Conteúdo do email a ser classificado"
    )
    provider: Optional[Literal["openai", "gemini"]] = Field(
        default=None,
        description="Provedor de IA a usar (openai ou gemini). Se não informado, usa o padrão do servidor."
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "conteudo": "Olá, gostaria de saber o status do meu chamado #12345. Aguardo retorno.",
                "provider": "openai"
            }
        }


class ClassificarEmailResponse(BaseModel):
    """Response da classificação de email."""
    
    categoria: str = Field(
        ...,
        description="Categoria atribuída: Produtivo ou Improdutivo"
    )
    confianca: float = Field(
        ...,
        ge=0,
        le=1,
        description="Nível de confiança da classificação (0 a 1)"
    )
    resposta_sugerida: str = Field(
        ...,
        description="Resposta automática sugerida para o email"
    )
    assunto: Optional[str] = Field(
        default=None,
        description="Assunto detectado do email original"
    )
    remetente: Optional[str] = Field(
        default=None,
        description="Remetente detectado do email original"
    )
    destinatario: Optional[str] = Field(
        default=None,
        description="Destinatário detectado do email original"
    )
    modelo_usado: Optional[str] = Field(
        default=None,
        description="Modelo de IA utilizado para gerar a resposta (ex: gpt-3.5-turbo, gemini-1.5-flash)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "categoria": "Produtivo",
                "confianca": 0.95,
                "resposta_sugerida": "Prezado(a), agradecemos o contato. Seu chamado #12345 está em análise e retornaremos em breve.",
                "assunto": "Solicitação de Suporte",
                "remetente": "João Silva <joao@empresa.com>",
                "destinatario": "suporte@autou.com.br",
                "modelo_usado": "gpt-3.5-turbo"
            }
        }


class ClassificarArquivoResponse(ClassificarEmailResponse):
    """Response da classificação de email via arquivo."""
    
    nome_arquivo: str = Field(
        ...,
        description="Nome do arquivo processado"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "categoria": "Produtivo",
                "confianca": 0.92,
                "resposta_sugerida": "Prezado(a), recebemos sua solicitação e estamos analisando.",
                "nome_arquivo": "email_cliente.txt",
                "assunto": "Dúvida sobre fatura",
                "remetente": "cliente@email.com",
                "destinatario": "financeiro@autou.com.br",
                "modelo_usado": "gemini-1.5-flash"
            }
        }
