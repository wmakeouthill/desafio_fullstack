/**
 * Componente principal de Chat para Classificação de Emails.
 *
 * Smart Component que gerencia o estado do chat,
 * mensagens e comunicação com a API.
 */

import { Component, inject, signal, computed, ChangeDetectionStrategy, ElementRef, viewChild, AfterViewChecked } from '@angular/core';
import { EmailService } from '../../services/email.service';
import { ClassificacaoResultado, AIProvider, ProvidersResponse } from '../../models';
import { ChatMessageComponent, ChatMessage } from '../chat-message/chat-message.component';
import { ChatInputComponent } from '../chat-input/chat-input.component';

@Component({
    selector: 'app-email-classifier-chat',
    standalone: true,
    imports: [ChatMessageComponent, ChatInputComponent],
    templateUrl: './email-classifier-chat.component.html',
    styleUrl: './email-classifier-chat.component.scss',
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class EmailClassifierChatComponent implements AfterViewChecked {
    private readonly emailService = inject(EmailService);

    // ViewChild para scroll
    readonly messagesContainer = viewChild<ElementRef>('messagesContainer');

    // State
    readonly mensagens = signal<ChatMessage[]>([]);
    readonly carregando = signal(false);
    readonly providerSelecionado = signal<AIProvider>('openai');
    readonly providers = signal<ProvidersResponse | null>(null);

    private shouldScrollToBottom = false;
    private messageIdCounter = 0;

    readonly temMensagens = computed(() => this.mensagens().length > 0);

    constructor() {
        this.carregarProviders();
    }

    ngAfterViewChecked(): void {
        if (this.shouldScrollToBottom) {
            this.scrollToBottom();
            this.shouldScrollToBottom = false;
        }
    }

    private carregarProviders(): void {
        this.emailService.getProviders().subscribe({
            next: (providers) => {
                this.providers.set(providers);
                this.providerSelecionado.set(providers.default);
            },
            error: () => {
                this.providerSelecionado.set('openai');
            }
        });
    }

    private gerarId(): string {
        return `msg-${++this.messageIdCounter}-${Date.now()}`;
    }

    private scrollToBottom(): void {
        const container = this.messagesContainer();
        if (container) {
            container.nativeElement.scrollTop = container.nativeElement.scrollHeight;
        }
    }

    onProviderChange(provider: AIProvider): void {
        this.providerSelecionado.set(provider);
    }

    onEnviarTexto(data: { conteudo: string; provider: AIProvider }): void {
        // Log no console mostrando qual provider foi selecionado
        console.log(`%c🔵 [Frontend] Enviando classificação por texto`, 'color: #2196F3; font-weight: bold;');
        console.log(`   └─ Provider selecionado: ${data.provider}`);

        // Adiciona mensagem do usuário
        const userMessage: ChatMessage = {
            id: this.gerarId(),
            tipo: 'user',
            conteudo: data.conteudo,
            timestamp: new Date()
        };

        // Adiciona mensagem de loading da IA
        const aiLoadingMessage: ChatMessage = {
            id: this.gerarId(),
            tipo: 'ai',
            provider: data.provider,
            timestamp: new Date(),
            carregando: true,
            emailOriginal: data.conteudo
        };

        this.mensagens.update(msgs => [...msgs, userMessage, aiLoadingMessage]);
        this.carregando.set(true);
        this.shouldScrollToBottom = true;

        this.emailService.classificarPorTexto({
            conteudo: data.conteudo,
            provider: data.provider
        }).subscribe({
            next: (resultado) => this.handleSucesso(resultado, aiLoadingMessage.id, data.provider),
            error: (err) => this.handleErro(err, aiLoadingMessage.id)
        });
    }

    onEnviarArquivo(data: { arquivo: File; provider: AIProvider }): void {
        // Log no console mostrando qual provider foi selecionado
        console.log(`%c🔵 [Frontend] Enviando classificação por arquivo`, 'color: #2196F3; font-weight: bold;');
        console.log(`   ├─ Arquivo: ${data.arquivo.name}`);
        console.log(`   └─ Provider selecionado: ${data.provider}`);

        // Adiciona mensagem do usuário com arquivo
        const userMessage: ChatMessage = {
            id: this.gerarId(),
            tipo: 'user',
            arquivo: {
                nome: data.arquivo.name,
                tamanho: data.arquivo.size
            },
            timestamp: new Date()
        };

        // Adiciona mensagem de loading da IA
        const aiLoadingMessage: ChatMessage = {
            id: this.gerarId(),
            tipo: 'ai',
            provider: data.provider,
            timestamp: new Date(),
            carregando: true
        };

        this.mensagens.update(msgs => [...msgs, userMessage, aiLoadingMessage]);
        this.carregando.set(true);
        this.shouldScrollToBottom = true;

        this.emailService.classificarPorArquivo(data.arquivo, data.provider).subscribe({
            next: (resultado) => this.handleSucesso(resultado, aiLoadingMessage.id, data.provider),
            error: (err) => this.handleErro(err, aiLoadingMessage.id)
        });
    }

    private handleSucesso(resultado: ClassificacaoResultado, messageId: string, provider: AIProvider): void {
        // Log no console mostrando qual modelo foi usado
        console.log(`%c✅ [Frontend] Resposta gerada com: ${resultado.modelo_usado || 'N/A'}`, 'color: #4CAF50; font-weight: bold;');
        console.log(`   ├─ Provider: ${provider}`);
        console.log(`   ├─ Modelo: ${resultado.modelo_usado}`);
        console.log(`   ├─ Categoria: ${resultado.categoria}`);
        console.log(`   └─ Confiança: ${(resultado.confianca * 100).toFixed(0)}%`);

        this.mensagens.update(msgs =>
            msgs.map(msg =>
                msg.id === messageId
                    ? { ...msg, carregando: false, resultado, provider }
                    : msg
            )
        );
        this.carregando.set(false);
        this.shouldScrollToBottom = true;
    }

    private handleErro(error: any, messageId: string): void {
        const mensagemErro = error.error?.detail || 'Erro ao classificar email. Tente novamente.';

        // Atualiza a mensagem de loading para mostrar erro
        this.mensagens.update(msgs =>
            msgs.map(msg =>
                msg.id === messageId
                    ? {
                        ...msg,
                        carregando: false,
                        resultado: {
                            categoria: 'Improdutivo' as const,
                            confianca: 0,
                            resposta_sugerida: `❌ Erro: ${mensagemErro}`
                        }
                    }
                    : msg
            )
        );
        this.carregando.set(false);
    }
}
