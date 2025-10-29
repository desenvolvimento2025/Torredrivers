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
    initial_sidebar_state="collapsed"
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

# Inicialização da sessão - SIMPLIFICADA
if 'pagina' not in st.session_state:
    st.session_state.pagina = "📄 Arquivos HTML"

if 'menu_aberto' not in st.session_state:
    st.session_state.menu_aberto = False

if 'mostrar_codigo_fonte' not in st.session_state:
    st.session_state.mostrar_codigo_fonte = False

# Carrega dados
if gerenciador.dados is None:
    gerenciador.carregar_dados()

# CSS SIMPLIFICADO
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.menu-flutuante {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    z-index: 1000;
    border: 2px solid #e0e0e0;
    min-width: 300px;
}
.overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.5);
    z-index: 999;
}
.botao-menu-principal {
    background: #667eea;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    font-size: 14px;
    cursor: pointer;
    margin: 5px;
}
.botao-menu-principal:hover {
    background: #5a6fd8;
}
</style>
""", unsafe_allow_html=True)

# FUNÇÃO DO MENU PRINCIPAL - SIMPLIFICADA
def mostrar_menu_principal():
    """Mostra o menu principal como overlay"""
    # Overlay de fundo
    st.markdown('<div class="overlay"></div>', unsafe_allow_html=True)
    
    # Container do menu
    with st.container():
        st.markdown('<div class="menu-flutuante">', unsafe_allow_html=True)
        
        st.markdown("### 🚗 Menu Principal")
        st.markdown("---")
        
        # Opções do menu
        opcoes = [
            ("📄 Arquivos HTML", "📄 Arquivos HTML"),
            ("📊 Dashboard", "📊 Dashboard"),
            ("👥 Cadastrar Motorista", "👥 Cadastrar Motorista"),
            ("📤 Importar Excel", "📤 Importar Excel"),
            ("✏️ Editar Motorista", "✏️ Editar Motorista"),
            ("🗑️ Excluir Motorista", "🗑️ Excluir Motorista"),
            ("📋 Lista Completa", "📋 Lista Completa"),
            ("🏢 Cadastrar Cliente", "🏢 Cadastrar Cliente"),
            ("✏️ Editar Cliente", "✏️ Editar Cliente"),
            ("🗑️ Excluir Cliente", "🗑️ Excluir Cliente"),
            ("📋 Lista de Clientes", "📋 Lista de Clientes"),
            ("🌐 Gerenciar HTML", "🌐 Gerenciar HTML")
        ]
        
        for texto, pagina in opcoes:
            if st.button(texto, key=f"menu_{pagina}", use_container_width=True):
                st.session_state.pagina = pagina
                st.session_state.menu_aberto = False
                st.rerun()
        
        st.markdown("---")
        if st.button("❌ Fechar Menu", key="fechar_menu", use_container_width=True):
            st.session_state.menu_aberto = False
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# BOTÃO DO MENU PRINCIPAL - SEMPRE VISÍVEL
col1, col2, col3 = st.columns([6, 1, 1])
with col3:
    if st.button("📋 Menu", key="abrir_menu_global"):
        st.session_state.menu_aberto = True
        st.rerun()

# LÓGICA PRINCIPAL SIMPLIFICADA
if st.session_state.menu_aberto:
    mostrar_menu_principal()
else:
    # PÁGINA PRINCIPAL - ARQUIVOS HTML
    if st.session_state.pagina == "📄 Arquivos HTML":
        st.title("📄 Relatórios HTML")
        
        # Atualizar lista de arquivos
        gerenciador_html.carregar_arquivos()
        
        if gerenciador_html.arquivos_html:
            if len(gerenciador_html.arquivos_html) > 1:
                arquivo_selecionado = st.selectbox(
                    "Selecione o relatório:",
                    gerenciador_html.arquivos_html,
                    index=0
                )
            else:
                arquivo_selecionado = gerenciador_html.arquivos_html[0]
            
            # Obter conteúdo do arquivo
            conteudo_html = gerenciador_html.obter_conteudo_html(arquivo_selecionado)
            
            if conteudo_html:
                st.markdown("---")
                st.components.v1.html(conteudo_html, height=600, scrolling=True)
            else:
                st.error("❌ Não foi possível carregar o conteúdo do relatório")
        
        else:
            st.info("📭 Nenhum relatório HTML encontrado. Use a página 'Gerenciar HTML' para importar relatórios.")
    
    # DASHBOARD
    elif st.session_state.pagina == "📊 Dashboard":
        st.title("📊 Dashboard de Motoristas")
        
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
        else:
            st.info("Nenhum motorista cadastrado ainda.")
    
    # CADASTRAR MOTORISTA (exemplo - mantenha as outras páginas similares)
    elif st.session_state.pagina == "👥 Cadastrar Motorista":
        st.title("👥 Cadastrar Novo Motorista")
        
        with st.form("form_cadastro"):
            nome = st.text_input("Nome completo*")
            usuario = st.text_input("Usuário*")
            empresa = st.selectbox("Empresa*", ["EXPRESSO", "LOGIKA"])
            
            if st.form_submit_button("💾 Cadastrar Motorista"):
                if nome and usuario and empresa:
                    dados_motorista = {
                        'nome': nome,
                        'usuario': usuario,
                        'empresa': empresa,
                        'status': 'ATIVO'
                    }
                    if gerenciador.adicionar_motorista(dados_motorista):
                        st.success("✅ Motorista cadastrado com sucesso!")
                    else:
                        st.error("❌ Erro ao cadastrar motorista")
                else:
                    st.error("❌ Preencha os campos obrigatórios")
    
    # IMPORTAR EXCEL
    elif st.session_state.pagina == "📤 Importar Excel":
        st.title("📤 Importar Dados do Excel")
        
        arquivo = st.file_uploader("Selecione o arquivo Excel", type=['xlsx', 'xls'])
        
        if arquivo is not None:
            if st.button("🚀 Importar Dados"):
                if gerenciador.importar_excel(arquivo):
                    st.success("✅ Dados importados com sucesso!")
                else:
                    st.error("❌ Erro ao importar dados")
    
    # EDITAR MOTORISTA
    elif st.session_state.pagina == "✏️ Editar Motorista":
        st.title("✏️ Editar Motorista")
        
        if gerenciador.dados is not None and not gerenciador.dados.empty:
            motoristas = gerenciador.dados['nome'].tolist()
            motorista_selecionado = st.selectbox("Selecione o motorista:", motoristas)
            st.info(f"Editar: {motorista_selecionado}")
        else:
            st.info("Nenhum motorista cadastrado.")
    
    # EXCLUIR MOTORISTA
    elif st.session_state.pagina == "🗑️ Excluir Motorista":
        st.title("🗑️ Excluir Motorista")
        
        if gerenciador.dados is not None and not gerenciador.dados.empty:
            motoristas = gerenciador.dados['nome'].tolist()
            motorista_selecionado = st.selectbox("Selecione o motorista para excluir:", motoristas)
            
            if st.button("🗑️ Excluir Permanentemente"):
                idx = gerenciador.dados[gerenciador.dados['nome'] == motorista_selecionado].index[0]
                if gerenciador.excluir_motorista(idx):
                    st.success("✅ Motorista excluído com sucesso!")
                    st.rerun()
        else:
            st.info("Nenhum motorista cadastrado.")
    
    # LISTA COMPLETA
    elif st.session_state.pagina == "📋 Lista Completa":
        st.title("📋 Lista Completa de Motoristas")
        
        if gerenciador.dados is not None and not gerenciador.dados.empty:
            st.dataframe(gerenciador.dados[COLUNAS_PRINCIPAIS], use_container_width=True)
        else:
            st.info("Nenhum motorista cadastrado.")
    
    # CADASTRAR CLIENTE
    elif st.session_state.pagina == "🏢 Cadastrar Cliente":
        st.title("🏢 Cadastrar Cliente")
        
        with st.form("form_cliente"):
            cliente = st.text_input("Código do Cliente*")
            nome = st.text_input("Nome*")
            
            if st.form_submit_button("💾 Cadastrar Cliente"):
                if cliente and nome:
                    dados_cliente = {
                        'cliente': cliente,
                        'nome': nome,
                        'status': 'ATIVO'
                    }
                    if gerenciador.adicionar_cliente(dados_cliente):
                        st.success("✅ Cliente cadastrado com sucesso!")
                    else:
                        st.error("❌ Erro ao cadastrar cliente")
    
    # EDITAR CLIENTE
    elif st.session_state.pagina == "✏️ Editar Cliente":
        st.title("✏️ Editar Cliente")
        
        if gerenciador.tem_dados_clientes():
            clientes = gerenciador.dados_clientes['nome'].tolist()
            cliente_selecionado = st.selectbox("Selecione o cliente:", clientes)
            st.info(f"Editar: {cliente_selecionado}")
        else:
            st.info("Nenhum cliente cadastrado.")
    
    # EXCLUIR CLIENTE
    elif st.session_state.pagina == "🗑️ Excluir Cliente":
        st.title("🗑️ Excluir Cliente")
        
        if gerenciador.tem_dados_clientes():
            clientes = gerenciador.dados_clientes['nome'].tolist()
            cliente_selecionado = st.selectbox("Selecione o cliente para excluir:", clientes)
            
            if st.button("🗑️ Excluir Permanentemente"):
                idx = gerenciador.dados_clientes[gerenciador.dados_clientes['nome'] == cliente_selecionado].index[0]
                if gerenciador.excluir_cliente(idx):
                    st.success("✅ Cliente excluído com sucesso!")
                    st.rerun()
        else:
            st.info("Nenhum cliente cadastrado.")
    
    # LISTA DE CLIENTES
    elif st.session_state.pagina == "📋 Lista de Clientes":
        st.title("📋 Lista de Clientes")
        
        if gerenciador.tem_dados_clientes():
            st.dataframe(gerenciador.dados_clientes, use_container_width=True)
        else:
            st.info("Nenhum cliente cadastrado.")
    
    # GERENCIAR HTML
    elif st.session_state.pagina == "🌐 Gerenciar HTML":
        st.title("🌐 Gerenciar Arquivos HTML")
        
        # Upload de arquivo
        arquivo_upload = st.file_uploader("Selecione o arquivo HTML", type=['html'])
        
        if arquivo_upload is not None:
            if st.button("📥 Importar Arquivo HTML"):
                if gerenciador_html.importar_html(arquivo_upload):
                    st.success("✅ Arquivo HTML importado com sucesso!")
                    st.rerun()
        
        # Lista de arquivos
        gerenciador_html.carregar_arquivos()
        if gerenciador_html.arquivos_html:
            st.subheader("Arquivos disponíveis:")
            for arquivo in gerenciador_html.arquivos_html:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(arquivo)
                with col2:
                    if st.button("🗑️", key=f"del_{arquivo}"):
                        try:
                            caminho_arquivo = os.path.join(gerenciador_html.pasta_html, arquivo)
                            os.remove(caminho_arquivo)
                            st.success(f"✅ {arquivo} excluído!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erro: {e}")
        else:
            st.info("Nenhum arquivo HTML na pasta.")

# FOOTER
st.markdown("---")
st.markdown("**Sistema de Motoristas v1.0**")