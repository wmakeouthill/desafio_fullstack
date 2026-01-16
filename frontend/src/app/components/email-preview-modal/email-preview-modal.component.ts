/**
 * Componente de Modal para Preview de Email.
 *
 * Exibe o email formatado de forma profissional em um modal,
 * simulando a visualização de um cliente de email corporativo.
 */

import { Component, input, output, signal, computed, ChangeDetectionStrategy } from '@angular/core';
import { ClassificacaoResultado } from '../../models';

@Component({
    selector: 'app-email-preview-modal',
    standalone: true,
    imports: [],
    templateUrl: './email-preview-modal.component.html',
    styleUrl: './email-preview-modal.component.scss',
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class EmailPreviewModalComponent {
    /** Resultado da classificação com a resposta sugerida */
    readonly resultado = input.required<ClassificacaoResultado>();

    /** Conteúdo original do email para extrair assunto */
    readonly emailOriginal = input<string>();

    /** Evento emitido ao fechar o modal */
    readonly fechar = output<void>();

    /** Estado de cópia */
    readonly copiado = signal(false);

    /** Dados do remetente (empresa) */
    readonly remetente = {
        nome: 'Ana Carolina Santos',
        email: 'ana.santos@autou.com.br',
        cargo: 'Especialista em Atendimento',
        departamento: 'Equipe de Soluções de IA para Comunicação',
        empresa: 'Autou',
        telefone: '(11) 3456-7890'
    };

    /** Extrai o assunto do resultado da IA ou do email original */
    readonly assuntoEmail = computed(() => {
        const resultado = this.resultado();
        
        // Prioridade 1: Assunto extraído pela IA
        if (resultado.assunto) {
            return `Re: ${resultado.assunto}`;
        }
        
        // Prioridade 2: Tentar extrair do email original
        const original = this.emailOriginal();
        if (original) {
            const padroes = [
                /^Assunto:\s*(.+)$/im,
                /^Subject:\s*(.+)$/im,
                /^Ref:\s*(.+)$/im,
                /^RE:\s*(.+)$/im,
                /^FW:\s*(.+)$/im,
                /^Enc:\s*(.+)$/im
            ];

            for (const padrao of padroes) {
                const match = original.match(padrao);
                if (match && match[1]) {
                    return `Re: ${match[1].trim()}`;
                }
            }
        }

        // Prioridade 3: Fallback para assunto padrão
        return this.gerarAssuntoPadrao();
    });

    /** Extrai o remetente do resultado da IA */
    readonly remetenteOriginal = computed(() => {
        const resultado = this.resultado();
        return resultado.remetente || null;
    });

    /** Extrai o destinatário do resultado da IA */
    readonly destinatarioOriginal = computed(() => {
        const resultado = this.resultado();
        return resultado.destinatario || null;
    });

    private gerarAssuntoPadrao(): string {
        if (this.resultado().categoria === 'Produtivo') {
            return 'Re: Solicitação Recebida - Em Atendimento';
        }
        return 'Re: Mensagem Recebida - Agradecemos o Contato';
    }

    /** Data/hora atual formatada */
    get dataHoraAtual(): string {
        return new Date().toLocaleDateString('pt-BR', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    /** Fecha o modal */
    onFechar(): void {
        this.fechar.emit();
    }

    /** Fecha o modal ao clicar no backdrop */
    onBackdropClick(event: MouseEvent): void {
        if ((event.target as HTMLElement).classList.contains('modal-backdrop')) {
            this.onFechar();
        }
    }

    /** Copia o email completo */
    async copiarEmail(): Promise<void> {
        const emailCompleto = this.gerarEmailTexto();

        try {
            await navigator.clipboard.writeText(emailCompleto);
            this.copiado.set(true);
            setTimeout(() => this.copiado.set(false), 2500);
        } catch (error) {
            console.error('Erro ao copiar email:', error);
        }
    }

    /** Gera o texto da resposta para cópia - apenas o conteúdo, sem saudação nem assinatura */
    gerarEmailTexto(): string {
        return this.resultado().resposta_sugerida;
    }
}
