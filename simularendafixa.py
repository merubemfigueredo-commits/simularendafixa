from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Reserva em juros compostos",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


def brl(value: float) -> str:
    """Format a number as Brazilian currency."""
    formatted = f"R$ {value:,.2f}"
    return formatted.replace(",", "_").replace(".", ",").replace("_", ".")


def percent(value: float) -> str:
    """Format a percentage using the Brazilian decimal separator."""
    return f"{value:.2f}%".replace(".", ",")


def monthly_rate_from_annual(annual_rate: float) -> float:
    """Convert an effective annual rate to its equivalent monthly rate."""
    return (1 + annual_rate / 100) ** (1 / 12) - 1


def build_projection(
    initial_amount: float,
    monthly_contribution: float,
    months: int,
    monthly_rate: float,
    contribution_timing: str,
) -> pd.DataFrame:
    """Build the monthly compound-interest projection."""
    balance = initial_amount
    rows = [
        {
            "Mês": 0,
            "Aporte no mês": 0.0,
            "Juros no mês": 0.0,
            "Total investido": initial_amount,
            "Juros acumulados": 0.0,
            "Montante": initial_amount,
        }
    ]

    for month in range(1, months + 1):
        if contribution_timing == "No início do mês":
            balance += monthly_contribution
            interest = balance * monthly_rate
            balance += interest
        else:
            interest = balance * monthly_rate
            balance += interest + monthly_contribution

        total_invested = initial_amount + monthly_contribution * month
        rows.append(
            {
                "Mês": month,
                "Aporte no mês": monthly_contribution,
                "Juros no mês": interest,
                "Total investido": total_invested,
                "Juros acumulados": balance - total_invested,
                "Montante": balance,
            }
        )

    return pd.DataFrame(rows)


def csv_bytes(projection: pd.DataFrame) -> bytes:
    return projection.to_csv(index=False).encode("utf-8-sig")

#def source_zip_bytes() -> bytes:
    """Package the source files so the user can download the complete app."""
#    project_root = Path(__file__).resolve().parent
#    files_to_include = [
#        Path("app.py"),
#       Path("requirements.txt"),
#        Path("README.md"),
#        Path(".streamlit/config.toml"),
#    ]
#    buffer = io.BytesIO()
#    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
#        for relative_path in files_to_include:
#            file_path = project_root / relative_path
#            if file_path.exists():
#                archive.write(file_path, arcname=relative_path.as_posix())
#    return buffer.getvalue()


st.title("Quanto sua reserva pode crescer?")
st.write(
    "Simule uma aplicação em renda fixa com juros compostos e acompanhe a evolução "
    "do seu patrimônio mês a mês."
)

with st.sidebar:
    st.header("Parâmetros da simulação")
    initial_amount = st.number_input(
        "Valor inicial",
        min_value=0.0,
        value=1_000.0,
        step=100.0,
        format="%.2f",
        help="Valor aplicado no primeiro dia da simulação.",
    )
    monthly_contribution = st.number_input(
        "Aporte mensal",
        min_value=0.0,
        value=500.0,
        step=50.0,
        format="%.2f",
        help="Deixe em zero para simular apenas a aplicação inicial.",
    )
    months = st.slider(
        "Período (meses)",
        min_value=1,
        max_value=360,
        value=24,
        help="Escolha de 1 mês a 30 anos.",
    )
    rate_type = st.radio(
        "Como informar a taxa?",
        options=["Mensal", "Anual efetiva"],
        horizontal=True,
    )
    rate = st.number_input(
        f"Taxa {rate_type.lower()} (%)",
        min_value=0.0,
        value=0.8 if rate_type == "Mensal" else 10.0,
        step=0.1,
        format="%.2f",
        help="Use uma taxa positiva. Esta simulação não considera impostos, inflação ou taxas da instituição.",
    )
    contribution_timing = st.selectbox(
        "Quando o aporte mensal acontece?",
        options=["No início do mês", "No fim do mês"],
        help="Aportes no início do mês passam a render já naquele mês.",
    )

monthly_rate = rate / 100 if rate_type == "Mensal" else monthly_rate_from_annual(rate)
projection = build_projection(
    initial_amount=initial_amount,
    monthly_contribution=monthly_contribution,
    months=months,
    monthly_rate=monthly_rate,
    contribution_timing=contribution_timing,
)
final_row = projection.iloc[-1]
total_invested = float(final_row["Total investido"])
final_amount = float(final_row["Montante"])
total_interest = float(final_row["Juros acumulados"])

metric_1, metric_2, metric_3 = st.columns(3)
metric_1.metric("Montante final", brl(final_amount))
metric_2.metric("Total investido", brl(total_invested))
metric_3.metric("Juros acumulados", brl(total_interest))

st.caption(
    f"Taxa equivalente usada no cálculo: {percent(monthly_rate * 100)} ao mês · "
    f"Período: {months} meses"
)

chart_data = projection.set_index("Mês")[["Total investido", "Montante"]]
st.subheader("Evolução da sua aplicação")
st.line_chart(chart_data, y_label="Valor (R$)", x_label="Mês", height=420)

left, right = st.columns([1.4, 1])
with left:
    st.subheader("Memória de cálculo")
    display_projection = projection.copy()
    currency_columns = [
        "Aporte no mês",
        "Juros no mês",
        "Total investido",
        "Juros acumulados",
        "Montante",
    ]
    st.dataframe(
        display_projection.style.format(
            {column: "R$ {:,.2f}" for column in currency_columns}
        ),
        use_container_width=True,
        hide_index=True,
        height=480,
    )

with right:
    st.subheader("Baixe seus dados")
    st.download_button(
        label="Baixar projeção em CSV",
        data=csv_bytes(projection),
        file_name="projecao-renda-fixa.csv",
        mime="text/csv",
        width="stretch",
    )
    #st.download_button(
    #    label="Baixar código completo (.zip)",
    #    data=source_zip_bytes(),
    #   file_name="simulador-renda-fixa-streamlit.zip",
    #   mime="application/zip",
    #    width="stretch",
    #)
    st.info(
        "A simulação usa juros compostos e serve como estimativa. "
        "Confira a rentabilidade, liquidez, impostos e taxas do produto escolhido "
        "antes de investir."
    )

st.divider()
st.caption(
    "Fórmula-base: saldo do mês = saldo anterior + aporte + juros do período. "
    "Os juros incidem sobre o saldo disponível conforme o momento do aporte."
)
