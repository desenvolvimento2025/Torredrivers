import streamlit as st
import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime, timedelta
import time
import io
import base64
import shutil
from pathlib import Path

# Configuração da página
st.set_page_config(
    page_title="Sistema de Motoristas",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"  # Sidebar colapsado por padrão
)

# ESTRUTURA ATUALIZADA COM NOMES EXATOS DO TEMPLATE
ESTRUTURA_COLUNAS = [
    'nome', 'usuario', 'grupo', 'empresa', 'filial', 'status', 
    'disponibilidade', 'ferias', 'licenca', 'folga', 'sobreaviso', 'atestado',
    'com-atend', 'com-veiculo', 'com-check', 'dirigindo', 
    'parado-ate1h', 'parado1ate2h', 'parado-acima2h', 
    'jornada-acm80', 'jornada-exced', 'sem-folga-acm7d', 'sem-folga-acm12d',
    'categoria', 'doc-vencendo', 'doc-vencido', 'localiz-atual', 
    'associacao-clientes', 'interj-menor8', 'interj-maior8',
    'placa1', 'placa2', 'placa3'
]

COLUNAS_PRINCIPAIS = [
    'nome', 'usuario', 'grupo', 'empresa', 'filial', 'status', 
    'categoria', 'placa1', 'placa2', 'placa3', 'localiz-atual',
    'disponibilidade', 'com-veiculo'
]

# ESTRUTURA DA TABELA CLIENTES
ESTRUTURA_CLIENTES = [
    'cliente', 'nome', 'usuario', 'empresa', 'filial', 'status'
]

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

# Classe para gerenciamento de dados
class GerenciadorMotoristas:
    def __init__(self):
        self.arquivo_excel = "tabela-motoristas.xlsx"
        self.ultima_atualizacao = None
        self.dados = None
        self.dados_clientes = None
        
    def carregar_dados(self):
        """Carrega dados do arquivo Excel"""
        try:
            if os.path.exists(self.arquivo_excel):
                # Carrega dados dos motoristas
                self.dados = pd.read_excel(self.arquivo_excel, sheet_name='motoristas')
                # Garante que todas as colunas existam na ordem correta
                for coluna in ESTRUTURA_COLUNAS:
                    if coluna not in self.dados.columns:
                        self.dados[coluna] = ""
                # Reordena as colunas conforme a estrutura
                self.dados = self.dados[ESTRUTURA_COLUNAS]
                
                # Carrega dados dos clientes
                try:
                    self.dados_clientes = pd.read_excel(self.arquivo_excel, sheet_name='clientes')
                    # Garante que todas as colunas existam na ordem correta
                    for coluna in ESTRUTURA_CLIENTES:
                        if coluna not in self.dados_clientes.columns:
                            self.dados_clientes[coluna] = ""
                    self.dados_clientes = self.dados_clientes[ESTRUTURA_CLIENTES]
                except:
                    # Cria dataframe vazio para clientes se não existir
                    self.dados_clientes = pd.DataFrame(columns=ESTRUTURA_CLIENTES)
                
                self.ultima_atualizacao = datetime.now()
                return True
            else:
                # Cria dataframe vazio com a estrutura exata
                self.dados = pd.DataFrame(columns=ESTRUTURA_COLUNAS)
                self.dados_clientes = pd.DataFrame(columns=ESTRUTURA_CLIENTES)
                self.salvar_dados()
                return True
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
            return False
    
    def salvar_dados(self):
        """Salva dados no arquivo Excel mantendo a estrutura"""
        try:
            # Garante a ordem correta das colunas para motoristas
            if self.dados is not None and not self.dados.empty:
                for coluna in ESTRUTURA_COLUNAS:
                    if coluna not in self.dados.columns:
                        self.dados[coluna] = ""
                self.dados = self.dados[ESTRUTURA_COLUNAS]
            else:
                self.dados = pd.DataFrame(columns=ESTRUTURA_COLUNAS)
            
            # Garante a ordem correta das colunas para clientes
            if self.dados_clientes is not None and not self.dados_clientes.empty:
                for coluna in ESTRUTURA_CLIENTES:
                    if coluna not in self.dados_clientes.columns:
                        self.dados_clientes[coluna] = ""
                self.dados_clientes = self.dados_clientes[ESTRUTURA_CLIENTES]
            else:
                self.dados_clientes = pd.DataFrame(columns=ESTRUTURA_CLIENTES)
            
            with pd.ExcelWriter(self.arquivo_excel, engine='openpyxl') as writer:
                self.dados.to_excel(writer, sheet_name='motoristas', index=False)
                self.dados_clientes.to_excel(writer, sheet_name='clientes', index=False)
                # Cria sheet de logs vazia
                pd.DataFrame().to_excel(writer, sheet_name='logs', index=False)
            return True
        except Exception as e:
            st.error(f"Erro ao salvar dados: {e}")
            return False
    
    def adicionar_motorista(self, dados_motorista):
        """Adiciona novo motorista com estrutura completa"""
        try:
            # Garante que todos os campos da estrutura existam
            dados_completos = {}
            for coluna in ESTRUTURA_COLUNAS:
                dados_completos[coluna] = dados_motorista.get(coluna, "")
            
            novo_registro = pd.DataFrame([dados_completos])
            if self.dados is None:
                self.dados = pd.DataFrame(columns=ESTRUTURA_COLUNAS)
            self.dados = pd.concat([self.dados, novo_registro], ignore_index=True)
            return self.salvar_dados()
        except Exception as e:
            st.error(f"Erro ao adicionar motorista: {e}")
            return False
    
    def atualizar_motorista(self, index, dados_motorista):
        """Atualiza motorista existente"""
        try:
            for coluna, valor in dados_motorista.items():
                if coluna in self.dados.columns:
                    self.dados.at[index, coluna] = valor
            return self.salvar_dados()
        except Exception as e:
            st.error(f"Erro ao atualizar motorista: {e}")
            return False
    
    def excluir_motorista(self, index):
        """Exclui motorista"""
        try:
            self.dados = self.dados.drop(index).reset_index(drop=True)
            return self.salvar_dados()
        except Exception as e:
            st.error(f"Erro ao excluir motorista: {e}")
            return False
    
    def importar_excel(self, arquivo):
        """Importa dados de arquivo Excel mantendo estrutura"""
        try:
            # Lê o arquivo Excel
            dados_importados = pd.read_excel(arquivo)
            
            # Verifica se as colunas necessárias existem
            colunas_necessarias = ['nome', 'usuario', 'empresa']
            colunas_faltantes = [col for col in colunas_necessarias if col not in dados_importados.columns]
            
            if colunas_faltantes:
                st.error(f"Colunas obrigatórias faltantes: {', '.join(colunas_faltantes)}")
                return False
            
            # Adiciona colunas faltantes da estrutura completa
            for coluna in ESTRUTURA_COLUNAS:
                if coluna not in dados_importados.columns:
                    dados_importados[coluna] = ""
            
            # Mantém apenas as colunas da estrutura definida na ordem correta
            dados_importados = dados_importados[ESTRUTURA_COLUNAS]
            
            # Remove duplicatas baseado no nome e usuário
            dados_importados = dados_importados.drop_duplicates(subset=['nome', 'usuario'], keep='last')
            
            # Se já existem dados, faz merge
            if self.dados is not None and not self.dados.empty:
                # Remove registros existentes com mesmo nome e usuário
                mask = ~self.dados[['nome', 'usuario']].apply(tuple, 1).isin(
                    dados_importados[['nome', 'usuario']].apply(tuple, 1)
                )
                self.dados = self.dados[mask]
                
                # Adiciona novos dados
                self.dados = pd.concat([self.dados, dados_importados], ignore_index=True)
            else:
                self.dados = dados_importados
            
            return self.salvar_dados()
            
        except Exception as e:
            st.error(f"Erro ao importar arquivo Excel: {e}")
            return False

    # MÉTODOS PARA CLIENTES
    def adicionar_cliente(self, dados_cliente):
        """Adiciona novo cliente"""
        try:
            # Garante que todos os campos da estrutura existam
            dados_completos = {}
            for coluna in ESTRUTURA_CLIENTES:
                dados_completos[coluna] = dados_cliente.get(coluna, "")
            
            novo_registro = pd.DataFrame([dados_completos])
            if self.dados_clientes is None:
                self.dados_clientes = pd.DataFrame(columns=ESTRUTURA_CLIENTES)
            self.dados_clientes = pd.concat([self.dados_clientes, novo_registro], ignore_index=True)
            return self.salvar_dados()
        except Exception as e:
            st.error(f"Erro ao adicionar cliente: {e}")
            return False
    
    def atualizar_cliente(self, index, dados_cliente):
        """Atualiza cliente existente"""
        try:
            for coluna, valor in dados_cliente.items():
                if coluna in self.dados_clientes.columns:
                    self.dados_clientes.at[index, coluna] = valor
            return self.salvar_dados()
        except Exception as e:
            st.error(f"Erro ao atualizar cliente: {e}")
            return False
    
    def excluir_cliente(self, index):
        """Exclui cliente"""
        try:
            self.dados_clientes = self.dados_clientes.drop(index).reset_index(drop=True)
            return self.salvar_dados()
        except Exception as e:
            st.error(f"Erro ao excluir cliente: {e}")
            return False

    def tem_dados_clientes(self):
        """Verifica se existem dados de clientes"""
        return self.dados_clientes is not None and not self.dados_clientes.empty

    # MÉTODOS NOVOS ADICIONADOS PARA CORRIGIR O ERRO
    def obter_usuarios_motoristas(self):
        """Obtém lista de usuários únicos dos motoristas"""
        try:
            if self.dados is not None and not self.dados.empty and 'usuario' in self.dados.columns:
                usuarios = self.dados['usuario'].dropna().unique().tolist()
                usuarios = [str(u) for u in usuarios if u and str(u).strip() and str(u).lower() != 'nan']
                return sorted(usuarios)
            return []
        except Exception as e:
            st.error(f"Erro ao obter usuários: {e}")
            return []

    def obter_nome_por_usuario(self, usuario):
        """Obtém o nome do motorista baseado no usuário"""
        try:
            if self.dados is not None and not self.dados.empty and 'usuario' in self.dados.columns:
                # Converte para string para comparação
                usuario_str = str(usuario).strip()
                # Remove valores NaN e converte para string
                self.dados['usuario'] = self.dados['usuario'].fillna('').astype(str)
                motorista = self.dados[self.dados['usuario'].str.strip() == usuario_str]
                if not motorista.empty:
                    return motorista.iloc[0]['nome']
            return ""
        except Exception as e:
            st.error(f"Erro ao obter nome por usuário: {e}")
            return ""

# Inicialização do gerenciador
@st.cache_resource
def get_gerenciador():
    return GerenciadorMotoristas()

gerenciador = get_gerenciador()

# Inicialização da sessão
if 'pagina' not in st.session_state:
    st.session_state.pagina = "📄 Arquivos HTML"

if 'menu_expandido' not in st.session_state:
    st.session_state.menu_expandido = False

if 'mostrar_codigo_fonte' not in st.session_state:
    st.session_state.mostrar_codigo_fonte = False

# Auto-atualização a cada 1 hora
if 'ultima_atualizacao' not in st.session_state:
    st.session_state.ultima_atualizacao = datetime.now()

tempo_decorrido = datetime.now() - st.session_state.ultima_atualizacao
if tempo_decorrido.total_seconds() > 3600:  # 1 hora
    st.session_state.ultima_atualizacao = datetime.now()
    gerenciador.carregar_dados()
    st.rerun()

# Carrega dados
if gerenciador.dados is None:
    gerenciador.carregar_dados()

# Função auxiliar para obter valores únicos de colunas com segurança
def obter_valores_unicos(coluna, dados):
    """Obtém valores únicos de uma coluna com tratamento de erro"""
    try:
        if dados is not None and not dados.empty and coluna in dados.columns:
            valores = dados[coluna].dropna().unique().tolist()
            # Remove valores vazios
            valores = [v for v in valores if v and str(v).strip() and str(v).lower() != 'nan']
            return valores
        else:
            return []
    except Exception:
        return []

# CSS para esconder elementos do Streamlit
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Botão flutuante para menu - CORRIGIDO
st.markdown("""
<style>
.floating-menu {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 1000;
    background: white;
    padding: 10px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    border: 1px solid #e0e0e0;
}
</style>
""", unsafe_allow_html=True)

# Menu principal no sidebar - CORRIGIDO
with st.sidebar:
    st.title("🚗 Sistema de Motoristas")
    
    # Botão para expandir/recolher menu - CORRIGIDO
    if st.button("📋 Menu Principal", key="menu_toggle"):
        st.session_state.menu_expandido = not st.session_state.menu_expandido
        st.rerun()
    
    if st.session_state.menu_expandido:
        pagina_selecionada = st.selectbox(
            "Navegação",
            ["📄 Arquivos HTML", "📊 Dashboard", "👥 Cadastrar Motorista", "📤 Importar Excel", "✏️ Editar Motorista", "🗑️ Excluir Motorista", "📋 Lista Completa", 
             "🏢 Cadastrar Cliente", "✏️ Editar Cliente", "🗑️ Excluir Cliente", "📋 Lista de Clientes",
             "🌐 Gerenciar HTML"],
            key="nav_select"
        )
        
        # Atualiza a página se selecionou uma diferente
        if pagina_selecionada != st.session_state.pagina:
            st.session_state.pagina = pagina_selecionada
            st.rerun()
        
        # Informações de atualização
        st.markdown("---")
        st.subheader("🔄 Atualização")
        if gerenciador.ultima_atualizacao:
            st.write(f"Última atualização: {gerenciador.ultima_atualizacao.strftime('%d/%m/%Y %H:%M')}")

        if st.button("🔄 Atualizar Agora", key="update_now"):
            gerenciador.carregar_dados()
            st.session_state.ultima_atualizacao = datetime.now()
            st.rerun()

        # Seção de Arquivos HTML
        st.markdown("---")
        st.subheader("🌐 Arquivos HTML")

        gerenciador_html.carregar_arquivos()
        if gerenciador_html.arquivos_html:
            st.success(f"📁 {len(gerenciador_html.arquivos_html)} arquivo(s)")
            
            # Mostrar apenas os primeiros 3 arquivos para não poluir
            for i, arquivo in enumerate(gerenciador_html.arquivos_html[:3]):
                if st.button(f"📄 {arquivo}", key=f"sidebar_{i}"):
                    st.session_state.pagina = "📄 Arquivos HTML"
                    st.session_state.arquivo_sidebar = arquivo
                    st.rerun()
            
            if len(gerenciador_html.arquivos_html) > 3:
                st.info(f"... e mais {len(gerenciador_html.arquivos_html) - 3} arquivos")
        else:
            st.info("📭 Nenhum arquivo")

        st.markdown("---")
        st.info("Sistema atualizado automaticamente a cada 1 hora")

# Página: Arquivos HTML (PÁGINA PRINCIPAL - TELA CHEIA)
if st.session_state.pagina == "📄 Arquivos HTML":
    # Atualizar lista de arquivos
    gerenciador_html.carregar_arquivos()
    
    if gerenciador_html.arquivos_html:
        # Seletor de arquivos discreto no topo (apenas se houver múltiplos arquivos)
        if len(gerenciador_html.arquivos_html) > 1:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                arquivo_selecionado = st.selectbox(
                    "Selecione o relatório:",
                    gerenciador_html.arquivos_html,
                    index=0,
                    label_visibility="collapsed"
                )
            with col2:
                # Botão para atualizar lista
                if st.button("🔄", help="Atualizar lista", key="refresh_list"):
                    gerenciador_html.carregar_arquivos()
                    st.rerun()
            with col3:
                # Botão para menu - CORRIGIDO
                if st.button("📋 Menu", help="Abrir menu principal", key="open_menu"):
                    st.session_state.menu_expandido = True
                    st.rerun()
        else:
            arquivo_selecionado = gerenciador_html.arquivos_html[0]
            
            # Botões de ação em uma linha
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("🔄", help="Atualizar lista", key="refresh_list_single"):
                    gerenciador_html.carregar_arquivos()
                    st.rerun()
            with col2:
                # Botão para menu - CORRIGIDO
                if st.button("📋 Menu", help="Abrir menu principal", key="open_menu_single"):
                    st.session_state.menu_expandido = True
                    st.rerun()
            with col3:
                st.write(f"**Visualizando:** {arquivo_selecionado}")
        
        # Obter conteúdo do arquivo
        conteudo_html = gerenciador_html.obter_conteudo_html(arquivo_selecionado)
        
        if conteudo_html:
            # Botões de ação flutuantes
            col_actions1, col_actions2, col_actions3 = st.columns([1, 1, 1])
            
            with col_actions1:
                # Download do arquivo
                st.download_button(
                    label="📥 Baixar",
                    data=conteudo_html,
                    file_name=arquivo_selecionado,
                    mime="text/html",
                    use_container_width=True,
                    key="download_html"
                )
            
            with col_actions2:
                # Ver código fonte
                if st.button("📝 Código Fonte", use_container_width=True, key="show_code"):
                    st.session_state.mostrar_codigo_fonte = not st.session_state.mostrar_codigo_fonte
                    st.rerun()
            
            with col_actions3:
                # Navegar para gerenciador
                if st.button("⚙️ Gerenciar", use_container_width=True, key="go_manage"):
                    st.session_state.pagina = "🌐 Gerenciar HTML"
                    st.rerun()
            
            # Renderizar HTML em tela cheia
            st.markdown("---")
            
            # Altura máxima para tela cheia (calculada dinamicamente)
            altura = 750
            
            # Renderizar HTML diretamente em tela cheia
            st.components.v1.html(conteudo_html, height=altura, scrolling=True)
            
            # Mostrar código fonte se solicitado (em expander para não atrapalhar a visualização)
            if st.session_state.mostrar_codigo_fonte:
                with st.expander("📝 Código Fonte do Relatório", expanded=True):
                    st.code(conteudo_html, language='html')
        
        else:
            st.error("❌ Não foi possível carregar o conteúdo do relatório")
    
    else:
        # Tela quando não há arquivos
        st.markdown("""
        <div style='
            text-align: center; 
            padding: 60px 20px; 
            background-color: #f8f9fa; 
            border-radius: 10px;
            border: 2px dashed #dee2e6;
            margin: 40px 0;
        '>
            <h3 style='color: #6c757d; margin-bottom: 20px;'>📭 Nenhum Relatório Encontrado</h3>
            <p style='color: #6c757d; font-size: 16px; margin-bottom: 30px;'>
                Importe seu primeiro relatório HTML para visualizá-lo aqui.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col_empty1, col_empty2, col_empty3 = st.columns([1, 2, 1])
        
        with col_empty2:
            if st.button("📤 Importar Primeiro Relatório", type="primary", use_container_width=True, key="import_first"):
                st.session_state.pagina = "🌐 Gerenciar HTML"
                st.rerun()

# [RESTANTE DO CÓDIGO PERMANECE IGUAL - APENAS AS PÁGINAS SEGUINTES]
# Página: Dashboard
elif st.session_state.pagina == "📊 Dashboard":
    st.title("📊 Dashboard de Motoristas")
    
    # Botão para voltar ao menu
    if st.button("← Voltar", key="back_dashboard"):
        st.session_state.pagina = "📄 Arquivos HTML"
        st.rerun()
    
    if gerenciador.dados is not None and not gerenciador.dados.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_motoristas = len(gerenciador.dados)
            st.metric("Total de Motoristas", total_motoristas)
        
        with col2:
            ativos = len(gerenciador.dados[gerenciador.dados['status'] == 'ATIVO'])
            st.metric("Motoristas Ativos", ativos)
        
        with col3:
            com_veiculo = len(gerenciador.dados[gerenciador.dados['com-veiculo'] == 'Sim'])
            st.metric("Com Veículo", com_veiculo)
        
        with col4:
            doc_vencido = len(gerenciador.dados[gerenciador.dados['doc-vencido'] == 'Sim'])
            st.metric("Docs Vencidos", doc_vencido)
        
        # Gráficos e estatísticas
        st.subheader("📈 Estatísticas")
        col1, col2 = st.columns(2)
        
        with col1:
            if 'empresa' in gerenciador.dados.columns:
                empresa_count = gerenciador.dados['empresa'].value_counts()
                st.bar_chart(empresa_count)
        
        with col2:
            if 'status' in gerenciador.dados.columns:
                status_count = gerenciador.dados['status'].value_counts()
                st.bar_chart(status_count)
        
        # Tabela resumo
        st.subheader("📋 Resumo dos Motoristas")
        if not gerenciador.dados.empty:
            dados_resumo = gerenciador.dados[COLUNAS_PRINCIPAIS]
            st.dataframe(dados_resumo, use_container_width=True)
    
    else:
        st.info("Nenhum motorista cadastrado ainda.")

# [AS DEMAIS PÁGINAS PERMANECEM COM O MESMO CÓDIGO ANTERIOR...]
# Apenas adicionei botões "Voltar" para facilitar a navegação

# Página: Cadastrar Motorista
elif st.session_state.pagina == "👥 Cadastrar Motorista":
    st.title("👥 Cadastrar Novo Motorista")
    
    # Botão para voltar ao menu
    if st.button("← Voltar", key="back_cadastrar"):
        st.session_state.pagina = "📄 Arquivos HTML"
        st.rerun()
    
    # [RESTANTE DO CÓDIGO DA PÁGINA...]

# Página: Importar Excel  
elif st.session_state.pagina == "📤 Importar Excel":
    st.title("📤 Importar Dados via Excel")
    
    # Botão para voltar ao menu
    if st.button("← Voltar", key="back_importar"):
        st.session_state.pagina = "📄 Arquivos HTML"
        st.rerun()
    
    # [RESTANTE DO CÓDIGO DA PÁGINA...]

# [CONTINUE COM TODAS AS OUTRAS PÁGINAS...]