# 📧 Email Classifier - Classificador de Emails com IA

> Aplicação web fullstack para classificação automática de emails usando Inteligência Artificial.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Angular](https://img.shields.io/badge/Angular-20+-red.svg)](https://angular.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

---

## 📋 Sobre o Projeto

Solução digital para empresas do setor financeiro que lidam com alto volume de emails diariamente. A aplicação automatiza a leitura e classificação de emails, sugerindo classificações e respostas automáticas, liberando tempo da equipe para atividades mais estratégicas.

### Funcionalidades

- ✅ **Classificação Automática**: Classifica emails em categorias predefinidas (Produtivo/Improdutivo)
- ✅ **Geração de Respostas**: Sugere respostas automáticas baseadas no conteúdo do email
- ✅ **Suporte a Múltiplos Formatos**: Aceita texto direto ou upload de arquivos (.txt, .pdf, .eml, .msg, .mbox)
- ✅ **Interface de Chat**: Experiência de chat interativa com histórico de mensagens
- ✅ **Seleção de Provider de IA**: Escolha entre OpenAI GPT e Google Gemini dinamicamente
- ✅ **Modal de Preview de Email**: Visualização profissional do email formatado com opção de cópia
- ✅ **Interface Moderna**: UI intuitiva e responsiva com Angular 20+ e Signals
- ✅ **API RESTful**: Backend robusto com FastAPI e Clean Architecture
- ✅ **Docker Compose**: Configuração completa para desenvolvimento e produção com hot-reload

### Categorias de Classificação

| Categoria | Descrição | Exemplos |
|-----------|-----------|----------|
| **Produtivo** | Requer ação ou resposta | Suporte técnico, dúvidas, solicitações, atualização sobre casos |
| **Improdutivo** | Não requer ação imediata | Felicitações, agradecimentos, mensagens não relevantes |

### Formatos de Arquivo Suportados

| Formato | Descrição | Extensão |
|---------|-----------|----------|
| **Texto** | Arquivo de texto simples | `.txt` |
| **PDF** | Documento PDF | `.pdf` |
| **Email** | Arquivo de email padrão | `.eml` |
| **Outlook** | Mensagem do Microsoft Outlook | `.msg` |
| **MBOX** | Formato de caixa de correio Unix | `.mbox` |

> **Nota:** Todos os formatos são processados automaticamente, extraindo o conteúdo do email para classificação.

---

## 🛠️ Tecnologias

### Backend

- **Python 3.11+** - Linguagem de programação
- **FastAPI** - Framework web assíncrono de alta performance
- **OpenAI GPT** - API de IA para classificação e geração de respostas
- **Google Gemini** - Alternativa de IA para classificação
- **PyPDF2** - Leitura de arquivos PDF
- **extract-msg** - Leitura de arquivos .msg (Outlook)
- **Pydantic** - Validação de dados e configurações
- **Uvicorn** - Servidor ASGI de alta performance
- **Pytest** - Framework de testes

### Frontend

- **Angular 20+** - Framework moderno de UI
- **TypeScript** - Linguagem tipada
- **SCSS** - Pré-processador CSS
- **Signals** - Gerenciamento de estado reativo
- **Angular SSR** - Server-Side Rendering para melhor performance
- **RxJS** - Programação reativa

### DevOps

- **Docker** - Containerização
- **Docker Compose** - Orquestração de containers

---

## 📐 Arquitetura

O projeto segue os princípios de **Clean Architecture** e **DDD (Domain-Driven Design)**, garantindo separação clara de responsabilidades e alta testabilidade.

### Camadas do Backend

```
┌─────────────────────────────────────┐
│      Interfaces (API REST)          │  ← Controllers, endpoints
├─────────────────────────────────────┤
│      Application (Use Cases)        │  ← Lógica de aplicação
├─────────────────────────────────────┤
│      Domain (Business Rules)        │  ← Entidades, Value Objects
├─────────────────────────────────────┤
│   Infrastructure (Implementations)  │  ← IA, File Readers, NLP
└─────────────────────────────────────┘
```

**Princípios:**

- **Domain**: Contém apenas regras de negócio puras, sem dependências externas
- **Application**: Orquestra os casos de uso, define contratos (ports)
- **Infrastructure**: Implementa os contratos (adapters), integra com APIs externas
- **Interfaces**: Expõe a API REST, valida entrada/saída

### Frontend

Arquitetura baseada em componentes Angular com:

- **Componentes**: Reutilizáveis e isolados
- **Serviços**: Comunicação com API backend
- **Models**: Tipos TypeScript para type-safety
- **SSR**: Server-Side Rendering para melhor SEO e performance

---

## 🚀 Como Executar

### Pré-requisitos

- **Python 3.11+** (para execução local do backend)
- **Node.js 18+** (para execução local do frontend)
- **Docker e Docker Compose** (opcional, para execução via containers)
- Chave de API da **OpenAI** ou **Google Gemini** (pelo menos uma)

### 🐳 Executando com Docker (Recomendado)

A forma mais simples de executar o projeto é usando Docker Compose:

```bash
# Copiar arquivo de variáveis de ambiente
cp .env.example .env

# Editar .env e adicionar suas chaves de API:
# OPENAI_API_KEY=sua_chave_aqui
# GEMINI_API_KEY=sua_chave_aqui (opcional)
# AI_PROVIDER=openai ou gemini

# Executar em modo desenvolvimento (com hot-reload)
docker-compose -f docker-compose.dev.yml up

# Ou executar em modo produção
docker-compose up
```

Após iniciar os containers:

- **Backend**: <http://localhost:8000>
  - Documentação Swagger: <http://localhost:8000/docs>
  - Documentação ReDoc: <http://localhost:8000/redoc>
- **Frontend**: <http://localhost:4200>

### 💻 Executando Localmente

#### Backend

```bash
# Entrar na pasta do backend
cd backend

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente (Windows)
.\venv\Scripts\activate

# Ativar ambiente (Linux/Mac)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
# Criar arquivo .env na raiz do projeto (ou na pasta backend)
# Editar .env e adicionar suas chaves de API

# Executar servidor
uvicorn main:app --reload --port 8000
```

O backend estará disponível em: <http://localhost:8000>

- Documentação Swagger: <http://localhost:8000/docs>
- Documentação ReDoc: <http://localhost:8000/redoc>

### Frontend

```bash
# Entrar na pasta do frontend
cd frontend

# Instalar dependências
npm install

# Executar servidor de desenvolvimento
ng serve --open
```

O frontend estará disponível em: <http://localhost:4200>

### 🎨 Interface de Chat

A aplicação oferece uma interface de chat moderna e interativa:

- **Histórico de Mensagens**: Todas as classificações são mantidas em um histórico conversacional
- **Upload de Arquivos**: Arraste e solte ou selecione arquivos diretamente no chat
- **Seleção de Provider**: Escolha o provedor de IA (OpenAI ou Gemini) antes de cada classificação
- **Preview de Email**: Visualize o email formatado profissionalmente em um modal
- **Cópia Rápida**: Copie a resposta sugerida com um clique
- **Scroll Automático**: O chat rola automaticamente para novas mensagens

---

## 📡 API Endpoints

A API RESTful está documentada automaticamente em `/docs` (Swagger UI) e `/redoc`.

### Principais Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/v1/emails/providers` | Lista provedores de IA disponíveis e seus status |
| `POST` | `/api/v1/emails/classificar` | Classificar email por texto (com parâmetro `provider` opcional) |
| `POST` | `/api/v1/emails/classificar/arquivo` | Classificar email por arquivo (.txt, .pdf, .eml, .msg, .mbox) |
| `GET` | `/api/v1/emails/health` | Health check do serviço |

### Exemplos de Uso

#### 1. Listar Provedores de IA

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/emails/providers"
```

**Response:**
```json
{
  "default": "openai",
  "providers": {
    "openai": {
      "available": true,
      "model": "gpt-3.5-turbo"
    },
    "gemini": {
      "available": true,
      "model": "gemini-1.5-flash"
    }
  }
}
```

#### 2. Classificar por Texto

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/emails/classificar" \
  -H "Content-Type: application/json" \
  -d '{
    "conteudo": "Olá, preciso de ajuda com meu pedido #12345. Quando será entregue?",
    "provider": "openai"
  }'
```

> **Nota:** O parâmetro `provider` é opcional. Se não fornecido, será usado o provider padrão configurado.

**Response:**
```json
{
  "categoria": "Produtivo",
  "confianca": 0.95,
  "resposta_sugerida": "Prezado(a), agradecemos o contato. Vamos verificar o status do seu pedido #12345 e retornaremos em breve com informações sobre a entrega."
}
```

#### 3. Classificar por Arquivo

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/emails/classificar/arquivo?provider=gemini" \
  -F "arquivo=@email.eml"
```

**Response:**
```json
{
  "categoria": "Improdutivo",
  "confianca": 0.88,
  "resposta_sugerida": "Agradecemos sua mensagem de felicitações. Desejamos um ótimo Natal e um próspero Ano Novo!",
  "nome_arquivo": "email.eml"
}
```

> **Formatos Suportados:** `.txt`, `.pdf`, `.eml`, `.msg` (Outlook), `.mbox`
> 
> **Tamanho Máximo:** 5MB por arquivo

### Documentação Interativa

Acesse a documentação interativa da API:

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

---

## 🧪 Testes

O projeto inclui testes unitários e de integração para garantir a qualidade do código.

### Backend

```bash
# Entrar na pasta do backend
cd backend

# Executar todos os testes
pytest

# Executar testes com cobertura de código
pytest --cov=. --cov-report=html

# Executar testes específicos
pytest tests/unit/application/test_classificar_email_use_case.py

# Executar com verbose
pytest -v
```

Os relatórios de cobertura serão gerados em `backend/htmlcov/index.html`.

### Frontend

```bash
# Entrar na pasta do frontend
cd frontend

# Executar testes unitários
npm test

# Executar testes em modo watch
npm test -- --watch
```

---

## 📁 Estrutura de Arquivos

```
desafio_fullstack/
├── backend/                      # Backend FastAPI
│   ├── domain/                   # Camada de domínio (regras de negócio)
│   │   ├── entities/             # Entidades de domínio
│   │   │   └── email.py
│   │   ├── value_objects/        # Objetos de valor
│   │   │   └── classificacao_resultado.py
│   │   └── exceptions.py         # Exceções de domínio
│   ├── application/              # Camada de aplicação
│   │   ├── ports/                # Interfaces (portas)
│   │   ├── dtos/                 # Data Transfer Objects
│   │   └── use_cases/            # Casos de uso
│   ├── infrastructure/           # Camada de infraestrutura
│   │   ├── ai/                   # Implementações de IA
│   │   │   ├── openai_classificador.py
│   │   │   ├── gemini_classificador.py
│   │   │   └── classificador_factory.py
│   │   ├── file_readers/         # Leitores de arquivo
│   │   │   ├── leitor_txt.py     # Arquivos de texto
│   │   │   ├── leitor_pdf.py     # Arquivos PDF
│   │   │   ├── leitor_eml.py     # Arquivos de email (.eml)
│   │   │   ├── leitor_msg.py     # Arquivos Outlook (.msg)
│   │   │   └── leitor_mbox.py    # Arquivos MBOX
│   │   └── nlp/                  # Processamento de linguagem natural
│   │       └── preprocessador.py
│   ├── interfaces/               # Camada de interface
│   │   └── api/v1/               # API REST
│   │       └── email_controller.py
│   ├── config/                   # Configurações
│   │   └── settings.py
│   ├── tests/                    # Testes
│   │   ├── unit/                 # Testes unitários
│   │   └── integration/          # Testes de integração
│   ├── main.py                   # Entry point
│   ├── requirements.txt          # Dependências Python
│   └── Dockerfile                # Dockerfile do backend
│
├── frontend/                     # Frontend Angular
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/       # Componentes Angular
│   │   │   │   ├── email-classifier-chat/    # Interface de chat principal
│   │   │   │   ├── email-upload/             # Upload de emails
│   │   │   │   ├── email-preview-modal/       # Modal de preview de email
│   │   │   │   ├── resultado-classificacao/   # Exibição de resultados
│   │   │   │   ├── chat-message/              # Componente de mensagem do chat
│   │   │   │   ├── chat-input/                # Input do chat
│   │   │   │   ├── chat-header/               # Cabeçalho do chat
│   │   │   │   └── ...
│   │   │   ├── services/         # Serviços HTTP
│   │   │   │   └── email.service.ts
│   │   │   ├── models/           # Interfaces TypeScript
│   │   │   └── ...
│   │   └── environments/         # Variáveis de ambiente
│   ├── package.json              # Dependências Node.js
│   └── angular.json              # Configuração Angular
│
├── docs/                         # Documentação e screenshots
│
├── docker-compose.yml            # Docker Compose (produção)
├── docker-compose.dev.yml        # Docker Compose (desenvolvimento)
├── .gitignore
├── README.md                     # Este arquivo
├── Projeto-escopo.md             # Escopo do projeto
└── ETAPAS-DESENVOLVIMENTO.md     # Etapas de desenvolvimento
```

---

## 🔧 Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

| Variável | Descrição | Padrão | Obrigatório |
|----------|-----------|--------|-------------|
| `OPENAI_API_KEY` | Chave da API OpenAI | - | Sim* |
| `GEMINI_API_KEY` | Chave da API Google Gemini | - | Sim* |
| `AI_PROVIDER` | Provedor de IA: `openai` ou `gemini` | `openai` | Não |
| `OPENAI_MODEL` | Modelo da OpenAI a usar | `gpt-3.5-turbo` | Não |
| `GEMINI_MODEL` | Modelo do Gemini a usar | `gemini-1.5-flash` | Não |
| `CORS_ORIGINS` | Origens permitidas (separadas por vírgula) | `http://localhost:4200,http://localhost:3000` | Não |
| `DEBUG` | Modo debug | `false` | Não |

\* Pelo menos uma chave de API (OpenAI ou Gemini) é obrigatória, dependendo do `AI_PROVIDER` escolhido.

### Exemplo de arquivo .env

```env
# Provedor de IA (openai ou gemini)
AI_PROVIDER=openai

# OpenAI (obrigatório se AI_PROVIDER=openai)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-3.5-turbo

# Google Gemini (obrigatório se AI_PROVIDER=gemini)
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxx
GEMINI_MODEL=gemini-1.5-flash

# CORS
CORS_ORIGINS=http://localhost:4200,http://localhost:3000

# Debug
DEBUG=false
```

---

## 🎯 Funcionalidades Implementadas

### Interface do Usuário

- ✅ **Interface de Chat Interativa**: Experiência de chat com histórico de mensagens, scroll automático e visualização clara das classificações
- ✅ **Upload de Arquivos**: Suporte para múltiplos formatos (.txt, .pdf, .eml, .msg, .mbox) com validação de tamanho
- ✅ **Seleção Dinâmica de Provider**: Interface permite escolher entre OpenAI e Gemini em tempo real
- ✅ **Modal de Preview de Email**: Visualização profissional do email formatado com opção de copiar resposta
- ✅ **Feedback Visual**: Indicadores de carregamento, erros e sucesso nas operações

### Backend

- ✅ **Clean Architecture**: Separação clara de responsabilidades (Domain, Application, Infrastructure, Interfaces)
- ✅ **Múltiplos Leitores de Arquivo**: Suporte nativo para formatos de email comuns
- ✅ **Factory Pattern**: Sistema flexível para adicionar novos provedores de IA
- ✅ **Tratamento de Erros**: Exceções específicas de domínio com mensagens claras
- ✅ **Health Check**: Endpoint para monitoramento do serviço
- ✅ **Validação de Dados**: Pydantic para validação de entrada e saída

### DevOps

- ✅ **Docker Compose**: Configuração completa para desenvolvimento e produção
- ✅ **Hot Reload**: Desenvolvimento com recarregamento automático (backend e frontend)
- ✅ **Health Checks**: Monitoramento automático dos containers

## 📝 Melhorias Futuras

- [ ] Adicionar testes de integração end-to-end
- [ ] Implementar cache de classificações
- [ ] Adicionar autenticação e autorização
- [ ] Implementar histórico persistente de classificações
- [ ] Adicionar dashboard de métricas e analytics
- [ ] Configurar CI/CD
- [ ] Deploy na nuvem (AWS, GCP, Azure)
- [ ] Suporte a mais formatos de arquivo (docx, odt, etc.)
- [ ] Exportação de resultados (CSV, JSON)

---

## 🛠️ Desenvolvimento

### Estrutura de Branches

- `main` - Branch principal (produção)
- `develop` - Branch de desenvolvimento
- `feature/*` - Novas funcionalidades
- `fix/*` - Correções de bugs

### Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

### Padrões de Código

- **Backend**: Seguir PEP 8, usar Black e isort para formatação
- **Frontend**: Seguir Angular Style Guide, usar Prettier
- **Commits**: Mensagens claras e descritivas

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👥 Autor

Desenvolvido como parte do desafio técnico fullstack.

## 📚 Recursos Adicionais

- [Documentação FastAPI](https://fastapi.tiangolo.com/)
- [Documentação Angular](https://angular.io/docs)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [OpenAI API](https://platform.openai.com/docs)
- [Google Gemini API](https://ai.google.dev/docs)
