"""
Implementação do Classificador usando OpenAI GPT.

Esta classe implementa a interface ClassificadorPort usando a API da OpenAI.
"""

import json
import logging
from typing import Optional

from openai import OpenAI

from application.ports.classificador_port import ClassificadorPort
from domain.value_objects.classificacao_resultado import ClassificacaoResultado
from domain.entities.email import CategoriaEmail
from domain.exceptions import ClassificacaoException
from infrastructure.nlp.preprocessador import PreprocessadorTexto


logger = logging.getLogger(__name__)


class OpenAIClassificador(ClassificadorPort):
    """
    Implementação do classificador usando OpenAI GPT.
    
    Classifica emails em Produtivo/Improdutivo e gera respostas automáticas
    utilizando a API da OpenAI.
    """
    
    def __init__(
        self,
        api_key: str,
        preprocessador: Optional[PreprocessadorTexto] = None,
        modelo: str = "gpt-4o-mini",
        max_tokens: int = 4000
    ):
        """
        Inicializa o classificador.
        
        Args:
            api_key: Chave de API da OpenAI
            preprocessador: Instância do preprocessador de texto (opcional)
            modelo: Modelo da OpenAI a ser usado
        """
        self._client = OpenAI(api_key=api_key)
        self._preprocessador = preprocessador or PreprocessadorTexto()
        self._modelo = modelo
        self._max_tokens = max_tokens
    
    def classificar(self, conteudo: str) -> ClassificacaoResultado:
        """
        Classifica o conteúdo do email usando a API da OpenAI.
        
        Args:
            conteudo: Texto do email a ser classificado
            
        Returns:
            ClassificacaoResultado com categoria, confiança e resposta
            
        Raises:
            ClassificacaoException: Se ocorrer erro na API
        """
        try:
            logger.info(f"🤖 [OpenAI] Iniciando classificação com modelo: {self._modelo}")
            
            # Pré-processar texto
            texto_processado = self._preprocessador.processar(conteudo)
            
            # Chamar API
            resposta = self._chamar_api(texto_processado)
            
            # Converter resposta
            resultado = self._converter_resposta(resposta)
            
            logger.info(f"✅ [OpenAI] Resposta gerada com: {self._modelo} | Categoria: {resultado.categoria.value} | Confiança: {resultado.confianca:.2f}")
            
            return resultado
        
        except Exception as e:
            logger.error(f"❌ [OpenAI] Erro ao classificar email com modelo {self._modelo}: {e}")
            raise ClassificacaoException(f"Falha na classificação: {str(e)}")
    
    def get_modelo(self) -> str:
        """Retorna o nome do modelo de IA sendo utilizado."""
        return self._modelo
    
    def get_provider(self) -> str:
        """Retorna o nome do provedor de IA."""
        return "openai"
    
    def _chamar_api(self, texto: str) -> dict:
        """
        Realiza a chamada à API da OpenAI.
        
        Args:
            texto: Texto preprocessado do email
            
        Returns:
            Dicionário com a resposta da API
        """
        system_prompt = self._criar_system_prompt()
        user_prompt = self._criar_user_prompt(texto)
        
        response = self._client.chat.completions.create(
            model=self._modelo,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=self._max_tokens,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
    
    def _criar_system_prompt(self) -> str:
        """Cria o prompt de sistema para a classificação."""
        return """Você é um especialista em atendimento ao cliente da empresa Autou, uma empresa do setor financeiro.
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

## FORMATO DE RESPOSTA (JSON):
{
    "categoria": "Produtivo" ou "Improdutivo",
    "confianca": número entre 0.0 e 1.0,
    "resposta_sugerida": "resposta apropriada ao contexto",
    "assunto": "assunto extraído do email ou null",
    "remetente": "remetente extraído ou null",
    "destinatario": "destinatário extraído ou null"
}

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
- Não faça suposições sobre o contexto além do que está escrito"""
    
    def _criar_user_prompt(self, texto: str) -> str:
        """Cria o prompt do usuário com o conteúdo do email."""
        return f"""Analise o email abaixo com INTELIGÊNCIA. Entenda o contexto, o tom, a intenção do remetente e o valor que essa mensagem traz para a relação empresa/cliente.

═══════════════════════════════════════
EMAIL RECEBIDO:
═══════════════════════════════════════
{texto}
═══════════════════════════════════════

Retorne sua análise em JSON com:
- Classificação inteligente (lembre: críticas construtivas, elogios, feedback = PRODUTIVO)
- Resposta PERSONALIZADA que demonstre que você leu e entendeu o email
- Tom adequado ao contexto da mensagem"""
    
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
            # Default para produtivo em caso de resposta inesperada
            categoria = CategoriaEmail.PRODUTIVO
        
        confianca = float(resposta.get("confianca", 0.5))
        confianca = max(0.0, min(1.0, confianca))  # Garantir range válido
        
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
