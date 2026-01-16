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
        modelo: str = "gemini-1.5-flash"
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
            # Pré-processar texto
            texto_processado = self._preprocessador.processar(conteudo)
            
            # Chamar API
            resposta = self._chamar_api(texto_processado)
            
            # Converter resposta
            return self._converter_resposta(resposta)
        
        except Exception as e:
            logger.error(f"Erro ao classificar email com Gemini: {e}")
            raise ClassificacaoException(f"Falha na classificação: {str(e)}")
    
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
                max_output_tokens=500,
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
        return f"""Você é um especialista em comunicação corporativa e atendimento ao cliente da empresa Autou.
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

IMPORTANTE: 
- Nunca inclua saudação inicial ("Prezado") nem despedida ("Atenciosamente") pois serão adicionadas automaticamente
- NUNCA use respostas prontas ou genéricas como "Obrigado pelo contato"
- SEMPRE personalize baseado no conteúdo específico do email

═══════════════════════════════════════
EMAIL PARA CLASSIFICAR:
═══════════════════════════════════════
{texto}
═══════════════════════════════════════

RESPONDA APENAS com um objeto JSON válido (sem markdown, sem explicações):
{{"categoria": "Produtivo ou Improdutivo", "confianca": número entre 0.0 e 1.0, "resposta_sugerida": "resposta personalizada e humana baseada no email acima"}}"""
    
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
        
        return ClassificacaoResultado(
            categoria=categoria,
            confianca=confianca,
            resposta_sugerida=resposta_sugerida
        )
