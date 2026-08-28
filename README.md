# Simulador de Renda Fixa

Aplicativo em Python + Streamlit para estimar quanto uma aplicação pode acumular
ao longo do tempo usando juros compostos.

## O que o app calcula

- Valor inicial da aplicação;
- Aportes mensais opcionais;
- Período de 1 a 360 meses;
- Taxa mensal ou taxa anual efetiva;
- Aportes no início ou no fim de cada mês;
- Montante final, total investido e juros acumulados;
- Gráfico de evolução mês a mês;
- Tabela completa da memória de cálculo;
- Download da projeção em CSV;
- Download do código completo em um arquivo ZIP dentro do próprio app.

## Como executar

1. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

2. Inicie o aplicativo:

   ```bash
   streamlit run app.py
   ```

3. Abra o endereço exibido no terminal.

## Observações

Esta é uma simulação matemática e não uma recomendação de investimento. Ela não
considera inflação, Imposto de Renda, IOF, taxas de administração, custos da
instituição ou variações na rentabilidade do produto. Confirme as condições da
aplicação antes de tomar uma decisão financeira.