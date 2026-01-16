/**
 * Componente Footer do Chat com Input.
 *
 * Smart Component que gerencia o input de texto/arquivo
 * e seleção de provider de IA.
 */

import { Component, input, output, signal, computed, ChangeDetectionStrategy, HostListener, PLATFORM_ID, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { isPlatformBrowser } from '@angular/common';
import { AIProvider, ProvidersResponse } from '../../models';

@Component({
  selector: 'app-chat-input',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './chat-input.component.html',
  styleUrl: './chat-input.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ChatInputComponent {
  // Injeções
  private readonly platformId = inject(PLATFORM_ID);
  readonly isBrowser = isPlatformBrowser(this.platformId);

  // Inputs
  readonly providers = input<ProvidersResponse | null>(null);
  readonly providerSelecionado = input<AIProvider>('openai');
  readonly carregando = input(false);

  // Outputs
  readonly enviarTexto = output<{ conteudo: string; provider: AIProvider }>();
  readonly enviarArquivo = output<{ arquivo: File; provider: AIProvider }>();
  readonly providerChange = output<AIProvider>();

  // State
  readonly conteudoEmail = signal('');
  readonly arquivoSelecionado = signal<File | null>(null);
  readonly menuProviderAberto = signal(false);
  readonly erro = signal<string | null>(null);

  // Computeds
  readonly podeEnviar = computed(() =>
    !this.carregando() &&
    (this.conteudoEmail().trim().length > 0 || this.arquivoSelecionado() !== null)
  );

  readonly providerAtual = computed(() => {
    const p = this.providers();
    if (!p) return null;

    const provider = this.providerSelecionado();
    if (provider === 'openai' && p.providers.openai) {
      return {
        value: 'openai' as AIProvider,
        label: 'OpenAI GPT',
        model: p.providers.openai.model,
        icon: '🤖'
      };
    }
    if (provider === 'gemini' && p.providers.gemini) {
      return {
        value: 'gemini' as AIProvider,
        label: 'Google Gemini',
        model: p.providers.gemini.model,
        icon: '✨'
      };
    }
    return null;
  });

  readonly providersDisponiveis = computed(() => {
    const p = this.providers();
    if (!p) return [];

    const lista: { value: AIProvider; label: string; available: boolean; model: string; icon: string }[] = [];

    if (p.providers.openai) {
      lista.push({
        value: 'openai',
        label: 'OpenAI GPT',
        available: p.providers.openai.available,
        model: p.providers.openai.model,
        icon: '🤖'
      });
    }

    if (p.providers.gemini) {
      lista.push({
        value: 'gemini',
        label: 'Google Gemini',
        available: p.providers.gemini.available,
        model: p.providers.gemini.model,
        icon: '✨'
      });
    }

    return lista;
  });

  onArquivoSelecionado(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const arquivo = input.files[0];

      const extensao = arquivo.name.split('.').pop()?.toLowerCase();
      const formatosSuportados = ['txt', 'pdf', 'eml', 'msg', 'mbox'];
      if (!extensao || !formatosSuportados.includes(extensao)) {
        this.erro.set('Formato não suportado. Use arquivos .txt, .pdf, .eml, .msg ou .mbox');
        return;
      }

      if (arquivo.size > 5 * 1024 * 1024) {
        this.erro.set('Arquivo muito grande. Tamanho máximo: 5MB');
        return;
      }

      this.arquivoSelecionado.set(arquivo);
      this.conteudoEmail.set('');
      this.erro.set(null);
    }
    // Reset input
    input.value = '';
  }

  limparArquivo(): void {
    this.arquivoSelecionado.set(null);
  }

  toggleMenuProvider(): void {
    this.menuProviderAberto.update(v => !v);
  }

  selecionarProvider(provider: AIProvider): void {
    this.providerChange.emit(provider);
    this.menuProviderAberto.set(false);
  }

  fecharMenu(): void {
    this.menuProviderAberto.set(false);
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: Event): void {
    if (!this.isBrowser) return;

    const target = event.target as HTMLElement;
    const providerSelector = target.closest('.provider-selector');

    if (!providerSelector && this.menuProviderAberto()) {
      this.fecharMenu();
    }
  }

  enviar(): void {
    if (!this.podeEnviar()) return;

    const arquivo = this.arquivoSelecionado();
    const provider = this.providerSelecionado();

    if (arquivo) {
      this.enviarArquivo.emit({ arquivo, provider });
      this.arquivoSelecionado.set(null);
    } else {
      const conteudo = this.conteudoEmail().trim();
      this.enviarTexto.emit({ conteudo, provider });
      this.conteudoEmail.set('');
    }
  }

  onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.enviar();
    }
  }
}
