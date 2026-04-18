# Contexto do Projeto: LiaFit (SaaS Multi-Tenant)

## 1. Visão Geral
LiaFit é um sistema SaaS (Software as a Service) focado no segmento fitness e de saúde (academias, clínicas, estúdios). O sistema utiliza uma arquitetura **Multi-Tenant**, onde cada cliente opera dentro de uma `Organization` (Tenant) isolada, garantindo que dados (alunos, treinos, finanças) de uma empresa não vazem para outra.

O projeto foi planejado com foco em:

- organização visual consistente
- arquitetura escalável
- separação clara entre website institucional e sistema interno
- reutilização de componentes
- base sólida para evolução futura

A stack principal utiliza:

- **Python / Django**
- **Django Templates**
- **CSS modular**
- **JavaScript modular**
- estrutura de design system própria com prefixo `lia-`

---

## Objetivos do Projeto

O sistema foi pensado para atender dois grandes contextos:

### 1. Website institucional
Parte pública da aplicação, usada para:

- apresentar o produto
- explicar funcionalidades
- captar leads
- exibir planos
- permitir acesso à tela de login

### 2. Sistema interno (app)
Parte autenticada da aplicação, usada para:

- gerenciar alunos
- acompanhar avaliações
- organizar agenda
- controlar dados operacionais
- oferecer experiência de uso produtiva e limpa

---

## Direção de Arquitetura

A arquitetura visual e estrutural foi planejada com separação entre:

- **fundação**
- **componentes**
- **layout**
- **páginas**
- **módulos JS**

Essa separação melhora:

- manutenção
- legibilidade
- reuso
- escalabilidade
- consistência entre telas

---

# Estrutura de CSS planejada

```text
static/css/
├── foundation/
│   ├── variables.css
│   ├── reset.css
│   └── typography.css
├── components/
│   ├── alerts.css
│   ├── buttons.css
│   ├── cards.css
│   ├── forms.css
│   ├── sidebar.css
│   └── tables.css
├── layout/
│   └── layout.css
├── pages/
│   └── website-home.css
└── website/
    └── website.css
