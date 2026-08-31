# Calculadora de Renda Fixa

## Descrição

Ferramenta simples para cálculo de fluxos de renda fixa, com suporte a operações básicas:

- Valor presente
- Valor futuro
- TIR
- Duration de Macaulay
- Taxa a partir de preço
- Preço a partir de taxa
- Cálculo de spread
- Customização da taxa de juros ao longo do tempo
- Customização da correção monetária ao longo do tempo
- Memória de cálculo
- Regras de arredondamento cálculo
- Visualização do fluxo de caixa
- Cálculo de dias úteis e dias corridos
- Lista de feriados


## Projeto

O projeto é separado em três partes:
- Motor de cálculo
- API HTTP
- Interface gráfica

### Motor de cálculo
O motor de cálculo é implementado em Python. Você poderá interagir com ele de três formas:
- Caso você use Python, você poderá importá-lo como biblioteca do seu projeto;
- Caso você use outra linguagem de programação, poderá acessar a API HTTP;
- Caso você queira interagir com o projeto, deverá executar a interface gráfica.

### API HTTP
A API é implementada utilizando FastAPI e é uma fina camada de tradução da ferramenta. Ela é idempotente e não possui persistência de dados.

### Interface gráfica
A interface gráfica busca explorar o máximo da ferramenta, sem focar em casos de usos específicos. Sua implementação foi feita em Svelte e possui uma fina camada de armazenamento do lado do cliente para melhor experiência do usuário.


## Executando o projeto
Para maior facilidade, o projeto foi condensado em um arquivo `docker-compose.yml`.

