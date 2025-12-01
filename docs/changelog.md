# CHANGELOG

Todos os itens seguem o padrão "Keep a Changelog" (https://keepachangelog.com/pt-BR/).
Versões são gerenciadas por SemVer: `vMAJOR.MINOR.PATCH`.

## [Unreleased]
- Preparar próxima release: incluir pequenas correções e testes adicionais.

---

## [v1.2.1] - 2025-11-30
### Adicionado
- Relatório de despesas: lógica para calcular e consolidar despesas (quilometragem, pedágios, estacionamento) e exibição de resumo na interface.

### Alterado
- Atualização de testes unitários relacionados à Calculadora de Despesas para validar a nova lógica.

### Corrigido
- Hotfix no cálculo das despesas para corrigir arredondamento/validação incorreta.

Arquivos principais afetados: app/app.py, test/test.py, requirements.txt

---

## [v1.1.0] - 2025-11-29
### Adicionado
- Integração opcional com Google Maps Routes API (computeRoutes) para cálculo automático de distância.
- Suíte de testes para a integração com a API (casos: sucesso, chave ausente, erro HTTP, ausência de rotas).
- Dependências: inclusão de `requests` e `python-dotenv`.

### Alterado
- Leitura de configuração via python-dotenv (facilita definição da chave da API).
- Documentação: README e docs com instruções para configuração da Google Maps API e uso de .env.

---

## [v1.0.0] - 2025-11-25
### Adicionado
- Registro de Viagens: formulário para inserção de dados (endereços, hodômetro, pedágios, estacionamento) e persistência em CSV.
- Teste de smoke que escreve e valida CSV de registros de viagem.
- Dockerfile inicial e documentação de execução via Docker.
- Workflows iniciais de CI para execução de testes/builds.

### Alterado
- README: instruções detalhadas para execução em Linux/macOS/Windows e uso de volumes para persistência.

### Corrigido
- Ajustes para execução de testes em ambientes headless (xvfb/xhost) e correções de integração com Docker no CI.

---

