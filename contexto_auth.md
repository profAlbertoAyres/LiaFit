# Contexto: Refatoração do Fluxo de Autenticação (LiaFit)

## 🎯 Objetivo
Transformar as telas de entrada do sistema (Login, Cadastro, Recuperação de Senha) em um layout premium, moderno e responsivo, estilo "SaaS de alta conversão" (tela dividida em duas colunas: formulário + hero area). 

Além da melhoria visual, o código foi componentizado para facilitar a manutenção e a criação de novas telas no futuro utilizando o ecossistema do Django.

## 🛠️ O que foi construído/alterado

### 1. Criação do Componente de Input (`components/form_field.html`)
- Criamos um componente reutilizável do Django (`{% include %}`) para renderizar os campos de formulário.
- **Funcionalidades:** 
  - Suporte nativo a ícones flutuantes (Lucide Icons) passados via parâmetro `icon="nome-do-icone"`.
  - Tratamento automático de estados de erro (borda vermelha e mensagens de validação abaixo do campo).
  - Controle de grid dinâmico via parâmetro `col="col-12"`.
- **Benefício:** Redução drástica de código HTML repetido nas telas de formulário.

### 2. Integração com Django Forms (`LiaFitStyleMixin`)
- O backend agora injeta automaticamente as classes CSS padrão do nosso design system (`lia-form-control`, `lia-form-label`) nos widgets dos formulários, garantindo que o HTML gerado pelo Django converse perfeitamente com o nosso CSS personalizado.

### 3. Refatoração da Herança de Templates (`base_auth.html`)
- Ajustamos o arquivo `base_auth.html` para remover travas de largura máxima (`max-width: 400px`), permitindo que as telas de autenticação ocupem 100% da viewport (tela cheia).
- Padronizamos a nomenclatura dos blocos do Django para as telas de auth:
  - `{% block page_css %}`: Para estilos específicos (ex: `auth.css`).
  - `{% block page_content %}`: Para o layout da tela.
  - `{% block page_js %}`: Para scripts da página.

### 4. Atualização das Telas (UI/UX)
Todas as telas abaixo foram reescritas para adotar a classe `.lia-auth` (layout em duas metades) e o componente de formulário inteligente:
- `login.html`: Layout principal com ícones Lucide atualizados e caixa de erros de formulário estilizada.
- `register.html`: Tela de criação de conta padronizada no novo visual.
- `setup_password.html`: Tela para o aluno/cliente definir a primeira senha.
- `password_reset_done.html`: Tela de sucesso "E-mail enviado".
- `setup_password_invalid.html`: Tela de erro para "Link expirado/inválido".

## 📐 Regras de Arquitetura Definidas
Para evitar que elementos internos do sistema (como barra lateral e menu de navegação) vazem para as telas de login, a hierarquia de templates ficou definida assim:

1. **`base.html`**: É a fundação invisível. Contém apenas a estrutura `<head>`, imports do Bootstrap, CSS global, Lucide e as tags `<body>`.
2. **`base_auth.html`**: Herda de `base.html`. Possui um fundo limpo, carrega scripts de validação de formulário e serve **exclusivamente** para o fluxo de entrada (Login/Registro).
3. **`base_dashboard.html`** *(Próximo passo/Conceitual)*: Herda de `base.html`. Adiciona a Sidebar (Menu Lateral), o Topbar e serve para todas as páginas internas de gestão da academia.

## 📦 Tecnologias Utilizadas
- **Backend:** Django (Templates, Forms, CSRF, Form Errors).
- **Estilização:** CSS Customizado (Padrão BEM `lia-*`) + Classes Utilitárias Bootstrap 5.
- **Ícones:** Lucide Icons (via CDN e tag `<i data-lucide="...">`).
