import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Função Cálculo Força Matriz e Força Reforço
def calcular_forcas(E_matriz, E_reforco, vol_matriz, vol_reforco, area, tensao):
    F_total = area * tensao
    F_matriz = F_total * (E_matriz * vol_matriz) / (E_matriz * vol_matriz + E_reforco * vol_reforco)
    F_reforco = F_total * (E_reforco * vol_reforco) / (E_matriz * vol_matriz + E_reforco * vol_reforco)
    return F_matriz, F_reforco, F_total

# Função para converter módulo de elasticidade
def converter_modulo_elasticidade(modulo, unidade_modulo):
    if unidade_modulo == "N/m²":
        return modulo * 1e9  # Converter GPa para N/m²
    elif unidade_modulo == "Psi":
        return modulo / 0.00000689476  # Converter GPa para Psi
    else:
        return modulo  # GPa (sem conversão)

# Função para converter tensão e área (para N e kgf)
def converter_unidades(tensao_input, unidade_tensao, area_input, unidade_area):
    if unidade_tensao == "kgf":
        tensao = tensao_input * 9.80665  # Converter kgf para N
    else:
        tensao = tensao_input  # N

    if unidade_area == "cm²":
        area = area_input / 10000  # cm² para m²
    elif unidade_area == "mm²":
        area = area_input / 1e6  # mm² para m²
    else:
        area = area_input  # m²

    return tensao, area

# Carregar a base de dados de materiais
df_materiais = pd.read_csv('materiais.csv')

# Interface Streamlit
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    h1 {
        text-align: center;
        font-size: 30px;
    }
    .custom-box {
        background-color: #4CAF50; 
        padding: 20px; 
        border-radius: 10px; 
        color: white; 
    }
    .entry-box {
        background-color: #2196F3; 
        padding: 20px; 
        border-radius: 10px; 
        color: white; 
    }
    .results-box {
        display: inline-block; 
        background-color: #FF5733; 
        color: white; 
        padding: 10px 20px; 
        text-align: center; 
        border-radius: 5px; 
        font-size: 16px; 
        margin: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Título centralizado
st.title("Cálculo de Forças em Materiais para Usinas Eólicas e Solares")
st.subheader(" ")

# Layout dividido em duas colunas
col1, col2 = st.columns(2)

# Controle de sessão para armazenar resultados
if 'results' not in st.session_state:
    st.session_state.results = None

with col1:
    st.markdown("<div class='custom-box'><h4>Materiais Compósitos</h4>", unsafe_allow_html=True)


    # Filtrar materiais por tipo
    materiais_matriz = df_materiais[df_materiais['tipo'] == 'Matriz']['nome']
    materiais_reforco = df_materiais[df_materiais['tipo'] == 'Reforço']['nome']
    
    # Seleção dos materiais
    material_matriz = st.selectbox("Material da Matriz", materiais_matriz)
    material_reforco = st.selectbox("Material do Reforço", materiais_reforco)
    
    # Filtrar os dados dos materiais selecionados
    dados_matriz = df_materiais[df_materiais['nome'] == material_matriz].iloc[0]
    dados_reforco = df_materiais[df_materiais['nome'] == material_reforco].iloc[0]
    
    # Seleção da unidade do módulo de elasticidade
    unidade_modulo = st.selectbox("Unidade do Módulo de Elasticidade", ["GPa", "N/m²", "Psi"])
    
    # Converter o módulo de elasticidade para a unidade selecionada
    modulo_matriz_convertido = converter_modulo_elasticidade(dados_matriz['modulo_elasticidade'], unidade_modulo)
    modulo_reforco_convertido = converter_modulo_elasticidade(dados_reforco['modulo_elasticidade'], unidade_modulo)
    
    # Mostrar as propriedades dos materiais selecionados com o módulo de elasticidade convertido
    st.write(f"**Matriz**: {material_matriz} (Módulo de Elasticidade: {modulo_matriz_convertido:.2f} {unidade_modulo})")
    st.write(f"**Reforço**: {material_reforco} (Módulo de Elasticidade: {modulo_reforco_convertido:.2f} {unidade_modulo})")
    
    # Entrada de frações volumétricas
    colA, colB = st.columns(2)
    with colA:
        vol_matriz = st.number_input("Volume Matriz", min_value=0.0, max_value=1.0, value=0.5)
    with colB:
        vol_reforco = st.number_input("Volume Reforço", min_value=0.0, max_value=1.0, value=0.5)
        
    # Calcular a soma dos volumes
    soma_volumes = vol_matriz + vol_reforco

    st.markdown("</div>", unsafe_allow_html=True)
    
 

with col2:
    st.markdown("<div class='entry-box'><h4>Entrada de Dados</h4>", unsafe_allow_html=True)


    # Seleção das unidades de tensão e área
    colA, colB = st.columns(2)
    with colA:
        unidade_tensao = st.selectbox("Unidade da Tensão", ["N", "kgf"])
        tensao_input = st.number_input(f"Tensão Aplicada ({unidade_tensao})", min_value=0.0, value=100.0)
    with colB:
        unidade_area = st.selectbox("Unidade da Área", ["m²", "cm²", "mm²"])
        area_input = st.number_input(f"Área ({unidade_area})", min_value=0.0, value=1.0)
    
    df = pd.DataFrame({
        'Composição (%)': [vol_matriz * 100, vol_reforco * 100]  # Multiplica por 100 para exibir em porcentagem
    }, index=['Matriz', 'Reforço'])

    # Mostrar o gráfico de barra horizontal
    st.bar_chart(df)

    st.markdown("</div>", unsafe_allow_html=True)


# Converter as entradas de tensão e área
tensao, area = converter_unidades(tensao_input, unidade_tensao, area_input, unidade_area)

# Botão Apagar

if st.button("Apagar"):
    st.session_state.results = None  # Limpar resultados
    
# Botão Calcular
if st.button("Calcular"):
    E_matriz = converter_modulo_elasticidade(dados_matriz['modulo_elasticidade'], unidade_modulo)
    E_reforco = converter_modulo_elasticidade(dados_reforco['modulo_elasticidade'], unidade_modulo)

    F_matriz, F_reforco, F_total = calcular_forcas(E_matriz, E_reforco, vol_matriz, vol_reforco, area, tensao)
        
        # Exibir os resultados em colunas
    colA, colB, colC = st.columns(3)
    with colA:
        colA.markdown(f"""
            <div class="results-box">
                <b>Força Total:</b> {F_total:.2f} N
            </div>
        """, unsafe_allow_html=True)

    with colB:
        colB.markdown(f"""
            <div class="results-box">
                <b>Força na Matriz:</b> {F_matriz:.2f} N
            </div>
        """, unsafe_allow_html=True)

    with colC:
        colC.markdown(f"""
            <div class="results-box">
                <b>Força no Reforço:</b> {F_reforco:.2f} N
            </div>
        """, unsafe_allow_html=True)
