import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

# Configuração da página
st.set_page_config(
    page_title="Sistema de Gestão",
    page_icon="📊",
    layout="wide"
)

# Função para conectar ao banco de dados
def init_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Inicializar banco de dados
init_db()

# Sidebar para navegação
st.sidebar.title("Navegação")
pagina = st.sidebar.radio(
    "Selecione a página:",
    ["🏠 Página Inicial", "📅 Lista Completa", "⚙️ Configurações"]
)

# Página Inicial
if pagina == "🏠 Página Inicial":
    st.title("🏠 Página Inicial")
    st.write("Bem-vindo ao sistema de gestão!")
    
    # Formulário para adicionar registros
    with st.form("novo_registro"):
        st.subheader("Adicionar Novo Registro")
        nome = st.text_input("Nome do registro:")
        enviar = st.form_submit_button("Adicionar")
        
        if enviar and nome:
            conn = sqlite3.connect('data.db')
            c = conn.cursor()
            c.execute("INSERT INTO registros (nome) VALUES (?)", (nome,))
            conn.commit()
            conn.close()
            st.success(f"Registro '{nome}' adicionado com sucesso!")
            st.rerun()

# Lista Completa
elif pagina == "📅 Lista Completa":
    st.title("📅 Lista Completa de Registros")
    
    # Carregar dados do banco
    conn = sqlite3.connect('data.db')
    df = pd.read_sql_query("SELECT * FROM registros ORDER BY data_criacao DESC", conn)
    conn.close()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        # Estatísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Registros", len(df))
        with col2:
            st.metric("Registro Mais Antigo", df['data_criacao'].min()[:10])
        with col3:
            st.metric("Registro Mais Recente", df['data_criacao'].max()[:10])
            
        # Opção de exportar
        if st.button("📤 Exportar para CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Baixar CSV",
                data=csv,
                file_name=f"registros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("Nenhum registro encontrado. Adicione registros na Página Inicial.")

# Configurações
elif pagina == "⚙️ Configurações":
    st.title("⚙️ Configurações")
    
    st.subheader("Gerenciamento de Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Limpar Todos os Registros", type="secondary"):
            conn = sqlite3.connect('data.db')
            c = conn.cursor()
            c.execute("DELETE FROM registros")
            conn.commit()
            conn.close()
            st.success("Todos os registros foram removidos!")
            st.rerun()
    
    with col2:
        if st.button("🔄 Recriar Banco de Dados", type="secondary"):
            init_db()
            st.success("Banco de dados recriado com sucesso!")
    
    st.subheader("Informações do Sistema")
    st.write(f"**Data e Hora Atual:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    st.write("**Versão do Streamlit:**", st.__version__)
    st.write("**Versão do Pandas:**", pd.__version__)

# Rodapé
st.sidebar.markdown("---")
st.sidebar.info("Sistema desenvolvido com Streamlit")

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)