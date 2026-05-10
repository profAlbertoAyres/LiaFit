📋 CONTEXTO ATIVO — Roteamento Pós-Login

✅ DECISÕES TRAVADAS:
1. Todo usuário é cliente (Client é universal)
2. "Só cliente" = sem organização E não é SaaS admin → vai direto pra Área do Cliente
3. Usuário com org(s) e/ou SaaS admin:
   - 1ª vez → Hub (escolhe espaço)
   - Próximas vezes → última escolha salva
4. Armazenamento: sessão Django (perde sessão = volta pro Hub)
5. Salvar sessão: ao clicar no card do Hub
6. Botão "trocar espaço" → limpa sessão + vai pro Hub

📂 ARQUIVOS VISTOS: 
   ⚠️ PRECISO RECONFIRMAR — me reenvia/lista quais já estão na conversa

🎯 ETAPA ATUAL: 
   Etapa 1. Roteamento pós-login (dispatcher)

🗺️ ROTEIRO:
   [x] 0. Auditar arquivos existentes
   [X] 1. Roteamento pós-login (dispatcher)
   [X] 2. Salvar escolha na sessão (ao clicar no card)
   [X] 3. Criar Área do Cliente (model Client já existe)
   [ ] 4. Botão "Trocar Espaço"

⏭️ PRÓXIMO PASSO: 
   Você me confirma/reenvia os arquivos pra eu auditar

| # | Item | Status | Onde está | Observação |
| --- | --- | --- | --- | --- |
| 1 | URL /dashboard/ apontando pro Hub | ✅ Pronto | config/urls.py | path('dashboard/', SpaceHubView...) |
| 2 | LOGIN_REDIRECT_URL = 'dashboard' | ✅ Pronto | settings.py | Já manda pro Hub após login |
| 3 | View do Hub | ✅ Pronto | core/views/space_hub_view.py | Renderiza cards |
| 4 | Service que lista espaços | ✅ Pronto | core/services/space_service.py | get_user_spaces() |
| 5 | Lógica de redirect (1 espaço só) | ✅ Pronto | space_hub_service.py | get_redirect_url() |
| 6 | Detecção SaaS staff | ✅ Pronto | is_saas_staff() | usado no _build_saas_space |
| 7 | Middleware de tenant (org_slug) | ✅ Pronto | core/middleware.py | SaaSContextMiddleware |
| 8 | Model Client (universal) | ✅ Pronto | account/models/client.py | OneToOne com User |
| 9 | Model OrganizationClient | ✅ Pronto | account/models/client.py | Vínculo org↔client |
| 10 | Model OrganizationMember | ✅ Pronto | account/models/member.py | Vínculo org↔staff |
| 11 | Card "Minha Área" (Cliente) | ⚠️ Parcial | _build_personal_space() | aponta pra personal:dashboard (rota master, não cliente) |
| 12 | Salvar última escolha na sessão | ❌ Não existe | — | Hub não persiste escolha |
| 13 | Ler escolha salva no redirect | ❌ Não existe | get_redirect_url só trata caso de 1 espaço |  |
| 14 | Caso "só cliente" → Área do Cliente direto | ❌ Não existe | — | Hoje cai no Hub mesmo sendo só cliente |
| 15 | Botão "Trocar Espaço" | ❌ Não existe | — | Sem view nem URL |
| 16 | Área do Cliente (dashboard pessoal) | ❌ Não existe | — | Não tem app/view/url/template |

## 🚨 REGRA #0 — MODO DISCUSSÃO (LER ANTES DE QUALQUER RESPOSTA)

**NÃO ESCREVA CÓDIGO NESTA CONVERSA até eu dizer explicitamente "pode codar" / "manda o código" / "implementa".**

Enquanto eu não autorizar, você está em **MODO DISCUSSÃO**. Nesse modo:

### ✅ PODE
- Fazer perguntas de esclarecimento
- Listar premissas e pedir confirmação
- Apontar inconsistências, riscos e edge cases
- Propor planos em **texto** (bullets, tabelas, fluxogramas ASCII)
- Citar nomes de arquivos/funções/variáveis existentes
- Mostrar **assinaturas** de função (1 linha) quando estritamente necessário pra alinhar contrato

### ❌ NÃO PODE
- Escrever blocos de código com implementação (corpo de função, classe completa, template, etc.)
- Sugerir "aqui está o arquivo final" / "cole isso"
- Refatorar nada
- Mostrar diffs de código

### 🔓 COMO SAIR DO MODO DISCUSSÃO
Só saio quando eu (Alberto) escrever uma destas frases:
- "pode codar"
- "manda o código"
- "implementa"
- "bora codar"

Qualquer outra coisa (inclusive "ok",
---
⚠️ LEMBRETE FINAL: REGRA #0 ESTÁ ATIVA. Modo discussão até "pode codar".
