/**
 * Componente de Exibição do Resultado da Classificação.
 *
 * Presentational Component que exibe o resultado da classificação
 * e permite copiar a resposta sugerida.
 */

import { Component, input, output, signal, ChangeDetectionStrategy } from '@angular/core';
import { PercentPipe } from '@angular/common';
import { ClassificacaoResultado, AIProvider } from '../../models';

@Component({
    selector: 'app-resultado-classificacao',
    standalone: true,
    imports: [PercentPipe],
    templateUrl: './resultado-classificacao.component.html',
    styleUrl: './resultado-classificacao.component.scss',
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class ResultadoClassificacaoComponent {
    // Inputs com signal (sintaxe moderna)
    readonly resultado = input.required<ClassificacaoResultado>();
    readonly provider = input<AIProvider>('openai');

    // Outputs
    readonly novaClassificacao = output<void>();

    // State
    readonly copiado = signal(false);

    /**
     * Copia a resposta sugerida para a área de transferência.
     */
    async copiarResposta(): Promise<void> {
        try {
            await navigator.clipboard.writeText(this.resultado().resposta_sugerida);
            this.copiado.set(true);

            // Resetar após 2 segundos
            setTimeout(() => this.copiado.set(false), 2000);
        } catch (error) {
            console.error('Erro ao copiar:', error);
        }
    }

    /**
     * Emite evento para nova classificação.
     */
    classificarNovamente(): void {
        this.novaClassificacao.emit();
    }

    /**
     * Retorna a cor baseada na categoria.
     */
    get categoriaClasse(): string {
        return this.resultado().categoria.toLowerCase();
    }

    /**
     * Retorna o ícone baseado no provider.
     */
    get providerIcon(): string {
        return this.provider() === 'gemini' ? '✨' : '🤖';
    }
}
