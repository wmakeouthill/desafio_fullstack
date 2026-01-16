"""
Controller de Emails - API REST.

Endpoints para classificação de emails via texto ou arquivo.
"""

from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, status

from application.dtos.email_dto import (
    ClassificarEmailRequest,
    ClassificarEmailResponse,
    ClassificarArquivoResponse,
)
from domain.exceptions import (
    ConteudoInvalidoException,
    ClassificacaoException,
    ArquivoInvalidoException,
    FormatoNaoSuportadoException,
)
from interfaces.api.v1.dependencies import (
    get_classificar_email_use_case,
    get_classificar_arquivo_use_case,
    get_available_providers,
)


router = APIRouter(prefix="/emails", tags=["Emails"])


@router.get(
    "/providers",
    status_code=status.HTTP_200_OK,
    summary="Listar provedores de IA",
    description="Retorna os provedores de IA disponíveis e seus status."
)
async def listar_providers():
    """
    Endpoint para listar os provedores de IA disponíveis.
    
    Retorna o provider padrão e o status de cada provider configurado.
    """
    return get_available_providers()


@router.post(
    "/classificar",
    response_model=ClassificarEmailResponse,
    status_code=status.HTTP_200_OK,
    summary="Classificar email por texto",
    description="Classifica o conteúdo de um email e sugere uma resposta automática."
)
async def classificar_email(
    request: ClassificarEmailRequest
) -> ClassificarEmailResponse:
    """
    Endpoint para classificar email a partir do texto.
    
    - **conteudo**: Texto do email a ser classificado
    - **provider**: Provedor de IA a usar (openai ou gemini). Opcional.
    
    Retorna a categoria (Produtivo/Improdutivo), nível de confiança e resposta sugerida.
    """
    try:
        use_case = get_classificar_email_use_case(provider=request.provider)
        return use_case.executar(request)
    
    except ConteudoInvalidoException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ClassificacaoException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )


@router.post(
    "/classificar/arquivo",
    response_model=ClassificarArquivoResponse,
    status_code=status.HTTP_200_OK,
    summary="Classificar email por arquivo",
    description="Classifica um email a partir de um arquivo .txt ou .pdf."
)
async def classificar_arquivo(
    arquivo: UploadFile = File(
        ...,
        description="Arquivo .txt ou .pdf contendo o email"
    ),
    provider: Optional[str] = Query(
        default=None,
        description="Provedor de IA: 'openai' ou 'gemini'"
    )
) -> ClassificarArquivoResponse:
    """
    Endpoint para classificar email a partir de um arquivo.
    
    - **arquivo**: Arquivo .txt ou .pdf contendo o email
    - **provider**: Provedor de IA a usar (openai ou gemini). Opcional.
    
    Retorna a categoria, nível de confiança, resposta sugerida e nome do arquivo.
    """
    # Validar tamanho do arquivo (máximo 5MB)
    MAX_SIZE = 5 * 1024 * 1024  # 5MB
    conteudo = await arquivo.read()
    
    if len(conteudo) > MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Arquivo muito grande. Tamanho máximo: 5MB"
        )
    
    if len(conteudo) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo está vazio"
        )
    
    try:
        use_case = get_classificar_arquivo_use_case(provider=provider)
        return use_case.executar(
            arquivo=conteudo,
            nome_arquivo=arquivo.filename or "arquivo_sem_nome"
        )
    
    except FormatoNaoSuportadoException as e:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(e)
        )
    except ArquivoInvalidoException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ConteudoInvalidoException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ClassificacaoException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Verifica se o serviço está funcionando."
)
async def health_check():
    """Endpoint de health check."""
    return {"status": "healthy", "service": "email-classifier"}
