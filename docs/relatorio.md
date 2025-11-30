# Relatório de Processos de Desenvolvimento

Este documento descreve a estratégia de branching adotada, os procedimentos de build e CI/CD, o modelo de versionamento (tags/releases) e o processo de gerenciamento de issues usado neste projeto.

## Estratégia de Branching

### Ramos principais

- `main` (produção) e `develop` (integração).

### Feature branches

- Prefixo `feature/` seguido de resumo e, opcionalmente, número da issue — ex.: `feature/123-expense-calculator`.

### Hotfix branches

- Prefixo `hotfix/` para correções críticas que precisam ir diretamente para produção — ex.: `hotfix/fix-calc-rounding`.

### Políticas de merge

- Pull Requests (PRs) exigem revisão por pelo menos um revisor, execução bem-sucedida de CI (testes + lint) e aprovação antes do merge.
- Merges de `feature/*` vão para `develop`; merges para `main` são feitos a partir de `develop` (ou `hotfix/*` quando aplicável).
- Merges são acompanhados de tag de release.

### Convencionalidade

- Mensagens de commit seguem um padrão curto e descritivo.
- Usar palavras-chave da issue no corpo do PR para rastreabilidade.

## Procedimentos de Build e CI/CD

### Pipeline (CI) típico

- **Instalação do ambiente:** `pip install -r requirements.txt` ou criar ambiente virtual.
- **Linter/estática:** rodar ferramentas como `flake8` / `pylint` (opcional).
- **Testes automatizados:** `python -m unittest discover -v` (ou `python -m pytest` se adotado pytest).
- **Verificações adicionais:** checagem de formatação (`black --check`) e análise estática (opcional).

### Gatilhos

- Executar CI em cada push a `feature/*`, `develop` e em cada PR.
- Branches protegidas (`main`, `develop`) exigem CI verde para merge.

### Build de imagem / artefato

- Quando a pipeline de CI para `main` é bem-sucedida (ou em `release/*`), gerar artefato (ex.: imagem Docker via `Dockerfile`).
- Armazenar em um registry (ex.: Docker Hub, Azure Container Registry, GitHub Container Registry).

### CD (deploy)

- Ao criar uma release/tag em `main`, a pipeline de CD é disparada para publicar a imagem e atualizar o ambiente de destino.
- Para stacks simples, pode-se usar `docker-compose` com a nova tag.
- Exemplo de etapas: build image → push registry → aplicar update (ssh/ansible/docker-compose pull + up) ou usar uma plataforma de orquestração.

### Segredos e configuração

- Variáveis sensíveis (ex.: `GOOGLE_MAPS_API_KEY`) devem ser guardadas em variáveis de ambiente nos secrets do provedor CI/CD (GitHub Actions Secrets, Azure Key Vault, etc.).

### Exemplo de comandos locais rápidos

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m unittest discover -v
docker build -t myapp:dev .
```

## Forma de Versionamento (tags, releases)

- **Esquema:** adotar Semantic Versioning (SemVer) — `vMAJOR.MINOR.PATCH`.
- **Tags:** usar tags anotadas para cada release (ex.: `git tag -a v1.2.0 -m "Release v1.2.0"`).
- **Releases:** criar uma Release no repositório (GitHub/GitLab) a partir da tag, incluindo changelog resumido e binaries/artefatos se aplicável.
- **Fluxo de publicação:** merge para `main` → tag de versão → pipeline de CI/CD que faz build e publica a imagem/artefato.
- **Histórico/Changelog:** manter um changelog conciso (manual ou gerado a partir de mensagens convencionais), idealmente agrupando mudanças por categoria (fix, feat, docs).

## Gerenciamento de Issues (ciclo de vida de um bug/feature)

- **Criação:** toda nova demanda (bug ou feature) começa com uma issue descrevendo objetivo, passos para reproduzir (se for bug), e critérios de aceitação.
- **Triagem:** time ou mantenedor avalia prioridade, severidade, e atribui labels (ex.: `bug`, `feature`, `urgent`, `low-priority`).
- **Desenvolvimento:**
  - Criar branch: `feature/<issue>-descrição` ou `hotfix/<issue>` conforme o caso.
  - Linkar branch/PR à issue (número no título/descrição) para rastreabilidade.
  - Implementar alterações com commits pequenos e atômicos, incluindo testes automatizados quando pertinente.
- **Revisão:** abrir PR e solicitar revisão de pelo menos um colega; CI deve passar antes da aprovação.
- **Release e fechamento:** depois de validado, a release é criada a partir de `develop` → `main` (ou diretamente de `hotfix`), tag publicada e a issue é fechada com referência à release.
- **Feedback loop:** se regressão ou novo bug é detectado, reabrir issue ou criar nova issue vinculada, priorizar e seguir o ciclo novamente.

## Boas práticas e automações sugeridas

- **Automatizar:** rodar CI em PRs, bloquear merges com CI falhando, usar templates de issues/PRs para padronizar descrições.
- **Labels:** padronizar um conjunto de labels (ex.: `bug`, `enhancement`, `documentation`, `help wanted`, `wontfix`) e regras de priorização.
- **Templates:** usar templates de PR/issue (ex.: checklist de PR com "tests added", "docs updated").

---

# Lições Aprendidas

## Desafios Encontrados

### 1. Sincronização entre branches e conflitos de merge

- **Desafio:** Durante o desenvolvimento de features em paralelo, especialmente na feature `expense-calculation`, houve períodos onde `develop` estava à frente da `feature/expenses_calculation`, causando conflitos ao tentar sincronizar.
- **Como foi lidado:** Implementamos rebases frequentes e pulls regulares de `develop` para manter as branches sincronizadas. Isso evitou conflitos grandes no momento do merge final.
- **Melhoria sugerida:** adotar uma política de "pull antes de push" ou usar squash commits em features menores para reduzir o ruído de merge.

### 2. Testes falhando e precisão de arredondamento em cálculos monetários

- **Desafio:** Os testes unitários para `ExpenseCalculator` falhavam porque a arredondamento de valores monetários usando Python floats + `round()` produzia resultados inesperados (ex.: 16.665 arredondava para 16.66 em vez de 16.67).
- **Como foi lidado:** Substituímos a arredondamento com float para Decimal + ROUND_HALF_UP, garantindo comportamento determinístico e correto para operações monetárias.
- **Melhoria sugerida:** estabelecer uma política de usar `Decimal` desde o início para qualquer cálculo financeiro; documentar essa prática no guia de contribuição.

### 3. Dependências opcionais e imports defensivos

- **Desafio:** O projeto usava `requests` (Google Maps API) e `python-dotenv` (configuração), mas esses packages não estavam instalados em todos os ambientes, causando falhas de import em tempo de execução.
- **Como foi lidado:** Guardamos os imports com try/except, exibindo avisos ao usuário se a integração com Google Maps ficasse indisponível, e atualizamos `requirements.txt` com versões mínimas pinadas.
- **Melhoria sugerida:** criar um arquivo `requirements-optional.txt` separado e documentar claramente quais dependências são essenciais vs. opcionais no README.

### 4. Fixtures de testes e criação de widgets Tkinter

- **Desafio:** Um teste de widget falhava porque não havia uma instância de `MileageTracker` e `tk.Tk()` disponível; o setUp da classe de testes não criava esses objetos.
- **Como foi lidado:** Adicionamos setUp/tearDown na classe `TestExpenseCalculatorEdgeCases` para instanciar a raiz Tk e a aplicação, garantindo que widgets possam ser testados.
- **Melhoria sugerida:** criar uma classe base (TestCase) customizada para testes de UI que automaticamente configura e destrói widgets.

### 5. CSV com múltiplas colunas e evolução do schema

- **Desafio:** Ao adicionar novas colunas (`km_expense`, `total_expense`) ao CSV, tivemos que garantir que registros antigos fossem compatíveis ou migrados.
- **Como foi lidado:** Verificamos se o arquivo CSV existe e adicionamos header automaticamente na primeira escrita; registros novos incluem todas as colunas.
- **Melhoria sugerida:** implementar uma função de migração explícita para evoluir o schema de dados entre versões.

## Melhorias Implementadas

1. **Rounding determinístico:** migração para Decimal com ROUND_HALF_UP.
2. **Guarda defensiva de imports:** tratamento de dependências opcionais com warnings amigáveis ao usuário.
3. **Tests mais robustos:** fixtures adequadas para UI, cobertura expandida de edge cases.
4. **Documentação:** adição de comentários inline e este relatório explicando procedimentos.
5. **Versionamento:** estrutura pronta para tags SemVer e releases no repositório.

## Como o time lidou com problemas de SCM

- **Comunicação:** commits descritivos e PRs bem documentadas facilitam a rastreabilidade de mudanças.
- **Revisão de código:** cada PR passa por pelo menos um revisor antes de merge, reduzindo bugs e melhorando qualidade.
- **CI automatizado:** testes rodam em cada PR, bloqueando merges com falhas — isso evitou regressões.
- **Branch naming:** convenção clara (feature/, hotfix/) facilita identificar o tipo de mudança no histórico git.
- **Issue linking:** vincular commits/PRs a issues melhora rastreabilidade do "por quê" de cada mudança.

---

# Reflexões por Membro da Equipe

## Danilo Varini

### Experiência com Git e Branching

Eu não tinha experiência profunda com GIT ou SCM até este momento. Ao longo deste projeto, pude vivenciar na prática como uma estratégia de branching bem definida é crucial para evitar caos em repositórios colaborativos.

**O que funcionou bem:**
- A convenção de naming (feature/, hotfix/, release/) deixou claro o propósito de cada branch, reduzindo confusão.
- Fazer rebases frequentes de `develop` mantinha as features atualizadas e reduzia conflitos grandes.

**Desafios:**
- No início, havia incerteza sobre quando fazer/criar PRs, edições simples, rebase vs. merge. Aprender a diferenciar essas operações ajudou muito.
- Resolver conflitos em arquivos grandes (como `app.py` com múltiplas mudanças paralelas) exigiu cuidado para não perder código.

**Como evoluí:**
- Pedi ajuda a colegas de equipe (Thiago, Hugo, Gustavo) e comecei a revisar PRs de forma mais rigorosa, procurando por possíveis conflitos e inconsistências antes do merge.

### Uso de Testes e CI

O projeto me mostrou o valor importante de testes automatizados.

**Pontos positivos:**
- Escrever testes unitários para `ExpenseCalculator` (e depois corrigir bugs de rounding) melhorou minha confiança no código.

**Aprendizados:**
- Usar `Decimal` para operações monetárias em vez de float, uma lição que levarei para outros projetos.
- Cobertura de edge cases (distâncias muito pequenas, muito grandes, strings vazias) catch bugs reais.


### Gerenciamento de Issues

Usar issues para documentar features e bugs, e linká-los a commits/PRs, foi ótimo aprendizado.


**Desafio:**
- No início, tudo era novidade, mas com o tempo e prática o processo foi ficando mais claro.

### Lições gerais

1. **SCM é um processo, não apenas uma ferramenta:** usar git bem exige disciplina, comunicação e automação.
2. **Pequenos commits frequentes > grandes commits espaçados:** facilitam reviews.
3. **Testes + CI = confiança:** ter uma suite de testes passando continuamente libera o time para iterar com segurança.
4. **Documentação integrada:** manter README e este Relatório atualizado ajuda a onboard novos membros e evita retrabalho.
5. **Refatoração iterativa:** a mudança de float para Decimal foi pequena, mas importante: não tenha medo de melhorar código.

## Thiago Nogueira

### Reflexões sobre colaboração e melhorias técnicas

- A equipe apresentou níveis de conhecimento técnico distintos no início do projeto. Gerenciar essa diferença exigiu paciência, mais comunicação e atividades de pair programming para nivelar entendimento das ferramentas (Git, Docker, Tkinter).
- Resolver conflitos entre features foi um desafio recorrente, especialmente quando múltiplas pessoas trabalhavam em arquivos grandes como app.py. A adoção do fluxo GitFlow (features mescladas primeiro em develop) ajudou a proteger a branch main e reduzir impactos em produção.
- Padronizar ambientes com Dockerfile trouxe um ganho real: apesar da curva de aprendizagem inicial para alguns membros, hoje temos builds e execuções mais previsíveis. A normalização facilitou onboarding e reduziu "works on my machine".
- Recomenda-se manter sessões curtas de formação sobre ferramentas críticas (Git, CI, Docker) e documentar procedures comuns no repositório.

### Reflexões da Equipe

- Desafios enfrentados:
  - Níveis técnicos variados entre membros demandaram investimento em orientação e revisão mais detalhada.
  - Conflitos de merge em features concorrentes exigiram disciplina em rebases/merges e comunicação prévia sobre áreas do código que seriam alteradas.
  - A curva de aprendizado do Docker inicialmente atrasou testes locais para alguns colaboradores.

- Ganhos e melhorias:
  - O uso de GitFlow (feature → develop → main) provou ser eficaz para preservar estabilidade na main e organizar releases.
  - A introdução do Dockerfile normalizou ambientes de desenvolvimento e execução, aumentando a reprodutibilidade e facilitando a CI.
  - Lições compartilhadas sobre Decimal para cálculos monetários, testes e tratamento de dependências deixaram a base de código mais robusta.

- Ações sugeridas:
  - Sessões regulares de compartilhamento de conhecimento (15–30 min) para nivelar habilidades.
  - Checklist de PR obrigatório (tests, lint, doc) para acelerar a revisão e reduzir regressões.
  - Manter e evoluir o Dockerfile e os workflows de CI para criar builds automatizados e artefatos de release reproduzíveis.


## Hugo Cardoso

### Desempenho de time diverso no desenvolvimento colaborativo
- Ficou evidente os mais diversos níveis de proficiência dos integrantes da equipe nos mas diversos assuntos sobre SCM. Apesar dessa diferença de maturidade de cada integrante, houve um esforço muito grande por parte daqueles que tinham mais experiência em auxiliar os que tinham mais dificuldades.
- Essa sinergia colaborativa foi muito produtiva, acelerando o tempo de aprendizado daqueles que tinham mais dúvidas e acelerando o tempo de desenvolvimento do projeto.
- Ainda sobre a diferença de experiências, cada integrante assumiu papeis nos quais se sentiam mais confortáveis. Nos momentos de rotação de resposabilidades a colaboração do time possibilitou que todos pudessem ter experiência nos diferentes papeis em um ambiente de SCM.

### Visão indindividual do processo de desenvolvimento da aplicação
- Mesmo tendo um pouco de experiência em processos de desenvolvimento e SCM, é sempre um novo desafio e uma oportunidade de aprender pontos novos. Em especial, desenvolver uma aplicação com recursos de GUI utilizando containers foi um ponto que não tinha trabalhado e que a solução foi um grande processo de aprendizado.
- O desenvolvimento de ciclos de CI também foi um ponto que possuia pouco conhecimento, e a durante o projeto pude me aprofundar mais no assunto, também verificando a importância de ter estabelecido no projeto um workflow contento testes. Nosso workflow em certo momento foi capaz de identificar uma versão defeituosa, impedindo que propagassemos o erro em branches importantes como o main.
- Como um todo, achei o projeto extremamente proveitoso e de muito aprendisado. Pude complementar conhecimentos de SCM, pondo em pratica todos esses aspectos em um único projeto, melhorando a compreensão geral do processo de desenvolvimento de software de maneira colaborativa com foco em SCM, garantindo controle e qualidade do produto final.

--- 

Fim do documento.

