# Mileage Tracker

## Descrição
O Mileage Tracker é um aplicativo de desktop simples projetado para indivíduos e empresas rastrearem a quilometragem percorrida. Seu objetivo principal é facilitar a prestação de contas (expense reporting) e o reembolso de despesas de viagem.
A ferramenta automatiza o cálculo da distância e permite a exportação de todos os dados para um formato de tabela (.csv).

## Funcionalidades
- Registro de Viagens: Inserção de dados básicos da viagem (endereços, hodômetro, pedágios, estacionamento).
- Cálculo Automático de KM: Utiliza a Google Maps API para calcular a distância entre os endereços.
- Cálculo de Despesas: Consolida o custo total baseado na quilometragem, pedágios e taxas de estacionamento.
- Exportação de Dados: Gera e exporta os dados e cálculos da viagem para um arquivo .csv.

## Executando a aplicação
1. Realize um clone do repositório em sua máquina, ou baixe o arquvo .zip da aplicação
2. No diretório principal da aplicação, crie a imagem Docker da aplicação:
```
docker build -t mileage_app .
```
3. Execução

    1. Execução em ambiente macOS
        Como o container necessita realizar a exibição da GUI no servidor, é necessário garantir a ele o acesso ao X server.
        ```
        xhost +
        docker run -e DISPLAY=host.docker.internal:0 -v /tmp/.X11-unix:/tmp/.X11-unix -it --rm mileage_app
        ```

4. Testes
Os testes da aplicação encontram-se no diretório test. A execução dos casos de testes podem ser realizada executando o seguinte comando dentro do diretório raiz do projeto
```
python3 -m unittest discover -s test
```
