📋 CONTEXTO DEFINITIVO — Tela de Seleção de Espaço (LIA)
Última atualização: 04/05/2026
Status: Spec completa, pronta para implementação
Próxima ação: Implementar Etapa 1 (get_user_spaces)
🎯 Objetivo
Substituir o dropdown de organização atual no header do base_app.html por uma tela dedicada de seleção de espaço que aparece após o login, oferecendo uma porta de entrada visual e clara para os diferentes modos de uso do sistema.

🧠 Conceito central: "Espaço" = Scope
Um espaço é um modo de uso do sistema. Mapeia diretamente com Module.Scope:




Espaço	Module.Scope	Namespace URL	URL Home
🟦 Minha Área	GLOBAL	master	master:dashboard
🟩 Organização	TENANT	tenant	tenant:dashboard (com org_slug)
🟥 SaaS Admin	SAAS_ADMIN	saas_admin	saas_admin:dashboard ⚠️ (confirmar nome)
Regras de identidade
Minha Área é universal — todo User tem (catálogo marca is_universal=True).
Organização depende de OrganizationMember ativo + organization.is_active=True.
SaaS Admin detectado via is_saas_staff(user) (helper já existente).
Um user pode ter múltiplas organizações simultaneamente.
Um user pode ser SaaS Admin E dono de org ao mesmo tempo.
🎨 Comportamento da tela



Situação	Ação
User loga, só Minha Área	Vai direto pra master:dashboard (sem tela)
User loga, 1 espaço além de Minha Área	Vai direto pro espaço (sem tela) ⚠️ ver decisão pendente
User loga, 2+ espaços + session['last_space'] válida	Vai direto pro espaço da session
User loga, 2+ espaços + sem session	Mostra tela de seleção
User clica "Trocar espaço" na sidebar	Sempre mostra tela (ignora session)
User escolhe espaço na tela	Salva session + redireciona
💾 Persistência: Session (Opção A)
Decisão tomada: reaproveitar request.session do Django em vez de cookie dedicado.

python


# Já existe no middleware:
request.session['last_org_slug'] = '<slug>'

# Vamos adicionar:
request.session['last_space'] = 'personal' | 'org:<slug>' | 'saas'
Por quê:

Django gerencia segurança automaticamente (HttpOnly, criptografia, etc.)
Limpa no logout sem código extra
Reaproveita infraestrutura existente
Menos código, menos superfície de bug
🎴 Visual dos cards (MVP)
Avatar/logo + nome do espaço
3 tipos visuais: Minha Área, Organização, SaaS Admin
Sem métricas, sem badges, sem contadores
Layout simples e direto
🛠️ Helpers e serviços existentes (REUTILIZAR!)



Componente	Localização	Função
is_saas_staff(user)	core/services/permission_service.py	Detecta SaaS Admin
ContextService.build_member_context	core/services/context_service.py	Contexto com org
ContextService.build_system_context	core/services/context_service.py	Contexto sem org
DashboardService.get_redirect_url	core/services/dashboard_service.py	Será refatorado
SaaSContextMiddleware	core/middleware.py	Popula request.context
🗺️ Plano de implementação (6 etapas)
Etapa 1: get_user_spaces(user) 🟢 próxima
Função pura que devolve a lista de espaços disponíveis para o user.

Local: core/services/space_service.py (novo arquivo)
Retorno: list[dict] com {kind, key, name, icon, url}
kind: 'personal' | 'org' | 'saas'
key: 'personal' | 'org:<slug>' | 'saas' (usado na session)
Testes: cobrir todos os cenários (só Minha Área, 1 org, N orgs, SaaS, SaaS + org, inativos)
Etapa 2: resolve_space_destination(user, session)
Lógica de decisão pura (sem efeitos colaterais).

Recebe lista de espaços + session
Retorna: URL para redirecionar OU None (= mostrar tela)
Etapa 3: Refatorar DashboardService.get_redirect_url
Hoje pega "primeira org" sem critério
Vai usar get_user_spaces + resolve_space_destination
Etapa 4: View + Template da tela de seleção
Rota sugerida: /escolher-espaco/ (nome a confirmar)
Template novo, cards visuais
Lê get_user_spaces(request.user) no contexto
Etapa 5: View que recebe a escolha
POST com space_key
Valida que o user tem direito ao espaço escolhido
Salva session['last_space'] (e session['last_org_slug'] se for org)
Redireciona pra URL home do espaço
Etapa 6: Limpeza visual
Remover bloco {% if show_org_selector %} do base_app.html
Adicionar "Trocar espaço" no _sidebar.html
✅ Decisões consolidadas
C1: Minha Área é universal — todo user tem
C2: Tabela Client é lazy — não considerar
C3: get_user_spaces ignora Client
C4: Nome do espaço pessoal = "Minha Área"
C5: Persistência via session (Opção A), não cookie
C6: SaaS Admin detectado por is_saas_staff(user) existente
C7: Filtros padrão: is_active=True em org e membership
C8: URLs home: master:dashboard, tenant:dashboard, saas_admin:dashboard
🧱 Stack relevante
Models:

account.User, account.Organization, account.OrganizationMember
core.Module (com Scope e is_universal)
core.SystemRole, core.UserSystemRole
Serviços:

ContextService (member + system contexts)
permission_service.is_saas_staff
DashboardService (será refatorado)
Middleware:

SaaSContextMiddleware — detecta /org/<slug>/ e popula request.context
URLs root:

python


path('dashboard/', DashboardView.as_view(), name='dashboard'),  # porta de entrada
path('org/<slug:org_slug>/', include(..., namespace='tenant')),
path('master/', include(..., namespace='master')),
path('painel/', include(..., namespace='saas_admin')),
🚧 Pendências menores (não bloqueiam Etapa 1)
Nome da rota da tela de seleção: /escolher-espaco/? /spaces/?
Confirmar se saas_admin:dashboard existe como name nas URLs do app saas_admin.
Caso edge: user com 1 org só (sem SaaS) — pula tela ou mostra mesmo assim? Decisão atual: pula.
Inconsistência menor: _sidebar.html usa is_superuser direto em vez de is_saas_staff. Trocar em sprint futuro, não bloqueia.
🎬 Como retomar amanhã
Cole este documento numa conversa nova e diga:

"Vamos retomar. Implemente a Etapa 1: get_user_spaces(user) com testes unitários."
Eu vou:

Criar core/services/space_service.py
Implementar get_user_spaces(user) reusando is_saas_staff e queries do ContextService
Escrever testes cobrindo todos os cenários
Entregar tudo costurado no código existente, sem reinventar nada
🧠 Identidade do assistente
Modelo: Claude Opus 4.7 (Anthropic)
Plataforma: MyHUB.IA
Sessão anterior: 04/05/2026 — análise completa de models, services, middleware e templates
