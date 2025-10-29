# =============================================================================
# NOVA SEÇÃO: GERENCIADOR DE ARQUIVOS HTML
# =============================================================================

import os
import shutil
from pathlib import Path

# Configuração da pasta de arquivos HTML
PASTA_HTML = "arquivos_html"

# Garantir que a pasta existe
def garantir_pasta_html():
    """Cria a pasta para arquivos HTML se não existir"""
    if not os.path.exists(PASTA_HTML):
        os.makedirs(PASTA_HTML)
    return PASTA_HTML

# Classe para gerenciar arquivos HTML
class GerenciadorHTML:
    def __init__(self):
        self.pasta_html = garantir_pasta_html()
        self.arquivos_html = []
        self.carregar_arquivos()
    
    def carregar_arquivos(self):
        """Carrega a lista de arquivos HTML disponíveis"""
        try:
            arquivos = os.listdir(self.pasta_html)
            self.arquivos_html = [f for f in arquivos if f.lower().endswith('.html')]
            return self.arquivos_html
        except Exception as e:
            st.error(f"Erro ao carregar arquivos HTML: {e}")
            return []
    
    def limpar_pasta(self):
        """Remove todos os arquivos da pasta HTML"""
        try:
            for arquivo in os.listdir(self.pasta_html):
                caminho_arquivo = os.path.join(self.pasta_html, arquivo)
                if os.path.isfile(caminho_arquivo):
                    os.remove(caminho_arquivo)
            self.arquivos_html = []
            return True
        except Exception as e:
            st.error(f"Erro ao limpar pasta HTML: {e}")
            return False
    
    def importar_html(self, arquivo_upload):
        """Importa um arquivo HTML para a pasta"""
        try:
            # Limpa a pasta antes de importar (conforme solicitado)
            self.limpar_pasta()
            
            # Salva o novo arquivo
            caminho_destino = os.path.join(self.pasta_html, arquivo_upload.name)
            
            with open(caminho_destino, "wb") as f:
                f.write(arquivo_upload.getbuffer())
            
            # Atualiza a lista de arquivos
            self.carregar_arquivos()
            return True
        except Exception as e:
            st.error(f"Erro ao importar arquivo HTML: {e}")
            return False
    
    def obter_conteudo_html(self, nome_arquivo):
        """Obtém o conteúdo de um arquivo HTML"""
        try:
            caminho_arquivo = os.path.join(self.pasta_html, nome_arquivo)
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            st.error(f"Erro ao ler arquivo HTML: {e}")
            return None

# Inicialização do gerenciador HTML
@st.cache_resource
def get_gerenciador_html():
    return GerenciadorHTML()

gerenciador_html = get_gerenciador_html()

# =============================================================================
# ADICIONAR NOVA OPÇÃO NO MENU (na seção do sidebar)
# =============================================================================

# No código existente, modificar a variável 'pagina' no sidebar para incluir:
pagina = st.sidebar.selectbox(
    "Navegação",
    ["📊 Dashboard", "👥 Cadastrar Motorista", "📤 Importar Excel", "✏️ Editar Motorista", "🗑️ Excluir Motorista", "📋 Lista Completa", 
     "🏢 Cadastrar Cliente", "✏️ Editar Cliente", "🗑️ Excluir Cliente", "📋 Lista de Clientes",
     "🌐 Gerenciar HTML"]  # NOVA OPÇÃO ADICIONADA
)

# =============================================================================
# PÁGINA: GERENCIAR HTML
# =============================================================================

elif pagina == "🌐 Gerenciar HTML":
    st.title("🌐 Gerenciador de Arquivos HTML")
    
    # Criar abas para organização
    tab1, tab2, tab3 = st.tabs(["📤 Importar HTML", "📁 Arquivos Disponíveis", "👁️ Visualizar HTML"])
    
    with tab1:
        st.subheader("📤 Importar Arquivo HTML")
        
        st.markdown("""
        ### Instruções para Importação:
        - **Formato suportado**: .html
        - **Limpeza automática**: Todos os arquivos anteriores serão removidos
        - **Visualização**: Clique no arquivo na aba "Arquivos Disponíveis" para visualizar
        """)
        
        # Upload do arquivo HTML
        arquivo_html = st.file_uploader(
            "Selecione o arquivo HTML para importar",
            type=['html'],
            help="Arquivo HTML para importação"
        )
        
        if arquivo_html is not None:
            # Mostrar informações do arquivo
            st.info(f"**Arquivo selecionado:** {arquivo_html.name}")
            st.info(f"**Tamanho:** {arquivo_html.size} bytes")
            
            # Botão para importar
            if st.button("🚀 Importar Arquivo HTML", type="primary"):
                with st.spinner("Importando arquivo HTML..."):
                    if gerenciador_html.importar_html(arquivo_html):
                        st.success("✅ Arquivo HTML importado com sucesso!")
                        st.balloons()
                        
                        # Mostrar estatísticas
                        st.subheader("📊 Estatísticas da Importação")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Arquivos na Pasta", len(gerenciador_html.arquivos_html))
                        
                        with col2:
                            st.metric("Arquivo Importado", arquivo_html.name)
                    else:
                        st.error("❌ Erro ao importar arquivo HTML")
    
    with tab2:
        st.subheader("📁 Arquivos HTML Disponíveis")
        
        # Atualizar lista de arquivos
        gerenciador_html.carregar_arquivos()
        
        if gerenciador_html.arquivos_html:
            st.success(f"✅ {len(gerenciador_html.arquivos_html)} arquivo(s) HTML encontrado(s)")
            
            # Lista de arquivos com opção para visualizar
            for i, arquivo in enumerate(gerenciador_html.arquivos_html):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**{i+1}. {arquivo}**")
                
                with col2:
                    # Botão para visualizar
                    if st.button(f"👁️ Visualizar", key=f"view_{i}"):
                        st.session_state.arquivo_selecionado = arquivo
                        st.rerun()
                
                with col3:
                    # Botão para excluir arquivo individual
                    if st.button(f"🗑️ Excluir", key=f"delete_{i}"):
                        caminho_arquivo = os.path.join(gerenciador_html.pasta_html, arquivo)
                        try:
                            os.remove(caminho_arquivo)
                            st.success(f"✅ Arquivo {arquivo} excluído com sucesso!")
                            gerenciador_html.carregar_arquivos()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erro ao excluir arquivo: {e}")
            
            # Botão para limpar toda a pasta
            st.markdown("---")
            st.warning("⚠️ **Atenção:** Esta ação não pode ser desfeita!")
            
            if st.button("🗑️ Limpar Toda a Pasta HTML", type="secondary"):
                if gerenciador_html.limpar_pasta():
                    st.success("✅ Pasta HTML limpa com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao limpar pasta HTML")
        
        else:
            st.info("📭 Nenhum arquivo HTML encontrado na pasta.")
            st.info("Use a aba 'Importar HTML' para adicionar arquivos.")
    
    with tab3:
        st.subheader("👁️ Visualizar Arquivo HTML")
        
        # Verificar se há arquivo selecionado para visualização
        if 'arquivo_selecionado' in st.session_state and st.session_state.arquivo_selecionado:
            arquivo_selecionado = st.session_state.arquivo_selecionado
            
            st.success(f"Visualizando: **{arquivo_selecionado}**")
            
            # Obter conteúdo do arquivo
            conteudo_html = gerenciador_html.obter_conteudo_html(arquivo_selecionado)
            
            if conteudo_html:
                # Opções de visualização
                modo_visualizacao = st.radio(
                    "Modo de visualização:",
                    ["Visualização Direta", "Código Fonte"],
                    horizontal=True
                )
                
                if modo_visualizacao == "Visualização Direta":
                    # Renderizar o HTML diretamente
                    st.components.v1.html(conteudo_html, height=600, scrolling=True)
                
                else:  # Código Fonte
                    # Mostrar o código fonte
                    st.code(conteudo_html, language='html')
                
                # Botões de ação
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📥 Download HTML"):
                        # Criar download do arquivo
                        st.download_button(
                            label="💾 Baixar Arquivo HTML",
                            data=conteudo_html,
                            file_name=arquivo_selecionado,
                            mime="text/html"
                        )
                
                with col2:
                    if st.button("🔄 Voltar para Lista"):
                        del st.session_state.arquivo_selecionado
                        st.rerun()
            
            else:
                st.error("❌ Não foi possível carregar o conteúdo do arquivo HTML")
                if st.button("🔄 Tentar Novamente"):
                    st.rerun()
        
        else:
            st.info("ℹ️ Selecione um arquivo HTML na aba 'Arquivos Disponíveis' para visualizar.")
            
            # Mostrar lista rápida de arquivos disponíveis
            if gerenciador_html.arquivos_html:
                st.write("**Arquivos disponíveis para visualização:**")
                for arquivo in gerenciador_html.arquivos_html:
                    if st.button(f"👁️ Visualizar {arquivo}", key=f"quick_view_{arquivo}"):
                        st.session_state.arquivo_selecionado = arquivo
                        st.rerun()

# =============================================================================
# ATUALIZAR A BARRA LATERAL COM INFORMAÇÕES DE HTML
# =============================================================================

# Adicionar informações sobre arquivos HTML no sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("🌐 Arquivos HTML")

if gerenciador_html.arquivos_html:
    st.sidebar.success(f"📁 {len(gerenciador_html.arquivos_html)} arquivo(s) HTML")
    for arquivo in gerenciador_html.arquivos_html:
        st.sidebar.write(f"• {arquivo}")
else:
    st.sidebar.info("📭 Nenhum arquivo HTML")

# Botão rápido para acessar o gerenciador HTML
if st.sidebar.button("🌐 Gerenciar Arquivos HTML"):
    st.session_state.pagina = "🌐 Gerenciar HTML"
    st.rerun()