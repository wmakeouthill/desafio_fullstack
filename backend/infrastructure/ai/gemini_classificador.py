"""
Implementação do Classificador usando Google Gemini.

Esta classe implementa a interface ClassificadorPort usando a API do Google Gemini.
"""

import json
import logging
from typing import Optional

import google.generativeai as genai

from application.ports.classificador_port import ClassificadorPort
from domain.value_objects.classificacao_resultado import ClassificacaoResultado
from domain.entities.email import CategoriaEmail
from domain.exceptions import ClassificacaoException
from infrastructure.nlp.preprocessador import PreprocessadorTexto


logger = logging.getLogger(__name__)


class GeminiClassificador(ClassificadorPort):
    """
    Implementação do classificador usando Google Gemini.
    
    Classifica emails em Produtivo/Improdutivo e gera respostas automáticas
    utilizando a API do Google Gemini.
    """
    
    def __init__(
        self,
        api_key: str,
        preprocessador: Optional[PreprocessadorTexto] = None,
        modelo: str = "gemini-2.5-flash",
        max_tokens: int = 8192
    ):
        """
        Inicializa o classificador.
        
        Args:
            api_key: Chave de API do Google Gemini
            preprocessador: Instância do preprocessador de texto (opcional)
            modelo: Modelo do Gemini a ser usado
        """
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(modelo)
        self._preprocessador = preprocessador or PreprocessadorTexto()
        self._modelo = modelo
        self._max_tokens = max_tokens
    
    def classificar(self, conteudo: str) -> ClassificacaoResultado:
        """
        Classifica o conteúdo do email usando a API do Google Gemini.
        
        Args:
            conteudo: Texto do email a ser classificado
            
        Returns:
            ClassificacaoResultado com categoria, confiança e resposta
            
        Raises:
            ClassificacaoException: Se ocorrer erro na API
        """
        try:
            logger.info(f"🤖 [Gemini] Iniciando classificação com modelo: {self._modelo}")
            
            # Pré-processar texto
            texto_processado = self._preprocessador.processar(conteudo)
            
            # Chamar API
            resposta = self._chamar_api(texto_processado)
            
            # Converter resposta
            resultado = self._converter_resposta(resposta)
            
            logger.info(f"✅ [Gemini] Resposta gerada com: {self._modelo} | Categoria: {resultado.categoria.value} | Confiança: {resultado.confianca:.2f}")
            
            return resultado
        
        except Exception as e:
            logger.error(f"❌ [Gemini] Erro ao classificar email com modelo {self._modelo}: {e}")
            raise ClassificacaoException(f"Falha na classificação: {str(e)}")
    
    def get_modelo(self) -> str:
        """Retorna o nome do modelo de IA sendo utilizado."""
        return self._modelo
    
    def get_provider(self) -> str:
        """Retorna o nome do provedor de IA."""
        return "gemini"
    
    def _chamar_api(self, texto: str) -> dict:
        """
        Realiza a chamada à API do Google Gemini.
        
        Args:
            texto: Texto preprocessado do email
            
        Returns:
            Dicionário com a resposta da API
        """
        prompt = self._criar_prompt(texto)
        
        response = self._model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=self._max_tokens,
            )
        )
        
        # Extrair JSON da resposta
        content = response.text
        
        # Tentar encontrar JSON na resposta
        try:
            # Tentar parse direto
            return json.loads(content)
        except json.JSONDecodeError:
            # Tentar extrair JSON de markdown code block
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
                return json.loads(json_str.strip())
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0]
                return json.loads(json_str.strip())
            else:
                # Fallback para resposta padrão
                logger.warning(f"Não foi possível parsear JSON: {content}")
                return {
                    "categoria": "Produtivo",
                    "confianca": 0.5,
                    "resposta_sugerida": "Obrigado pelo seu email. Retornaremos em breve."
                }
    
    def _criar_prompt(self, texto: str) -> str:
        """Cria o prompt para classificação."""
        return f"""Você é um especialista em atendimento ao cliente da empresa Autou, uma empresa do setor financeiro.
Sua missão é analisar emails recebidos e classificá-los para otimizar o tempo da equipe de suporte.

## CONTEXTO IMPORTANTE:
- A empresa recebe alto volume de emails diariamente
- Precisamos identificar quais emails REQUEREM UMA AÇÃO ou RESPOSTA da equipe
- O email analisado é sempre algo que CHEGOU na caixa de entrada (ou seja, foi RECEBIDO)
- Identifique quem é o REMETENTE (quem enviou) e quem é o DESTINATÁRIO (quem recebeu)

## SUA TAREFA:
1. **Extrair metadados** do email: assunto, remetente e destinatário
2. **Classificar** o email como "Produtivo" ou "Improdutivo"
3. **Atribuir** um nível de confiança (0.0 a 1.0)
4. **Sugerir** uma resposta apropriada (se necessário)

## EXTRAÇÃO DE METADADOS (MUITO IMPORTANTE - EXTRAIA COM PRECISÃO):
- **assunto**: EXTRAIA O ASSUNTO EXATO E COMPLETO do email original. 
  - Procure por "Assunto:", "Subject:", "Ref:", "Re:", "Fwd:" no texto
  - O assunto geralmente aparece no início do email ou nos cabeçalhos
  - Copie o assunto EXATAMENTE como está escrito, sem modificar
  - Exemplo: Se o email tem "Assunto: Próxima Fase | Processo Seletivo AutoU", retorne exatamente "Próxima Fase | Processo Seletivo AutoU"
  - Use null APENAS se realmente não houver assunto identificável
- **remetente**: Extraia quem ENVIOU o email original.
  - Procure por "De:", "From:" no texto
  - Formato: "Nome <email>" ou apenas o nome/email disponível
- **destinatario**: Extraia para quem o email foi ENVIADO.
  - Procure por "Para:", "To:" no texto
  - Use null se não encontrar

## CRITÉRIOS DE CLASSIFICAÇÃO:

### ✅ PRODUTIVO - Emails de CLIENTES que REQUEREM AÇÃO ou RESPOSTA:
- **Solicitações de suporte técnico**: Problemas, bugs, erros no sistema
- **Atualizações sobre casos em aberto**: Follow-up de tickets, pendências
- **Dúvidas sobre o sistema**: Perguntas sobre funcionalidades, uso do produto
- **Reclamações de clientes**: Insatisfações que precisam ser resolvidas
- **Solicitações de informação**: Pedidos de dados, relatórios, esclarecimentos
- **Pedidos de orçamento/proposta**: Interesse comercial direto de clientes

### ❌ IMPRODUTIVO - Emails que NÃO necessitam de ação imediata:
- **Mensagens de felicitações**: Aniversário, Natal, Ano Novo, etc.
- **Agradecimentos simples**: "Obrigado", "Valeu" sem solicitação
- **Newsletters e divulgações**: Anúncios de eventos, cursos, promoções
- **Emails de marketing**: Propagandas, ofertas, convites para eventos
- **Notificações automatizadas**: Lembretes de sistema, avisos de vencimento, boletos
- **Emails de cobrança/financeiro automatizado**: Faturas, lembretes de pagamento
- **Confirmações automáticas de sistemas**: Cadastros, senhas, códigos
- **Spam**: Mensagens não solicitadas
- **Auto-respostas automáticas**: Confirmações de recebimento
- **Correntes e conteúdo viral**: Piadas, memes, etc.

## REGRA PRINCIPAL:
> "Classifique como PRODUTIVO apenas se o email for de um CLIENTE pedindo ajuda, suporte ou informação. Notificações automáticas de sistemas, lembretes, cobranças e marketing são IMPRODUTIVOS."

## EXEMPLOS:
- "Estou com problema no login" → PRODUTIVO (cliente pedindo suporte)
- "Qual o status do meu chamado #123?" → PRODUTIVO (follow-up de cliente)
- "Como faço para exportar relatório?" → PRODUTIVO (dúvida de cliente)
- "Feliz Natal!" → IMPRODUTIVO (felicitação)
- "Obrigado pela ajuda!" → IMPRODUTIVO (agradecimento)
- "Inscreva-se no nosso evento!" → IMPRODUTIVO (marketing)
- "Sua fatura vence dia 20" → IMPRODUTIVO (notificação automática)
- "Lembrete: Declaração Anual" → IMPRODUTIVO (lembrete de sistema)
- "Seu boleto está disponível" → IMPRODUTIVO (notificação financeira)

## CONFIANÇA:
- 0.9 a 1.0: Certeza absoluta da classificação
- 0.7 a 0.89: Alta confiança
- 0.5 a 0.69: Confiança moderada (caso ambíguo)
- Abaixo de 0.5: Baixa confiança (revisar manualmente)

## REGRAS DA RESPOSTA SUGERIDA:
- A resposta deve ser um email COMPLETO e pronto para enviar
- DEVE incluir saudação apropriada no INÍCIO (detecte quem é o remetente do email):
  - Se for pessoa física: "Prezado(a) [Nome REAL extraído]," ou "Olá [Nome REAL],"
  - Se for empresa/equipe: "Prezada Equipe [Nome da Empresa]," ou "Prezados,"
  - Se não souber o nome: "Prezado(a)," ou "Olá,"
- DEVE terminar APENAS com "Atenciosamente," - NADA MAIS após isso!
- Para PRODUTIVO: Resposta útil que ajude a resolver a solicitação
- Para IMPRODUTIVO: Resposta breve e cordial OU apenas "Não é necessário responder este email."

## REGRA CRÍTICA SOBRE DESPEDIDA (OBRIGATÓRIO):
- A resposta DEVE terminar EXATAMENTE com a palavra "Atenciosamente," e PONTO FINAL
- **NUNCA** escreva NADA após "Atenciosamente," - nem nome, nem [Seu Nome], nem assinatura
- **PROIBIDO**: "Atenciosamente, [Seu Nome]" ou "Atenciosamente, Maria" ou qualquer variação
- **CORRETO**: A resposta termina em "Atenciosamente," e nada mais
- A assinatura será adicionada automaticamente pelo sistema

## REGRAS CRÍTICAS (ANTI-ALUCINAÇÃO):
- **NUNCA** invente informações que não estão no email
- **NUNCA** assuma dados como números de protocolo, datas ou valores não mencionados
- **NUNCA** prometa prazos, descontos ou soluções específicas
- **NUNCA** mencione produtos, serviços ou recursos não citados no email
- Se não tiver certeza de algo, use termos genéricos
- Base sua resposta APENAS no conteúdo do email fornecido
- Não faça suposições sobre o contexto além do que está escrito

═══════════════════════════════════════
EMAIL PARA CLASSIFICAR:
═══════════════════════════════════════
{texto}
═══════════════════════════════════════

RESPONDA APENAS com um objeto JSON válido (sem markdown, sem explicações):
{{"categoria": "Produtivo ou Improdutivo", "confianca": número entre 0.0 e 1.0, "resposta_sugerida": "resposta apropriada ao contexto", "assunto": "assunto extraído do email ou null", "remetente": "remetente extraído ou null", "destinatario": "destinatário extraído ou null"}}"""
    
    def _limpar_resposta(self, resposta: str) -> str:
        """
        Remove placeholders e texto após a despedida.
        
        Args:
            resposta: Texto da resposta sugerida
            
        Returns:
            Resposta limpa sem placeholders
        """
        import re
        
        # Padrões para remover após "Atenciosamente," ou "Cordialmente,"
        # Remove: [Seu Nome], [Nome], [Assinatura], ou qualquer nome após a despedida
        padroes_remover = [
            r'(Atenciosamente,?)\s*\[.*?\]',  # [Seu Nome], [Nome], etc
            r'(Cordialmente,?)\s*\[.*?\]',
            r'(Atenciosamente,?)\s+[A-Z][a-záàâãéèêíïóôõöúçñ]+(\s+[A-Z][a-záàâãéèêíïóôõöúçñ]+)*\s*$',  # Nome próprio após
            r'(Cordialmente,?)\s+[A-Z][a-záàâãéèêíïóôõöúçñ]+(\s+[A-Z][a-záàâãéèêíïóôõöúçñ]+)*\s*$',
        ]
        
        resultado = resposta
        for padrao in padroes_remover:
            resultado = re.sub(padrao, r'\1', resultado, flags=re.IGNORECASE | re.MULTILINE)
        
        # Garantir que termina com "Atenciosamente," limpo
        resultado = resultado.strip()
        
        return resultado
    
    def _converter_resposta(self, resposta: dict) -> ClassificacaoResultado:
        """
        Converte a resposta da API para o value object.
        
        Args:
            resposta: Dicionário com a resposta da API
            
        Returns:
            ClassificacaoResultado
        """
        categoria_str = resposta.get("categoria", "").strip()
        
        if categoria_str.lower() == "produtivo":
            categoria = CategoriaEmail.PRODUTIVO
        elif categoria_str.lower() == "improdutivo":
            categoria = CategoriaEmail.IMPRODUTIVO
        else:
            categoria = CategoriaEmail.PRODUTIVO
        
        confianca = float(resposta.get("confianca", 0.5))
        confianca = max(0.0, min(1.0, confianca))
        
        resposta_sugerida = resposta.get(
            "resposta_sugerida",
            "Obrigado pelo seu email. Retornaremos em breve."
        )
        
        # Limpar a resposta: remover [Seu Nome] e variações após "Atenciosamente,"
        resposta_sugerida = self._limpar_resposta(resposta_sugerida)
        
        # Extrair metadados (podem ser null/None)
        assunto = resposta.get("assunto")
        remetente = resposta.get("remetente")
        destinatario = resposta.get("destinatario")
        
        # Limpar valores "null" string
        if assunto and str(assunto).lower() == "null":
            assunto = None
        if remetente and str(remetente).lower() == "null":
            remetente = None
        if destinatario and str(destinatario).lower() == "null":
            destinatario = None
        
        return ClassificacaoResultado(
            categoria=categoria,
            confianca=confianca,
            resposta_sugerida=resposta_sugerida,
            assunto=assunto,
            remetente=remetente,
            destinatario=destinatario
        )
