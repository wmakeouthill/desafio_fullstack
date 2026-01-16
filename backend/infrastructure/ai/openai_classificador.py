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
        modelo: str = "gpt-3.5-turbo"
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
            # Pré-processar texto
            texto_processado = self._preprocessador.processar(conteudo)
            
            # Chamar API
            resposta = self._chamar_api(texto_processado)
            
            # Converter resposta
            return self._converter_resposta(resposta)
        
        except Exception as e:
            logger.error(f"Erro ao classificar email: {e}")
            raise ClassificacaoException(f"Falha na classificação: {str(e)}")
    
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
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
    
    def _criar_system_prompt(self) -> str:
        """Cria o prompt de sistema para a classificação."""
        return """Você é um especialista em atendimento ao cliente da empresa Autou, uma empresa do setor financeiro.
Sua missão é analisar emails recebidos e classificá-los para otimizar o tempo da equipe de suporte.

## CONTEXTO:
A empresa recebe alto volume de emails diariamente. Precisamos identificar quais emails REQUEREM UMA AÇÃO ou RESPOSTA da equipe de suporte.

## SUA TAREFA:
1. **Classificar** o email como "Produtivo" ou "Improdutivo"
2. **Atribuir** um nível de confiança (0.0 a 1.0)
3. **Sugerir** uma resposta apropriada

## CRITÉRIOS DE CLASSIFICAÇÃO:

### ✅ PRODUTIVO - Emails que REQUEREM AÇÃO ou RESPOSTA da equipe:
- **Solicitações de suporte técnico**: Problemas, bugs, erros no sistema
- **Atualizações sobre casos em aberto**: Follow-up de tickets, pendências
- **Dúvidas sobre o sistema**: Perguntas sobre funcionalidades, uso do produto
- **Reclamações**: Insatisfações que precisam ser resolvidas
- **Solicitações de informação**: Pedidos de dados, relatórios, esclarecimentos
- **Pedidos de orçamento/proposta**: Interesse comercial direto

### ❌ IMPRODUTIVO - Emails que NÃO necessitam de ação imediata:
- **Mensagens de felicitações**: Aniversário, Natal, Ano Novo, etc.
- **Agradecimentos simples**: "Obrigado", "Valeu" sem solicitação
- **Newsletters e divulgações**: Anúncios de eventos, cursos, promoções
- **Emails de marketing**: Propagandas, ofertas, convites para eventos
- **Spam**: Mensagens não solicitadas
- **Auto-respostas automáticas**: Confirmações de recebimento
- **Mensagens informativas sem necessidade de resposta**: Avisos gerais
- **Correntes e conteúdo viral**: Piadas, memes, etc.

## REGRA PRINCIPAL:
> "Classifique como PRODUTIVO apenas se o email EXIGE uma ação, resposta ou suporte da equipe. Se for apenas informativo, divulgação, agradecimento ou felicitação, é IMPRODUTIVO."

## EXEMPLOS:
- "Estou com problema no login" → PRODUTIVO (precisa de suporte)
- "Qual o status do meu chamado #123?" → PRODUTIVO (follow-up)
- "Como faço para exportar relatório?" → PRODUTIVO (dúvida)
- "Feliz Natal!" → IMPRODUTIVO (felicitação)
- "Obrigado pela ajuda!" → IMPRODUTIVO (agradecimento)
- "Inscreva-se no nosso evento!" → IMPRODUTIVO (divulgação/marketing)
- "FC Tech Week começa segunda!" → IMPRODUTIVO (newsletter/anúncio)

## CONFIANÇA:
- 0.9 a 1.0: Certeza absoluta da classificação
- 0.7 a 0.89: Alta confiança
- 0.5 a 0.69: Confiança moderada (caso ambíguo)
- Abaixo de 0.5: Baixa confiança (revisar manualmente)

## FORMATO DE RESPOSTA (JSON):
{
    "categoria": "Produtivo" ou "Improdutivo",
    "confianca": número entre 0.0 e 1.0,
    "resposta_sugerida": "resposta apropriada ao contexto"
}

## REGRAS DA RESPOSTA SUGERIDA:
- Para PRODUTIVO: Resposta útil que ajude a resolver a solicitação
- Para IMPRODUTIVO: Resposta cordial e breve (agradecimento, confirmação)
- Pode incluir saudação e despedida
- **NUNCA** coloque nome após a despedida (ex: "Atenciosamente," está OK, "Atenciosamente, João" NÃO)
- Personalize baseado no conteúdo do email"""
    
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
        
        return ClassificacaoResultado(
            categoria=categoria,
            confianca=confianca,
            resposta_sugerida=resposta_sugerida
        )
