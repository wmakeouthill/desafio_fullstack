/**
 * Componente de Mensagem do Chat.
 *
 * Presentational Component que exibe uma mensagem no chat,
 * podendo ser do usuário ou da IA.
 */

import { Component, input, output, signal, computed, ChangeDetectionStrategy } from '@angular/core';
import { PercentPipe } from '@angular/common';
import { ClassificacaoResultado, AIProvider } from '../../models';
import { EmailPreviewModalComponent } from '../email-preview-modal/email-preview-modal.component';

export interface ChatMessage {
    id: string;
    tipo: 'user' | 'ai';
    conteudo?: string;
    arquivo?: { nome: string; tamanho: number };
    resultado?: ClassificacaoResultado;
    provider?: AIProvider;
    timestamp: Date;
    carregando?: boolean;
    emailOriginal?: string;
}

@Component({
    selector: 'app-chat-message',
    standalone: true,
    imports: [PercentPipe, EmailPreviewModalComponent],
    templateUrl: './chat-message.component.html',
    styleUrl: './chat-message.component.scss',
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class ChatMessageComponent {
    readonly message = input.required<ChatMessage>();
    readonly copiarResposta = output<string>();

    readonly copiado = signal(false);
    readonly modalAberto = signal(false);

    readonly categoriaClasse = computed(() =>
        this.message().resultado?.categoria.toLowerCase() ?? ''
    );

    readonly providerIcon = computed(() =>
        this.message().provider === 'gemini' ? '✨' : '🤖'
    );

    readonly providerLabel = computed(() =>
        this.message().provider === 'gemini' ? 'Gemini' : 'OpenAI'
    );

    readonly nomeFuncionario = 'Ana Carolina Santos';

    async copiar(): Promise<void> {
        const resposta = this.gerarTextoEmail();
        if (!resposta) return;

        try {
            await navigator.clipboard.writeText(resposta);
            this.copiado.set(true);
            setTimeout(() => this.copiado.set(false), 2000);
        } catch (error) {
            console.error('Erro ao copiar:', error);
        }
    }

    gerarTextoEmail(): string {
        const resposta = this.message().resultado?.resposta_sugerida;
        if (!resposta) return '';

        return `${resposta}

Atenciosamente,

${this.nomeFuncionario}
Equipe de Soluções de IA para Comunicação - Autou`;
    }

    abrirModal(): void {
        this.modalAberto.set(true);
    }

    fecharModal(): void {
        this.modalAberto.set(false);
    }

    formatarHora(): string {
        return this.message().timestamp.toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}
