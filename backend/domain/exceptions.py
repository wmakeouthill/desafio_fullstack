"""
Exceções de Domínio.

Exceções específicas do domínio que representam violações de regras de negócio.
"""


class DomainException(Exception):
    """Exceção base do domínio. Todas as exceções de domínio herdam desta."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ConteudoInvalidoException(DomainException):
    """Exceção para quando o conteúdo do email é inválido."""
    
    def __init__(self, message: str = "Conteúdo do email inválido"):
        super().__init__(message)


class ClassificacaoException(DomainException):
    """Exceção para erros durante o processo de classificação."""
    
    def __init__(self, message: str = "Erro ao classificar email"):
        super().__init__(message)


class ArquivoInvalidoException(DomainException):
    """Exceção para quando o arquivo enviado é inválido."""
    
    def __init__(self, message: str = "Arquivo inválido"):
        super().__init__(message)


class FormatoNaoSuportadoException(DomainException):
    """Exceção para formatos de arquivo não suportados."""
    
    def __init__(self, formato: str):
        message = f"Formato '{formato}' não é suportado. Use .txt ou .pdf"
        super().__init__(message)
