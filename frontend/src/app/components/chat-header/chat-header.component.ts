/**
 * Componente Header do Chat Classificador.
 *
 * Presentational Component que exibe o header do chat
 * com nome e ícone de IA.
 */

import { Component, ChangeDetectionStrategy } from '@angular/core';

@Component({
    selector: 'app-chat-header',
    standalone: true,
    template: `
        <header class="chat-header">
            <div class="header-content">
                <span class="ai-icon">🤖</span>
                <h1 class="header-title">Classificador de Emails</h1>
            </div>
        </header>
    `,
    styles: [`
        .chat-header {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1rem 1.5rem;
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border-bottom: 1px solid #475569;
        }

        .header-content {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .ai-icon {
            font-size: 1.75rem;
            line-height: 1;
        }

        .header-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: #f8fafc;
            margin: 0;
            letter-spacing: -0.025em;
        }

        @media (max-width: 640px) {
            .chat-header {
                padding: 0.875rem 1rem;
            }

            .ai-icon {
                font-size: 1.5rem;
            }

            .header-title {
                font-size: 1.125rem;
            }
        }
    `],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class ChatHeaderComponent { }
