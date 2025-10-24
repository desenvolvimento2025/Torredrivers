import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

# Configuração da página (mantendo layout anterior)
st.set_page_config(
    page_title="Sistema de Gestão",
    page_icon="📊",
    layout="centered"  # Mantendo layout centered como anterior
)

# Função para conectar ao banco de dados
def init_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT,
            telefone TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Inicializar banco de dados
init_db()

# CSS personalizado mantendo estilo anterior
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: bold;
    }
    .section-header {
        font-size: 1.5rem;
        color: #A23B72;
        margin: 1.5rem 0 1rem 0;
        border-bottom: 2px solid #F18F01;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .sidebar-content {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar para navegação (mantendo estilo anterior)
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.title("📱 Navegação")
    pagina = st.radio(
        "Selecione a página:",
        ["🏠 Página Inicial", "📅 Lista Completa", "⚙️ Configurações"],
        key="nav_radio"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Informações adicionais na sidebar
    st.markdown("---")
    st.markdown("**Desenvolvido com:**")
    st.markdown("🐍 Python + Streamlit")
    st.markdown("💾 SQLite Database")

# Página Inicial (mantendo estrutura anterior)
if pagina == "🏠 Página Inicial":
    st.markdown('<div class="main-title">🏠 Página Inicial</div>', unsafe_allow_html=True)
    
    # Cards de métricas no topo
    col1, col2, col3 = st.columns(3)
    
    with col1:
        conn = sqlite3.connect('data.db')
        total_registros = pd.read_sql_query("SELECT COUNT(*) as total FROM registros", conn)['total'][0]
        conn.close()
        st.markdown(f'''
        <div class="metric-card">
            <h3>📊 Total</h3>
            <h2>{total_registros}</h2>
            <p>Registros</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown('''
        <div class="metric-card">
            <h3>🔄 Status</h3>
            <h2>Ativo</h2>
            <p>Sistema Online</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="metric-card">
            <h3>📅 Hoje</h3>
            <h2>{datetime.now().strftime("%d/%m")}</h2>
            <p>{datetime.now().strftime("%Y")}</p>
        </div>
        ''', unsafe_allow_html=True)
    
    # Formulário para adicionar registros
    st.markdown('<div class="section-header">📝 Adicionar Novo Registro</div>', unsafe_allow_html=True)
    
    with st.form("novo_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome Completo*", placeholder="Digite o nome completo")
            email = st.text_input("E-mail", placeholder="exemplo@email.com")
        
        with col2:
            telefone = st.text_input("Telefone", placeholder="(11) 99999-9999")
        
        enviar = st.form_submit_button("💾 Salvar Registro", use_container_width=True)
        
        if enviar:
            if nome:
                conn = sqlite3.connect('data.db')
                c = conn.cursor()
                c.execute(
                    "INSERT INTO registros (nome, email, telefone) VALUES (?, ?, ?)", 
                    (nome, email, telefone)
                )
                conn.commit()
                conn.close()
                st.success(f"✅ Registro '{nome}' adicionado com sucesso!")
            else:
                st.error("❌ Por favor, preencha pelo menos o nome do registro.")

# Lista Completa (mantendo estrutura anterior)
elif pagina == "📅 Lista Completa":
    st.markdown('<div class="main-title">📅 Lista Completa de Registros</div>', unsafe_allow_html=True)
    
    # Carregar dados do banco
    conn = sqlite3.connect('data.db')
    df = pd.read_sql_query("""
        SELECT id, nome, email, telefone, 
               datetime(data_criacao) as data_criacao 
        FROM registros 
        ORDER BY data_criacao DESC
    """, conn)
    conn.close()
    
    if not df.empty:
        # Estatísticas
        st.markdown('<div class="section-header">📈 Estatísticas</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Registros", len(df))
        with col2:
            st.metric("Registros Hoje", len(df[df['data_criacao'].str.startswith(datetime.now().strftime('%Y-%m-%d'))]))
        with col3:
            st.metric("Com E-mail", len(df[df['email'].notna() & (df['email'] != '')]))
        with col4:
            st.metric("Com Telefone", len(df[df['telefone'].notna() & (df['telefone'] != '')]))
        
        # Tabela de registros
        st.markdown('<div class="section-header">📋 Todos os Registros</div>', unsafe_allow_html=True)
        
        # Formatação da tabela
        df_display = df.copy()
        df_display['data_criacao'] = pd.to_datetime(df_display['data_criacao']).dt.strftime('%d/%m/%Y %H:%M')
        df_display = df_display.rename(columns={
            'id': 'ID',
            'nome': 'Nome',
            'email': 'E-mail', 
            'telefone': 'Telefone',
            'data_criacao': 'Data de Criação'
        })
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Opções de exportação
        st.markdown('<div class="section-header">📤 Exportar Dados</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Exportar para CSV", use_container_width=True):
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="⬇️ Baixar CSV",
                    data=csv,
                    file_name=f"registros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with col2:
            if st.button("📊 Exportar para Excel", use_container_width=True):
                excel_buffer = pd.ExcelWriter('temp.xlsx', engine='xlsxwriter')
                df.to_excel(excel_buffer, index=False, sheet_name='Registros')
                excel_buffer.close()
                
                with open('temp.xlsx', 'rb') as f:
                    excel_data = f.read()
                
                st.download_button(
                    label="⬇️ Baixar Excel",
                    data=excel_data,
                    file_name=f"registros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.ms-excel",
                    use_container_width=True
                )
    else:
        st.warning("📭 Nenhum registro encontrado. Vá para a **Página Inicial** para adicionar registros.")

# Configurações (mantendo estrutura anterior)
elif pagina == "⚙️ Configurações":
    st.markdown('<div class="main-title">⚙️ Configurações do Sistema</div>', unsafe_allow_html=True)
    
    # Informações do sistema
    st.markdown('<div class="section-header">ℹ️ Informações do Sistema</div>', unsafe_allow_html=True)
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.info(f"**Data e Hora:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        st.info(f"**Total de Registros:** {total_registros}")
    
    with info_col2:
        st.info(f"**Streamlit:** {st.__version__}")
        st.info(f"**Pandas:** {pd.__version__}")
    
    # Gerenciamento de dados
    st.markdown('<div class="section-header">🗃️ Gerenciamento de Dados</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Limpar Todos os Registros", use_container_width=True, type="secondary"):
            with st.expander("Confirmação Necessária"):
                st.warning("⚠️ **ATENÇÃO:** Esta ação não pode ser desfeita!")
                if st.button("✅ Confirmar Limpeza Total", type="primary"):
                    conn = sqlite3.connect('data.db')
                    c = conn.cursor()
                    c.execute("DELETE FROM registros")
                    conn.commit()
                    conn.close()
                    st.success("✅ Todos os registros foram removidos!")
                    st.rerun()
    
    with col2:
        if st.button("🔄 Recriar Banco de Dados", use_container_width=True, type="secondary"):
            init_db()
            st.success("✅ Banco de dados recriado com sucesso!")
    
    # Backup e restauração
    st.markdown('<div class="section-header">💾 Backup dos Dados</div>', unsafe_allow_html=True)
    
    if st.button("📦 Fazer Backup dos Dados", use_container_width=True):
        conn = sqlite3.connect('data.db')
        df_backup = pd.read_sql_query("SELECT * FROM registros", conn)
        conn.close()
        
        backup_csv = df_backup.to_csv(index=False)
        st.download_button(
            label="⬇️ Baixar Backup (CSV)",
            data=backup_csv,
            file_name=f"backup_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# Rodapé fixo
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
    "Sistema desenvolvido com ❤️ usando Streamlit | "
    f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    "</div>", 
    unsafe_allow_html=True
)