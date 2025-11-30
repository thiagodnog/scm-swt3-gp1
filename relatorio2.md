# Relatório de Gerência de Configuração – Projeto Mileage Tracker

Repositório: https://github.com/thiagodnog/scm-swt3-gp1    
Período do projeto: <início do semestre> – 30/11/2025

---

## 1. Visão Geral do Projeto

O projeto consiste na adaptação e evolução do aplicativo **Mileage Tracker**, originalmente desenvolvido por outro autor, para servir como base de prática dos conceitos de **Gerência de Configuração de Software (SCM)**. A aplicação é um aplicativo desktop simples, em Python/Tkinter, voltado para:

- Registrar viagens (endereços de origem/destino, hodômetro, pedágios, estacionamento);
- Calcular automaticamente a distância entre endereços por meio da **Google Maps Routes API**, com *fallback* para cálculo por hodômetro;
- Consolidar e calcular despesas e exportar dados para um arquivo `.csv` para uso posterior (ex.: prestação de contas, relatórios).

O foco do trabalho, conforme as **Diretrizes da disciplina**, não é apenas o código, mas a correta aplicação de práticas de SCM: versionamento, branching, issues, PRs, build, testes e CI/CD.

---

## 2. Estratégia de Branching e Fluxo de Trabalho

### 2.1 Estratégia adotada

Foi adotada uma estratégia inspirada no **Git Flow**, conforme sugerido nas diretrizes do projeto:[1]

- **`main`**
  - Contém sempre a versão estável mais recente do sistema.
  - A partir dessa branch são criadas **tags** para releases (por exemplo, `v1.0.0`, `v1.1.0`).
- **`develop`**
  - Branch de integração principal durante o desenvolvimento.
  - Novas funcionalidades são integradas primeiro em `develop` antes de seguirem para `main`.
- **`feature/*`**
  - Branches derivadas de `develop` para desenvolvimento de funcionalidades específicas.
  - Exemplos:
    - `feature/API_calculo_km` – implementação do cálculo de distância usando Google Maps Routes API;
    - `feature/expanses_calculation` – adição do cálculo das despesas somando as depesas de estacionamento, pedágio e de trajeto (km);
- **`fix/*` ou `hotfix/*`**
  - Branches usadas para correção de bugs pontuais, principalmente quando impactam a versão já liberada em `main`.

### 2.2 Fluxo típico de desenvolvimento

1. **Criação de issue** descrevendo a tarefa ou bug (ex.: “Implementar cálculo de distância com Google Maps Routes API”).
2. **Criação de branch `feature/...`** a partir de `develop`.
3. Desenvolvimento da funcionalidade, com commits incrementais.
4. **Criação de Pull Request (PR)** da branch `feature/...` para `develop`.
   - No título e/ou descrição do PR, é usada uma palavra-chave de rastreabilidade (`closes #X`, `fixes #Y`) apontando para a issue relacionada.[3]
5. Execução automática do **workflow de CI** (testes + build Docker).
6. Revisão de código por outro integrante do grupo (ao menos 1 *review* antes do merge).[4]
7. Resolução de comentários e ajustes, se necessário.
8. **Merge em `develop`** após aprovação.
9. Periodicamente, quando o conjunto de funcionalidades atinge um estado estável, é aberto um PR de `develop` para `main`, seguido de:
   - criação de **tag de release** (ex.: `v1.1.0`),
   - atualização do `CHANGELOG.md`.

---

## 3. Ambiente de Desenvolvimento e Docker

### 3.1 Objetivo do uso de Docker

Em conformidade com as diretrizes, utlizamos **Docker** para garantir um ambiente de desenvolvimento replicável, independente do sistema operacional de cada integrante (Windows, Linux, macOS).[5]  
O container encapsula:

- Versão do Python utilizada;
- Dependências de sistema (ex.: Tkinter e bibliotecas de X11 para exibir a GUI);
- Dependências de Python (bibliotecas usadas pela aplicação e pelos testes).

### 3.2 Arquivos principais

- **`Dockerfile`**
  - Define a imagem base (ex.: `python:3.14-slim`).
  - Instala dependências de sistema (Tkinter, bibliotecas gráficas, etc.).
  - Copia o código-fonte para dentro da imagem.
  - Instala dependências Python a partir de `requirements.txt` ou similar.
  - Define o comando padrão de execução da aplicação.
- **`.dockerignore`**
  - Exclui arquivos desnecessários do contexto de build (ex.: `__pycache__`, `.git`, etc.) para agilizar o build e reduzir o tamanho da imagem.

> Observação: há um arquivo `docker-compose.yml` no repositório, mas ele ainda não foi configurado com serviços/volumes, portanto não é utilizado como parte central do fluxo de build/execução descrito neste relatório.

### 3.3 Execução documentada

No `README.md`, foram descritos os passos para:

- Executar a aplicação localmente em um ambiente com Python instalado;
- Executar via Docker em:
  - Linux (com X11 nativo);
  - macOS (usando XQuartz);
  - Windows (usando VcXsrv/Xming + Docker Desktop);
- Configurar o arquivo `.env` com a chave da Google Maps API, ou executar sem API (utilizando somente o hodômetro).

---

## 4. Procedimentos de Build, Testes e CI/CD

### 4.1 Testes automatizados

Os testes automatizados foram implementados em **Python**, utilizando o módulo padrão `unittest`, no diretório:

- `test/test.py`

Os testes cobrem principalmente:

- Inicialização da aplicação (criação da janela principal sem erros críticos);
- Lógica de cálculo de despesas;
- Escrita e leitura de registros de viagem em arquivos `.csv` (usando diretório temporário durante os testes).

### 4.2 Workflow de CI (GitHub Actions)

Atendendo às diretrizes, foi criado um workflow de CI em:

- `.github/workflows/ci.yml`

Esse workflow é disparado em eventos como:

- `push` para as branches principais (`main`, `develop`);
- `pull_request` direcionados para `main` ou `develop`.

Etapas principais do workflow:

1. **Checkout do repositório**
   - Usa a ação `actions/checkout` para obter o código da branch alvo.
2. **Configuração do ambiente Python**
   - Instala a versão do Python declarada no workflow.
3. **Instalação de dependências**
   - Instala bibliotecas Python necessárias para rodar a aplicação e os testes.
4. **Execução de testes automatizados**
   - Os testes são executados com o comando padrão do `unittest`, por exemplo:
     - `python -m unittest discover -s test`
   - Esse comando funciona tanto no ambiente local (Windows, Linux, macOS) quanto no runner do GitHub Actions, e é suficiente porque a suíte de testes atual não depende de abrir janelas gráficas reais, focando na lógica de negócios e na manipulação de arquivos.
5. **Build de imagem Docker**
   - Opcionalmente, o workflow gera a imagem Docker da aplicação, garantindo que o `Dockerfile` esteja sempre consistente e buildável.

### 4.3 CI/CD no contexto do projeto

- **Continuous Integration (CI):**
  - Assegura que cada PR/merge passe pelos testes.
  - Reduz o risco de introduzir regressões em `develop` ou `main`.
- **Continuous Delivery (CD):**
  - Não há um pipeline de deploy automatizado para produção (o escopo do trabalho não exigia isso), mas o build automático da imagem Docker e a documentação de deploy são passos que aproximam o projeto de um cenário de CD.

---

## 5. Versionamento, Releases e CHANGELOG

### 5.1 Estratégia de versionamento

Foi adotado o **versionamento semântico (SemVer)**, com o formato:

- `MAJOR.MINOR.PATCH`

Interpretação:

- **MAJOR**: mudanças incompatíveis na API/forma de uso;
- **MINOR**: novas funcionalidades compatíveis;
- **PATCH**: correções de bugs sem novas funcionalidades.

Exemplos de releases (ajustar conforme as tags reais do repositório):

- `v1.0.0` – Versão inicial da aplicação, já adaptada para o contexto da disciplina, com registro básico de viagens e exportação para CSV.
- `v1.1.0` – Inclusão da funcionalidade de cálculo automático de distância via Google Maps Routes API, ajustes no README e ampliação da suíte de testes.

### 5.2 Tags e Releases no GitHub

Para cada versão estável liberada em `main`, é criada:

- uma **tag anotada** (ex.: `v1.1.0`);
- uma **Release** no GitHub, contendo:
  - título da versão;
  - breve resumo das mudanças;
  - link para o commit/PR principal associado.

As diretrizes recomendam explicitamente o uso de Releases e tags imutáveis para cada versão.

### 5.3 `CHANGELOG.md`

As mudanças entre versões são documentadas em um arquivo `CHANGELOG.md`, seguindo uma estrutura simples, por exemplo:

```md
# Changelog

## [v1.1.0] - 2025-11-30

### Added

- Integração com Google Maps Routes API para cálculo de distância.
- Novos testes automatizados para validação da lógica de despesas e registro de viagens.

### Changed

- Atualização do README com instruções de configuração da API e uso via Docker.

## [v1.0.0] - 2025-11-20

### Added

- Versão inicial do Mileage Tracker adaptado para o projeto de SCM.
- Registro de viagens com exportação para arquivo CSV.
```

## 6. Gerenciamento de Mudanças e Rastreabilidade

### 6.1 Issues

Para cada funcionalidade, melhoria ou bug, foi criada uma issue correspondente no GitHub.  
As issues foram categorizadas com labels, como:

- `enhancement` – novas funcionalidades;
- `bug` – correções de defeitos;
- `documentation` – ajustes de documentação;
- `ci / build` – tarefas relacionadas a automação e pipelines.

O ciclo de vida típico de uma issue:

- Criação da issue com descrição do problema ou funcionalidade.
- Associação a um ou mais integrantes responsáveis.
- Criação de branch `feature/...` associada à issue.
- Desenvolvimento + commits referenciando a issue (ex.: `feat: adiciona cálculo de distância (refs #X)`).
- Abertura de PR mencionando a issue (`closes #X`).
- Merge do PR após review.
- Fechamento automático da issue pelo GitHub devido à keyword `closes`.

### 6.2 Pull Requests e Revisões de Código

Cada `feature/*` ou `hotfix/*` foi integrada via Pull Request.  
Pelo menos um integrante diferente do autor realizou code review antes de cada merge para as branches principais, conforme recomendado nas diretrizes.  
Foram verificados:

- impacto das mudanças na base de código;
- resultado dos testes no pipeline de CI;
- aderência à estrutura do projeto e ao padrão de mensagens de commit.

### 6.3 Convenção de Commits

A equipe adotou uma convenção simples, inspirada em Conventional Commits, usando prefixos como:

- `feat:` – para novas funcionalidades;
- `hotfix:` – para correções de bugs;
- `docs:` – alterações apenas em documentação;

Essa convenção facilita a compreensão do histórico e, potencialmente, a automatização de geração de notas de release no futuro.

## 7. Papéis, Responsabilidades e Atividades dos Integrantes

Conforme as diretrizes, cada integrante assumiu ao menos dois papéis entre Desenvolvedor, Responsável por Build/CI, Gerente de Configuração e Testador.  


### 7.1 Integrante 1 – Gustavo Igor da Silva

Papéis exercidos: Desenvolvedor, Testador, Gerente de Configuração  

Principais atividades:

- Implementação da funcionalidade de cálculo de distância via Google Maps Routes API na branch `feature/API_calculo_km`.
- Tratamento de erros de comunicação com a API e fallback para cálculo via hodômetro.
- Atualização do `README.md` com instruções de configuração do arquivo `.env` e exemplos de uso.
- Implementação/ajuste de testes automatizados em `test/test.py` relacionados ao cálculo de despesas e persistência em CSV.
- Revisão de pull request e de rastreabilidade.

### 7.2 Integrante 2 – <NOME_2>



### 7.3 Integrante 3 – <NOME_3>



### 7.4 Integrante 4 – <NOME_4>



## 8. Lições Aprendidas

As diretrizes da disciplina solicitam que cada membro registre suas lições aprendidas em SCM, destacando desafios e pontos de melhoria.  


### 8.1 Gustavo Igor da Silva


No início do projeto, minha maior dificuldade foi transformar a teoria de Gerência de Configuração em práticas concretas no repositório. Eu já usava Git de forma isolada, mas lidar com **GitFlow**, múltiplas branches, PRs, issues, **SemVer** e trabalho em equipe expôs várias lacunas — especialmente na hora de entender o momento certo de criar/atualizar branches, sincronizar o repositório remoto (`git fetch`/`git pull`, SSH no Windows), relacionar PR com issue e resolver conflitos em arquivos compartilhados.  
Além disso, a integração da **Google Maps Routes API** trouxe desafios extras: configuração de `.env`, tratamento de erros de comunicação, limites de uso e implementação do *fallback* para o hodômetro quando a API não está disponível. Integrar a Google Maps API mostrou a importância de isolar configurações sensíveis em arquivos `.env` e de documentar claramente dependências externas.

Ao longo do projeto, essas dificuldades viraram meus principais aprendizados:

- Passei a entender o **GitFlow na prática**, desde a criação de uma *feature branch* até o merge em `main` via PR revisada.  
- Aprendi a usar **issues e PRs como ferramentas de rastreabilidade**, ligando cada mudança a uma demanda específica.  
- Consolidei a importância do **versionamento semântico e do changelog**, entendendo como as releases (como a `1.1.0`) registram a evolução do sistema.  
- Passei a valorizar **ambiente reprodutível e automatizado** (Docker, variáveis de ambiente, documentação), reduzindo o “funciona só na minha máquina”.  
- Ganhei segurança para **ler código existente, propor mudanças, escrever testes e receber feedback em code reviews**, aproximando a experiência do que acontece em projetos reais.  
- Na parte de API, entendi melhor como **isolar configurações sensíveis**, tratar falhas externas sem quebrar a aplicação e pensar sempre em estratégias de *fallback*.

### 8.2 <NOME_2>



### 8.3 <NOME_3>



### 8.4 <NOME_4>


## 9. Conclusão

O projeto cumpriu o papel de simulação de desenvolvimento com foco em SCM, permitindo que o grupo praticasse:

- Definição de estratégia de branching e uso disciplinado de branches `main`, `develop` e `feature/...`;
- Criação e acompanhamento de issues e Pull Requests, com rastreabilidade por meio de keywords (`closes #...`);
- Configuração de ambiente padronizado com Docker;
- Criação de pipeline de CI com GitHub Actions, incluindo testes automatizados e build de imagem Docker;
- Adoção de versionamento semântico, uso de tags e construção de um `CHANGELOG.md`;
- Registro de lições aprendidas, consolidando o entendimento de práticas de Gerência de Configuração para além da teoria.