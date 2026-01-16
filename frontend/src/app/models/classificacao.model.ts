/**
 * Tipos e interfaces para classificação de emails.
 */

export type CategoriaEmail = 'Produtivo' | 'Improdutivo';
export type AIProvider = 'openai' | 'gemini';

export interface ClassificacaoResultado {
    categoria: CategoriaEmail;
    confianca: number;
    resposta_sugerida: string;
    assunto?: string | null;
    remetente?: string | null;
    destinatario?: string | null;
    modelo_usado?: string | null;
}

export interface ClassificarEmailRequest {
    conteudo: string;
    provider?: AIProvider;
}

export interface ClassificarArquivoResponse extends ClassificacaoResultado {
    nome_arquivo: string;
}

export interface ProviderInfo {
    available: boolean;
    model: string;
    fallback_models?: string[];
    max_tokens?: number;
}

export interface ProvidersResponse {
    default: AIProvider;
    providers: {
        openai: ProviderInfo;
        gemini: ProviderInfo;
    };
}
