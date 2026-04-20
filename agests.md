# LiaFit — Notas de Desenvolvimento

> **Versão:** 3.0  
> **Última atualização:** 18/04/2026  
> **Mantenedor:** Alberto  
> **Propósito:** Documento vivo de referência para arquitetura, regras de negócio, estado atual da implementação, roadmap técnico e decisões de desenvolvimento do projeto LiaFit.

---

## Sumário

1. [Visão Geral do Produto](#visão-geral-do-produto)
2. [Escopo e Princípios do Domínio](#escopo-e-princípios-do-domínio)
3. [Modelo Conceitual do Sistema](#modelo-conceitual-do-sistema)
4. [Arquitetura de Navegação e Contexto](#arquitetura-de-navegação-e-contexto)
5. [Arquitetura Técnica e Convenções](#arquitetura-técnica-e-convenções)
6. [Estado Atual da Implementação](#estado-atual-da-implementação)
7. [Problemas Identificados e Pontos de Atenção](#problemas-identificados-e-pontos-de-atenção)
8. [Plano de Correção e Evolução](#plano-de-correção-e-evolução)
9. [Roadmap por Sprints](#roadmap-por-sprints)
10. [Modelo de Dados Atual](#modelo-de-dados-atual)
11. [Fluxos Críticos do Sistema](#fluxos-críticos-do-sistema)
12. [Notas Técnicas e Débitos Técnicos](#notas-técnicas-e-débitos-técnicos)
13. [Histórico de Versões](#histórico-de-versões)

---

## Visão Geral do Produto

## Visão Geral do Produto

**LiaFit** é uma plataforma SaaS multi-tenant voltada para gestão de academias, estúdios, clínicas e profissionais da área de saúde, movimento e bem-estar.

A proposta central do produto é permitir que diferentes tipos de usuários convivam dentro de uma única plataforma, com a possibilidade de assumirem papéis distintos em contextos diferentes, sem precisar manter múltiplos cadastros ou múltiplos logins.

### Objetivo do produto

O LiaFit busca centralizar, em um único ambiente:

- a operação administrativa e comercial das organizações;
- a atuação dos profissionais vinculados a essas organizações;
- a experiência do cliente final, que pode acompanhar sua jornada em diferentes empresas por meio de um único acesso.

### Proposta de valor

A plataforma deve permitir que:

- a **organização** gerencie sua operação, agenda, equipe, clientes, módulos contratados e dados internos;
- o **profissional** acompanhe seus atendimentos, clientes, agenda e informações relacionadas à sua atuação;
- o **cliente final** tenha um ponto central de acesso à plataforma, podendo consultar sua própria área mesmo sem vínculo ativo com uma organização específica no momento.

### Premissa estrutural do produto

Um mesmo usuário pode:

- existir globalmente na plataforma sem vínculo com nenhuma organização;
- ser cliente de uma ou mais organizações;
- ser membro interno de uma ou mais organizações;
- acumular múltiplos papéis ao mesmo tempo, em organizações diferentes ou até dentro da mesma organização, conforme as regras do sistema.

Essa premissa é central para o produto e impacta diretamente:

- modelagem de dados;
- autenticação;
- navegação;
- construção de menus;
- controle de permissões;
- definição de contexto ativo durante a sessão.

### Tese central do sistema

O sistema deve tratar como cenário normal, e não como exceção, o fato de que:

- um mesmo CPF/email representa uma pessoa global;
- essa pessoa pode transitar entre contextos diferentes;
- o contexto organizacional é adicional ao contexto global do usuário;
- o acesso à plataforma não pode depender exclusivamente de vínculo com organização.

### Princípio funcional mais importante

O primeiro nível de acesso do sistema é o **nível global da plataforma**.

Isso significa que, após autenticação, o usuário entra inicialmente em seu contexto global e tem acesso à base da aplicação independentemente de possuir ou não vínculo organizacional naquele momento.

O contexto de organização, quando existir, deve ser tratado como uma camada complementar, ativada posteriormente conforme os vínculos do usuário.

### Perfis de uso previstos

O produto precisa suportar de forma nativa, entre outros, os seguintes cenários:

- usuário autenticado que ainda não possui vínculo com nenhuma organização;
- cliente que nunca foi atendido, mas já possui conta na plataforma;
- cliente atendido por múltiplas organizações;
- profissional vinculado a uma ou mais organizações;
- usuário híbrido, que ao mesmo tempo é cliente e profissional;
- administrador interno de uma organização;
- superusuário da plataforma.

### Consequência arquitetural

Por causa dessa visão de produto, a arquitetura do sistema não pode ser pensada apenas como tenant-first.

O sistema precisa operar com dois níveis de contexto:

1. **contexto global da plataforma**, disponível ao usuário autenticado;
2. **contexto organizacional**, opcional e dependente da existência de vínculos com organização.

Essa distinção deve orientar tanto o desenho do domínio quanto a implementação técnica.


---

## Escopo e Princípios do Domínio
## Escopo e Princípios do Domínio

Esta seção define os princípios estruturais que orientam o domínio do LiaFit.  
Esses princípios devem prevalecer sobre decisões locais de implementação.

### 1. O `User` é global na plataforma

O model `User` representa a pessoa em nível global.

Ele concentra os dados compartilhados entre todos os contextos da plataforma, como:

- identificação;
- credenciais de acesso;
- email;
- telefone;
- dados pessoais;
- estado de autenticação e ativação da conta.

O `User` não pertence a uma organização específica.  
Ele existe antes, acima e independentemente de qualquer vínculo organizacional.

---

### 2. Autenticação acontece antes do contexto organizacional

O login do sistema deve autenticar o usuário no escopo global da plataforma.

Em outras palavras:

- o usuário primeiro entra na plataforma;
- só depois o sistema verifica se ele possui contexto organizacional adicional.

O acesso inicial não deve depender de:

- `OrganizationMember`;
- organização ativa;
- papel organizacional;
- tenant previamente selecionado.

---

### 3. O contexto global é a camada base da experiência autenticada

Todo usuário autenticado deve ter acesso à camada base da aplicação.

Essa camada representa a experiência global da plataforma e deve existir mesmo quando o usuário:

- não possui vínculos com nenhuma organização;
- ainda não foi atendido por nenhuma organização;
- não atua como profissional;
- não possui membership em empresa alguma.

Esse contexto global é a base sobre a qual contextos adicionais podem ser carregados.

---

### 4. O contexto organizacional é opcional

O contexto organizacional só deve ser ativado quando houver vínculo válido entre o usuário e uma organização.

Esse contexto é complementar ao contexto global e pode incluir:

- organização ativa;
- membership;
- roles;
- módulos contratados;
- permissões;
- perfis funcionais dependentes do vínculo.

Se o usuário não possuir vínculo organizacional, o sistema deve continuar funcional no contexto global, sem erro e sem exigir tenant.

---

### 5. Cliente não é membro da organização

No domínio do LiaFit, cliente e membro interno da organização são conceitos diferentes.

#### `OrganizationMember`
Representa vínculo interno com a organização, voltado para operação e equipe.  
Exemplos:
- owner;
- admin;
- profissional;
- assistente;
- colaboradores internos.

#### `OrganizationClient`
Representa vínculo da pessoa como cliente atendido por uma organização.

Portanto:

- cliente **não deve depender** de `OrganizationMember`;
- cliente **não deve ser modelado como staff**;
- role `CLIENT` **não deve ser usada para representar usuário interno**.

---

### 6. O cliente é um ator global da plataforma

Mesmo quando não possui vínculo ativo com nenhuma organização, o cliente continua sendo um usuário válido da plataforma.

Isso significa que:

- ele pode autenticar;
- ele pode acessar sua área base;
- ele pode visualizar elementos globais compatíveis com seu estado atual;
- ele não deve ser bloqueado apenas por não possuir atendimento ou organização vinculada naquele momento.

A existência de atendimentos, organizações associadas ou dados clínicos/comerciais é um enriquecimento do contexto do cliente, e não um pré-requisito para sua existência na plataforma.

---

### 7. Usuário pode ser híbrido

O sistema deve assumir como cenário normal que um mesmo `User` possa acumular múltiplos contextos, como por exemplo:

- cliente de uma ou mais organizações;
- profissional em outra organização;
- assistente em outra;
- owner ou administrador de uma empresa.

Esses papéis não invalidam uns aos outros.  
Eles coexistem e devem ser tratados como camadas de relacionamento distintas.

---

### 8. Organização é extensão de contexto, não pré-requisito de acesso

A organização não é o ponto de entrada obrigatório no sistema.

O fluxo correto é:

1. autenticar o usuário;
2. carregar o contexto global;
3. disponibilizar a navegação base da plataforma;
4. verificar vínculos organizacionais;
5. carregar contexto organizacional quando aplicável.

Esse princípio deve orientar:

- middleware;
- redirecionamento pós-login;
- composição de menus;
- mixins de views;
- serviços de contexto;
- regras de permissão.

---

### 9. Menu global e menu organizacional devem ser separados

A navegação do sistema deve distinguir claramente dois níveis:

#### Menu global
Disponível a partir da autenticação, sem depender de tenant.

Exemplos:
- dashboard global;
- minha conta;
- perfil;
- preferências;
- área base do cliente.

#### Menu organizacional
Disponível apenas quando houver organização ativa e vínculo válido.

Exemplos:
- agenda da empresa;
- equipe;
- clientes da organização;
- módulos contratados;
- recursos internos condicionados por papel e permissão.

---

### 10. Superuser também deve ser tratado fora da lógica obrigatória de membership

O superusuário da plataforma não deve depender de `OrganizationMember` para acessar áreas administrativas ou atravessar fluxos internos.

Mesmo quando acessar um contexto organizacional específico, esse comportamento deve ser tratado como exceção de privilégio administrativo, e não como regra base do domínio.

---

### 11. O documento funcional deve distinguir domínio desejado de implementação atual

Sempre que houver divergência entre:

- regra de negócio desejada;
- modelagem conceitual;
- implementação atual do código;

isso deve ser explicitado na documentação.

O objetivo é evitar que limitações temporárias da implementação sejam confundidas com regra definitiva de negócio.

---

### 12. Regra-mãe do projeto

A regra principal que deve orientar todas as decisões futuras é:

**todo usuário autenticado entra primeiro no contexto global da plataforma; o contexto organizacional é adicional, opcional e dependente de vínculo.**


---

## Modelo Conceitual do Sistema

## Modelo Conceitual do Sistema

Esta seção descreve o modelo conceitual desejado do LiaFit, isto é, a forma como o domínio deve ser entendido independentemente de detalhes temporários de implementação.

Sempre que houver divergência entre este modelo conceitual e o código atual, a divergência deve ser registrada explicitamente na seção de problemas, débitos técnicos ou estado atual da implementação.

---

### Visão em camadas do domínio

O domínio do sistema deve ser interpretado em três níveis:

1. **Pessoa global**
2. **Vínculo com organização**
3. **Perfil funcional dentro do vínculo**

Representação conceitual:

```
User
├── vínculos como cliente
│   └── OrganizationClient
│       └── Client
│
└── vínculos internos com organização
    └── OrganizationMember
        ├── Professional
        └── Assistant
```

1. User
User representa a pessoa em nível global na plataforma.

É o ponto central de identidade e autenticação do sistema.
Todos os demais vínculos e perfis partem dele.

Responsabilidades conceituais de User
identificar uma pessoa única na plataforma;
armazenar dados globais compartilhados;
concentrar credenciais de autenticação;
existir independentemente de qualquer organização;
servir como raiz para vínculos de cliente e de staff.
Exemplos de dados típicos
nome;
email;
telefone;
CPF;
foto;
data de nascimento;
credenciais;
estado de ativação da conta.
Observação importante
User não é um papel.
User é a pessoa.

Papéis e contextos surgem a partir dos vínculos dessa pessoa com organizações.

2. Organization
Organization representa a empresa, clínica, estúdio, academia ou operação autônoma dentro da plataforma.

É a unidade de contexto organizacional do sistema.

Responsabilidades conceituais de Organization
definir o tenant lógico da operação;
agrupar recursos internos de negócio;
servir de referência para vínculos organizacionais;
concentrar módulos contratados, equipe, clientes e operação própria.
Observação importante
A organização é uma entidade de contexto e operação.
Ela não substitui o contexto global do usuário e não deve ser tratada como ponto obrigatório de entrada na plataforma.

3. OrganizationMember
OrganizationMember representa o vínculo interno de um User com uma Organization.

Esse vínculo é usado para modelar participação operacional na empresa.

Exemplos de uso
proprietário;
administrador;
profissional;
assistente;
colaborador interno.
Responsabilidades conceituais de OrganizationMember
indicar que um usuário faz parte da estrutura interna da organização;
armazenar relacionamento organizacional do staff;
associar papéis, permissões e contexto interno;
servir de base para perfis funcionais internos.
Observações importantes
um mesmo User pode ter múltiplos OrganizationMember, um para cada organização;
um mesmo vínculo pode acumular múltiplos papéis;
esse vínculo não representa cliente.
4. OrganizationClient
OrganizationClient representa o vínculo de um User com uma Organization na condição de cliente atendido.

Esse vínculo registra o relacionamento da pessoa com a empresa do ponto de vista de consumo, atendimento ou acompanhamento.

Responsabilidades conceituais de OrganizationClient
indicar que uma pessoa é cliente daquela organização;
armazenar dados do relacionamento cliente-organização;
preservar histórico do vínculo;
servir de base para dados específicos do cliente naquele contexto.
Exemplos de informações associadas ao vínculo
data do primeiro atendimento;
observações internas;
responsável pelo cadastro;
status do vínculo;
arquivamento lógico.
Observações importantes
um mesmo User pode ser cliente de várias organizações;
um mesmo User pode ser cliente e membro interno ao mesmo tempo;
esse vínculo é diferente de OrganizationMember;
o fim do vínculo não deve apagar histórico operacional.
5. Client
Client representa o perfil funcional do cliente dentro de um vínculo específico com organização.

Ele existe para armazenar dados que fazem sentido no contexto daquela relação com aquela empresa.

Exemplos de dados possíveis
objetivo;
observações de contexto;
preferências específicas;
dados complementares daquele atendimento ou jornada.
Princípio conceitual
O perfil de cliente não deve ser entendido como global por pessoa quando os dados pertencem ao contexto da relação com uma organização específica.

Isso porque uma mesma pessoa pode ter objetivos, histórico e contexto diferentes em empresas diferentes.

Consequência conceitual
O entendimento de domínio mais consistente é:

User = pessoa global;
OrganizationClient = vínculo da pessoa com a organização;
Client = perfil contextual derivado desse vínculo.
6. Professional
Professional representa o perfil funcional de atuação profissional de um usuário dentro de uma organização.

Ele não representa a pessoa global e nem o vínculo organizacional em si, mas sim a especialização funcional daquele vínculo.

Exemplos de dados possíveis
especialidade;
conselho ou tipo de registro;
número de registro;
biografia;
dados profissionais específicos.
Princípio conceitual
Professional só faz sentido se houver vínculo interno com a organização.
Por isso, conceitualmente, ele deriva de OrganizationMember.

7. Assistant
Assistant representa o perfil funcional de apoio operacional de um usuário dentro de uma organização.

Assim como Professional, ele depende de vínculo interno com a empresa e existe para armazenar dados específicos desse papel.

Exemplos de dados possíveis
departamento;
área de atuação;
observações operacionais internas.
Princípio conceitual
Assistant também deriva de OrganizationMember, pois é uma especialização funcional do vínculo interno.

8. Papéis e perfis não são a mesma coisa
O sistema deve diferenciar claramente:

Papéis
Indicam capacidade de atuação, privilégios ou nível de acesso.
Exemplos:

OWNER
ADMIN
PROFESSIONAL
ASSISTANT
Perfis
Indicam a existência de dados funcionais especializados relacionados a um papel ou vínculo.
Exemplos:

Professional
Assistant
Client
Nem todo papel exige necessariamente um perfil funcional detalhado, mas alguns papéis naturalmente se associam a um perfil específico.

9. Relações permitidas no domínio
O sistema deve permitir naturalmente cenários como:

um User sem organização;
um User cliente de uma organização;
um User cliente de várias organizações;
um User membro de uma organização;
um User membro de várias organizações;
um User que é cliente e membro simultaneamente;
um User com múltiplos papéis em uma mesma organização.
Essas combinações são parte do domínio esperado e não devem ser tratadas como exceção arquitetural.

10. Hierarquia conceitual correta
A leitura conceitual correta do domínio é:

a pessoa existe globalmente como User;
a pessoa pode adquirir vínculos com organizações;
cada vínculo pode gerar perfis funcionais específicos;
permissões e menus derivam do contexto ativo da sessão.
Essa hierarquia evita erros comuns, como:

tratar organização como pré-requisito de existência do usuário;
tratar cliente como subtipo global fixo de usuário;
tratar membership como condição obrigatória de autenticação;
misturar dados globais com dados contextuais.
11. Observação sobre implementação atual
A implementação atual do projeto pode conter diferenças em relação a esse desenho conceitual.

Quando isso acontecer, a documentação deve sempre separar:

modelo conceitual desejado;
modelo atualmente implementado;
ajustes necessários para convergência.
Essa separação é obrigatória para evitar que decisões temporárias de código contaminem a visão correta do domínio.

---

## Arquitetura de Navegação e Contexto


---

## Parte 5 — Arquitetura de Navegação e Contexto

Esta seção define como o usuário transita pela plataforma após autenticação e como os contextos do sistema devem ser organizados na experiência logada.

O princípio central é que a navegação autenticada começa no contexto global e só depois, quando aplicável, incorpora contexto organizacional.

---

### 1. Dois níveis de contexto

A aplicação deve operar com dois níveis distintos de contexto:

#### 1. Contexto global da plataforma
É o contexto base do usuário autenticado.

Esse contexto:

- existe independentemente de tenant;
- não depende de `OrganizationMember`;
- não depende de organização ativa;
- não depende de papel organizacional;
- representa a presença do usuário dentro da plataforma como um todo.

#### 2. Contexto organizacional
É um contexto adicional e opcional.

Esse contexto só existe quando o usuário possui vínculo válido com uma organização e seleciona, explícita ou implicitamente, uma organização ativa.

Esse contexto pode carregar:

- organização atual;
- membership atual;
- roles;
- permissões;
- módulos contratados;
- perfis organizacionais;
- escopo tenant para recursos operacionais.

---

### 2. Fluxo correto após login

O fluxo correto de entrada na área autenticada é:

1. usuário autentica com sucesso;
2. sistema carrega o contexto global;
3. sistema renderiza a navegação base da plataforma;
4. sistema verifica se há vínculos organizacionais disponíveis;
5. se houver, habilita ou carrega o contexto organizacional;
6. se não houver, a sessão continua funcional apenas no contexto global.

#### Regra importante

A ausência de vínculo organizacional não deve impedir o login nem quebrar a navegação autenticada.

---

### 3. Contexto global como camada obrigatória

Todo usuário autenticado deve ter acesso ao núcleo básico da área logada.

Esse núcleo deve conter pelo menos:

- dashboard global ou página inicial autenticada;
- minha conta;
- perfil;
- configurações/preferências;
- área base do cliente;
- eventual seletor de organizações, se aplicável.

#### Observação

A área base do cliente deve ser tratada como parte da experiência global da plataforma, e não como subproduto exclusivo de um tenant.

---

### 4. Contexto organizacional como camada condicional

O contexto organizacional só deve ser resolvido quando necessário para acessar recursos dependentes de organização.

Exemplos:

- agenda da empresa;
- equipe;
- clientes da organização;
- módulos contratados;
- financeiro;
- dashboards internos da empresa;
- views operacionais com escopo tenant.

Quando o contexto organizacional estiver ativo, o sistema pode usar informações como:

- `organization`;
- `membership`;
- `roles`;
- `modules`;
- `permissions`.

Se esse contexto não existir, essas informações devem estar ausentes, vazias ou nulas, sem comprometer a camada global da aplicação.

---

### 5. Estrutura esperada da navegação logada

A navegação autenticada deve ser organizada em blocos distintos.

#### Bloco 1 — Minha Conta
Sempre visível ao usuário autenticado.

Exemplos:
- meu perfil;
- alterar senha;
- preferências;
- dados pessoais.

#### Bloco 2 — Área do Cliente
Bloco global do usuário autenticado.

Esse bloco representa a visão da pessoa sobre sua própria jornada na plataforma.

Pode incluir, conforme evolução do produto:

- visão consolidada de atendimentos;
- organizações com as quais possui relacionamento;
- histórico pessoal;
- pagamentos;
- documentos;
- agenda do cliente.

#### Regra importante

Esse bloco não deve depender da existência de uma organização ativa no seletor do topo.

#### Bloco 3 — Empresa Atual
Bloco contextual e dependente de organização ativa.

Esse bloco deve refletir:

- a organização selecionada;
- os papéis do usuário naquele contexto;
- os módulos habilitados para aquela organização;
- as permissões efetivamente disponíveis naquela sessão tenant.

---

### 6. Seletor de organização

Se o usuário possuir contexto organizacional em uma ou mais organizações, o sistema pode disponibilizar um seletor de organização ativa.

Esse seletor serve para definir o contexto tenant da navegação organizacional.

#### Regras do seletor

- só faz sentido para usuários com vínculo organizacional;
- não substitui o contexto global;
- não deve bloquear a área global da aplicação;
- deve afetar apenas os recursos contextuais dependentes de organização.

---

### 7. Usuário híbrido

O sistema deve tratar como cenário normal o usuário que é, ao mesmo tempo:

- cliente;
- profissional;
- assistente;
- administrador;
- owner;

em combinações variadas.

#### Consequência na navegação

O usuário híbrido pode visualizar simultaneamente:

- elementos globais da sua conta;
- área global de cliente;
- recursos da empresa atual;
- opções adicionais conforme papel organizacional.

A navegação não deve forçar uma escolha exclusiva entre "ser cliente" e "ser profissional".  
Esses contextos coexistem.

---

### 8. Superuser

O superuser é um contexto administrativo especial da plataforma.

Ele não deve depender de membership obrigatório para navegar nas áreas de administração ou para inspecionar contextos internos.

#### Regra de arquitetura

O bypass de superuser deve ser tratado como exceção administrativa controlada, e não como justificativa para acoplar toda a aplicação ao modelo de membership.

---

### 9. Implicações para middleware

O middleware de tenant não deve presumir que toda rota autenticada possui organização ativa.

Ele deve ser capaz de lidar com pelo menos dois cenários:

#### Rotas globais autenticadas
- seguem sem tenant;
- não exigem membership;
- não montam contexto organizacional obrigatório.

#### Rotas tenantizadas
- resolvem organização a partir da URL ou da estratégia definida;
- buscam vínculo do usuário com a organização;
- carregam contexto organizacional;
- aplicam regras adicionais de permissão.

---

### 10. Implicações para mixins e views base

As views base do sistema precisam separar claramente:

#### Requisitos globais
- usuário autenticado;
- acesso à área logada;
- contexto base da plataforma.

#### Requisitos organizacionais
- organização ativa;
- membership válido;
- roles;
- permissões específicas.

Essa separação evita que toda view autenticada passe a depender indevidamente de tenant.

---

### 11. Implicações para pós-login

O redirecionamento pós-login deve considerar primeiro o acesso global.

Fluxo recomendado:

1. login concluído;
2. redireciona para dashboard global ou landing autenticada;
3. a partir dali, o sistema mostra:
   - área global;
   - organizações disponíveis, se existirem;
   - caminhos para entrar em contexto organizacional.

#### Observação

Se no futuro houver automação para abrir a última organização usada, isso deve ser tratado como conveniência de navegação, e não como regra estrutural de autenticação.

---

### 12. Regra final desta seção

A navegação autenticada do LiaFit deve sempre partir do contexto global da plataforma.

O contexto organizacional é uma camada adicional, ativada conforme vínculos, seleção de organização e acesso a recursos tenantizados.

---

## Arquitetura Técnica e Convenções

## Arquitetura Técnica e Convenções

Esta seção consolida as decisões técnicas estruturais do projeto, as convenções adotadas e os princípios de implementação que devem orientar o desenvolvimento.

Ela descreve como o sistema deve ser construído tecnicamente para sustentar o domínio definido nas seções anteriores.

---

### 1. Stack técnica

| Camada | Tecnologia |
|---|---|
| Backend | Django 5.x + Django REST Framework |
| Banco de dados em produção | PostgreSQL |
| Banco de dados em desenvolvimento | SQLite |
| Autenticação API | JWT com SimpleJWT |
| Autenticação web/admin | Session |
| Frontend | Templates Django (MPA) + CSS BEM com prefixo `lia-` + JavaScript vanilla |
| Documentação de API | drf-spectacular |
| Locale | pt-BR |
| Timezone | America/Porto_Velho |
| Storage de arquivos | Local em desenvolvimento / S3-compatible no futuro |

---

### 2. Estratégia arquitetural geral

O projeto segue uma arquitetura baseada em:

- separação clara de responsabilidades;
- services para regra de negócio;
- models enxutos;
- views finas;
- templates focados em renderização;
- multi-tenant por contexto organizacional;
- contexto global como base da aplicação autenticada.

A aplicação deve permitir evolução incremental sem acoplamento excessivo entre autenticação, tenant e regra de negócio.

---

### 3. Separação de responsabilidades

| Camada | Responsabilidade | Não deve fazer |
|---|---|---|
| **Models** | Estrutura, campos, constraints, validações simples, propriedades de leitura | Orquestração de negócio, acesso a `request`, regras complexas |
| **Services** | Regras de negócio, fluxos multi-model, transações, orquestração | Renderização, controle de interface, dependência direta de view |
| **Forms / Serializers** | Validação e normalização de entrada | Regras de negócio pesadas, persistência complexa |
| **Views** | Receber request, chamar service, devolver response | Concentrar regra de negócio, consultas complexas, lógica de domínio |
| **Templates** | Estrutura HTML e exibição | Lógica de negócio, decisão complexa de fluxo |

#### Regra prática
Se uma view começar a concentrar fluxo, decisão, múltiplos updates ou coordenação entre models, essa lógica deve ser extraída para um service.

---

### 4. Convenções de nomenclatura

#### Codenames internos
Devem permanecer em inglês para manter consistência técnica, banco de dados e integração com código.

Exemplos:
- `OWNER`
- `ADMIN`
- `PROFESSIONAL`
- `ASSISTANT`
- `CLIENT`

#### Labels de interface
Devem permanecer em PT-BR.

Exemplos:
- Proprietário
- Administrador
- Profissional
- Assistente
- Cliente

#### CSS
Padrão BEM com prefixo `lia-`.

Exemplos:
- `lia-sidebar`
- `lia-sidebar__item`
- `lia-sidebar__item--active`

---

### 5. Estratégia de multi-tenant

No MVP, o contexto organizacional é resolvido por URL.

Exemplo conceitual:

/app/<org_slug>/dashboard/

Princípios dessa estratégia
tenant por URL é suficiente para o MVP;
a arquitetura deve permanecer aberta para futura migração para subdomínio;
nem toda rota autenticada é tenantizada;
rotas globais e rotas organizacionais devem coexistir claramente.
6. Models base do projeto
BaseModel
Todos os models principais devem herdar de uma base comum com:

id UUID;
created_at;
updated_at;
is_active, quando aplicável ao modelo base adotado.
TenantModel
Models operacionais ligados a uma organização devem herdar também de uma base tenantizada com FK para Organization.

Princípio importante
Nem todo model do sistema deve ser tenantizado.
Somente os models cujo ciclo de vida pertence a uma organização específica.

7. Padrões de relacionamento com User
O User é uma entidade global e estratégica.
Relacionamentos com User devem preservar histórico e evitar exclusões destrutivas indevidas.

Regra preferencial
Usar on_delete=PROTECT em FKs para User sempre que o relacionamento representar histórico, autoria, responsabilidade ou vínculo relevante.

Exceções legítimas
Podem existir casos específicos em que CASCADE faça sentido, como tokens efêmeros ou estruturas transitórias diretamente subordinadas ao ciclo de vida do usuário.

8. Regra para operações multi-model
Sempre que um fluxo de negócio envolver criação, atualização ou invalidação coordenada de múltiplos models, a operação deve ser encapsulada em service e protegida por transação atômica.

Exemplos típicos
onboarding de organização;
setup de senha;
criação de cliente com vínculo e perfil;
convites;
ativação ou desativação de vínculos;
consumo de token.
9. Princípios para services
Services devem:

encapsular regra de negócio;
receber dados explícitos como parâmetros;
evitar depender diretamente de objetos request completos;
aceitar apenas os dados necessários, como ip, user_agent, organization, actor, etc.;
ser reutilizáveis entre views web, API, tarefas assíncronas e comandos internos.
Regra de desenho
Se um service precisa de dados do request, a view extrai esses dados e os passa de forma explícita.

10. Princípios para middleware
O middleware deve ser responsável por infraestrutura de contexto, e não por regra de negócio de alto nível.

Pode fazer
extrair org_slug;
resolver organização;
montar contexto organizacional;
anexar informações contextuais à request;
permitir rotas globais sem tenant.
Não deve fazer
executar regra de negócio complexa;
decidir fluxo funcional do usuário;
substituir services;
assumir que toda sessão autenticada possui membership.
11. Princípios para templates
Templates devem permanecer simples, previsíveis e orientados à exibição.

Devem conter
estrutura visual;
condicionais leves de apresentação;
blocos reutilizáveis;
composição de layout.
Não devem conter
lógica de negócio;
decisões de permissão complexas;
acesso indireto a dados não preparados pela view;
manipulação de fluxo.
12. Convenções para interface logada
A aplicação autenticada deve usar um layout principal único, com blocos de navegação capazes de refletir:

contexto global do usuário;
área de conta;
área do cliente;
contexto organizacional ativo, quando existir.
A existência de um layout único para a área logada não elimina a necessidade de separar, conceitualmente, os contextos global e organizacional.

13. Estratégia de documentação
Este documento deve funcionar como fonte primária de referência do projeto.

Por isso:

decisões relevantes devem ser registradas aqui;
divergências entre código e domínio devem ser explicitadas;
mudanças estruturais devem atualizar este arquivo;
roadmap e débitos técnicos devem permanecer visíveis.
Regra de manutenção
Sempre que uma decisão alterar domínio, fluxo principal, arquitetura ou contrato importante entre camadas, este documento deve ser revisado.

14. Princípio de evolução controlada
Mudanças arquiteturais devem ser feitas de forma incremental e consciente.

O projeto não deve:

sofrer refatorações radicais sem validação;
misturar correção conceitual com reescrita desnecessária;
assumir soluções temporárias como definitivas;
expandir complexidade antes de estabilizar fundamentos.
A prioridade é manter coerência entre:

visão do produto;
modelo de domínio;
arquitetura de navegação;
implementação técnica.

---

## Parte 7 — Estado Atual da Implementação

Esta seção registra o estado atual real do projeto com base nas entregas já realizadas, no histórico recente e na arquitetura atualmente existente.

O objetivo é separar claramente o que já está implementado do que ainda está apenas definido conceitualmente.

---

### 1. Situação geral do projeto

O projeto já possui base funcional inicial consolidada, com fundação de domínio, autenticação customizada, onboarding inicial de organização e primeiros componentes da área autenticada.

Há uma base arquitetural relevante já implementada, mas ainda existem pontos que precisam ser revisados para alinhar completamente a implementação com o modelo conceitual mais recente, especialmente em relação à separação entre contexto global e contexto organizacional.

---

### 2. Fundação já implementada

#### Estrutura inicial concluída
- projeto Django estruturado;
- apps principais criados;
- base de templates e front-end inicial estabelecida;
- convenções centrais já definidas.

#### Componentes estruturais existentes
- `BaseModel`;
- `TenantModel`;
- catálogo de `Role`;
- custom user com login por email;
- estrutura inicial para multi-tenant;
- layout autenticado principal.

---

### 3. Estado da Sprint 1

A Sprint 1, focada em onboarding de organização, está registrada como concluída.

#### Entregas concluídas da Sprint 1
- refatoração de `account/models.py`;
- migrations aplicadas;
- seed de roles;
- infraestrutura de tokens com auditoria;
- `TokenService` com exceptions tipadas;
- `OnboardingService.register_organization()`;
- `OnboardingService.setup_password()`;
- forms de registro e setup de senha;
- views e URLs de onboarding;
- templates de registro e setup de senha.

#### Fluxo funcional já validado
- registro público de organização;
- criação de usuário inativo;
- criação de organização inativa;
- geração de token;
- envio de email em ambiente de desenvolvimento;
- setup de senha por token;
- ativação do usuário;
- ativação da organização;
- invalidação auditável do token.

---

### 4. Sistema de tokens

A infraestrutura de tokens já evoluiu além da versão original simplificada.

#### Situação atual registrada
Existe model `OnboardingToken` com uso ampliado por `purpose`, incluindo:

- onboarding;
- reset de senha;
- mudança de email;
- verificação de email;
- convites;
- magic link.

#### Recursos já documentados como implementados
- token UUID;
- TTL por propósito;
- `data` em JSON;
- associação opcional com organização;
- auditoria de criação;
- auditoria de uso;
- validação por `TokenService`;
- exceptions tipadas;
- consumo com invalidação controlada.

#### Observação importante
Embora o nome da entidade ainda seja `OnboardingToken`, a documentação já reconhece que o comportamento atual é mais próximo de um token genérico de usuário/autenticação.

Isso configura um débito técnico de nomenclatura a ser tratado em momento adequado.

---

### 5. Modelagem de domínio atualmente registrada

A documentação registra como arquitetura de dados principal:

- `User` como pessoa global;
- `OrganizationMember` como vínculo staff;
- `OrganizationClient` como vínculo cliente;
- `Professional`, `Assistant` e `Client` como perfis funcionais.

#### Observação importante
Há indícios de divergência entre o modelo conceitual descrito e partes da implementação efetiva do código atual.  
Essas divergências devem ser mapeadas explicitamente na seção de problemas identificados, e não assumidas como resolvidas apenas porque aparecem na documentação.

---

### 6. Arquitetura autenticada existente hoje

A documentação indica a existência de uma base já implementada para a área logada, incluindo:

#### Middleware
- `TenantMiddleware`;
- extração de `org_slug`;
- busca de organização;
- busca de membership;
- montagem de `request.context`.

#### Views base
- `BaseAuthMixin`;
- `ContextMixin`;
- views base de CRUD;
- filtragem por tenant;
- bypass de superuser em partes da base.

#### Templates
- `base_app.html`;
- `dashboard.html`.

#### JavaScript inicial
- `sidebar.js`;
- `forms.js`.

---

### 7. Estado atual da navegação

A base de navegação autenticada já começou a ser construída, mas ainda carrega forte orientação tenant-first em parte da estrutura descrita.

#### O que já existe
- layout autenticado principal;
- dashboard inicial;
- sidebar;
- middleware com contexto tenant;
- bypass para superuser.

#### O que ainda precisa maturar
- dashboard global claramente separado de dashboard organizacional;
- seletor de organização;
- context processor para tenant/global context;
- navegação consistente para usuários sem membership;
- estrutura explícita de menu global versus menu de empresa atual.

---

### 8. Checklist consolidado do que já consta como pronto

#### Marcado como concluído na documentação
- models principais;
- middleware tenant;
- views base;
- bypass de superuser;
- layout `base_app.html`;
- dashboard;
- JavaScript de sidebar;
- onboarding completo da Sprint 1.

#### Marcado como pendente
- views da área `manage`;
- seletor de organização;
- context processor de tenant;
- testes automatizados;
- módulos funcionais do SaaS;
- expansão das sprints seguintes.

---

### 9. Estado de maturidade do projeto

O projeto está em um ponto intermediário de fundação:

- já não está mais em fase de blueprint puro;
- já possui implementação concreta relevante;
- ainda precisa consolidar melhor os contratos arquiteturais principais antes de avançar com muita velocidade sobre módulos de negócio.

A principal necessidade no momento não é somente criar novas features, mas garantir coerência entre:

- documentação;
- domínio;
- contexto de navegação;
- middleware;
- mixins base;
- estratégia de acesso pós-login.

---

### 10. Próximo foco técnico recomendado

Com a Sprint 1 concluída, o foco técnico recomendado passa a ser a preparação correta da base para a Sprint 2, com atenção especial a:

- separação entre contexto global e organizacional;
- revisão do fluxo pós-login;
- revisão da navegação autenticada;
- definição do seletor de organização;
- revisão do middleware tenant para não assumir membership como pré-requisito universal;
- alinhamento entre documento e código antes de expandir os módulos do produto.

---

### 11. Regra de leitura desta seção

Esta seção deve descrever o estado atual real do projeto, e não o estado ideal desejado.

Sempre que houver diferença entre:
- o que já está implementado;
- o que está documentado;
- o que deveria existir conceitualmente;

essa diferença deve ser tratada de forma explícita nas seções seguintes.

---

## Problemas Identificados e Pontos de Atenção
## Problemas Identificados e Pontos de Atenção

Esta seção registra inconsistências, riscos arquiteturais, divergências entre domínio e implementação e pontos que exigem atenção antes da evolução das próximas sprints.

O objetivo não é invalidar o que já foi construído, mas explicitar onde a base atual ainda precisa convergir para o modelo correto do produto.

---

### 1. Mistura entre domínio desejado, documentação e implementação atual

O documento histórico acumulou, ao longo das versões, três camadas diferentes:

1. visão conceitual do produto;
2. modelagem desejada do domínio;
3. estado real da implementação.

Essas três camadas aparecem misturadas em vários trechos como se fossem equivalentes.

#### Risco
Isso pode levar a decisões erradas, como:

- assumir que um comportamento já está implementado quando ainda é apenas intenção;
- tratar uma limitação temporária de código como regra definitiva de negócio;
- continuar expandindo features sobre premissas contraditórias.

#### Diretriz
Sempre que houver diferença entre conceito e código, a documentação deve marcar explicitamente essa diferença.

---

### 2. Tendência tenant-first excessiva na camada autenticada

Parte da arquitetura atual parece ter sido construída com forte orientação a fluxo tenant-first, isto é, assumindo que o usuário autenticado entra no sistema já a partir de um contexto organizacional.

#### Problema
Essa premissa conflita com o domínio mais correto do LiaFit, no qual:

- o usuário é global;
- o contexto global vem primeiro;
- o contexto organizacional é adicional;
- o login não pode depender de membership.

#### Impactos possíveis
- redirecionamento pós-login acoplado a tenant;
- mixins exigindo membership cedo demais;
- sidebar pensada primeiro para empresa atual;
- dificuldade para usuários sem organização ou sem membership;
- dificuldade para cliente global existir como cidadão de primeira classe.

---

### 3. Risco de acoplamento indevido entre autenticação e membership

A existência de `BaseAuthMixin`, `ContextMixin` e `TenantMiddleware` é positiva, mas há risco arquitetural se essas estruturas forem interpretadas como obrigatórias para toda rota autenticada.

#### Problema
Se toda área logada exigir implicitamente:

- `org_slug`;
- `OrganizationMember`;
- contexto tenant resolvido;

então o sistema passa a negar, na prática, o princípio fundamental do domínio: o acesso autenticado começa no nível global.

#### Consequência
Usuários válidos da plataforma podem ficar sem fluxo natural de entrada apenas porque não pertencem a uma organização naquele momento.

---

### 4. Inconsistência na definição da área do cliente

Em versões anteriores da documentação, a área do cliente aparece condicionada à existência de ao menos um `OrganizationClient` ativo.

#### Problema conceitual
Essa leitura é limitada e conflita com a visão mais correta do produto.

O cliente deve existir como ator global da plataforma, e sua área base não pode ser tratada apenas como reflexo de vínculos ativos com organizações.

#### Correção de direção
A área do cliente deve ser entendida como bloco global da experiência autenticada, ainda que certos conteúdos internos dependam de vínculos ou histórico.

---

### 5. Divergência potencial entre documentação e código na modelagem de `Client`

A documentação em parte descreve `Client` como perfil contextual derivado de `OrganizationClient`, o que é coerente com o domínio multi-organização.

Porém, há indícios de que o código atual pode refletir outra modelagem em alguns pontos.

#### Risco
Se `Client` estiver implementado como entidade global ligada diretamente a `User`, pode ocorrer confusão entre:

- identidade global da pessoa;
- perfil funcional do cliente;
- contexto específico da relação com cada organização.

#### Impacto
Isso pode gerar dificuldade futura para representar corretamente objetivos, estado, preferências e histórico distintos por organização.

---

### 6. Divergência potencial em `OrganizationClient`

Também há indícios de divergência sobre o alvo correto da relação de `OrganizationClient`.

Em uma visão conceitual madura, esse vínculo representa a relação entre:

- uma pessoa global (`User`);
- e uma organização (`Organization`).

Se o código estiver ligando `OrganizationClient` a outra entidade intermediária de forma estruturalmente inadequada, isso pode distorcer a leitura do domínio.

#### Risco
A modelagem do vínculo cliente-organização pode ficar semanticamente confusa, dificultando:

- consultas;
- consistência de nomenclatura;
- clareza nas services;
- manutenção futura.

---

### 7. Nome `OnboardingToken` já não representa o comportamento real

O model de token já evoluiu para múltiplos `purposes`, TTLs distintos, auditoria e uso em diferentes fluxos além do onboarding inicial.

#### Problema
O nome atual sugere um escopo mais restrito do que a funcionalidade real.

#### Consequência
- leitura enganosa do domínio;
- naming inconsistente em services e views futuras;
- aumento de débito técnico semântico.

#### Direção recomendada
Planejar renomeação futura para algo como `UserToken` ou `AuthToken`, em janela apropriada de migração.

---

### 8. Dupla narrativa sobre auditoria de tokens

O próprio histórico do documento contém duas leituras diferentes sobre auditoria de criação de token:

- em uma parte, a auditoria de criação (`created_ip`, `created_ua`) aparece como implementada;
- em outra nota técnica, essa mesma auditoria aparece como algo ainda futuro e de baixa prioridade.

#### Problema
Isso gera ambiguidade documental.

#### Diretriz
A documentação precisa consolidar um único estado real:
- ou a auditoria de criação já existe e está ativa;
- ou ainda não existe e continua pendente.

As duas narrativas não podem coexistir como se fossem simultaneamente verdadeiras.

---

### 9. Duplicidade e acúmulo de trechos históricos

O documento atual possui repetições de:
- roadmap;
- status de sprint;
- próximos passos;
- notas de implementação.

#### Problema
Embora isso preserve contexto histórico, também aumenta ruído e reduz confiabilidade operacional do arquivo como fonte de consulta rápida.

#### Consequência
Fica mais difícil saber:
- qual é o estado atual verdadeiro;
- qual trecho é histórico;
- qual trecho já foi superado;
- qual orientação ainda vale.

---

### 10. Falta de fronteira explícita entre rotas globais e rotas tenantizadas

A arquitetura já menciona middleware tenant e contexto por `org_slug`, mas ainda precisa de formalização mais precisa sobre quais áreas:

- pertencem ao contexto global;
- dependem de tenant;
- podem funcionar nos dois modos.

#### Risco
Sem essa fronteira, cresce a chance de:
- mixins genéricos serem usados em views globais indevidamente;
- redirecionamentos se tornarem inconsistentes;
- navegação ficar confusa para usuários híbridos;
- expansão da Sprint 2 ocorrer sobre uma base ambígua.

---

### 11. Pós-login ainda precisa de contrato claro

O projeto já possui onboarding e base autenticada, mas o comportamento oficial do sistema após login ainda precisa ser formalizado com mais clareza.

#### Perguntas que precisam de resposta arquitetural explícita
- o usuário cai em dashboard global ou tenant?
- se houver uma única organização, entra automaticamente nela ou não?
- se não houver organização, qual é a página inicial oficial?
- o cliente puro sem membership entra em qual fluxo?
- o usuário híbrido vê quais blocos logo ao entrar?

Sem esse contrato, a camada de navegação tende a evoluir por conveniência local e não por princípio arquitetural.

---

### 12. Sprint 2 depende de alinhamento conceitual prévio

A documentação aponta como próximo passo a Sprint 2, voltada a dashboard multi-empresa e seletor de organização.

#### Ponto de atenção
Esses recursos só devem avançar com segurança depois que estiver claro que:

- existe dashboard global;
- existe dashboard/contexto organizacional;
- existe distinção entre menu global e menu da empresa atual;
- middleware e mixins não forçam tenant em toda área logada.

Caso contrário, a Sprint 2 corre o risco de solidificar uma navegação incorreta.

---

### 13. Falta de mapeamento explícito entre modelo desejado e código atual

A documentação já evoluiu bastante em visão conceitual, mas ainda precisa de uma tabela objetiva de convergência entre:

- conceito esperado;
- código atual;
- status da aderência;
- ação necessária.

#### Benefício dessa tabela
Ela facilitaria decisões como:
- o que corrigir agora;
- o que aceitar temporariamente;
- o que é bug conceitual;
- o que é apenas débito técnico tolerável.

---

### 14. Principal risco do momento

O maior risco atual não é ausência de funcionalidade, mas sim crescimento sobre uma base parcialmente desalinhada.

Em outras palavras:

- já existe bastante estrutura;
- já existe bastante código;
- já existe direção de produto;
- mas ainda há pontos sensíveis em que a implementação pode cristalizar premissas erradas se não forem corrigidas agora.

#### Conclusão desta seção
Antes de expandir módulos de negócio, o projeto precisa consolidar corretamente:
- a entrada na área autenticada;
- a separação entre global e organizacional;
- a leitura correta do cliente;
- a convergência entre documento e código.


---

## Plano de Correção e Evolução

## Plano de Correção e Evolução

Esta seção define a ordem recomendada de ajustes para alinhar a implementação atual ao modelo conceitual do LiaFit sem promover refatorações caóticas ou reescritas desnecessárias.

A estratégia deve ser incremental, priorizando a estabilização da fundação antes da expansão de novos módulos.

---

### Objetivo do plano

Garantir convergência entre:

1. visão do produto;
2. modelo de domínio;
3. navegação autenticada;
4. middleware e mixins;
5. implementação atual do código.

---

### Princípio de execução

A correção deve seguir esta lógica:

- primeiro alinhar contratos arquiteturais;
- depois ajustar fluxo de navegação;
- depois revisar pontos de modelagem divergente;
- só então expandir a Sprint 2 e módulos futuros.

---

### Etapa 1 — Consolidar a documentação como fonte confiável

Antes de qualquer ajuste técnico maior, o documento principal precisa refletir um estado coerente e legível.

#### Ações
- separar claramente domínio desejado, estado atual e histórico;
- remover duplicidades desnecessárias;
- consolidar uma única narrativa para tokens, auditoria e sprints;
- explicitar divergências entre modelo conceitual e implementação atual;
- atualizar a numeração e o versionamento do documento.

#### Resultado esperado
Ter um arquivo de referência que realmente oriente decisões futuras sem ambiguidade.

---

### Etapa 2 — Formalizar o contrato de navegação pós-login

O sistema precisa definir oficialmente qual é o comportamento padrão após autenticação.

#### Decisões que devem ser fixadas
- página inicial autenticada padrão;
- existência oficial de um dashboard global;
- papel do seletor de organização;
- comportamento para usuário sem organização;
- comportamento para usuário com uma única organização;
- comportamento para usuário com múltiplas organizações;
- comportamento para usuário híbrido.

#### Resultado esperado
Evitar que cada view ou fluxo passe a decidir isoladamente para onde o usuário deve ir.

---

### Etapa 3 — Separar rotas globais de rotas tenantizadas

A aplicação precisa explicitar essa fronteira tanto conceitualmente quanto tecnicamente.

#### Ações
- classificar views e URLs em globais ou organizacionais;
- revisar o uso de `org_slug`;
- garantir que rotas globais autenticadas não dependam de membership;
- manter rotas tenantizadas com escopo claro e controlado.

#### Resultado esperado
Reduzir acoplamento indevido entre autenticação e tenant.

---

### Etapa 4 — Revisar middleware de tenant

O `TenantMiddleware` deve continuar existindo, mas com contrato mais preciso.

#### Ações
- garantir que ele trate rotas globais sem erro;
- evitar pressuposto de que toda request autenticada precisa de organização;
- padronizar comportamento quando `org_slug` não existir;
- definir claramente o formato de `request.context` em rotas globais e organizacionais.

#### Resultado esperado
Ter uma infraestrutura de contexto robusta, previsível e compatível com o domínio global-first.

---

### Etapa 5 — Revisar mixins e base views

As classes base da camada de views precisam refletir a distinção entre requisitos globais e requisitos organizacionais.

#### Ações
- revisar `BaseAuthMixin` para autenticação global;
- revisar `ContextMixin` para só exigir tenant onde fizer sentido;
- separar claramente mixins globais e mixins tenantizados, se necessário;
- impedir que CRUDs globais herdem acidentalmente restrições de tenant.

#### Resultado esperado
Uma base de views mais limpa, reutilizável e coerente com os dois níveis de contexto da aplicação.

---

### Etapa 6 — Formalizar a navegação da área logada

A interface autenticada precisa traduzir visualmente a arquitetura do sistema.

#### Ações
- definir o bloco permanente "Minha Conta";
- definir a "Área do Cliente" como bloco global;
- definir o bloco "Empresa Atual" como contextual;
- planejar o seletor de organização no header;
- revisar a sidebar para refletir a separação entre contexto global e organizacional.

#### Resultado esperado
Uma navegação compreensível para usuário sem organização, usuário cliente, usuário staff e usuário híbrido.

---

### Etapa 7 — Mapear divergências reais entre código e modelo conceitual

Antes de refatorar models, é necessário produzir um mapeamento objetivo.

#### Ações
Criar uma tabela com pelo menos estas colunas:

- entidade;
- modelo conceitual desejado;
- implementação atual;
- aderência;
- impacto;
- ação recomendada.

#### Entidades prioritárias
- `User`
- `Client`
- `OrganizationClient`
- `OrganizationMember`
- `OnboardingToken`

#### Resultado esperado
Tomar decisões de refatoração com base em evidência, e não em impressão.

---

### Etapa 8 — Corrigir divergências de modelagem por prioridade

Nem toda divergência exige ação imediata.  
As correções devem ser priorizadas pelo impacto no domínio e no risco de contaminar novas features.

#### Prioridade alta
- tudo que afeta fluxo pós-login;
- tudo que afeta existência de usuário global;
- tudo que afeta cliente global versus tenant;
- tudo que afeta navegação base autenticada.

#### Prioridade média
- nomenclatura inadequada, mas funcional;

---

## Roadmap por Sprints

## Roadmap por Sprints

Esta seção organiza a evolução do projeto em sprints incrementais, respeitando a prioridade atual de estabilização arquitetural antes da expansão funcional do produto.

O roadmap deve ser entendido como diretriz de execução e pode ser ajustado conforme validações técnicas e de negócio.

---

### Visão geral da ordem de evolução

A ordem recomendada de evolução do projeto é:

1. consolidar fundação conceitual e arquitetural;
2. estabilizar navegação autenticada;
3. estruturar experiência multi-organização;
4. expandir módulos operacionais centrais;
5. fortalecer qualidade, testes e observabilidade.

---

### Sprint 0 — Fundação inicial
**Status:** concluída

#### Objetivo
Criar a base estrutural do projeto.

#### Entregas principais
- setup inicial do projeto Django;
- organização dos apps;
- custom user com email como login;
- `BaseModel`;
- `TenantModel`;
- catálogo de roles;
- base inicial de templates;
- convenções de front-end;
- primeiros artefatos da área autenticada.

#### Resultado
O projeto deixou de ser apenas uma ideia e passou a ter fundação técnica inicial.

---

### Sprint 1 — Onboarding de organização
**Status:** concluída

#### Objetivo
Viabilizar o registro inicial de organização e ativação de conta por token.

#### Entregas principais
- formulário público de registro;
- criação de usuário inativo;
- criação de organização inativa;
- geração de token;
- serviço de onboarding;
- setup de senha;
- ativação de usuário e organização;
- invalidação controlada do token;
- templates e URLs do fluxo.

#### Resultado
O sistema passou a ter primeiro fluxo real de entrada de novos usuários e organizações.

---

### Sprint 1.5 — Alinhamento arquitetural
**Status:** recomendada antes da Sprint 2

#### Objetivo
Ajustar a fundação para refletir corretamente o domínio global-first da plataforma.

#### Entregas esperadas
- consolidação do documento principal;
- formalização do pós-login;
- separação entre rotas globais e tenantizadas;
- revisão do `TenantMiddleware`;
- revisão de mixins e base views;
- definição da estrutura de navegação logada;
- revisão da sidebar;
- definição do papel oficial da área global do cliente;
- mapeamento de divergências entre conceito e código.

#### Resultado esperado
Base estabilizada para crescer sem cristalizar premissas tenant-first incorretas.

---

### Sprint 2 — Navegação autenticada e multi-organização
**Status:** próxima sprint recomendada

#### Objetivo
Implementar corretamente a experiência logada com contexto global e contexto organizacional opcional.

#### Entregas principais
- dashboard global;
- landing autenticada oficial;
- seletor de organização;
- bloco "Minha Conta";
- bloco global "Área do Cliente";
- bloco contextual "Empresa Atual";
- comportamento para usuário sem organização;
- comportamento para usuário com uma organização;
- comportamento para usuário com múltiplas organizações;
- refinamento da navegação para usuário híbrido.

#### Dependências
Esta sprint deve ocorrer após o alinhamento arquitetural mínimo da Sprint 1.5.

#### Resultado esperado
Experiência logada coerente com o domínio do produto.

---

### Sprint 3 — Gestão de organizações e memberships
**Status:** planejada

#### Objetivo
Fortalecer a camada de gestão organizacional e vínculos internos.

#### Entregas principais
- CRUD de organização em área administrativa apropriada;
- gestão de membros da organização;
- atribuição de roles;
- convites;
- ativação e desativação de vínculos;
- validações de permissão;
- refinamento do acesso multi-organização.

#### Resultado esperado
Organizações passam a gerir sua própria estrutura interna de forma consistente.

---

### Sprint 4 — Gestão de clientes
**Status:** planejada

#### Objetivo
Implementar a camada de relacionamento cliente-organização conforme o modelo do domínio.

#### Entregas principais
- criação de `OrganizationClient`;
- CRUD de clientes da organização;
- vínculo de usuário existente como cliente;
- cadastro de novo cliente;
- perfil contextual `Client`;
- listagens e filtros;
- arquivamento lógico;
- base para histórico de relacionamento.

#### Ponto de atenção
Antes desta sprint, a modelagem de `Client` e `OrganizationClient` deve estar suficientemente validada.

#### Resultado esperado
O sistema passa a suportar corretamente cliente como pessoa global com vínculos contextuais por organização.

---

### Sprint 5 — Agenda e operação básica
**Status:** planejada

#### Objetivo
Adicionar primeiros módulos operacionais centrais da empresa.

#### Entregas principais
- agenda organizacional;
- disponibilidade;
- agendamentos;
- associação com profissional;
- visão básica para cliente;
- visão operacional interna.

#### Resultado esperado
A plataforma começa a sustentar rotinas reais de operação da organização.

---

### Sprint 6 — Financeiro e relacionamento
**Status:** futura

#### Possíveis entregas
- cobranças;
- pagamentos;
- planos;
- pacotes;
- recorrência;
- status financeiro do cliente;
- visão consolidada por organização.

---

### Sprint 7 — Experiência consolidada do cliente
**Status:** futura

#### Possíveis entregas
- visão global de organizações com as quais o usuário possui relacionamento;
- agenda pessoal do cliente;
- histórico;
- documentos;
- pagamentos;
- central de comunicação.

---

### Sprint 8 — Qualidade, testes e observabilidade
**Status:** paralela e contínua, com reforço formal futuro

#### Objetivo
Aumentar confiabilidade operacional do projeto.

#### Entregas esperadas
- testes unitários;
- testes de integração;
- testes de services;
- testes de middleware;
- cobertura de onboarding;
- logs estruturados;
- monitoramento;
- tratamento de erro mais robusto.

---

### Backlog transversal

Há temas que atravessam várias sprints e não pertencem a apenas uma fase.

#### Itens transversais
- revisão de nomenclaturas;
- melhoria de documentação;
- internacionalização futura, se necessária;
- storage S3-compatible;
- ajustes de segurança;
- otimizações de performance;
- padronização de permissões;
- refino de UX.

---

### Critério de prioridade do roadmap

Sempre que houver conflito entre:
- criar nova feature;
- corrigir desalinhamento estrutural;

a prioridade deve ser dada primeiro ao que protege a coerência do domínio e da navegação base da plataforma.

---

### Regra final desta seção

O roadmap do LiaFit deve crescer de forma incremental, sem acelerar módulos de negócio sobre uma fundação conceitualmente inconsistente.

---

## Modelo de Dados Atual

## Modelo de Dados Atual

Esta seção organiza o modelo de dados atual do projeto em nível documental, separando:

1. entidades centrais;
2. relações principais;
3. intenção conceitual de cada entidade;
4. possíveis divergências entre domínio e implementação.

O objetivo não é substituir o código-fonte como verdade operacional do schema, mas oferecer uma visão estruturada e inteligível do desenho atual da aplicação.

---

### 1. Visão geral das entidades centrais

As entidades principais já registradas no projeto são:

- `User`
- `Organization`
- `Role`
- `OrganizationMember`
- `OrganizationClient`
- `Client`
- `Professional`
- `Assistant`
- `OnboardingToken`

Dependendo do estado exato do código, pode haver também entidades auxiliares de auditoria, abstrações base e estruturas de suporte não listadas aqui como entidades de domínio principal.

---

### 2. Entidades base

#### `BaseModel`
Base abstrata comum para models principais.

**Responsabilidade:**
- padronizar identificador;
- timestamps;
- campos comuns adotados no projeto.

**Campos esperados:**
- `id`
- `created_at`
- `updated_at`

---

#### `TenantModel`
Base abstrata para models pertencentes ao escopo de uma organização.

**Responsabilidade:**
- padronizar presença de `organization`;
- marcar entidades com ciclo de vida tenantizado.

**Campos esperados:**
- `organization`

---

### 3. `User`

#### Papel no sistema
Representa a pessoa global autenticável da plataforma.

#### Intenção conceitual
- identidade global;
- autenticação;
- dados pessoais compartilhados;
- raiz dos vínculos com organização.

#### Campos típicos esperados
- `email`
- `password`
- `full_name`
- `phone`
- `cpf`
- `is_active`
- `is_staff`
- `is_superuser`
- timestamps

#### Relações principais
- um `User` pode ter vários `OrganizationMember`;
- um `User` pode ter vários `OrganizationClient`;
- um `User` pode ter perfis derivados conforme implementação;
- um `User` pode possuir vários tokens.

#### Observação
`User` não deve ser reduzido semanticamente a "cliente", "profissional" ou "membro".  
Esses são contextos derivados.

---

### 4. `Organization`

#### Papel no sistema
Representa a empresa ou operação dentro da plataforma.

#### Intenção conceitual
- tenant lógico;
- unidade operacional;
- agrupador de recursos internos.

#### Campos típicos esperados
- `name`
- `slug`
- `legal_name`
- `document`
- `email`
- `phone`
- `is_active`

#### Relações principais
- uma `Organization` possui vários `OrganizationMember`;
- uma `Organization` possui vários `OrganizationClient`;
- uma `Organization` pode possuir dados operacionais tenantizados.

---

### 5. `Role`

#### Papel no sistema
Catálogo de papéis possíveis no contexto organizacional.

#### Intenção conceitual
Representar capacidades e níveis de acesso.

#### Exemplos de registros
- `OWNER`
- `ADMIN`
- `PROFESSIONAL`
- `ASSISTANT`
- `CLIENT`

#### Observação importante
A existência de `CLIENT` no catálogo não significa, por si só, que cliente deva ser modelado como membro interno.  
Esse ponto depende do uso efetivo no código e precisa ser tratado com cuidado semântico.

---

### 6. `OrganizationMember`

#### Papel no sistema
Representa vínculo interno entre `User` e `Organization`.

#### Intenção conceitual
- participação operacional na equipe;
- base para roles internas;
- contexto de permissões tenantizadas.

#### Relações esperadas
- FK para `User`;
- FK para `Organization`;
- relação com `Role`.

#### Campos típicos esperados
- `user`
- `organization`
- status do vínculo
- timestamps
- eventual auditoria básica

#### Observações
- um usuário pode ter múltiplos memberships;
- um membership pode ter um ou mais papéis;
- não deve ser usado para representar cliente comum.

---

### 7. `OrganizationClient`

#### Papel no sistema
Representa o vínculo da pessoa com a organização na condição de cliente.

#### Intenção conceitual
- registrar relação cliente-organização;
- preservar histórico;
- permitir múltiplos vínculos por pessoa em organizações diferentes.

#### Relações esperadas
Conceitualmente, o mais consistente é que tenha:
- FK para `User`;
- FK para `Organization`.

#### Campos típicos esperados
- `user`
- `organization`
- `status`
- `archived_at`, se existir
- datas de relacionamento
- observações internas

#### Ponto de atenção
É necessário confirmar se a implementação atual segue exatamente essa estrutura ou se ainda existe divergência relevante.

---

### 8. `Client`

#### Papel no sistema
Perfil funcional contextual de cliente.

#### Intenção conceitual
Armazenar dados específicos do cliente em uma relação concreta com organização.

#### Campos típicos possíveis
- preferências;
- objetivo;
- observações;
- dados complementares de jornada.

#### Relação conceitualmente desejada
O mais coerente é que `Client` derive de `OrganizationClient` ou esteja semanticamente acoplado a esse vínculo.

#### Ponto de atenção
É necessário validar se a implementação atual segue essa linha ou se `Client` está acoplado diretamente a `User` de modo global.

---

### 9. `Professional`

#### Papel no sistema
Perfil funcional profissional em contexto organizacional.

#### Intenção conceitual
Armazenar dados especializados de atuação profissional.

#### Relação conceitualmente desejada
Deve derivar de `OrganizationMember`.

#### Campos típicos possíveis
- especialidade;
- conselho;
- número de registro;
- bio;
- dados profissionais específicos.

---

### 10. `Assistant`

#### Papel no sistema
Perfil funcional de apoio operacional.

#### Intenção conceitual
Armazenar dados especializados do papel de assistente em contexto organizacional.

#### Relação conceitualmente desejada
Também deve derivar de `OrganizationMember`.

#### Campos típicos possíveis
- área;
- observações internas;
- dados operacionais específicos.

---

### 11. `OnboardingToken`

#### Papel no sistema
Entidade de token atualmente utilizada em múltiplos fluxos de autenticação e validação.

#### Intenção registrada
Embora o nome remeta a onboarding, o uso já se expandiu para finalidades diversas.

#### Campos típicos registrados na documentação
- `token`
- `purpose`
- `user`
- `organization` opcional
- `expires_at`
- `used_at`
- `revoked_at`
- `data`
- campos de auditoria de criação
- campos de auditoria de uso

#### Ponto de atenção
O nome da entidade parece defasado em relação ao comportamento real.

---

### 12. Relações conceituais resumidas

Representação simplificada:

```text
User
├── OrganizationMember ──> Organization
│   ├── roles
│   ├── Professional
│   └── Assistant
│
└── OrganizationClient ──> Organization
    └── Client

User
└── OnboardingToken
```
13. Tabela de aderência entre conceito e implementação
Esta tabela deve ser preenchida e mantida conforme revisão do código.


| Entidade | Conceito desejado | Implementação atual | Aderência | Ação necessária |
| --- | --- | --- | --- | --- |
| User | Pessoa global | A confirmar no código | Parcialmente aderente | Revisar campos e usos |
| Organization | Tenant lógico | A confirmar no código | Aparentemente aderente | Validar detalhes |
| OrganizationMember | Vínculo interno staff | A confirmar no código | Aparentemente aderente | Validar regras de acesso |
| OrganizationClient | Vínculo cliente-organização | A confirmar no código | Incerto | Revisar modelagem |
| Client | Perfil contextual por vínculo | A confirmar no código | Incerto | Revisar modelagem prioritariamente |
| Professional | Perfil derivado de membership | A confirmar no código | Aparentemente aderente | Validar |
| Assistant | Perfil derivado de membership | A confirmar no código | Aparentemente aderente | Validar |
| OnboardingToken | Token genérico multiuso | Implementado com nome legado | Parcialmente aderente | Planejar rename futuro |


14. Regra de manutenção desta seção
Sempre que houver alteração em:

relacionamentos principais;
nomes de entidades;
dependência entre perfis;
natureza global ou tenantizada de um model;
esta seção deve ser atualizada para continuar servindo como mapa documental do schema.

---

## Fluxos Críticos do Sistema

## Fluxos Principais do Sistema

Esta seção descreve os principais fluxos funcionais do LiaFit em nível de comportamento esperado do sistema.

O objetivo é registrar, de forma clara, como a plataforma deve reagir em cenários centrais de autenticação, entrada na área logada, ativação de conta, mudança de contexto e evolução futura do uso.

Os fluxos aqui descritos representam contratos de comportamento do sistema e devem orientar implementação, testes e evolução da arquitetura.

---

### 1. Fluxo de registro público de organização

Este é o fluxo inicial já existente para entrada de uma nova organização na plataforma.

#### Objetivo
Permitir que uma nova empresa se registre e crie sua conta inicial no sistema.

#### Passos esperados
1. visitante acessa a página pública de registro;
2. preenche dados pessoais e dados da organização;
3. sistema valida os dados do formulário;
4. sistema cria:
   - `User` inativo;
   - `Organization` inativa;
   - vínculo inicial apropriado;
   - token de ativação/configuração;
5. sistema envia ou registra instrução para setup de senha;
6. usuário recebe link/token de configuração;
7. fluxo público é encerrado com mensagem de sucesso orientativa.

#### Resultado esperado
A organização entra no sistema em estado pendente até conclusão do setup de senha.

---

### 2. Fluxo de setup de senha por token

Fluxo utilizado após o onboarding inicial e potencialmente reaproveitável em cenários análogos.

#### Objetivo
Permitir que o usuário configure sua senha a partir de token válido.

#### Passos esperados
1. usuário acessa a URL com token;
2. sistema valida:
   - existência do token;
   - finalidade;
   - expiração;
   - estado de uso ou revogação;
3. se válido, o sistema apresenta formulário de senha;
4. usuário informa nova senha;
5. sistema valida política de senha;
6. sistema consome token de forma controlada;
7. sistema ativa os registros necessários;
8. sistema confirma conclusão do processo.

#### Resultado esperado
Usuário passa a conseguir autenticar normalmente na plataforma.

---

### 3. Fluxo de login

#### Objetivo
Autenticar um usuário previamente ativo.

#### Passos esperados
1. usuário acessa tela de login;
2. informa credenciais;
3. sistema valida autenticação;
4. se autenticado com sucesso, cria sessão ou retorna token conforme canal;
5. sistema resolve o ponto de entrada pós-login;
6. usuário entra na área autenticada.

#### Regra arquitetural
O login autentica a pessoa global (`User`), não um papel específico e não uma organização específica.

---

### 4. Fluxo pós-login

Este é um dos fluxos mais importantes da arquitetura atual.

#### Objetivo
Definir como o sistema recebe o usuário imediatamente após autenticação.

#### Contrato esperado
1. login concluído com sucesso;
2. sistema carrega contexto global do usuário;
3. usuário é redirecionado para a landing autenticada principal;
4. sistema verifica vínculos organizacionais disponíveis;
5. se houver organizações acessíveis, exibe mecanismos de entrada em contexto organizacional;
6. se não houver, a navegação continua funcional em modo global.

#### Regra central
O usuário autenticado deve conseguir entrar no sistema mesmo sem organização ativa.

---

### 5. Fluxo de usuário sem organização

#### Objetivo
Garantir experiência válida para usuário autenticado sem vínculo organizacional.

#### Situação típica
- usuário recém-criado;
- usuário em fase inicial de onboarding;
- usuário que ainda não foi vinculado a nenhuma organização;
- usuário com uso restrito ao contexto global.

#### Comportamento esperado
- acesso à área autenticada global;
- acesso a "Minha Conta";
- acesso a perfil e preferências;
- eventual acesso à área base do cliente;
- ausência de erros por falta de tenant;
- ausência de bloqueio indevido de navegação.

---

### 6. Fluxo de usuário com uma organização

#### Objetivo
Definir comportamento quando existe exatamente um contexto organizacional disponível.

#### Comportamento recomendado
- usuário entra primeiro na camada global;
- sistema pode destacar a organização disponível;
- sistema pode oferecer entrada rápida na empresa atual;
- eventual abertura automática da última organização deve ser tratada como conveniência futura, não como obrigação estrutural.

#### Regra
Ter apenas uma organização disponível não elimina a existência do contexto global.

---

### 7. Fluxo de usuário com múltiplas organizações

#### Objetivo
Permitir navegação clara para usuários multi-organização.

#### Comportamento esperado
- usuário entra na camada global;
- sistema exibe seletor ou lista de organizações disponíveis;
- usuário escolhe organização ativa quando desejar acessar recursos tenantizados;
- mudança de organização altera apenas o contexto organizacional;
- contexto global permanece estável.

#### Resultado esperado
O sistema suporta operação multi-tenant sem confundir identidade global com contexto ativo.

---

### 8. Fluxo de troca de organização ativa

#### Objetivo
Permitir mudança controlada do tenant atual.

#### Passos esperados
1. usuário possui acesso a mais de uma organização;
2. escolhe nova organização no seletor;
3. sistema valida vínculo válido;
4. atualiza contexto organizacional ativo;
5. recalcula permissões, papéis e módulos;
6. redireciona para página apropriada no novo contexto.

#### Regra
A troca de organização não deve reautenticar o usuário nem alterar sua identidade global.

---

### 9. Fluxo do usuário híbrido

#### Objetivo
Dar suporte a usuários com múltiplas naturezas de vínculo.

#### Exemplos
- cliente e profissional ao mesmo tempo;
- cliente e owner;
- assistente em uma organização e cliente em outra;
- profissional em uma empresa e cliente em outra.

#### Comportamento esperado
A navegação deve permitir coexistência de:
- conta global;
- área global do cliente;
- empresa atual;
- permissões específicas conforme tenant ativo.

#### Regra
O sistema não deve obrigar o usuário a escolher uma identidade única e exclusiva por sessão.

---

### 10. Fluxo de acesso a rota global autenticada

#### Objetivo
Formalizar comportamento de rotas que exigem login, mas não exigem tenant.

#### Exemplos
- meu perfil;
- preferências;
- segurança da conta;
- dashboard global;
- listagem global das organizações acessíveis.

#### Comportamento esperado
- autenticação obrigatória;
- tenant opcional ou ausente;
- nenhuma dependência estrutural de `OrganizationMember` para renderização básica.

---

### 11. Fluxo de acesso a rota tenantizada

#### Objetivo
Formalizar comportamento para rotas dependentes de organização.

#### Exemplos
- dashboard da empresa;
- equipe;
- clientes da organização;
- agenda da organização;
- financeiro interno.

#### Passos esperados
1. usuário autenticado solicita rota tenantizada;
2. sistema resolve organização alvo;
3. valida acesso do usuário ao tenant;
4. monta contexto com organização, membership, roles e permissões;
5. renderiza recurso ou bloqueia acesso de forma controlada.

#### Resultado esperado
As rotas organizacionais operam com escopo seguro sem contaminar as rotas globais.

---

### 12. Fluxo de superuser

#### Objetivo
Definir o comportamento de exceção administrativa da plataforma.

#### Comportamento esperado
- superuser autentica como usuário global;
- pode acessar áreas administrativas da plataforma;
- pode atravessar contextos com regras especiais controladas;
- não deve servir como justificativa para exigir membership de todos os demais usuários.

---

### 13. Fluxos futuros relacionados a cliente

Alguns fluxos ainda dependem da consolidação da modelagem de cliente, mas já podem ser descritos em nível conceitual.

#### Fluxos futuros esperados
- vincular usuário existente como cliente de uma organização;
- cadastrar nova pessoa e vinculá-la como cliente;
- visualizar organizações com as quais o usuário possui relação;
- exibir jornada do cliente por organização;
- consolidar visão global do cliente na plataforma.

---

### 14. Regra de manutenção desta seção

Sempre que um fluxo principal mudar em:
- ordem de execução;
- ponto de entrada;
- dependência de tenant;
- ativação de contexto;
- uso de token;
- relacionamento entre usuário e organização;

esta seção deve ser atualizada.

---

## Notas Técnicas e Débitos Técnicos

## Regras de Permissão e Acesso

Esta seção define as regras gerais de autenticação, autorização e resolução de permissões do LiaFit.

O objetivo é separar com clareza:

1. identidade global do usuário;
2. vínculo com organização;
3. papéis organizacionais;
4. permissões efetivas em cada contexto.

---

### 1. Princípio central

Permissões sempre devem ser avaliadas a partir de dois níveis:

#### Nível 1 — Autenticação global
Verifica se existe um `User` autenticado válido na plataforma.

#### Nível 2 — Contexto organizacional
Quando a rota ou recurso exigir organização, verifica:
- organização ativa;
- vínculo válido;
- papéis do usuário naquele tenant;
- permissões derivadas.

---

### 2. Identidade não é permissão

Ter um `User` autenticado significa que a pessoa existe e entrou na plataforma.

Isso **não significa automaticamente** que ela:
- pertença a uma organização;
- tenha acesso a qualquer tenant;
- possua privilégios administrativos;
- possa acessar qualquer recurso contextual.

---

### 3. Membership não é autenticação

Ter `OrganizationMember` significa que o usuário possui vínculo interno com determinada organização.

Isso **não deve ser usado** como requisito universal para login ou para toda navegação autenticada.

#### Regra
Membership é requisito de autorização contextual, não de identidade global.

---

### 4. Cliente não deve ser tratado como staff por padrão

O fato de existir `Role.CLIENT` em algum catálogo não significa que cliente deva automaticamente ser tratado como membro interno da organização.

#### Diretriz
O acesso do cliente deve ser pensado com semântica própria, respeitando:
- vínculo como `OrganizationClient`;
- eventual área global do cliente;
- acessos contextuais específicos sem confundir cliente com equipe.

---

### 5. Papéis organizacionais

Os papéis organizacionais representam capacidades dentro de um tenant específico.

#### Papéis atualmente previstos
- `OWNER`
- `ADMIN`
- `PROFESSIONAL`
- `ASSISTANT`
- `CLIENT` (com uso a validar cuidadosamente)

#### Observação
Esses papéis não são globais ao usuário.  
Eles só fazem sentido quando associados a uma organização ou a um vínculo contextual.

---

### 6. Permissões derivam do contexto ativo

A permissão efetiva do usuário deve ser calculada a partir de:

- identidade global autenticada;
- organização ativa, quando houver;
- vínculo válido;
- papéis daquele vínculo;
- estado da organização;
- estado do vínculo;
- módulos contratados, quando aplicável.

#### Fórmula conceitual
Permissão efetiva = autenticação global + contexto organizacional válido + regras do recurso

---

### 7. Regras para rotas globais

Rotas globais autenticadas exigem apenas:

- usuário autenticado;
- conta em estado válido.

#### Não devem exigir por padrão
- `org_slug`;
- membership;
- role tenantizada;
- organização ativa.

#### Exemplos
- perfil;
- configurações;
- segurança da conta;
- dashboard global;
- visão global das organizações do usuário.

---

### 8. Regras para rotas tenantizadas

Rotas tenantizadas exigem, além da autenticação:

- organização alvo válida;
- contexto tenant resolvido;
- vínculo do usuário com a organização, quando aplicável;
- permissões compatíveis com o recurso.

#### Possíveis validações
- membership ativo;
- role específica;
- módulo habilitado;
- status da organização;
- relação cliente-organização válida, em casos de área contextual do cliente.

---

### 9. Superuser

O superuser possui capacidade administrativa especial da plataforma.

#### Regras
- autentica globalmente como qualquer usuário;
- pode ter bypass controlado em algumas validações;
- não redefine o modelo conceitual do restante da aplicação;
- deve ser tratado como exceção administrativa e não como padrão de autorização.

---

### 10. Estado do vínculo importa

Não basta existir registro de relacionamento.  
O estado do vínculo deve influenciar autorização.

#### Exemplos de estados relevantes
- ativo;
- pendente;
- inativo;
- arquivado;
- revogado.

#### Regra
Permissões não devem ser concedidas apenas pela existência histórica de vínculo.

---

### 11. Estado da organização importa

Mesmo que o usuário tenha vínculo com uma organização, o estado da organização também pode limitar acesso.

#### Exemplos
- organização inativa;
- organização bloqueada;
- organização em onboarding incompleto.

#### Regra
A autorização tenantizada deve considerar a saúde do tenant.

---

### 12. Permissão e navegação não são a mesma coisa

O fato de um item aparecer ou não no menu é apenas um reflexo de navegação.

#### Regra importante
- esconder item de menu não substitui verificação de permissão;
- toda rota protegida deve validar acesso no backend;
- templates não devem concentrar a regra principal de autorização.

---

### 13. Camadas de aplicação da autorização

A autorização pode ser aplicada em múltiplas camadas, cada uma com papel específico.

#### Middleware
Pode resolver contexto, mas não deve concentrar regra de negócio detalhada.

#### Mixins / Views base
Devem validar pré-condições de acesso ao recurso.

#### Services
Devem reforçar invariantes de negócio quando a operação for sensível.

#### Templates
Devem apenas refletir permissões já resolvidas pela camada apropriada.

---

### 14. Estratégia recomendada de verificação

A ordem recomendada de verificação para recurso tenantizado é:

1. usuário autenticado?
2. rota exige tenant?
3. tenant foi resolvido?
4. usuário possui vínculo válido nesse tenant?
5. estado do vínculo permite acesso?
6. roles/permissões atendem ao requisito?
7. recurso específico impõe regra adicional?

---

### 15. Usuário híbrido e permissões

Usuário híbrido pode ter permissões diferentes em contextos diferentes.

#### Exemplo
O mesmo `User` pode ser:
- `OWNER` em uma organização;
- `PROFESSIONAL` em outra;
- cliente em uma terceira;
- apenas usuário global fora desses contextos.

#### Regra
Permissões devem ser sempre calculadas com base no contexto ativo, não em uma classificação fixa e global da pessoa.

---

### 16. Regra de manutenção desta seção

Sempre que houver mudança em:
- catálogo de papéis;
- política de acesso;
- critérios de validação de tenant;
- tratamento de cliente;
- comportamento de superuser;

esta seção deve ser atualizada para manter coerência entre domínio, navegação e segurança.

---


---

## Parte 15 — Pendências, Débitos Técnicos e Próximas Decisões

```md
## Pendências, Débitos Técnicos e Próximas Decisões

Esta seção registra o que ainda está em aberto, o que já é reconhecido como débito técnico e quais decisões precisam ser tomadas para permitir evolução segura do projeto.

O objetivo é tornar explícito o que ainda não está resolvido, evitando que lacunas arquiteturais permaneçam implícitas.

---

### 1. Pendências arquiteturais imediatas

Estas pendências impactam diretamente a coerência da fundação atual e devem ser tratadas antes da expansão mais ampla dos módulos.

#### Pendências prioritárias
- formalizar o contrato oficial de pós-login;
- separar claramente dashboard global e dashboard organizacional;
- definir a fronteira entre rotas globais e tenantizadas;
- revisar o `TenantMiddleware` para comportamento global-first;
- revisar mixins base para não exigir membership indevidamente;
- definir estrutura oficial da navegação logada;
- definir papel visual e funcional do seletor de organização.

---

### 2. Pendências de modelagem

Existem pontos do domínio que ainda precisam de verificação objetiva no código atual.

#### Itens a validar
- modelagem real de `Client`;
- modelagem real de `OrganizationClient`;
- relação efetiva entre `Professional` e `OrganizationMember`;
- relação efetiva entre `Assistant` e `OrganizationMember`;
- uso real de `Role.CLIENT`;
- formato final dos vínculos de equipe versus cliente.

#### Necessidade
Esses pontos devem ser confirmados por leitura direta do schema e não apenas por memória documental.

---

### 3. Débito técnico de nomenclatura em `OnboardingToken`

O nome atual não representa mais adequadamente o comportamento real da entidade.

#### Situação
A entidade já suporta múltiplos propósitos além de onboarding inicial.

#### Débito
- nome semântico defasado;
- potencial confusão em services futuros;
- aumento de inconsistência documental.

#### Próxima decisão
Definir se haverá rename para:
- `UserToken`
- `AuthToken`
- outro nome mais aderente

#### Prioridade
Média, salvo se novos fluxos ampliarem ainda mais o uso antes do rename.

---

### 4. Débito documental acumulado

O documento principal cresceu com histórico, iterações e ajustes progressivos.

#### Problemas atuais
- duplicidade de algumas informações;
- coexistência de trechos históricos e normativos;
- pontos com narrativas potencialmente conflitantes;
- necessidade de consolidação final.

#### Ação necessária
Executar uma rodada de limpeza editorial e consolidação estrutural.

---

### 5. Decisão pendente sobre landing autenticada

Ainda precisa ser formalmente decidido qual página representa a entrada padrão na área logada.

#### Opções possíveis
- dashboard global;
- home autenticada híbrida;
- redirecionamento contextual condicional;
- última organização acessada como conveniência opcional.

#### Recomendação
Adotar dashboard global como padrão arquitetural e usar shortcuts contextuais apenas como conveniência.

---

### 6. Decisão pendente sobre comportamento para usuário com uma única organização

Esse cenário precisa de contrato explícito para evitar comportamento inconsistente.

#### Questão
O sistema deve:
- sempre entrar no dashboard global;
- sugerir entrada na organização;
- redirecionar automaticamente para a organização;
- lembrar última escolha do usuário?

#### Recomendação
Preservar entrada global como padrão e tratar automações como otimização posterior, configurável ou validada por uso real.

---

### 7. Decisão pendente sobre estrutura final da sidebar

A sidebar já existe em forma inicial, mas precisa refletir o modelo correto do produto.

#### Pontos a decidir
- quais blocos são sempre globais;
- como exibir “Minha Conta”;
- como exibir “Área do Cliente”;
- como exibir “Empresa Atual”;
- como lidar com ausência de organização;
- como lidar com usuário híbrido.

---

### 8. Decisão pendente sobre context processor

A documentação já aponta necessidade de context processor para melhorar renderização do layout autenticado.

#### Questão
Quais dados globais e tenantizados devem estar universalmente disponíveis nos templates?

#### Recomendação
Definir contrato mínimo e estável, evitando jogar lógica demais na camada de template.

---

### 9. Decisão pendente sobre estratégia de permissões

A base conceitual já está definida, mas a implementação prática ainda pode precisar de padrão mais explícito.

#### Pontos a decidir
- quais checks ficam em mixins;
- quais checks ficam em helpers;
- quais checks ficam em services;
- como padronizar mensagens de acesso negado;
- como estruturar permissões para clientes contextuais.

---

### 10. Pendência de testes automatizados

A documentação já reconhece que a cobertura de testes ainda está aquém do ideal.

#### Prioridades imediatas
- `TokenService`;
- `OnboardingService`;
- setup de senha;
- middleware tenant;
- fluxo pós-login;
- permissões em rotas globais;
- permissões em rotas tenantizadas.

#### Risco
Sem testes nesses pontos, ajustes arquiteturais podem introduzir regressões silenciosas.

---

### 11. Pendência de tabela de convergência conceito vs código

O documento já sugere isso, mas a tabela ainda precisa ser preenchida a partir da implementação real.

#### Objetivo
Mapear entidade por entidade:
- conceito desejado;
- implementação atual;
- nível de aderência;
- impacto do desalinhamento;
- ação necessária.

#### Benefício
Transformar debate conceitual em plano operacional verificável.

---

### 12. Pendência sobre política de cliente global

A visão correta aponta que cliente deve ter presença global na experiência autenticada.

#### O que ainda precisa ser decidido
- quais páginas compõem a área global do cliente no MVP;
- o que depende de vínculo ativo com organização;
- o que pode aparecer mesmo sem vínculo atual;
- como representar múltiplas relações cliente-organização.

---

### 13. Pendência de revisão do uso de `Role.CLIENT`

Esse ponto merece atenção especial porque pode contaminar a semântica de autorização.

#### Risco
Se `CLIENT` for tratado como role staff comum, a fronteira entre equipe e cliente pode ficar confusa.

#### Ação necessária
Revisar onde esse codename existe, para que ele serve e se deve continuar no mesmo catálogo sem ajustes de interpretação.

---

### 14. Pendência sobre naming e semântica de perfis

Também é importante validar se os nomes dos perfis funcionais realmente expressam o domínio do produto.

#### Itens a observar
- `Client` é realmente o melhor nome para o perfil contextual?
- `OrganizationClient` está semanticamente claro?
- `Professional` e `Assistant` representam perfis ou tipos de vínculo?
- vale usar composição em vez de proliferação de perfis?

---

### 15. Próxima decisão recomendada

A próxima decisão estruturante mais importante é:

**formalizar o contrato de entrada na área autenticada e a separação entre contexto global e organizacional.**

Essa decisão influencia diretamente:
- middleware;
- mixins;
- sidebar;
- dashboard;
- seletor de organização;
- permissões;
- Sprint 2 inteira.

---

### 16. Regra final desta seção

Pendências e débitos técnicos do LiaFit não devem ficar implícitos.

Tudo o que puder afetar:
- domínio;
- navegação;
- autorização;
- modelagem;
- entendimento futuro do código;

deve ser registrado explicitamente até ser resolvido.
```
