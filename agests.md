# Documento de Arquitetura de Software

## 1. Objetivo

Definir a arquitetura base do sistema, estabelecendo princípios, limites técnicos, responsabilidades dos módulos e diretrizes de implementação.

Este documento serve como referência para manter consistência técnica, acelerar desenvolvimento e reduzir decisões ad hoc ao longo do projeto.

## 2. Visão Geral

O sistema será construído como um monólito modular em Django, com frontend server-rendered usando Django Templates, HTML, CSS e JavaScript.

A plataforma terá autenticação global de usuários e acesso contextual por organização, permitindo que um mesmo usuário possa participar de uma ou mais organizações com diferentes papéis.

## 3. Objetivos Arquiteturais

- simplicidade de implementação
- clareza organizacional do código
- isolamento lógico entre organizações
- facilidade de manutenção
- baixo acoplamento entre módulos
- boa base para evolução futura

## 4. Fora de Escopo Inicial

Neste momento, não faz parte do escopo:
- microsserviços
- SPA complexa
- mensageria distribuída
- Kubernetes
- multi-database por tenant
- event sourcing

## 5. Estilo Arquitetural

A arquitetura adotada será:
- monólito modular
- multi-tenant por coluna de organização
- backend centrado em regras de negócio
- frontend orientado a páginas renderizadas no servidor

## 6. Princípios Norteadores

- começar simples
- explicitar contexto de organização
- centralizar regra de negócio fora das views
- priorizar legibilidade sobre “sofisticação”
- evoluir com segurança, não com pressa

## 7. Stack Tecnológica

### Backend
- Python
- Django
- PostgreSQL

### Frontend
- Django Templates
- HTML
- CSS
- JavaScript

### Infraestrutura inicial
- deploy simples
- banco relacional único
- arquivos locais ou storage compatível com S3 futuramente

### Ferramentas de qualidade
- pytest
- factory_boy
- flake8 ou ruff
- black

## 8. Estratégia de Modularização

O sistema será dividido por apps de domínio, evitando separar por camada técnica como “models”, “services” e “controllers” globais.

### Apps iniciais sugeridos
- `account`
- `organization`
- `membership`
- `onboarding`
- `clients`
- `professionals`
- `schedule`
- `workout`
- `financial`
- `crm`
- `portal`
- `core`

### Regra de organização
Cada app deve conter, quando fizer sentido:
- models
- services
- selectors
- forms
- views
- urls
- tests

## 9. Limites entre Camadas

### Models
Responsáveis por estrutura e comportamentos simples diretamente ligados à entidade.

### Services
Responsáveis por casos de uso e regras de negócio.

### Selectors
Responsáveis por consultas e leitura otimizada de dados.

### Views
Responsáveis por receber requisições, acionar services/selectors e retornar resposta.

### Forms
Responsáveis por validação de entrada no fluxo server-rendered.

## 10. Estratégia Multi-tenant

O sistema utilizará multi-tenancy por coluna, com `organization_id` nas entidades de domínio que pertencem a uma organização.

### Regras gerais
- `User` é global
- `Organization` representa o tenant
- `Membership` liga usuário à organização
- entidades de domínio devem carregar vínculo com organização quando aplicável

### Cuidados obrigatórios
- toda query sensível deve considerar organização ativa
- nenhuma view operacional deve assumir tenant implicitamente sem validação
- permissões devem ser contextuais, não apenas globais

## 11. Modelo Conceitual de Identidade e Acesso

### User
Representa a identidade global do sistema.

### Organization
Representa a unidade organizacional que agrupa dados, operação e permissões.

### Membership
Representa o vínculo entre `User` e `Organization`.

Campos conceituais sugeridos para `Membership`:
- user
- organization
- role
- status
- is_default
- joined_at

### Papéis iniciais sugeridos
- owner
- admin
- manager
- staff

## 12. Contexto Ativo de Organização

Após autenticação, o sistema deve operar com uma organização ativa definida no contexto do usuário.

### Possíveis formas de armazenar contexto ativo
- sessão
- subdomínio no futuro
- parâmetro contextual em fluxos específicos

### Regras
- usuário sem organização deve ir para onboarding
- usuário com uma organização pode entrar direto nela
- usuário com múltiplas organizações pode alternar contexto

## 13. Estratégia de Permissões

As permissões devem combinar:
- autenticação global
- vínculo ativo com organização
- role contextual
- validações adicionais por recurso

### Exemplo conceitual
Para editar agenda:
- usuário autenticado
- membership ativo na organização
- role com permissão de gestão de agenda

## 14. Base de Dados e Convenções

### Convenções gerais
- usar chave primária padrão ou UUID conforme decisão do projeto
- timestamps padrão (`created_at`, `updated_at`)
- soft delete apenas onde houver necessidade clara
- índices em colunas de busca frequente
- constraints para integridade

### Base model sugerida
Entidades multi-tenant podem herdar de uma base comum com:
- organization
- created_at
- updated_at


## 15. Fluxos Críticos Iniciais

### Onboarding
1. usuário cria conta ou faz login
2. sistema verifica memberships
3. se não houver organização, direciona para criação inicial
4. usuário cria organização
5. sistema cria membership como owner
6. sistema define organização ativa

### Acesso recorrente
1. usuário autentica
2. sistema recupera memberships ativos
3. define organização ativa padrão ou solicita escolha
4. redireciona para dashboard contextual

### Troca de organização
1. usuário solicita mudança
2. sistema valida vínculo ativo
3. atualiza contexto ativo
4. recarrega navegação e dados dentro do tenant selecionado

## 16. Segurança e Isolamento

### Regras essenciais
- nunca confiar apenas no ID recebido pela URL
- sempre validar organização do recurso consultado
- proteger ações por autenticação e membership
- registrar eventos relevantes de auditoria futuramente

### Riscos principais
- vazamento de dados entre organizações
- consultas sem filtro de tenant
- permissões amplas demais
- regras espalhadas diretamente nas views

## 17. Estratégia de Evolução

### Evoluções futuras possíveis
- RBAC mais granular
- permissões por feature
- convite de usuários por organização
- subdomínio por tenant
- API pública
- frontend desacoplado
- filas assíncronas
- observabilidade mais madura

### Regra de evolução
Só avançar para maior sofisticação quando houver necessidade real medida por produto, operação ou escala.

## 18. Estrutura Inicial Sugerida

```text
project/
  config/
  apps/
    core/
    account/
    organization/
    membership/
    onboarding/
    clients/
    professionals/
    schedule/
    workout/
    financial/
    crm/
    portal/
  templates/
  static/
```

## 19. Diretrizes de Código

### Boas práticas
- views finas
- services com responsabilidade clara
- selectors para leitura
- nomes explícitos
- regras de negócio testáveis
- evitar dependências circulares entre apps

### Evitar
- regra crítica dentro de template
- query complexa espalhada em múltiplas views
- permissões implícitas
- app genérico demais concentrando tudo

## 20. Estratégia de Testes

### Prioridades de teste
- services
- selectors críticos
- permissões
- fluxos de onboarding
- troca de organização
- isolamento entre tenants

### Tipos de teste
- unitários para regras de negócio
- integração para fluxo entre camadas
- testes de view quando necessário
- testes de regressão para regras multi-tenant

## 21. Observabilidade Inicial

No início, manter simples:
- logging estruturado quando possível
- tratamento consistente de erros
- páginas de erro adequadas
- monitoramento evolutivo conforme crescimento

## 22. Decisões Arquiteturais Iniciais

- monólito modular em Django
- frontend server-rendered
- autenticação global com contexto por organização
- `Membership` como entidade central de acesso
- multi-tenant por coluna
- regras concentradas em services
- consultas concentradas em selectors

## 23. Resumo Executivo

A arquitetura proposta privilegia simplicidade, clareza e segurança de contexto organizacional.

Ela oferece uma base sólida para iniciar rápido, com baixo custo cognitivo, sem impedir evolução futura para cenários mais complexos.

## 24. Convenções de Nomenclatura

Definir convenções de nomenclatura no início reduz ambiguidade, facilita manutenção e melhora a comunicação entre código, negócio e equipe.

### Objetivo
Padronizar como os elementos do sistema serão nomeados para que a estrutura fique previsível e escalável.

### Princípios gerais
- usar nomes explícitos
- evitar abreviações desnecessárias
- nomear por responsabilidade de negócio
- manter consistência entre app, model, service, selector e rota
- preferir singular para entidades de domínio e plural apenas quando fizer sentido na navegação ou URL

### Apps
Os apps devem representar contextos de negócio ou capacidades bem definidas.

#### Sugestão
- `core`
- `account`
- `organization`
- `membership`
- `onboarding`
- `clients`
- `professionals`
- `schedule`
- `workout`
- `financial`
- `crm`
- `portal`

#### Regras
- evitar app `utils` para concentrar regra solta
- evitar app `common` como depósito genérico
- evitar misturar muitos domínios em um único app
- nome do app deve indicar claramente sua responsabilidade

### Models
Models devem usar nomes no singular e orientados ao domínio.

#### Exemplos
- `User`
- `Organization`
- `Membership`
- `Client`
- `Professional`
- `Appointment`
- `WorkoutPlan`
- `Invoice`

#### Evitar
- nomes vagos como `Data`, `Item`, `Record`, `Entity`
- nomes excessivamente técnicos sem significado de negócio
- plural em model, como `Clients`

### Services
Services devem refletir ação ou caso de uso.

#### Padrões possíveis
- `create_organization`
- `invite_user_to_organization`
- `switch_active_organization`
- `create_client`
- `schedule_appointment`

#### Alternativa com módulos
```python
organization/services/create_organization.py
membership/services/invite_user.py
schedule/services/create_appointment.py
```

Regra
Nomear o service pelo que ele faz, não por um termo abstrato.

Evitar
process_data
handle_request
execute
manager
Selectors
Selectors devem expressar intenção de leitura.

Exemplos
get_user_memberships
get_active_organization_for_user
list_organization_clients
get_professional_schedule
list_open_invoices
Regra
Nome deve indicar claramente:

o que retorna
de qual contexto retorna
se busca um item ou uma lista
Views
Views devem seguir o caso de uso entregue à interface.

Exemplos baseados em classe
OrganizationCreateView
OrganizationSwitchView
ClientListView
ClientCreateView
AppointmentCalendarView
Exemplos baseados em função
create_organization_view
switch_organization_view
Regra
Se usar class-based views, manter padrão uniforme no projeto.

Templates
Templates devem refletir app + tela.

Exemplo
text


templates/
  organization/
    create.html
    switch.html
  clients/
    list.html
    detail.html
    form.html
Regra
Evitar nomes genéricos soltos como:

page.html
screen.html
index.html em excesso sem contexto claro
Rotas
Rotas devem ser legíveis e estáveis.

Exemplos
python


organizations/create/
organizations/switch/
clients/
clients/new/
clients/<id>/
schedule/calendar/
Nomes internos
python


organization:create
organization:switch
clients:list
clients:create
schedule:calendar
Princípios
URLs amigáveis
nomes previsíveis
coerência entre rota e view
evitar padrões muito diferentes entre módulos semelhantes
Campos e atributos
Campos devem usar nomes claros e consistentes.

Exemplos
created_at
updated_at
is_active
joined_at
start_date
end_date
Evitar
dt_cad
fl_ativo
data1
obs2
Papéis e permissões
Papéis devem usar nomes de negócio.

Exemplos
owner
admin
manager
staff
Permissões
Se houver codinomes:

clients.view_client
clients.create_client
schedule.manage_appointment
financial.view_invoice
Benefícios esperados
leitura mais rápida do código
menor ambiguidade entre camadas
onboarding técnico mais fácil
menor risco de duplicidade conceitual
maior previsibilidade arquitetural


## 25. Estrutura de Services e Selectors

Definir uma estrutura clara para services e selectors ajuda a separar leitura de escrita, reduzir acoplamento entre views e models e organizar melhor as regras de negócio.

### Objetivo
Criar uma convenção prática para concentrar:
- escrita e regras de negócio em `services`
- leitura e consultas em `selectors`

### Princípio central
A aplicação deve separar claramente:
- comandos: alteram estado
- consultas: leem estado

Essa separação melhora legibilidade, testabilidade e previsibilidade.

### Services
Services são responsáveis por executar casos de uso que alteram o sistema.

#### Devem conter
- criação de entidades
- atualização de dados
- exclusões lógicas ou físicas
- validações de negócio
- verificações de permissão ligadas ao caso de uso
- orquestração entre models e outros serviços
- uso de transações quando necessário

#### Exemplos
- criar organização
- convidar usuário
- trocar organização ativa
- cadastrar cliente
- agendar atendimento
- gerar cobrança

#### O que não devem conter
- formatação para interface
- montagem de contexto de template
- lógica de exibição
- consultas genéricas sem intenção de alteração

### Selectors
Selectors são responsáveis por leitura estruturada de dados.

#### Devem conter
- consultas reutilizáveis
- filtros por organização
- otimização com `select_related` e `prefetch_related`
- listagens
- detalhamentos
- agregações e contagens para dashboard

#### Exemplos
- listar clientes da organização
- obter memberships do usuário
- listar agenda do profissional
- buscar cobranças em aberto
- montar indicadores resumidos

#### O que não devem conter
- alteração de estado
- criação de registros
- efeitos colaterais
- regra de negócio de escrita

### Organização sugerida por app
```
clients/
  services/
    create_client.py
    update_client.py
    archive_client.py
  selectors/
    list_clients.py
    get_client.py
    list_birthdays.py
```


Alternativa mais simples no início
Se o projeto estiver pequeno, pode começar com:

text


clients/
  services.py
  selectors.py
E migrar para estrutura em diretórios quando crescer.

Convenção de assinatura para services
Services devem receber argumentos explícitos e retornar resultado útil para a camada chamadora.

Exemplo
python


def create_client(*, organization, created_by, name, email, phone=None):
    ...
Boas práticas para services
usar parâmetros nomeados
evitar depender diretamente de request quando possível
trabalhar com entidades e valores explícitos
centralizar validações de negócio importantes
encapsular transações críticas
retornar objeto criado ou resultado estruturado
Exemplo de service
python


from django.db import transaction

@transaction.atomic
def create_client(*, organization, created_by, name, email, phone=None):
    client = Client.objects.create(
        organization=organization,
        name=name,
        email=email,
        phone=phone,
        created_by=created_by,
    )
    return client
Convenção de assinatura para selectors
Selectors devem comunicar claramente intenção de leitura.

Exemplos
python


def list_organization_clients(*, organization):
    ...

def get_client_by_id(*, organization, client_id):
    ...
Boas práticas para selectors
filtrar por organização explicitamente
evitar retornar queryset sem critério quando o domínio exige isolamento
aplicar otimizações de consulta
nomear de forma compatível com o retorno
manter foco em leitura
Exemplo de selector
python


def list_organization_clients(*, organization):
    return (
        Client.objects
        .filter(organization=organization, is_active=True)
        .order_by("name")
    )
Relação entre view, service e selector
Fluxo recomendado:

a view recebe a requisição
a view delega leitura para selectors
a view delega escrita para services
models permanecem focados em estrutura e comportamentos simples da entidade
Exemplo de fluxo
python


def client_create_view(request):
    organization = request.active_organization

    if request.method == "POST":
        client = create_client(
            organization=organization,
            created_by=request.user,
            name=request.POST["name"],
            email=request.POST["email"],
        )
        ...
Benefícios arquiteturais
views mais finas
regras reutilizáveis
testes mais objetivos
menor duplicação
isolamento mais claro entre leitura e escrita
menor risco de espalhar regra multi-tenant pela aplicação
Cuidados importantes
não transformar service em depósito caótico de funções
não criar selector genérico demais
não duplicar regra entre form, view e service
não deixar filtro por organização implícito quando ele é obrigatório
não acoplar service à camada HTTP sem necessidade
Recomendação prática
Para este projeto, a abordagem recomendada é:

usar services para comandos de negócio
usar selectors para consultas
começar simples
evoluir por app conforme aumento de complexidade



## 26. Estrutura das Views e da Camada HTTP

A camada HTTP deve ser fina, previsível e responsável apenas por receber a requisição, delegar o processamento e devolver a resposta adequada.

### Objetivo
Definir uma estrutura para views que:
- reduza acoplamento
- mantenha a regra de negócio fora da camada HTTP
- facilite manutenção e testes
- preserve clareza entre entrada, processamento e resposta

### Responsabilidade da view
A view deve coordenar a interação entre:
- requisição HTTP
- autenticação e autorização
- forms ou serializers
- services
- selectors
- resposta final

### A view deve fazer
- receber parâmetros da URL, query string e corpo da requisição
- validar entrada com form ou serializer
- obter contexto necessário da sessão ou organização ativa
- chamar selectors para leitura
- chamar services para escrita
- decidir qual resposta retornar
- renderizar template, redirecionar ou devolver JSON

### A view não deve fazer
- conter regra de negócio complexa
- executar criação e atualização diretamente no model sem service
- repetir consultas de domínio por toda parte
- concentrar regras multi-tenant manualmente em excesso
- misturar lógica de interface com regra central de negócio

### Estrutura recomendada
A camada HTTP deve funcionar como uma orquestração simples:

1. autenticar o usuário
2. resolver organização ativa
3. validar entrada
4. delegar leitura ou escrita
5. montar resposta

### Exemplo de fluxo em POST
```python
def client_create_view(request):
    organization = request.active_organization

    if request.method == "POST":
        form = ClientCreateForm(request.POST)
        if form.is_valid():
            client = create_client(
                organization=organization,
                created_by=request.user,
                **form.cleaned_data,
            )
            return redirect("clients:detail", client_id=client.id)
    else:
        form = ClientCreateForm()

    return render(request, "clients/form.html", {"form": form})
``


Exemplo de fluxo em GET
python


def client_list_view(request):
    organization = request.active_organization
    clients = list_organization_clients(organization=organization)

    return render(request, "clients/list.html", {"clients": clients})
Class-Based Views ou Function-Based Views
As duas abordagens funcionam, desde que haja consistência.

Function-Based Views
Vantagens:

leitura direta
menos abstração
ótimo para casos de uso específicos
fácil integração com services e selectors
Class-Based Views
Vantagens:

reaproveitamento com mixins
padronização em telas CRUD
melhor composição quando há muitas telas semelhantes
Recomendação prática
Se o projeto tiver muitos fluxos específicos de negócio, Function-Based Views costumam ser mais claras. Se houver muitas páginas administrativas e CRUD repetitivo, Class-Based Views podem ajudar.

O mais importante é:

escolher um padrão dominante
evitar mistura excessiva sem critério
Forms na camada HTTP
Forms devem cuidar da validação de entrada e da adaptação dos dados enviados pela interface.

Devem conter
validações de formato
validações simples de consistência
campos da interface
mensagens de erro para o usuário
Não devem concentrar
orquestração de caso de uso
transações complexas
regras centrais que precisam ser reutilizadas fora da interface
Autorização
A view deve aplicar autorização de forma explícita e previsível.

Pode usar
decorators
mixins
verificações simples antes de chamar o service
Exemplo
python


@login_required
def client_list_view(request):
    if not user_can_access_clients(request.user, request.active_organization):
        raise PermissionDenied

    clients = list_organization_clients(
        organization=request.active_organization
    )
    return render(request, "clients/list.html", {"clients": clients})
Camada HTTP e multi-tenant
Como o projeto depende de organização ativa, a view deve trabalhar sempre com esse contexto explícito.

Regra importante
Toda operação de leitura ou escrita dependente de tenant deve usar a organização ativa resolvida na requisição.

Evitar
buscar registros apenas por id
confiar que o frontend restringe acesso
esquecer filtro por organização nos fluxos internos
Respostas da view
A resposta deve ser coerente com o tipo de interface.

Em páginas HTML
render
redirect
mensagens de sucesso e erro
Em endpoints assíncronos ou APIs internas
JsonResponse
códigos HTTP adequados
mensagens objetivas
Tratamento de erros
A camada HTTP deve traduzir falhas em respostas adequadas ao usuário.

Exemplos
entrada inválida: mostrar erros no form
permissão insuficiente: 403
registro inexistente no tenant: 404
regra de negócio violada: mensagem clara e controlada
Padrão recomendado para organização de views
text


clients/
  views/
    list_clients.py
    create_client.py
    update_client.py
    detail_client.py
Alternativa simples no início
text


clients/
  views.py
Se crescer:

quebrar por caso de uso
manter nomes previsíveis
separar leitura e escrita quando necessário
Benefícios esperados
views menores e mais legíveis
menor duplicação de lógica
melhor separação entre HTTP e domínio
testes mais simples
mais segurança em fluxos multi-tenant
Diretriz final
A view deve ser uma camada de coordenação, não o centro da regra de negócio. Ela recebe a requisição, delega o trabalho certo para a camada certa e devolve a resposta correta.
```

## 27. Estratégia para Forms e Validação

Forms e validações devem garantir entrada confiável, mensagens claras para o usuário e separação adequada entre validação de interface e regra de negócio.

### Objetivo
Definir como a aplicação deve validar dados recebidos da interface sem concentrar responsabilidade demais na camada HTTP nem espalhar regras pelo sistema.

### Papel dos forms
Forms devem atuar como porta de entrada dos dados vindos da interface HTML.

Eles são responsáveis por:
- receber dados do usuário
- validar formato e consistência básica
- converter valores para tipos adequados
- expor erros de forma amigável
- entregar dados limpos para a camada de serviço

### O que deve ficar nos forms
- obrigatoriedade de campos
- formato de e-mail
- tamanho mínimo ou máximo
- normalização de strings
- validações simples entre campos
- mensagens de erro para interface
- escolha de opções disponíveis no formulário

### O que não deve ficar nos forms
- regra de negócio central
- transações
- orquestração entre múltiplas entidades
- efeitos colaterais
- criação complexa de objetos fora de casos muito simples
- lógica que precise ser reutilizada por API, task ou outro fluxo fora da interface HTML

### Separação recomendada
A validação deve ser distribuída em camadas:

#### Form
Valida entrada da interface.

#### Service
Valida regra de negócio e executa o caso de uso.

#### Model
Mantém estrutura da entidade e comportamentos simples e intrínsecos ao domínio.

### Exemplo prático
#### Form valida:
- nome obrigatório
- e-mail com formato válido
- telefone opcional
- data final maior que data inicial

#### Service valida:
- usuário pode cadastrar cliente nessa organização
- limite do plano permite novo cliente
- e-mail já existente dentro do tenant
- ação exige vínculo ativo com a organização

### Exemplo de form simples
```python
from django import forms

class ClientCreateForm(forms.Form):
    name = forms.CharField(max_length=120)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20, required=False)

    def clean_name(self):
        value = self.cleaned_data["name"].strip()
        if len(value) < 3:
            raise forms.ValidationError("Informe um nome válido.")
        return value
```

### Exemplo de uso na view

def client_create_view(request):
    if request.method == "POST":
        form = ClientCreateForm(request.POST)
        if form.is_valid():
            client = create_client(
                organization=request.active_organization,
                created_by=request.user,
                **form.cleaned_data,
            )
            return redirect("clients:detail", client_id=client.id)
    else:
        form = ClientCreateForm()

    return render(request, "clients/form.html", {"form": form})


Forms baseados em ModelForm
ModelForm pode ser útil quando:

o caso é simples
o formulário mapeia quase diretamente para o model
não há orquestração relevante fora da entidade
Usar com cuidado
Mesmo com ModelForm, a gravação não deve necessariamente acontecer com form.save() direto se houver regra de negócio importante.

Preferir
form.is_valid()
envio dos dados limpos para um service
Exemplo
python


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["name", "email", "phone"]
python


def client_create_view(request):
    form = ClientForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        client = create_client(
            organization=request.active_organization,
            created_by=request.user,
            **form.cleaned_data,
        )
        return redirect("clients:detail", client_id=client.id)

    return render(request, "clients/form.html", {"form": form})
Validação entre campos
Quando a validação depende da relação entre campos, usar clean().

Exemplo
python


class ScheduleForm(forms.Form):
    start_at = forms.DateTimeField()
    end_at = forms.DateTimeField()

    def clean(self):
        cleaned_data = super().clean()
        start_at = cleaned_data.get("start_at")
        end_at = cleaned_data.get("end_at")

        if start_at and end_at and end_at <= start_at:
            raise forms.ValidationError("O horário final deve ser maior que o inicial.")

        return cleaned_data
Mensagens de erro
As mensagens devem ser:

claras
curtas
úteis para correção
orientadas ao usuário final
Evitar
mensagens técnicas
traceback
termos internos da arquitetura
Preferir
"Informe um e-mail válido."
"Esse horário não está disponível."
"Você não tem permissão para realizar essa ação."
Regras duplicadas
Um cuidado importante é evitar duplicar a mesma validação em:

form
view
service
model
Estratégia prática
validação de entrada e UX no form
validação de regra e segurança no service
restrições estruturais no banco e model quando necessário
Validação em contexto multi-tenant
Sempre que a validação depender da organização ativa, isso deve aparecer explicitamente.

Exemplo
Se o formulário exibe profissionais disponíveis, ele deve receber a organização no construtor.

python


class AppointmentForm(forms.Form):
    professional = forms.ChoiceField()

    def __init__(self, *args, organization, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["professional"].choices = get_professional_choices(
            organization=organization
        )
Benefícios dessa abordagem
validação mais organizada
melhor experiência para o usuário
menor acoplamento com a camada HTTP
possibilidade de reutilizar regra de negócio fora da interface
menor risco de inconsistência entre fluxos
Diretriz final
Forms devem validar a entrada. Services devem proteger a regra de negócio. A combinação das duas camadas produz fluxos seguros, reutilizáveis e fáceis de manter.



## 28. Estratégia de Permissões e Controle de Acesso

Permissões e controle de acesso devem ser tratados como parte central da arquitetura, especialmente em um sistema multi-tenant com múltiplos perfis de usuário e contextos de organização.

### Objetivo
Definir uma estratégia clara para:
- autenticar usuários
- controlar acesso por organização
- limitar ações conforme papel e contexto
- evitar vazamento de dados entre tenants
- manter regras de autorização reutilizáveis e previsíveis

### Princípio central
Autenticação responde:
- quem é o usuário

Autorização responde:
- o que esse usuário pode fazer
- em qual organização
- sob quais condições

Essas duas responsabilidades devem ser tratadas separadamente.

### Autenticação
A autenticação identifica o usuário logado.

#### Requisitos
- login obrigatório para áreas internas
- sessão persistente segura
- logout explícito
- proteção contra acesso anônimo às áreas privadas

#### Prática recomendada
Usar as ferramentas padrão do Django para autenticação, mantendo customizações apenas quando houver necessidade real.

### Autorização
A autorização deve considerar sempre:
- usuário autenticado
- organização ativa
- papel do usuário naquela organização
- permissões específicas do caso de uso

### Regra fundamental em ambiente multi-tenant
Não basta saber se o usuário está autenticado.
É necessário validar se ele tem acesso à organização ativa e se pode executar a ação desejada naquele contexto.

### Camadas de autorização
A autorização pode ser aplicada em mais de um nível.

#### 1. Na entrada da view
Bloqueia acesso precoce e melhora clareza da resposta.

#### 2. No service
Garante segurança mesmo se o fluxo for chamado por outra view, task ou integração interna.

#### 3. Na consulta dos dados
Garante isolamento entre tenants e impede exposição indevida de registros.

### Estratégia recomendada
Aplicar autorização em profundidade:
- view protege a entrada
- selector restringe leitura ao tenant
- service protege escrita e regra crítica

### Modelo baseado em membership
Como o sistema possui organizações, a autorização deve girar em torno de um vínculo entre usuário e organização.

#### Exemplo conceitual
- `User`
- `Organization`
- `Membership`

A `Membership` define:
- vínculo do usuário com a organização
- papel exercido
- status do vínculo
- permissões derivadas

### Exemplo de papéis
- `owner`
- `admin`
- `manager`
- `staff`

### Recomendação
Papéis devem representar responsabilidade de negócio, não apenas níveis genéricos de sistema.

### Abordagem para verificação
Criar funções ou políticas explícitas para autorização.

#### Exemplos
- `user_can_manage_clients(user, organization)`
- `user_can_schedule_appointment(user, organization)`
- `user_can_view_financial(user, organization)`

### Exemplo simples
```python
def user_can_manage_clients(user, organization):
    membership = get_user_membership(user=user, organization=organization)
    if not membership or not membership.is_active:
        return False
    return membership.role in {"owner", "admin", "manager"}


```

### Uso na view

@login_required
def client_list_view(request):
    organization = request.active_organization

    if not user_can_manage_clients(request.user, organization):
        raise PermissionDenied

    clients = list_organization_clients(organization=organization)
    return render(request, "clients/list.html", {"clients": clients})

###USo no service

def create_client(*, organization, created_by, name, email, phone=None):
    if not user_can_manage_clients(created_by, organization):
        raise PermissionDenied

    return Client.objects.create(
        organization=organization,
        name=name,
        email=email,
        phone=phone,
        created_by=created_by,
    )


Por que validar também no service
Porque a regra de autorização não deve depender apenas da camada HTTP. Se amanhã o mesmo caso de uso for executado por:

painel administrativo
API
comando interno
task assíncrona
a proteção continua válida.

Permissões por papel versus permissão por ação
Há duas abordagens complementares.

Papéis
Mais simples para o início. Exemplo:

manager pode gerenciar clientes
staff pode apenas visualizar agenda
Permissões por ação
Mais flexível quando o sistema cresce. Exemplo:

clients.view_client
clients.create_client
clients.change_client
financial.view_invoice
Recomendação prática
Começar com papéis de negócio e evoluir para permissões mais granulares apenas quando houver necessidade real.

Escopo da autorização
Toda verificação deve responder três perguntas:

o usuário pertence a essa organização?
o vínculo está ativo?
esse papel pode executar essa ação?
Controle de acesso a registros
Além de autorizar a ação, é preciso restringir os registros acessados.

Errado
python


client = Client.objects.get(id=client_id)
Correto
python


client = Client.objects.get(
    id=client_id,
    organization=organization,
)
Benefício
Mesmo que um usuário tente acessar um ID de outro tenant, o sistema não expõe o dado.

Erros esperados
Quando usar 403
Quando o usuário está autenticado, mas não tem permissão para a ação.

Quando usar 404
Quando o registro não existe dentro do escopo acessível daquele tenant.

Importante
Em muitos casos, retornar 404 para recursos fora do tenant é melhor do que revelar que o registro existe.

Organização recomendada
text


core/
  permissions/
    clients.py
    schedule.py
    financial.py
Ou, se preferir por app:

text


clients/
  permissions.py
schedule/
  permissions.py
financial/
  permissions.py
Boas práticas
manter nomes explícitos nas funções de autorização
não espalhar lógica de papel por várias views
sempre validar organização ativa
não confiar apenas em elementos visuais da interface
aplicar autorização também em rotinas internas
revisar permissões em fluxos sensíveis
Anti-padrões a evitar
verificar apenas is_staff de forma genérica
misturar autenticação com autorização
deixar regra crítica só no frontend
consultar registro sem filtro por tenant
duplicar regras inconsistentes em vários pontos
Benefícios esperados
maior segurança entre organizações
menor risco de vazamento de dados
regras mais reutilizáveis
código mais previsível
evolução mais segura do sistema
Diretriz final
Controle de acesso deve ser explícito, centralizado e orientado ao contexto da organização ativa. Em sistema multi-tenant, toda ação relevante precisa validar usuário, vínculo, papel e escopo do dado


## 29. Estratégia de Middleware para Organização Ativa

Em um sistema multi-tenant baseado em organização, o conceito de organização ativa deve ser resolvido de forma centralizada, previsível e segura. O middleware é o lugar ideal para isso.

### Objetivo
Definir uma estratégia para:
- descobrir a organização ativa da requisição
- validar se o usuário tem acesso a ela
- disponibilizar esse contexto para toda a aplicação
- reduzir repetição de lógica nas views
- evitar inconsistência entre fluxos

### Papel do middleware
O middleware deve atuar no início do ciclo da requisição para:
- identificar o usuário autenticado
- resolver qual organização está ativa
- validar vínculo e acesso
- anexar esse contexto ao `request`

### Benefício principal
Sem um mecanismo central, cada view precisaria:
- descobrir a organização atual
- validar se o usuário pertence a ela
- tratar ausência de vínculo
- repetir regras de fallback

Isso gera duplicação e risco de falhas.

### Resultado esperado
Após o middleware executar, a aplicação deve poder usar algo como:
```python
request.active_organization
request.active_membership
Fontes possíveis para resolver a organização ativa
A estratégia pode variar conforme o produto.

Opção 1: sessão
A organização ativa fica salva na sessão do usuário.

Exemplo:

usuário escolhe a organização em um seletor
o sistema salva active_organization_id na sessão
o middleware recupera esse valor a cada requisição
Opção 2: subdomínio
A organização é inferida pelo host.

Exemplo:

empresa1.sistema.com
empresa2.sistema.com
Opção 3: URL
A organização aparece na rota.

Exemplo:

/orgs/10/clientes/
/o/clinica-centro/agenda/
Recomendação para este projeto
Se o sistema permite ao mesmo usuário alternar entre múltiplas organizações com interface web tradicional, usar sessão costuma ser a abordagem mais simples e prática.

Fluxo recomendado do middleware
verificar se o usuário está autenticado
recuperar a organização ativa da sessão
validar se a organização existe
validar se o usuário possui vínculo ativo com ela
anexar organização e membership ao request
tratar fallback quando não houver organização válida
Exemplo conceitual
python


class ActiveOrganizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.active_organization = None
        request.active_membership = None

        if request.user.is_authenticated:
            organization_id = request.session.get("active_organization_id")

            if organization_id:
                membership = (
                    Membership.objects
                    .select_related("organization")
                    .filter(
                        user=request.user,
                        organization_id=organization_id,
                        is_active=True,
                    )
                    .first()
                )

                if membership:
                    request.active_membership = membership
                    request.active_organization = membership.organization

        return self.get_response(request)
O que fazer quando não houver organização ativa
Esse ponto deve ser tratado explicitamente.

Possibilidades
redirecionar para uma tela de escolha de organização
selecionar automaticamente se houver apenas uma disponível
limpar valor inválido da sessão
bloquear áreas que exigem tenant ativo
Estratégia recomendada
Se o usuário possui apenas uma organização
Selecionar automaticamente.

Se possui várias
Exigir escolha explícita ou restaurar a última usada.

Se não possui nenhuma
Redirecionar para fluxo apropriado, como onboarding ou tela informativa.

Exemplo de fallback
python


memberships = list_user_memberships(user=request.user)

if len(memberships) == 1:
    request.session["active_organization_id"] = memberships[0].organization_id
Validação de segurança
O middleware não deve confiar cegamente no valor salvo em sessão.

Sempre validar:

se a organização existe
se o vínculo pertence ao usuário atual
se o vínculo está ativo
Caso o valor da sessão seja inválido
Ações recomendadas:

limpar active_organization_id
não definir tenant ativo
redirecionar quando a rota exigir contexto organizacional
Rotas que não exigem organização ativa
Nem toda rota precisa de tenant ativo.

Exemplos
login
logout
escolha de organização
onboarding inicial
convite para entrar em organização
páginas públicas
Estratégia prática
Criar uma convenção para distinguir:

rotas livres de tenant
rotas que exigem tenant obrigatório
Como impor tenant obrigatório
Há algumas opções:

Decorator
python


@require_active_organization
def client_list_view(request):
    ...
Mixin
Para Class-Based Views.

Verificação global com exceções
Middleware adicional que exige tenant em áreas específicas.

Organização sugerida
text


core/
  middleware/
    active_organization.py
Ou, se preferir estrutura simples:

text


core/middleware.py
Funções auxiliares úteis
get_user_memberships(user)
set_active_organization(request, organization)
clear_active_organization(request)
user_has_access_to_organization(user, organization)
Exemplo de troca de organização
python


@login_required
def switch_organization_view(request, organization_id):
    membership = get_object_or_404(
        Membership,
        user=request.user,
        organization_id=organization_id,
        is_active=True,
    )
    request.session["active_organization_id"] = membership.organization_id
    return redirect("dashboard:index")
Cuidados importantes
não resolver organização ativa em cada view manualmente
não confiar só no frontend para troca de organização
não assumir que sessão válida implica acesso válido permanente
não esquecer de tratar usuários sem vínculo
não misturar organização ativa com autorização de ação
Organização ativa não substitui permissão
Ter uma organização ativa significa apenas:

este é o tenant em contexto atual
Isso não significa automaticamente:

o usuário pode fazer qualquer ação dentro dele
Permissões continuam sendo verificadas separadamente.

Benefícios esperados
padronização do contexto multi-tenant
menos duplicação
views mais limpas
menor risco de acesso indevido
melhor experiência ao alternar organização
Diretriz final
A organização ativa deve ser resolvida cedo, de forma centralizada e segura. O middleware deve transformar o contexto multi-tenant em uma informação confiável disponível para toda a aplicação.

```
## 30. Estratégia para Troca de Organização e Contexto do Usuário

A troca de organização é uma operação sensível em sistemas multi-tenant. Ela altera o contexto ativo do usuário e impacta diretamente leituras, escritas, permissões e experiência de navegação. Por isso, deve seguir um fluxo claro, seguro e consistente.

### Objetivo
Definir como o usuário pode:
- visualizar as organizações às quais pertence
- escolher uma organização ativa
- alternar entre organizações com segurança
- manter o contexto corretamente durante a navegação
- evitar inconsistências entre sessão, permissões e tenant ativo

### Princípio central
O usuário pode pertencer a múltiplas organizações, mas a aplicação opera com uma organização ativa por vez.

Essa organização ativa:
- define o escopo de leitura e escrita
- influencia permissões contextuais
- orienta navegação, menus e dashboards
- deve estar disponível de forma explícita no `request`

### Regra principal
Trocar de organização não é apenas mudar interface.
É alterar o contexto operacional do sistema.

### Quando a troca deve acontecer
A troca pode ser iniciada por:
- seletor no cabeçalho
- tela de escolha após login
- redirecionamento após aceitar convite
- onboarding inicial
- acesso a link específico de uma organização permitida

### Estratégia recomendada
A troca deve acontecer por uma action explícita no backend, validando sempre:
- se o usuário está autenticado
- se pertence à organização desejada
- se o vínculo está ativo
- se a organização pode ser usada naquele momento

### Fluxo recomendado
1. usuário solicita trocar para uma organização
2. backend valida vínculo ativo
3. sistema grava `active_organization_id` na sessão
4. próxima requisição passa a usar novo tenant ativo
5. interface é atualizada com o novo contexto

### Exemplo de view para troca
```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from organizations.models import Membership

@login_required
def switch_organization_view(request, organization_id):
    membership = get_object_or_404(
        Membership,
        user=request.user,
        organization_id=organization_id,
        is_active=True,
    )

    request.session["active_organization_id"] = membership.organization_id
    return redirect("dashboard:index")
```
Por que essa abordagem é segura
Porque o backend não aceita simplesmente qualquer organization_id. Ele confirma que:

a organização existe
o usuário possui vínculo com ela
o vínculo está ativo
O que mostrar na interface
A interface deve deixar claro:

qual organização está ativa
quais organizações estão disponíveis para troca
qual papel o usuário exerce, quando isso for relevante
para onde o usuário será levado após a troca
Exemplo de contexto para template
python


def organization_context(request):
    return {
        "active_organization": getattr(request, "active_organization", None),
        "active_membership": getattr(request, "active_membership", None),
    }
Lista de organizações do usuário
A listagem disponível para seleção deve vir sempre do backend com base nos vínculos ativos.

Exemplo de selector
python


def list_user_organizations(*, user):
    return (
        Membership.objects
        .select_related("organization")
        .filter(user=user, is_active=True)
        .order_by("organization__name")
    )
Seleção automática
Quando o usuário possui apenas uma organização válida, o sistema pode ativá-la automaticamente.

Recomendação prática
Se há uma única organização
Selecionar automaticamente e seguir fluxo normal.

Se há múltiplas
Permitir escolha explícita e manter última organização usada.

Se não há nenhuma
Redirecionar para onboarding, convite pendente ou tela informativa.

Persistência do contexto
O contexto da organização ativa deve ficar na sessão.

Exemplo
python


request.session["active_organization_id"] = organization.id
Quando limpar o contexto
O contexto deve ser limpo quando:

o usuário faz logout
o vínculo com a organização deixa de ser válido
a organização é desativada
o valor da sessão se torna inconsistente
há troca forçada de contexto após revogação de acesso
Função auxiliar recomendada
python


def clear_active_organization(request):
    request.session.pop("active_organization_id", None)
Cuidados com URL de retorno
Se a troca ocorrer a partir de uma tela interna, pode haver vontade de redirecionar o usuário de volta para a página anterior.

Isso deve ser feito com cuidado, porque a rota anterior pode:

depender de um registro que não existe no novo tenant
exigir permissão que o usuário não tem na nova organização
apontar para contexto inconsistente
Recomendação
Após a troca de organização, redirecionar para uma página segura e neutra, como:

dashboard
agenda principal
lista principal do módulo
Papel do middleware após a troca
Depois que a sessão é atualizada, o middleware passa a resolver:

nova organização ativa
novo membership ativo
permissões contextuais aplicáveis à requisição
Troca de organização não substitui autorização
Mesmo com a organização ativa corretamente definida, cada ação ainda deve validar:

se o usuário pode executar aquela operação
se o papel atual permite acesso ao recurso
se o registro pertence ao tenant ativo
Problemas que essa estratégia evita
acesso a tenant sem vínculo
sessão apontando para organização inválida
navegação em contexto incorreto
vazamento de dados entre organizações
duplicação de lógica nas views
Organização sugerida
text


organizations/
  views/
    switch_organization.py
  selectors.py
  services.py
Ou, em estrutura simples:

text


organizations/
  views.py
Possível evolução
Com o crescimento do sistema, a troca de organização pode incluir:

auditoria de mudança de contexto
seleção de unidade ou filial dentro da organização
restauração de última página válida por tenant
preferências específicas por organização
Benefícios esperados
experiência previsível para o usuário
segurança no contexto multi-tenant
menor acoplamento da interface com regras de tenant
facilidade para expandir o sistema com múltiplos papéis e organizações
Diretriz final
Troca de organização deve ser uma operação explícita, validada no backend e persistida na sessão. O sistema deve tratar contexto ativo como parte essencial da segurança e da navegação, nunca como um simples detalhe visual.


## 31. Estratégia para Queries, Selectors e Leitura de Dados

A leitura de dados precisa seguir uma estratégia consistente para manter o sistema previsível, seguro e fácil de evoluir.

### Objetivo
Definir como consultar dados sem espalhar regras de acesso, filtros de tenant e otimizações por toda a aplicação.

### Princípio central
Nem toda leitura deve acontecer diretamente na view.
Consultas importantes devem ser centralizadas em funções explícitas de leitura.

### O que são selectors
Selectors são funções responsáveis por buscar e preparar dados para consumo da aplicação.

### Responsabilidades dos selectors
- encapsular consultas
- aplicar filtros corretos
- respeitar tenant ativo
- concentrar otimizações
- melhorar reutilização

### O que selectors não devem fazer
- regras de escrita
- efeitos colaterais
- criação ou alteração de registros
- decisões de fluxo HTTP

### Benefício
Quando a leitura fica centralizada:
- views ficam menores
- regras de consulta ficam previsíveis
- manutenção se torna mais simples
- segurança de escopo melhora

### Exemplo ruim
```python
def client_list_view(request):
    clients = Client.objects.filter(
        organization=request.active_organization
    ).order_by("name")
    return render(request, "clients/list.html", {"clients": clients})
```

Problema
Parece simples, mas a lógica de leitura começa a se espalhar.

Exemplo recomendado
python


def list_clients(*, organization):
    return (
        Client.objects
        .filter(organization=organization)
        .order_by("name")
    )
md


### Uso na view
```python
def client_list_view(request):
    clients = list_clients(organization=request.active_organization)
    return render(request, "clients/list.html", {"clients": clients})
Vantagem
Se amanhã a consulta precisar:

filtrar ativos
usar select_related
usar prefetch_related
mudar ordenação
aplicar busca
a mudança acontece em um único lugar.

Tipos comuns de selectors
listar registros
buscar detalhe por ID
buscar por slug
carregar dashboards
montar opções para formulários
consultas agregadas
Exemplo de listagem
python


def list_active_clients(*, organization):
    return (
        Client.objects
        .filter(
            organization=organization,
            is_active=True,
        )
        .order_by("name")
    )
Exemplo de detalhe com escopo
python


def get_client_by_id(*, organization, client_id):
    return get_object_or_404(
        Client,
        id=client_id,
        organization=organization,
    )
Regra importante
Toda leitura de entidade multi-tenant deve receber o tenant explicitamente.

Errado
python


def get_client_by_id(*, client_id):
    return Client.objects.get(id=client_id)
Certo
python


def get_client_by_id(*, organization, client_id):
    return Client.objects.get(
        id=client_id,
        organization=organization,
    )
Por que isso importa
Porque o isolamento entre organizações deve existir também na camada de leitura.

Selectors e performance
Selectors também são o lugar certo para otimizar consultas.

Exemplos de otimização
select_related() para relações diretas
prefetch_related() para relações reversas
only() ou defer() quando fizer sentido
agregações com annotate()
paginação



```md
### Exemplo com otimização
```python
def list_appointments_for_calendar(*, organization, start, end):
    return (
        Appointment.objects
        .select_related("client", "professional")
        .filter(
            organization=organization,
            starts_at__gte=start,
            starts_at__lt=end,
        )
        .order_by("starts_at")
    )
Selectors não substituem permissão
Mesmo uma consulta filtrada por tenant não elimina a necessidade de autorização.

Separação correta
permissão decide se pode acessar
selector decide como ler os dados
Organização sugerida
text


clients/
  selectors.py
schedule/
  selectors.py
financial/
  selectors.py
Convenção de nomes
Prefira nomes que indiquem intenção:

list_clients
get_client_by_id
list_open_invoices
get_dashboard_metrics
Evite nomes vagos
fetch_data
handle_query
get_info
Retorno esperado
Selectors normalmente retornam:

QuerySet
objeto único
estrutura agregada de leitura
Quando retornar QuerySet
Quando a camada chamadora ainda pode paginar, compor ou avaliar depois.

Quando retornar objeto único
Quando o caso de uso exige um único registro específico.

Quando retornar estrutura pronta
Em dashboard, relatórios ou telas com composição de múltiplas fontes.

Exemplo de agregação
python


from django.db.models import Count

def get_clients_summary(*, organization):
    return (
        Client.objects
        .filter(organization=organization)
        .aggregate(total=Count("id"))
    )
Cuidados importantes
não esconder filtro de tenant implícito demais
não colocar lógica de escrita em selector
não misturar regra HTTP com consulta
não duplicar a mesma query em várias views
não consultar fora do escopo da organização
Benefícios esperados
leitura padronizada
melhor isolamento entre tenants
consultas mais reutilizáveis
otimização centralizada
código mais limpo
Diretriz final
Leitura de dados deve ser explícita, reutilizável e orientada ao tenant. Selectors ajudam a transformar consultas em contratos claros de acesso à informação.
``

## 32. Estratégia para Services e Regras de Negócio

Services são responsáveis por concentrar regras de negócio que não pertencem ao model, à view ou ao form. Eles organizam operações importantes da aplicação de forma explícita, testável e reutilizável.

### Objetivo
Definir como encapsular fluxos de negócio para evitar lógica espalhada entre views, signals, serializers e models.

### Princípio central
Views devem orquestrar requisição e resposta.
Models representam dados e comportamentos essenciais da entidade.
Services executam casos de uso da aplicação.

### Quando usar service
Use service quando houver:
- operação com múltiplas etapas
- alteração de vários registros
- validação de negócio contextual
- integração com outras camadas
- necessidade de transação
- fluxo reutilizado em mais de um ponto

### Exemplos comuns
- criar agendamento
- cancelar atendimento
- registrar pagamento
- aceitar convite
- trocar organização ativa
- gerar cobrança
- reativar cliente

### O que não colocar na view
A view não deve conter:
- regras longas de validação de negócio
- múltiplas escritas encadeadas
- transações complexas
- efeitos colaterais relevantes
- integração direta com muitos modelos

### Exemplo ruim
```python
def create_appointment_view(request):
    client = Client.objects.get(
        id=request.POST["client_id"],
        organization=request.active_organization,
    )
    professional = Professional.objects.get(
        id=request.POST["professional_id"],
        organization=request.active_organization,
    )
    appointment = Appointment.objects.create(
        organization=request.active_organization,
        client=client,
        professional=professional,
        starts_at=request.POST["starts_at"],
    )
    AuditLog.objects.create(
        organization=request.active_organization,
        actor=request.user,
        action="appointment_created",
        target_id=appointment.id,
    )
    return redirect("appointments:detail", appointment_id=appointment.id)
```

Problema
A regra fica acoplada ao HTTP e difícil de testar isoladamente.

Exemplo recomendado
python


from django.db import transaction

@transaction.atomic
def create_appointment(*, organization, actor, client, professional, starts_at):
    appointment = Appointment.objects.create(
        organization=organization,
        client=client,
        professional=professional,
        starts_at=starts_at,
    )

    AuditLog.objects.create(
        organization=organization,
        actor=actor,
        action="appointment_created",
        target_id=appointment.id,
    )

    return appointment
Uso na view
python


def create_appointment_view(request):
    appointment = create_appointment(
        organization=request.active_organization,
        actor=request.user,
        client=client,
        professional=professional,
        starts_at=starts_at,
    )
    return redirect("appointments:detail", appointment_id=appointment.id)
Benefícios
regra reutilizável
testes mais simples
menor acoplamento com HTTP
melhor legibilidade
transações centralizadas
Assinatura recomendada
Services devem receber parâmetros explícitos, evitando depender de request inteiro.

Prefira
python


def cancel_appointment(*, appointment, actor, reason):
    ...
Evite
python


def cancel_appointment(request):
    ...
Regras de escrita
Toda alteração relevante de dados deve passar por um ponto de negócio claro.

Services e transações
Quando uma operação altera múltiplos registros, prefira transaction.atomic.

Services não são depósito genérico
Evite criar arquivos com funções aleatórias e sem fronteira clara.

Organização sugerida
text


appointments/
  services.py
clients/
  services.py
billing/
  services.py
Ou por caso de uso
text


appointments/services/
  create_appointment.py
  cancel_appointment.py
Services e validação
Validação simples de formato pode ficar em form ou serializer. Validação de negócio deve ficar no service.

Exemplos de validação de negócio
impedir conflito de agenda
impedir pagamento duplicado
impedir cancelamento após prazo
garantir vínculo com tenant ativo
Services e efeitos colaterais
Se a operação precisa:

auditar
disparar evento
enviar notificação
atualizar histórico
o service é um bom ponto para coordenar isso.

Diretriz final
Service é a camada de casos de uso. Ele deve concentrar operações de negócio com entrada explícita, comportamento previsível e foco em consistência.




```md
## 33. Estratégia para Permissões por Organização e Papel

Permissão em ambiente multi-tenant não depende apenas de autenticação. O usuário precisa estar autenticado, vinculado à organização ativa e autorizado conforme seu papel naquele contexto.

### Objetivo
Definir como controlar acesso por organização, papel e ação permitida.

### Princípio central
Permissão é contextual.
O mesmo usuário pode ter papéis diferentes em organizações diferentes.

### Consequência prática
Não basta perguntar se o usuário está logado.
É preciso verificar:
- qual organização está ativa
- qual vínculo ele possui nela
- qual papel está associado ao vínculo
- se a ação é permitida naquele contexto

### Exemplo
Um usuário pode ser:
- administrador na organização A
- recepcionista na organização B
- sem acesso à organização C

### Fonte da permissão
A autorização deve se basear no `membership` ativo ou equivalente.

### Exemplo de campos úteis
- `user`
- `organization`
- `role`
- `is_active`

### Regra essencial
Toda checagem de permissão deve considerar o tenant ativo.

### Erro comum
Usar grupos globais do Django como única fonte de autorização em sistema multi-tenant.

### Problema
Grupos globais não representam bem papéis diferentes por organização.

### Estratégia recomendada
Ter papéis associados ao vínculo do usuário com a organização.

### Exemplo
```python
class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
Função simples de autorização
python


def user_has_role(*, membership, allowed_roles):
    return membership is not None and membership.role in allowed_roles
Exemplo de uso
python


def can_manage_clients(*, membership):
    return user_has_role(
        membership=membership,
        allowed_roles={"owner", "admin", "manager"},
    )
Na view
python


from django.http import HttpResponseForbidden

def client_create_view(request):
    if not can_manage_clients(membership=request.active_membership):
        return HttpResponseForbidden("Sem permissão")
Melhor prática
Permissões devem ser nomeadas por capacidade, não apenas por cargo.

Prefira
can_manage_clients
can_view_financial_reports
can_cancel_appointments
Evite
is_admin_or_owner_or_manager_for_clients
Vantagem
A regra fica legível e pode evoluir sem quebrar todas as views.

Permissão por ação
Permissões podem variar por operação:

visualizar
criar
editar
excluir
exportar
aprovar
cancelar
Permissão por módulo
Também pode haver capacidades por área:

agenda
clientes
financeiro
relatórios
equipe
Cuidado importante
Permissão não substitui filtro de tenant. Mesmo autorizado, o usuário só pode atuar sobre dados da organização ativa.

Combinação correta
middleware resolve tenant e membership
policy verifica capacidade
selector ou service atua no escopo do tenant
Organização sugerida
text


permissions/
  policies.py
Ou por app:

text


clients/policies.py
billing/policies.py
schedule/policies.py
Benefícios
regras explícitas
menos duplicação
autorização contextual
evolução segura de papéis
melhor testabilidade
Diretriz final
Autorização em multi-tenant deve ser orientada por organização ativa e papel contextual, nunca apenas por autenticação ou permissão global isolada.




```md
## 34. Estratégia para Auditoria e Rastreabilidade

Em operações críticas, não basta alterar dados. É importante registrar quem fez a ação, quando ela ocorreu, em qual organização e sobre qual recurso.

### Objetivo
Definir como registrar eventos relevantes para investigação, suporte, conformidade e segurança.

### Princípio central
Toda ação importante deve ser rastreável.

### O que auditar
Priorize ações como:
- criação
- atualização relevante
- cancelamento
- exclusão lógica
- mudança de status
- troca de organização
- alteração de permissão
- emissão financeira
- ações administrativas

### Campos comuns em auditoria
- organização
- ator
- ação
- tipo de recurso
- identificador do recurso
- timestamp
- metadados
- origem da ação

### Exemplo de model
```python
class AuditLog(models.Model):
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE)
    actor = models.ForeignKey("auth.User", null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=100)
    target_model = models.CharField(max_length=100)
    target_id = models.CharField(max_length=64)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
O que registrar em metadata
valores antigos e novos quando fizer sentido
motivo informado pelo usuário
contexto da operação
origem técnica
identificadores auxiliares
Exemplo de uso
python


def log_audit_event(*, organization, actor, action, target_model, target_id, metadata=None):
    return AuditLog.objects.create(
        organization=organization,
        actor=actor,
        action=action,
        target_model=target_model,
        target_id=str(target_id),
        metadata=metadata or {},
    )
Quando chamar
A auditoria pode ser disparada dentro de services que executam ações relevantes.

Exemplo
python


def cancel_appointment(*, appointment, actor, reason):
    appointment.status = "cancelled"
    appointment.cancel_reason = reason
    appointment.save(update_fields=["status", "cancel_reason"])

    log_audit_event(
        organization=appointment.organization,
        actor=actor,
        action="appointment_cancelled",
        target_model="Appointment",
        target_id=appointment.id,
        metadata={"reason": reason},
    )
O que evitar
auditar tudo indiscriminadamente
depender apenas de logs de aplicação
registrar informação sensível sem necessidade
misturar auditoria com mensagens para usuário
Auditoria não é log técnico comum
Log técnico ajuda diagnóstico. Auditoria ajuda rastrear ações de negócio e segurança.

Exemplos de diferença
log técnico: erro de timeout no banco
auditoria: usuário X cancelou agendamento Y
Multi-tenant
Todo evento auditável deve guardar a organização associada.

Benefícios
investigação de incidentes
suporte operacional
histórico confiável
responsabilização
trilha de segurança
Evoluções futuras
interface para consulta de auditoria
filtros por ator e período
retenção por política
exportação segura
correlação com eventos de sistema
Diretriz final
Auditoria deve registrar ações de negócio relevantes com contexto suficiente para reconstruir o que aconteceu de forma segura e objetiva.




```md
## 35. Estratégia para Soft Delete e Ciclo de Vida dos Registros

Nem todo dado deve ser removido fisicamente. Em muitos cenários, é melhor marcar registros como inativos, arquivados ou removidos logicamente.

### Objetivo
Definir como tratar exclusão lógica, arquivamento e estados de vida dos dados sem comprometer integridade e histórico.

### Princípio central
Excluir do ponto de vista do usuário nem sempre significa apagar do banco.

### Quando usar soft delete
Use quando houver necessidade de:
- preservar histórico
- manter rastreabilidade
- evitar perda acidental
- sustentar vínculos antigos
- atender regras de negócio

### Exemplo de campos
- `is_deleted`
- `deleted_at`
- `deleted_by`
- `status`

### Exemplo simples
```python
class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
Exclusão lógica
python


from django.utils import timezone

def soft_delete_instance(*, instance):
    instance.is_deleted = True
    instance.deleted_at = timezone.now()
    instance.save(update_fields=["is_deleted", "deleted_at"])
Regra importante
Se usar soft delete, as consultas padrão devem excluir registros removidos.

Exemplo de selector
python


def list_active_clients(*, organization):
    return Client.objects.filter(
        organization=organization,
        is_deleted=False,
    )
Problema comum
Implementar soft delete no model, mas esquecer de filtrar em todas as leituras.

Consequência
Registros “apagados” continuam aparecendo em listas, relatórios e seletores.

Ciclo de vida
Além de ativo e removido, muitas entidades têm estados intermediários:

draft
active
inactive
archived
cancelled
Exemplo
Um cliente pode estar:

ativo
inativo
arquivado
Um agendamento pode estar:

agendado
confirmado
concluído
cancelado
ausente
Recomendação
Nem tudo precisa virar soft delete. Às vezes um status representa melhor o ciclo de vida.

Quando preferir status
Quando a entidade continua válida no negócio, apenas mudou de fase.

Quando preferir soft delete
Quando a entidade deixa de aparecer operacionalmente, mas ainda precisa existir historicamente.

Cuidados
não permitir edição indevida de item removido
validar dependências antes de ocultar
registrar auditoria da remoção lógica
decidir se restauração será permitida
Restauração
Se fizer sentido no negócio, mantenha ação explícita de restore.

Benefícios
preservação de histórico
menor risco de perda
suporte a auditoria
reversibilidade em casos controlados
Diretriz final
Ciclo de vida dos registros deve ser modelado de forma explícita. Use status para fases de negócio e soft delete para remoção lógica com preservação de histórico.




```md
## 36. Estratégia para Idempotência e Operações Sensíveis

Algumas operações não podem gerar efeitos duplicados quando repetidas por clique duplo, retry de rede ou reprocessamento acidental.

### Objetivo
Definir como proteger operações sensíveis contra duplicação indevida.

### Princípio central
Uma mesma intenção do usuário não deve produzir efeitos múltiplos por acidente.

### Exemplos críticos
- registrar pagamento
- gerar cobrança
- criar agendamento
- emitir nota
- enviar convite
- concluir atendimento
- processar webhook

### Problema comum
O usuário clica duas vezes em “salvar” e o sistema cria dois registros.

### Idempotência
Uma operação idempotente produz o mesmo resultado lógico quando repetida com a mesma chave de intenção.

### Estratégias possíveis
- chave idempotente
- restrição única no banco
- verificação prévia por referência externa
- lock transacional
- deduplicação por evento

### Exemplo de chave idempotente
```python
class IdempotencyKey(models.Model):
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE)
    key = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "key"],
                name="uniq_idempotency_key_per_org",
            )
        ]
Uso conceitual
Antes de executar uma ação sensível:

verifica se a chave já foi usada
se já existe, retorna resultado compatível
se não existe, processa e registra
Outra proteção importante
Use restrições únicas quando houver identificador natural da operação.

Exemplo
python


class Payment(models.Model):
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE)
    external_reference = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "external_reference"],
                name="uniq_payment_reference_per_org",
            )
        ]
Benefício
Mesmo que a aplicação falhe em algum ponto, o banco ajuda a impedir duplicidade.

Casos com webhook
Webhooks são candidatos clássicos a reentrega. O sistema deve tratar reprocessamento como comportamento esperado.

Cuidados
não confiar só no frontend para evitar duplo envio
não depender apenas de desabilitar botão
não tratar duplicidade só visualmente
não ignorar retries legítimos
Services e idempotência
A lógica de deduplicação deve ficar próxima da operação sensível, geralmente em services.

Benefícios
evita registros duplicados
reduz inconsistência financeira
melhora robustez contra falhas de rede
suporta retries seguros
Diretriz final
Operações críticas devem ser desenhadas para tolerar repetição sem gerar efeitos duplicados indevidos, preferencialmente com proteção no banco e na camada de negócio.




```md
## 37. Estratégia para Concorrência e Consistência Transacional

Quando múltiplas ações acontecem ao mesmo tempo, o sistema precisa preservar integridade e evitar estados inválidos.

### Objetivo
Definir como tratar concorrência, disputas de escrita e consistência em operações críticas.

### Princípio central
Se duas requisições competem pelo mesmo recurso, a aplicação deve ter comportamento previsível.

### Exemplos de risco
- dois usuários tentando ocupar o mesmo horário
- pagamento sendo processado ao mesmo tempo
- alteração simultânea de saldo
- mudança concorrente de status
- baixa duplicada de cobrança

### Ferramentas principais
- `transaction.atomic`
- `select_for_update`
- restrições únicas
- validação de estado atual
- versionamento otimista em alguns cenários

### Exemplo de transação
```python
from django.db import transaction

@transaction.atomic
def confirm_appointment(*, appointment):
    if appointment.status != "scheduled":
        raise ValueError("Agendamento não pode ser confirmado")

    appointment.status = "confirmed"
    appointment.save(update_fields=["status"])
Limite desse exemplo
Sem lock, outra transação pode alterar o mesmo registro ao mesmo tempo dependendo do fluxo.

Exemplo com lock
python


from django.db import transaction

@transaction.atomic
def confirm_appointment(*, appointment_id):
    appointment = (
        Appointment.objects
        .select_for_update()
        .get(id=appointment_id)
    )

    if appointment.status != "scheduled":
        raise ValueError("Agendamento não pode ser confirmado")

    appointment.status = "confirmed"
    appointment.save(update_fields=["status"])
Quando usar lock
Use em operações onde leitura e escrita precisam ocorrer de forma consistente sobre o mesmo recurso.

Exemplo clássico
Reservar horário disponível.

Complemento importante
Mesmo com verificação de negócio, restrições no banco continuam valiosas.

Exemplo
Uma constraint de unicidade pode impedir dois agendamentos para o mesmo slot lógico, conforme a modelagem adotada.

Cuidados
não usar lock sem necessidade
manter transações curtas
evitar consultas externas dentro de transação
reduzir tempo de retenção de recursos
Concorrência não é só questão técnica
Ela impacta regras de negócio. O sistema precisa definir qual operação vence, falha ou deve ser repetida.

Benefícios
integridade de dados
menor risco de duplicidade
previsibilidade em cenários simultâneos
proteção em fluxos financeiros e agenda
Diretriz final
Operações com risco de disputa devem combinar transação, validação de estado e proteção no banco para manter consistência sob concorrência.




```md
## 38. Estratégia para Testes em Arquitetura Multi-tenant

Uma arquitetura multi-tenant exige testes que validem não apenas comportamento funcional, mas também isolamento entre organizações, autorização contextual e consistência de regras.

### Objetivo
Definir o que testar para garantir segurança, previsibilidade e evolução segura do sistema.

### Princípio central
Em multi-tenant, testar funcionalidade sem testar isolamento é insuficiente.

### Camadas prioritárias
Devem existir testes para:
- models
- selectors
- services
- permissões
- views ou endpoints
- middleware de tenant

### O que validar sempre
- usuário acessa apenas seus tenants
- dados não vazam entre organizações
- permissões respeitam papel contextual
- troca de organização funciona corretamente
- services preservam regras de negócio
- queries filtram tenant ativo

### Exemplo de cenário essencial
Criar duas organizações e verificar que um cliente da organização A não aparece na listagem da organização B.

### Testes de selector
Selectors devem ser testados para garantir:
- filtro correto por organização
- ordenação esperada
- exclusão de removidos logicamente
- otimizações quando relevante

### Testes de service
Services devem cobrir:
- fluxo feliz
- regras de negócio
- falhas esperadas
- efeitos colaterais
- auditoria
- transação em caso crítico

### Testes de permissão
É importante validar combinações como:
- mesmo usuário com papéis diferentes em tenants diferentes
- papel autorizado em um módulo, mas não em outro
- vínculo inativo bloqueando acesso

### Testes de view
Views e endpoints devem confirmar:
- autenticação obrigatória
- tenant ativo exigido quando necessário
- redirecionamentos corretos
- resposta proibida sem permissão
- escopo correto do objeto acessado

### Teste importante de segurança
Acessar diretamente o ID de um objeto de outra organização deve falhar.

### Exemplo esperado
- 404 quando o objeto é filtrado por tenant
- ou 403 quando a política for explícita nesse sentido

### Fixtures e factories
Use factories para montar cenários com:
- múltiplas organizações
- memberships variados
- objetos de tenants distintos
- papéis diferentes

### Benefícios
- regressões detectadas cedo
- maior confiança em refatorações
- segurança de isolamento
- estabilidade da arquitetura

### Diretriz final
Testes em multi-tenant devem provar isolamento, autorização e consistência de negócio, não apenas funcionamento superficial das telas.
md


## 39. Estratégia para Observabilidade e Logs

Sistemas em produção precisam permitir entendimento rápido do que está acontecendo. Observabilidade ajuda a diagnosticar falhas, acompanhar comportamento e identificar gargalos operacionais.

### Objetivo
Definir como registrar informações úteis para operação, suporte e evolução do sistema.

### Princípio central
Não basta o sistema funcionar. Ele precisa ser observável.

### Componentes principais
- logs
- métricas
- tracing, quando aplicável
- correlação de eventos
- monitoramento de erros

### O que registrar em logs
- erros de aplicação
- falhas de integração
- eventos operacionais importantes
- tempo de execução de fluxos críticos
- contexto mínimo para diagnóstico

### Contexto útil em multi-tenant
- organization_id
- user_id
- request_id
- nome da ação
- status da operação

### Cuidado importante
Logs não devem expor:
- senhas
- tokens
- dados sensíveis desnecessários
- informações pessoais em excesso

### Exemplo conceitual
```python
logger.info(
    "appointment_created",
    extra={
        "organization_id": organization.id,
        "user_id": actor.id,
        "appointment_id": appointment.id,
    },
)
Logs estruturados
Prefira logs estruturados quando possível, porque facilitam busca, filtro e correlação.

Diferença entre log e auditoria
log operacional ajuda diagnóstico técnico
auditoria registra ação de negócio rastreável
Métricas úteis
número de erros por endpoint
tempo médio de resposta
quantidade de agendamentos criados
falhas de pagamento
volume por organização
taxa de retry em integrações
Alertas
O sistema deve permitir alertas para:

aumento abrupto de erro
fila travada
falha recorrente em integração
latência elevada
exceções críticas
Benefícios
diagnóstico mais rápido
suporte mais eficiente
visibilidade de gargalos
operação mais confiável
Diretriz final
Observabilidade deve combinar logs úteis, contexto identificável e métricas acionáveis, sem expor dados sensíveis e sem confundir diagnóstico com auditoria.




```md
## 40. Estratégia para Escalabilidade e Evolução da Arquitetura

Arquitetura não deve atender apenas o presente. Ela precisa permitir crescimento de volume, times, módulos e complexidade sem exigir reescrita constante.

### Objetivo
Definir direções para evolução sustentável da arquitetura ao longo do crescimento do produto.

### Princípio central
Escalabilidade não é só suportar mais acesso. É continuar evoluindo com clareza e segurança.

### Tipos de crescimento esperados
- mais organizações
- mais usuários por organização
- mais módulos de negócio
- mais regras contextuais
- mais integrações
- mais volume de dados
- mais equipe de desenvolvimento

### Base para evoluir bem
A arquitetura deve preservar:
- separação entre leitura e escrita
- isolamento por tenant
- regras de negócio em services
- consultas em selectors
- autorização contextual
- fronteiras claras entre apps

### Sinais de boa evolução
- novas features entram sem duplicar regra antiga
- permissões não se espalham caoticamente
- consultas críticas têm ponto claro de manutenção
- onboarding de novos devs é viável
- testes acompanham crescimento

### Possíveis evoluções técnicas
- cache em consultas específicas
- processamento assíncrono para tarefas demoradas
- particionamento de carga
- filas para integrações e notificações
- replicação de leitura em cenários avançados
- extração de módulos mais independentes

### Cuidado
Escalar cedo demais com complexidade desnecessária pode piorar manutenção.

### Estratégia saudável
Evolua por necessidade comprovada, preservando fundamentos simples e consistentes.

### O que evitar
- regras duplicadas por app
- acesso direto ao model em qualquer lugar
- permissão acoplada à view de forma caótica
- integrações síncronas em fluxos críticos sem controle
- ausência de testes nas camadas centrais

### Decisão importante
Antes de distribuir mais a arquitetura, garanta que o monólito esteja bem modularizado.

### Monólito bem organizado pode escalar muito
Com:
- apps bem definidos
- services
- selectors
- políticas de autorização
- observabilidade
- testes
- filas quando necessário

### Benefícios dessa visão
- menor custo de mudança
- maior previsibilidade
- crescimento incremental
- menor risco arquitetural
- base sólida para novas demandas

### Diretriz final
Escalabilidade sustentável nasce de uma arquitetura simples, modular e disciplinada. Antes de buscar complexidade estrutural, consolide separação de responsabilidades, isolamento de tenant e clareza das regras centrais.

