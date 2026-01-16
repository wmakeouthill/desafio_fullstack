/**
 * Componente de Upload e Classificação de Emails.
 *
 * Smart Component responsável por gerenciar o estado e a lógica
 * de classificação de emails via texto ou arquivo.
 */

import { Component, inject, signal, computed, ChangeDetectionStrategy } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { EmailService } from '../../services/email.service';
import {
    ClassificacaoResultado,
    AIProvider,
    ProvidersResponse
} from '../../models';
import { ResultadoClassificacaoComponent } from '../resultado-classificacao/resultado-classificacao.component';

@Component({
    selector: 'app-email-upload',
    standalone: true,
    imports: [FormsModule, ResultadoClassificacaoComponent],
    templateUrl: './email-upload.component.html',
    styleUrl: './email-upload.component.scss',
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class EmailUploadComponent {
    // Injeção via inject()
    private readonly emailService = inject(EmailService);

    // State com Signals
    readonly conteudoEmail = signal('');
    readonly arquivoSelecionado = signal<File | null>(null);
    readonly carregando = signal(false);
    readonly resultado = signal<ClassificacaoResultado | null>(null);
    readonly erro = signal<string | null>(null);
    readonly providerSelecionado = signal<AIProvider>('openai');
    readonly providers = signal<ProvidersResponse | null>(null);

    // Computeds
    readonly podeEnviar = computed(() =>
        !this.carregando() &&
        (this.conteudoEmail().trim().length > 0 || this.arquivoSelecionado() !== null)
    );

    readonly modoUpload = computed(() => this.arquivoSelecionado() !== null);

    readonly providersDisponiveis = computed(() => {
        const p = this.providers();
        if (!p) return [];

        const lista: { value: AIProvider; label: string; available: boolean; model: string }[] = [];

        if (p.providers.openai) {
            lista.push({
                value: 'openai',
                label: 'OpenAI GPT',
                available: p.providers.openai.available,
                model: p.providers.openai.model
            });
        }

        if (p.providers.gemini) {
            lista.push({
                value: 'gemini',
                label: 'Google Gemini',
                available: p.providers.gemini.available,
                model: p.providers.gemini.model
            });
        }

        return lista;
    });

    constructor() {
        this.carregarProviders();
    }

    private carregarProviders(): void {
        this.emailService.getProviders().subscribe({
            next: (providers) => {
                this.providers.set(providers);
                this.providerSelecionado.set(providers.default);
            },
            error: () => {
                // Fallback para OpenAI se não conseguir carregar providers
                this.providerSelecionado.set('openai');
            }
        });
    }

    onArquivoSelecionado(event: Event): void {
        const input = event.target as HTMLInputElement;
        if (input.files && input.files.length > 0) {
            const arquivo = input.files[0];

            // Validar extensão
            const extensao = arquivo.name.split('.').pop()?.toLowerCase();
            if (extensao !== 'txt' && extensao !== 'pdf') {
                this.erro.set('Formato não suportado. Use arquivos .txt ou .pdf');
                return;
            }

            // Validar tamanho (5MB)
            if (arquivo.size > 5 * 1024 * 1024) {
                this.erro.set('Arquivo muito grande. Tamanho máximo: 5MB');
                return;
            }

            this.arquivoSelecionado.set(arquivo);
            this.conteudoEmail.set('');
            this.erro.set(null);
        }
    }

    limparArquivo(): void {
        this.arquivoSelecionado.set(null);
    }

    limparResultado(): void {
        this.resultado.set(null);
        this.erro.set(null);
    }

    onProviderChange(provider: AIProvider): void {
        this.providerSelecionado.set(provider);
    }

    enviar(): void {
        this.carregando.set(true);
        this.erro.set(null);
        this.resultado.set(null);

        const arquivo = this.arquivoSelecionado();
        const provider = this.providerSelecionado();

        if (arquivo) {
            this.emailService.classificarPorArquivo(arquivo, provider).subscribe({
                next: (res) => this.handleSucesso(res),
                error: (err) => this.handleErro(err)
            });
        } else {
            this.emailService.classificarPorTexto({
                conteudo: this.conteudoEmail(),
                provider: provider
            }).subscribe({
                next: (res) => this.handleSucesso(res),
                error: (err) => this.handleErro(err)
            });
        }
    }

    private handleSucesso(resultado: ClassificacaoResultado): void {
        this.resultado.set(resultado);
        this.carregando.set(false);
    }

    private handleErro(error: any): void {
        const mensagem = error.error?.detail || 'Erro ao classificar email. Tente novamente.';
        this.erro.set(mensagem);
        this.carregando.set(false);
    }
}
