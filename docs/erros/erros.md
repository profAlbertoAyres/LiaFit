# 🐛 Relatório de Bugs — Lia Linda SaaS

Este diretório contém **22 bugs** identificados em auditoria arquitetural do projeto Lia Linda (SaaS multi-tenant em Django 4.2 para personal trainers).

## ⚠️ Fluxo obrigatório para qualquer correção

1. **Análise** do bug em conjunto (entender contexto, impactos, dependências)
2. **Plano de correção elaborado em conjunto** — discutir abordagens, trade-offs, testes
3. **Aprovação explícita** do plano
4. **Só então** a implementação

> **Nunca pular direto para o código.** Cada arquivo de bug é projetado para ser usado como prompt em qualquer IA assistente — ele contém contexto suficiente para discutir o problema sem precisar enviar arquivos do projeto.

## 📋 Índice

### 🔴 Críticos (5)
- [BUG-01](BUG-01-saas-admin-nao-instalado.md) — App `saas_admin` referenciado mas não instalado
- [BUG-02](BUG-02-resend-password-token-inexistente.md) — `OnboardingService.resend_password_token()` não existe
- [BUG-03](BUG-03-typo-changer-member.md) — Typo: `settings.changer_member`
- [BUG-04](BUG-04-url-role-permissions-view-errada.md) — URL `role_permissions_update` aponta para view errada
- [BUG-05](BUG-05-dashboardview-template-view-getqueryset.md) — DashboardView mistura TemplateView + ContextMixin

### 🟡 Importantes (10)
- [BUG-06](BUG-06-success-url-sem-namespace.md) — `success_url` sem namespace
- [BUG-07](BUG-07-typo-deshboard-service.md) — Typo no nome do arquivo `deshboard_service.py`
- [BUG-08](BUG-08-comentario-cabecalho-errado.md) — Comentário de cabeçalho errado
- [BUG-09](BUG-09-login-redirect-url-hardcoded.md) — `LOGIN_REDIRECT_URL` hard-coded
- [BUG-10](BUG-10-logging-vazio.md) — LOGGING vazio
- [BUG-11](BUG-11-action-invite-vs-add-member.md) — Inconsistência `INVITE` vs `ADD` para Member
- [BUG-12](BUG-12-rolelistview-conflito-namespaces.md) — `RoleListView` em dois namespaces
- [BUG-13](BUG-13-clientprofessional-import-faltante.md) — `ClientProfessional` import faltante
- [BUG-14](BUG-14-userpermissionform-export-incerto.md) — `UserPermissionForm` export incerto
- [BUG-15](BUG-15-roles-sem-scope-global.md) — Falta role com scope=global

### 🟢 Baixas (7)
- [BUG-16](BUG-16-comentarios-cabecalho-urls.md) — Comentários cabeçalho URLs <- Já corrigi
- [BUG-17](BUG-17-marca-inconsistente.md) — Marca inconsistente (Lia Linda / LiaFit / PersonalPro) <- Já corrigi
- [BUG-18](BUG-18-codigo-comentado-morto.md) — Código comentado morto <- Já corrigi
- [BUG-19](BUG-19-allowed-hosts-sem-comentario.md) — `ALLOWED_HOSTS` sem comentário prod <- Já resolvi
- [BUG-20](BUG-20-core-urls-init-faltante.md) — `core/urls/__init__.py` faltante <- Já resolvi
- [BUG-21](BUG-21-secret-key-fraca-em-prod.md) — SECRET_KEY fraca em prod
- [BUG-22](BUG-22-deny-redirect-master-dashboard-hardcoded.md) — `_deny()` hardcoded para master:dashboard

## 🎯 Ordem sugerida de ataque

1. Críticos #3, #1, #2, #6 (quick wins, ~15min total)
2. Críticos #4, #5 (precisam discussão arquitetural)
3. Importantes em ordem de impacto
4. Baixas em sprint de polimento

