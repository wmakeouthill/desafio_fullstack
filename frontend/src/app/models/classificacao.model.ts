/**
 * Tipos e interfaces para classificação de emails.
 */

export type CategoriaEmail = 'Produtivo' | 'Improdutivo';
export type AIProvider = 'openai' | 'gemini';

export interface ClassificacaoResultado {
    categoria: CategoriaEmail;
    confianca: number;
    resposta_sugerida: string;
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
}

export interface ProvidersResponse {
    default: AIProvider;
    providers: {
        openai: ProviderInfo;
        gemini: ProviderInfo;
    };
}
