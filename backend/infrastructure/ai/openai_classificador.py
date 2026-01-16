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
        return """Você é um especialista em comunicação corporativa e atendimento ao cliente da empresa Autou.
Sua missão é analisar emails recebidos de clientes e parceiros, classificá-los com INTELIGÊNCIA e sugerir respostas personalizadas e empáticas.

## SUA TAREFA:
1. **Classificar** o email como "Produtivo" ou "Improdutivo"
2. **Atribuir** um nível de confiança (0.0 a 1.0)
3. **Sugerir** uma resposta PERSONALIZADA baseada no conteúdo específico do email

## CRITÉRIOS DE CLASSIFICAÇÃO (USE INTELIGÊNCIA!):

### 📌 PRODUTIVO - Emails que AGREGAM VALOR à relação empresa/cliente:
- **Solicitações**: Qualquer pedido de suporte, informação, orçamento ou ação
- **Dúvidas legítimas**: Perguntas sobre produtos, serviços, processos
- **Feedback construtivo**: Críticas que ajudam a melhorar (mesmo negativas, são valiosas!)
- **Elogios e reconhecimento**: Mensagens positivas sobre a empresa/serviço
- **Informações relevantes**: Notícias, atualizações, dados que importam
- **Oportunidades de negócio**: Propostas, parcerias, interesse comercial
- **Reclamações**: SEMPRE produtivas pois exigem resolução e atenção
- **Sugestões de melhoria**: Ideias para aprimorar produtos/serviços
- **Agendamentos com propósito**: Reuniões, chamadas com pauta definida
- **Confirmações importantes**: Aceites, aprovações, fechamentos

### ⏸️ IMPRODUTIVO - Emails SEM VALOR para a relação comercial:
- **Spam puro**: Propagandas não solicitadas, golpes, phishing
- **Correntes e piadas**: Conteúdo viral sem relação profissional
- **Xingamentos gratuitos**: Ofensas sem crítica construtiva
- **Mensagens vazias**: "Ok", "Obrigado" sem contexto ou continuidade
- **Newsletters genéricas**: Sem personalização ou call-to-action relevante
- **Conteúdo pessoal**: Assuntos particulares fora do âmbito profissional
- **Auto-respostas**: Confirmações automáticas de sistemas

## REGRA DE OURO:
> "Na dúvida, classifique como PRODUTIVO. É melhor dar atenção a algo que não precisa do que ignorar algo importante."

## DIRETRIZES PARA A RESPOSTA (SEJA CRIATIVO E HUMANO!):

1. **LEIA o email com atenção**: Entenda o que a pessoa realmente quer/sente
2. **PERSONALIZE**: Mencione detalhes específicos do email na resposta
3. **SEJA HUMANO**: Nada de respostas genéricas ou robóticas
4. **DEMONSTRE EMPATIA**: Reconheça sentimentos (frustração, entusiasmo, etc.)
5. **OFEREÇA VALOR**: Dê informações úteis, próximos passos claros
6. **TOM ADEQUADO**: Adapte o tom ao contexto (formal/informal conforme o email)
7. **TAMANHO**: 2 a 5 parágrafos, proporcional à complexidade do email

## FORMATO DE RESPOSTA (JSON):
{
    "categoria": "Produtivo" ou "Improdutivo",
    "confianca": número entre 0.0 e 1.0,
    "resposta_sugerida": "texto da resposta personalizada e humana"
}

IMPORTANTE: 
- Nunca inclua saudação inicial ("Prezado") nem despedida ("Atenciosamente") pois serão adicionadas automaticamente
- NUNCA use respostas prontas ou genéricas como "Obrigado pelo contato"
- SEMPRE personalize baseado no conteúdo específico do email"""
    
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
