Objetivo
Definir uma arquitetura consistente para controle de navegação e autorização baseada em:

Module
ModuleItem
Permission
Role (TenantModel)
A estrutura deve:

separar agrupamento de funcionalidade navegável
permitir geração previsível de permissões
usar identificadores estáveis
funcionar bem com multi-tenant
facilitar montagem de menu e checagem de autorização
Decisão Arquitetural Principal
A modelagem adotada é:

text


Module -> ModuleItem -> Permission
Role -> permissions
Responsabilidade de cada entidade
Module
Representa o agrupador lógico/visual do sistema.

Exemplos:

Financeiro
Comercial
Cadastros
Função:

agrupar funcionalidades
organizar menu em alto nível
armazenar nome, slug, ícone e ordenação
ModuleItem
Representa a funcionalidade navegável real.

Exemplos:

Contas a Pagar
Contas a Receber
Controle de Caixa
Função:

apontar para rota/tela
pertencer a um módulo
servir de base para geração de permissões
controlar exibição em menu
Permission
Representa a permissão de ação sobre um ModuleItem.

Exemplos:

visualizar contas a pagar
adicionar contas a pagar
alterar contas a pagar
excluir contas a pagar
Função:

armazenar ação
possuir codename técnico único
permitir associação com papéis (Role)
Role
Representa um conjunto de permissões dentro de um tenant.

Exemplos:

Administrador Financeiro
Operador Financeiro
Gestor Comercial
Função:

agrupar permissões
existir por tenant
ser atribuída a usuários conforme regra do projeto
Decisão sobre Slug e Identidade Técnica
Foi decidido padronizar a identidade semântica com slug.

Regra adotada
name: valor humano, exibido em interface
slug: identificador estável e semântico
codename: identificador técnico da permissão, derivado dos slugs
Motivo
Isso melhora:

consistência
previsibilidade
composição de codenames
estabilidade técnica
clareza de modelagem
Regra de composição do codename
O codename da permissão deve seguir o padrão:

text


{action}_{module_key}_{item_key}
Onde:

module_key = module.slug.replace("-", "_")
item_key = item.slug.replace("-", "_")
Exemplo
text


view_financeiro_contas_pagar
add_financeiro_contas_pagar
change_financeiro_contas_pagar
delete_financeiro_contas_pagar
Decisão sobre name e codename em Permission
Foi decidido manter os dois campos.

name
Função:

nome amigável para humanos
uso em admin, telas, checkboxes, relatórios e auditoria
Exemplo:

text


Visualizar Contas a Pagar
codename
Função:

chave técnica única do sistema
uso em backend, autorização, comparações e regras de negócio
Exemplo:

text


view_financeiro_contas_pagar
Motivo para manter ambos
Usar apenas um dos dois traria problemas:

só name: ruim para regras técnicas
só codename: ruim para interface humana
Decisão sobre permission_key
A lógica de chave de permissão não fica mais em Module.

Motivo
Como a permissão é sobre a funcionalidade navegável, o centro da autorização passa a ser o ModuleItem.

Portanto
A lógica abaixo:

python


@property
def permission_key(self):
    return self.slug.replace("-", "_")
deve existir em ModuleItem.

O Module pode manter uma chave auxiliar como:

python


@property
def key(self):
    return self.slug.replace("-", "_")
Decisão sobre geração automática de permissões
As permissões padrão devem ser geradas a partir do ModuleItem.

Motivo
O Module não representa mais uma tela ou recurso diretamente; ele apenas agrupa.

Então a criação automática:

python


def create_default_permissions(self):
    for action in Permission.Action.values:
        Permission.objects.get_or_create(
            item=self,
            action=action,
        )
fica em ModuleItem.

Ações padrão adotadas
text


view
add
change
delete
Estrutura Final dos Models
Module
Papel
Agrupador lógico e visual.

Campos
name
slug
description
icon
order
is_active
show_in_menu
Observações
slug é gerado a partir de name, se ausente
possui propriedade key
Implementação
python


from django.db import models
from django.utils.text import slugify

from core.models.base import BaseModel


class Module(BaseModel):
    name = models.CharField("nome", max_length=100, unique=True)
    slug = models.SlugField("slug", max_length=120, unique=True, blank=True)
    description = models.TextField("descrição", blank=True, default="")
    icon = models.CharField("ícone", max_length=50, blank=True, default="")
    order = models.PositiveIntegerField("ordem", default=0)
    is_active = models.BooleanField("ativo", default=True)
    show_in_menu = models.BooleanField("exibir no menu", default=True)

    class Meta:
        db_table = "modules"
        verbose_name = "módulo"
        verbose_name_plural = "módulos"
        ordering = ["order", "name"]

    @property
    def key(self):
        return self.slug.replace("-", "_")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
ModuleItem
Papel
Funcionalidade navegável e base de permissão.

Campos
module
name
slug
description
url_name
icon
order
is_active
show_in_menu
Observações
slug é gerado a partir de name, se ausente
possui key
possui full_key
gera permissões padrão na criação
Implementação
python


from django.db import models
from django.utils.text import slugify

from core.models.base import BaseModel
from core.models.module import Module


class ModuleItem(BaseModel):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="módulo",
    )
    name = models.CharField("nome", max_length=100)
    slug = models.SlugField("slug", max_length=120, blank=True)
    description = models.TextField("descrição", blank=True, default="")
    url_name = models.CharField("nome da rota", max_length=150, blank=True, default="")
    icon = models.CharField("ícone", max_length=50, blank=True, default="")
    order = models.PositiveIntegerField("ordem", default=0)
    is_active = models.BooleanField("ativo", default=True)
    show_in_menu = models.BooleanField("exibir no menu", default=True)

    class Meta:
        db_table = "module_items"
        verbose_name = "item do módulo"
        verbose_name_plural = "itens do módulo"
        ordering = ["module__order", "module__name", "order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["module", "name"],
                name="unique_module_item_name",
            ),
            models.UniqueConstraint(
                fields=["module", "slug"],
                name="unique_module_item_slug",
            ),
        ]

    @property
    def key(self):
        return self.slug.replace("-", "_")

    @property
    def full_key(self):
        return f"{self.module.key}_{self.key}"

    def create_default_permissions(self):
        from core.models.permission import Permission

        for action in Permission.Action.values:
            Permission.objects.get_or_create(
                item=self,
                action=action,
            )

    def save(self, *args, **kwargs):
        creating = self.pk is None

        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

        if creating:
            self.create_default_permissions()

    def __str__(self):
        return f"{self.module.name} - {self.name}"
Permission
Papel
Permissão técnica derivada de uma ação sobre um ModuleItem.

Campos
item
action
name
codename
description
is_active
Observações
name é amigável
codename é único e técnico
unicidade por item + action
codename é derivado automaticamente se não informado
Implementação
python


from django.db import models

from core.models.base import BaseModel
from core.models.module_item import ModuleItem


class Permission(BaseModel):
    class Action(models.TextChoices):
        VIEW = "view", "Visualizar"
        ADD = "add", "Adicionar"
        CHANGE = "change", "Alterar"
        DELETE = "delete", "Excluir"

    item = models.ForeignKey(
        ModuleItem,
        on_delete=models.CASCADE,
        related_name="permissions",
        verbose_name="item do módulo",
    )
    action = models.CharField("ação", max_length=20, choices=Action.choices)
    name = models.CharField("nome", max_length=150, blank=True)
    codename = models.CharField("codename", max_length=150, unique=True, blank=True)
    description = models.TextField("descrição", blank=True, default="")
    is_active = models.BooleanField("ativo", default=True)

    class Meta:
        db_table = "permissions"
        verbose_name = "permissão"
        verbose_name_plural = "permissões"
        ordering = ["item__module__order", "item__order", "action"]
        constraints = [
            models.UniqueConstraint(
                fields=["item", "action"],
                name="unique_permission_item_action",
            ),
        ]

    @property
    def display_name(self):
        return self.name or f"{self.get_action_display()} {self.item.name}"

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = f"{self.get_action_display()} {self.item.name}"

        if not self.codename:
            self.codename = f"{self.action}_{self.item.full_key}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name
Role (TenantModel)
Papel
Conjunto de permissões pertencente a um tenant.

Campos
name
slug
description
level
is_active
permissions
Observações
slug gerado de name, se ausente
unicidade por tenant para name e slug
possui helper para listar codenames
possui helper has_permission
Implementação
python


from django.db import models
from django.utils.text import slugify

from core.models.permission import Permission
from core.models.tenant import TenantModel


class Role(TenantModel):
    name = models.CharField("nome", max_length=100)
    slug = models.SlugField("slug", max_length=120, blank=True)
    description = models.TextField("descrição", blank=True, default="")
    level = models.PositiveIntegerField("nível", default=0)
    is_active = models.BooleanField("ativo", default=True)
    permissions = models.ManyToManyField(
        Permission,
        related_name="roles",
        verbose_name="permissões",
        blank=True,
    )

    class Meta:
        db_table = "roles"
        verbose_name = "papel"
        verbose_name_plural = "papéis"
        ordering = ["level", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "name"],
                name="unique_role_name_per_tenant",
            ),
            models.UniqueConstraint(
                fields=["tenant", "slug"],
                name="unique_role_slug_per_tenant",
            ),
        ]

    @property
    def permission_codenames(self):
        return list(
            self.permissions.filter(is_active=True).values_list("codename", flat=True)
        )

    def has_permission(self, codename: str) -> bool:
        return self.permissions.filter(
            codename=codename,
            is_active=True,
        ).exists()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
Regras de Negócio Consolidadas
1. Module não representa mais uma tela
Ele representa apenas um agrupador.

2. ModuleItem representa a funcionalidade navegável
É nele que ficam rota, ícone específico, ordem e geração de permissões.

3. A permissão nasce do ModuleItem
Não do Module.

4. codename é técnico e previsível
Sempre derivado do padrão:

text


action + module.slug + item.slug
5. Role é contextual ao tenant
As permissões são globais; os papéis são específicos do tenant.

Exemplo Concreto
Module
python


name = "Financeiro"
slug = "financeiro"
ModuleItem
python


name = "Contas a Pagar"
slug = "contas-pagar"
url_name = "financial:accounts_payable_list"
Permission gerada
python


action = "view"
name = "Visualizar Contas a Pagar"
codename = "view_financeiro_contas_pagar"
Role
python


name = "Operador Financeiro"
slug = "operador-financeiro"
Benefícios da Arquitetura
separação clara de responsabilidades
menu dinâmico mais simples
autorização previsível
estrutura consistente com slug
suporte natural a multi-tenant
facilidade para seeds e administração
facilidade de checagem por codename
Observações Futuras
Melhorias possíveis depois:

mover criação automática de permissões para post_save
adicionar validadores para url_name
criar helper global user_has_permission(codename)
criar builder de menu com base em Role + Permission
considerar filtros por module.is_active e item.is_active ao montar menu/autorização
Resumo Executivo
A decisão final foi:

manter Module como agrupador
usar ModuleItem como unidade navegável e autorizável
usar Permission com name e codename
usar Role como agregador de permissões por tenant
padronizar identidade com slug
derivar codename a partir de ação + módulo + item
Estrutura final:

text


Module -> ModuleItem -> Permission
Role (TenantModel) -> permissions
Se quiser, eu também posso converter isso em um formato mais “documentação de projeto”, com seções como:

Contexto
Problema
Decisão
Consequências
Modelagem final
Exemplos
Próximos passos
