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
    initial_sidebar_state="collapsed"  # Menu minimizado por padrão
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

# Inicialização da página padrão
if 'pagina' not in st.session_state:
    st.session_state.pagina = "📄 Arquivos HTML"

# Sidebar para navegação
st.sidebar.title("🚗 Sistema de Motoristas")
pagina = st.sidebar.selectbox(
    "Navegação",
    ["📄 Arquivos HTML", "📊 Dashboard", "👥 Cadastrar Motorista", "📤 Importar Excel", "✏️ Editar Motorista", "🗑️ Excluir Motorista", "📋 Lista Completa", 
     "🏢 Cadastrar Cliente", "✏️ Editar Cliente", "🗑️ Excluir Cliente", "📋 Lista de Clientes",
     "🌐 Gerenciar HTML"]
)

# Verificar se há redirecionamento por arquivo específico do sidebar
if 'arquivo_sidebar' in st.session_state and st.session_state.arquivo_sidebar:
    st.session_state.arquivo_selecionado = st.session_state.arquivo_sidebar
    del st.session_state.arquivo_sidebar

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

# Página: Arquivos HTML (NOVA PÁGINA PRINCIPAL SIMPLIFICADA)
if pagina == "📄 Arquivos HTML":
    # Atualizar lista de arquivos
    gerenciador_html.carregar_arquivos()
    
    if gerenciador_html.arquivos_html:
        # Seletor de arquivos discreto no topo
        if len(gerenciador_html.arquivos_html) > 1:
            arquivo_selecionado = st.selectbox(
                "Selecione o relatório:",
                gerenciador_html.arquivos_html,
                index=0,
                label_visibility="collapsed"
            )
        else:
            arquivo_selecionado = gerenciador_html.arquivos_html[0]
        
        # Botões de ação compactos em uma linha - APENAS DOWNLOAD
        col1, col2 = st.columns([1, 11])
        
        with col1:
            # Download do arquivo
            conteudo_html = gerenciador_html.obter_conteudo_html(arquivo_selecionado)
            if conteudo_html:
                st.download_button(
                    label="📥",
                    data=conteudo_html,
                    file_name=arquivo_selecionado,
                    mime="text/html",
                    help="Baixar arquivo HTML"
                )
        
        with col2:
            st.write(f"**Visualizando:** {arquivo_selecionado}")
        
        # Obter conteúdo do arquivo
        conteudo_html = gerenciador_html.obter_conteudo_html(arquivo_selecionado)
        
        if conteudo_html:
            # Renderizar HTML em tela cheia - MAIS FOCO NA VISUALIZAÇÃO
            st.markdown("---")
            
            # Altura máxima para tela cheia - AUMENTADA
            altura = 900
            
            # Renderizar HTML diretamente em tela cheia
            st.components.v1.html(conteudo_html, height=altura, scrolling=True)
        
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
            if st.button("📤 Importar Primeiro Relatório", type="primary", use_container_width=True):
                st.session_state.pagina = "🌐 Gerenciar HTML"
                st.rerun()

# Página: Dashboard
elif pagina == "📊 Dashboard":
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

# Página: Cadastrar Motorista
elif pagina == "👥 Cadastrar Motorista":
    st.title("👥 Cadastrar Novo Motorista")
    
    with st.form("form_cadastro"):
        st.subheader("Informações Básicas")
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome completo*")
            usuario = st.text_input("Usuário*")
            grupo = st.selectbox("Grupo*", ["Motorista"])
            empresa = st.selectbox("Empresa*", ["EXPRESSO", "LOGIKA"])
            filial = st.selectbox("Filial*", ["MEA", "RIO", "CXA", "VIX", "SPO", "LGK", "NPA"])
        
        with col2:
            status = st.selectbox("Status*", ["ATIVO", "INATIVO"])
            categoria = st.selectbox("Categoria CNH", ["A", "B", "C", "D", "E"])
            placa1 = st.text_input("Placa Principal")
            placa2 = st.text_input("Placa Secundária")
            placa3 = st.text_input("Placa Terciária")
        
        st.subheader("Status do Motorista")
        col3, col4 = st.columns(2)
        
        with col3:
            disponibilidade = st.selectbox("Disponibilidade*", ["Trabalhando", "Interjornada", "Indisponíveis"])
            ferias = st.selectbox("Férias*", ["Sim", "Não"])
            licenca = st.selectbox("Licença*", ["Sim", "Não"])
            folga = st.selectbox("Folga*", ["Sim", "Não"])
        
        with col4:
            sobreaviso = st.selectbox("Sobreaviso*", ["Sim", "Não"])
            atestado = st.selectbox("Atestado*", ["Sim", "Não"])
            com_atend = st.selectbox("Com Atendimento", ["", "Sim", "Não"])
            com_veiculo = st.selectbox("Com Veículo", ["", "Sim", "Não"])
        
        st.subheader("Status Operacional")
        col5, col6 = st.columns(2)
        
        with col5:
            com_check = st.selectbox("Com Check", ["", "Sim", "Não"])
            dirigindo = st.selectbox("Dirigindo", ["", "Sim", "Não"])
            parado_ate1h = st.selectbox("Parado até 1h", ["", "Sim", "Não"])
            parado1ate2h = st.selectbox("Parado 1h a 2h", ["", "Sim", "Não"])
        
        with col6:
            parado_acima2h = st.selectbox("Parado acima 2h", ["", "Sim", "Não"])
            jornada_acm80 = st.selectbox("Jornada acima 80%", ["", "Sim", "Não"])
            jornada_exced = st.selectbox("Jornada Excedida", ["", "Sim", "Não"])
        
        st.subheader("Jornada e Documentação")
        col7, col8 = st.columns(2)
        
        with col7:
            sem_folga_acm7d = st.selectbox("Sem folga a partir 8d", ["", "Sim", "Não"])
            sem_folga_acm12d = st.selectbox("Sem folga a partir de 12d", ["", "Sim", "Não"])
            doc_vencendo = st.selectbox("Doc Vencendo", ["", "Sim", "Não"])
            doc_vencido = st.selectbox("Doc Vencido", ["", "Sim", "Não"])
        
        with col8:
            localiz_atual = st.text_input("Última localiz pelo veículo")
            associacao_clientes = st.selectbox("Associação a Clientes", ["", "Sim", "Não"])
            interj_menor8 = st.selectbox("Interjornada < 8h", ["", "Sim", "Não"])
            interj_maior8 = st.selectbox("Interjornada > 8h", ["", "Sim", "Não"])
        
        submitted = st.form_submit_button("💾 Cadastrar Motorista")
        
        if submitted:
            if nome and usuario and empresa:
                dados_motorista = {
                    # Informações básicas
                    'nome': nome,
                    'usuario': usuario,
                    'grupo': grupo,
                    'empresa': empresa,
                    'filial': filial,
                    'status': status,
                    'categoria': categoria,
                    'placa1': placa1,
                    'placa2': placa2,
                    'placa3': placa3,
                    
                    # Status do motorista
                    'disponibilidade': disponibilidade,
                    'ferias': ferias,
                    'licenca': licenca,
                    'folga': folga,
                    'sobreaviso': sobreaviso,
                    'atestado': atestado,
                    
                    # Status operacional
                    'com-atend': com_atend,
                    'com-veiculo': com_veiculo,
                    'com-check': com_check,
                    'dirigindo': dirigindo,
                    'parado-ate1h': parado_ate1h,
                    'parado1ate2h': parado1ate2h,
                    'parado-acima2h': parado_acima2h,
                    
                    # Jornada
                    'jornada-acm80': jornada_acm80,
                    'jornada-exced': jornada_exced,
                    'sem-folga-acm7d': sem_folga_acm7d,
                    'sem-folga-acm12d': sem_folga_acm12d,
                    
                    # Documentação
                    'doc-vencendo': doc_vencendo,
                    'doc-vencido': doc_vencido,
                    
                    # Localização e associação
                    'localiz-atual': localiz_atual,
                    'associacao-clientes': associacao_clientes,
                    
                    # Interjornada
                    'interj-menor8': interj_menor8,
                    'interj-maior8': interj_maior8
                }
                
                if gerenciador.adicionar_motorista(dados_motorista):
                    st.success("✅ Motorista cadastrado com sucesso!")
                    st.balloons()
                else:
                    st.error("❌ Erro ao cadastrar motorista")
            else:
                st.warning("⚠️ Preencha os campos obrigatórios (Nome, Usuário, Empresa)")

# Página: Importar Excel
elif pagina == "📤 Importar Excel":
    st.title("📤 Importar Dados via Excel")
    
    st.markdown("""
    ### 📋 Instruções para Importação
    
    1. **Preparar o arquivo Excel** com as colunas conforme modelo
    2. **Colunas obrigatórias**: `nome`, `usuario`, `empresa`
    3. **Formato suportado**: .xlsx ou .xls
    4. **Dados duplicados** serão atualizados (baseado em nome + usuário)
    """)
    
    # Download do template
    st.subheader("📥 Download do Template")
    
    # Cria template vazio com estrutura exata
    template_df = pd.DataFrame(columns=ESTRUTURA_COLUNAS)
    
    # Adiciona exemplo de dados
    exemplo = {
        'nome': 'João Silva',
        'usuario': 'joao.silva',
        'empresa': 'EXPRESSO',
        'status': 'ATIVO',
        'grupo': 'Motorista',
        'filial': 'SPO',
        'disponibilidade': 'Trabalhando',
        'ferias': 'Não',
        'licenca': 'Não',
        'folga': 'Não',
        'sobreaviso': 'Não',
        'atestado': 'Não',
        'com-veiculo': 'Sim',
        'doc-vencido': 'Não',
        'associacao-clientes': 'Sim',
        'placa1': 'ABC1234',
        'placa2': 'DEF5678',
        'placa3': 'GHI9012',
        'categoria': 'D'
    }
    for col, valor in exemplo.items():
        if col in template_df.columns:
            template_df.loc[0, col] = valor
    
    # Botão para download do template
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        template_df.to_excel(writer, sheet_name='motoristas', index=False)
    
    st.download_button(
        label="📋 Baixar Template Excel",
        data=buffer.getvalue(),
        file_name="template_motoristas.xlsx",
        mime="application/vnd.ms-excel"
    )
    
    # Upload do arquivo
    st.subheader("📤 Upload do Arquivo")
    
    arquivo = st.file_uploader(
        "Selecione o arquivo Excel para importar",
        type=['xlsx', 'xls'],
        help="Arquivo Excel com dados dos motoristas"
    )
    
    if arquivo is not None:
        try:
            # Pré-visualização dos dados
            st.subheader("👁️ Pré-visualização dos Dados")
            dados_preview = pd.read_excel(arquivo)
            st.dataframe(dados_preview.head(10), use_container_width=True)
            
            st.info(f"📊 Arquivo contém {len(dados_preview)} registros")
            
            # Mostra colunas encontradas
            colunas_encontradas = list(dados_preview.columns)
            st.write(f"**Colunas detectadas:** {', '.join(colunas_encontradas)}")
            
            # Verifica colunas obrigatórias
            colunas_necessarias = ['nome', 'usuario', 'empresa']
            colunas_faltantes = [col for col in colunas_necessarias if col not in dados_preview.columns]
            
            if colunas_faltantes:
                st.error(f"❌ Colunas obrigatórias faltantes: {', '.join(colunas_faltantes)}")
            else:
                st.success("✅ Todas as colunas obrigatórias presentes")
            
            # Opções de importação
            st.subheader("⚙️ Opções de Importação")
            
            col1, col2 = st.columns(2)
            
            with col1:
                modo_importacao = st.radio(
                    "Modo de importação:",
                    ["Adicionar/Atualizar", "Substituir Tudo"],
                    help="Adicionar/Atualizar: mantém dados existentes e atualiza duplicatas. Substituir Tudo: remove todos os dados atuais."
                )
            
            with col2:
                if st.checkbox("Mostrar detalhes avançados"):
                    st.write(f"**Total de registros no sistema atual:** {len(gerenciador.dados) if gerenciador.dados is not None else 0}")
                    st.write(f"**Estrutura esperada:** {len(ESTRUTURA_COLUNAS)} colunas")
            
            # Botão de importação
            if st.button("🚀 Iniciar Importação", type="primary"):
                if colunas_faltantes:
                    st.error("Não é possível importar. Corrija as colunas faltantes primeiro.")
                else:
                    with st.spinner("Importando dados..."):
                        if modo_importacao == "Substituir Tudo":
                            # Limpa dados atuais
                            gerenciador.dados = pd.DataFrame(columns=ESTRUTURA_COLUNAS)
                        
                        success = gerenciador.importar_excel(arquivo)
                        
                        if success:
                            st.success("✅ Importação concluída com sucesso!")
                            st.balloons()
                            
                            # Mostra estatísticas
                            st.subheader("📈 Estatísticas da Importação")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Total no Sistema", len(gerenciador.dados))
                            
                            with col2:
                                st.metric("Registros Importados", len(dados_preview))
                            
                            with col3:
                                duplicatas = len(dados_preview) - len(dados_preview.drop_duplicates(subset=['nome', 'usuario']))
                                st.metric("Duplicatas Removidas", duplicatas)
                            
                            # Atualiza a página após 2 segundos
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("❌ Erro na importação. Verifique o formato do arquivo.")
        
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {e}")
            st.info("💡 **Dica:** Verifique se o arquivo está no formato correto e contém as colunas obrigatórias.")

# Página: Editar Motorista
elif pagina == "✏️ Editar Motorista":
    st.title("✏️ Editar Motorista")
    
    if gerenciador.dados is not None and not gerenciador.dados.empty:
        motorista_selecionado = st.selectbox(
            "Selecione o motorista para editar",
            gerenciador.dados['nome'].tolist()
        )
        
        if motorista_selecionado:
            index = gerenciador.dados[gerenciador.dados['nome'] == motorista_selecionado].index[0]
            motorista_data = gerenciador.dados.iloc[index]
            
            with st.form("form_edicao"):
                st.subheader("Informações Básicas")
                col1, col2 = st.columns(2)
                
                with col1:
                    nome = st.text_input("Nome completo*", value=motorista_data.get('nome', ''))
                    usuario = st.text_input("Usuário*", value=motorista_data.get('usuario', ''))
                    grupo = st.selectbox("Grupo*", ["Motorista"], index=0)
                    empresa = st.selectbox("Empresa*", ["EXPRESSO", "LOGIKA"], 
                                         index=["EXPRESSO", "LOGIKA"].index(motorista_data.get('empresa', 'EXPRESSO')))
                    filial = st.selectbox("Filial*", ["MEA", "RIO", "CXA", "VIX", "SPO", "LGK", "NPA"],
                                        index=["MEA", "RIO", "CXA", "VIX", "SPO", "LGK", "NPA"].index(motorista_data.get('filial', 'SPO')))
                
                with col2:
                    status = st.selectbox("Status*", ["ATIVO", "INATIVO"],
                                        index=["ATIVO", "INATIVO"].index(motorista_data.get('status', 'ATIVO')))
                    categoria = st.selectbox("Categoria CNH", ["A", "B", "C", "D", "E"],
                                           index=["A", "B", "C", "D", "E"].index(motorista_data.get('categoria', 'B')))
                    placa1 = st.text_input("Placa Principal", value=motorista_data.get('placa1', ''))
                    placa2 = st.text_input("Placa Secundária", value=motorista_data.get('placa2', ''))
                    placa3 = st.text_input("Placa Terciária", value=motorista_data.get('placa3', ''))
                
                st.subheader("Status do Motorista")
                col3, col4 = st.columns(2)
                
                with col3:
                    disponibilidade = st.selectbox("Disponibilidade*", ["Trabalhando", "Interjornada", "Indisponíveis"],
                                                 index=["Trabalhando", "Interjornada", "Indisponíveis"].index(motorista_data.get('disponibilidade', 'Trabalhando')))
                    ferias = st.selectbox("Férias*", ["Sim", "Não"],
                                        index=["Sim", "Não"].index(motorista_data.get('ferias', 'Não')))
                    licenca = st.selectbox("Licença*", ["Sim", "Não"],
                                         index=["Sim", "Não"].index(motorista_data.get('licenca', 'Não')))
                    folga = st.selectbox("Folga*", ["Sim", "Não"],
                                       index=["Sim", "Não"].index(motorista_data.get('folga', 'Não')))
                
                with col4:
                    sobreaviso = st.selectbox("Sobreaviso*", ["Sim", "Não"],
                                            index=["Sim", "Não"].index(motorista_data.get('sobreaviso', 'Não')))
                    atestado = st.selectbox("Atestado*", ["Sim", "Não"],
                                          index=["Sim", "Não"].index(motorista_data.get('atestado', 'Não')))
                    com_atend = st.selectbox("Com Atendimento", ["", "Sim", "Não"],
                                           index=["", "Sim", "Não"].index(motorista_data.get('com-atend', '')))
                    com_veiculo = st.selectbox("Com Veículo", ["", "Sim", "Não"],
                                             index=["", "Sim", "Não"].index(motorista_data.get('com-veiculo', '')))
                
                st.subheader("Informações Adicionais")
                col5, col6 = st.columns(2)
                
                with col5:
                    localiz_atual = st.text_input("Última localiz pelo veículo", value=motorista_data.get('localiz-atual', ''))
                    doc_vencendo = st.selectbox("Doc Vencendo", ["", "Sim", "Não"],
                                              index=["", "Sim", "Não"].index(motorista_data.get('doc-vencendo', '')))
                    doc_vencido = st.selectbox("Doc Vencido", ["", "Sim", "Não"],
                                             index=["", "Sim", "Não"].index(motorista_data.get('doc-vencido', '')))
                    associacao_clientes = st.selectbox("Associação a Clientes", ["", "Sim", "Não"],
                                                     index=["", "Sim", "Não"].index(motorista_data.get('associacao-clientes', '')))
                
                with col6:
                    interj_menor8 = st.selectbox("Interjornada < 8h", ["", "Sim", "Não"],
                                               index=["", "Sim", "Não"].index(motorista_data.get('interj-menor8', '')))
                    interj_maior8 = st.selectbox("Interjornada > 8h", ["", "Sim", "Não"],
                                               index=["", "Sim", "Não"].index(motorista_data.get('interj-maior8', '')))
                
                submitted = st.form_submit_button("💾 Atualizar Motorista")
                
                if submitted:
                    if nome and usuario and empresa:
                        dados_atualizados = {
                            'nome': nome,
                            'usuario': usuario,
                            'grupo': grupo,
                            'empresa': empresa,
                            'filial': filial,
                            'status': status,
                            'categoria': categoria,
                            'placa1': placa1,
                            'placa2': placa2,
                            'placa3': placa3,
                            'disponibilidade': disponibilidade,
                            'ferias': ferias,
                            'licenca': licenca,
                            'folga': folga,
                            'sobreaviso': sobreaviso,
                            'atestado': atestado,
                            'com-atend': com_atend,
                            'com-veiculo': com_veiculo,
                            'localiz-atual': localiz_atual,
                            'doc-vencendo': doc_vencendo,
                            'doc-vencido': doc_vencido,
                            'associacao-clientes': associacao_clientes,
                            'interj-menor8': interj_menor8,
                            'interj-maior8': interj_maior8
                        }
                        
                        if gerenciador.atualizar_motorista(index, dados_atualizados):
                            st.success("✅ Motorista atualizado com sucesso!")
                            st.balloons()
                        else:
                            st.error("❌ Erro ao atualizar motorista")
                    else:
                        st.warning("⚠️ Preencha os campos obrigatórios (Nome, Usuário, Empresa)")
    else:
        st.info("Nenhum motorista cadastrado para editar.")

# Página: Excluir Motorista
elif pagina == "🗑️ Excluir Motorista":
    st.title("🗑️ Excluir Motorista")
    
    if gerenciador.dados is not None and not gerenciador.dados.empty:
        motorista_selecionado = st.selectbox(
            "Selecione o motorista para excluir",
            gerenciador.dados['nome'].tolist()
        )
        
        if motorista_selecionado:
            index = gerenciador.dados[gerenciador.dados['nome'] == motorista_selecionado].index[0]
            motorista_data = gerenciador.dados.iloc[index]
            
            st.warning("⚠️ **Atenção:** Esta ação não pode ser desfeita!")
            
            # Mostra informações do motorista
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Nome:**", motorista_data.get('nome', ''))
                st.write("**Usuário:**", motorista_data.get('usuario', ''))
                st.write("**Empresa:**", motorista_data.get('empresa', ''))
                st.write("**Status:**", motorista_data.get('status', ''))
            
            with col2:
                st.write("**Filial:**", motorista_data.get('filial', ''))
                st.write("**Categoria:**", motorista_data.get('categoria', ''))
                st.write("**Placa Principal:**", motorista_data.get('placa1', ''))
                st.write("**Disponibilidade:**", motorista_data.get('disponibilidade', ''))
            
            # Confirmação
            confirmacao = st.text_input("Digite 'EXCLUIR' para confirmar:")
            
            if st.button("🗑️ Excluir Permanentemente", type="primary"):
                if confirmacao == "EXCLUIR":
                    if gerenciador.excluir_motorista(index):
                        st.success("✅ Motorista excluído com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao excluir motorista")
                else:
                    st.error("❌ Confirmação incorreta. Digite 'EXCLUIR' para confirmar a exclusão.")
    else:
        st.info("Nenhum motorista cadastrado para excluir.")

# Página: Lista Completa
elif pagina == "📋 Lista Completa":
    st.title("📋 Lista Completa de Motoristas")
    
    if gerenciador.dados is not None and not gerenciador.dados.empty:
        # Filtros
        st.subheader("🔍 Filtros")
        
        # Primeira linha de filtros
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            valores_empresa = obter_valores_unicos('empresa', gerenciador.dados)
            filtro_empresa = st.selectbox(
                "Empresa",
                ["Todas"] + valores_empresa
            )
        
        with col2:
            valores_filial = obter_valores_unicos('filial', gerenciador.dados)
            filtro_filial = st.selectbox(
                "Filial",
                ["Todas"] + valores_filial
            )
        
        with col3:
            valores_categoria = obter_valores_unicos('categoria', gerenciador.dados)
            filtro_categoria = st.selectbox(
                "Categoria",
                ["Todas"] + valores_categoria
            )
        
        with col4:
            filtro_veiculo = st.selectbox(
                "Com Veículo",
                ["Todos", "Sim", "Não"]
            )
        
        # Segunda linha de filtros
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            valores_disponibilidade = obter_valores_unicos('disponibilidade', gerenciador.dados)
            filtro_disponibilidade = st.selectbox(
                "Disponibilidade",
                ["Todas"] + valores_disponibilidade
            )
        
        with col6:
            filtro_ferias = st.selectbox(
                "Férias",
                ["Todas", "Sim", "Não"]
            )
        
        with col7:
            filtro_licenca = st.selectbox(
                "Licença",
                ["Todas", "Sim", "Não"]
            )
        
        with col8:
            filtro_folga = st.selectbox(
                "Folga",
                ["Todas", "Sim", "Não"]
            )
        
        # Terceira linha de filtros
        col9, col10, col11, col12 = st.columns(4)
        
        with col9:
            filtro_sobreaviso = st.selectbox(
                "Sobreaviso",
                ["Todas", "Sim", "Não"]
            )
        
        with col10:
            filtro_atestado = st.selectbox(
                "Atestado",
                ["Todas", "Sim", "Não"]
            )
        
        with col11:
            filtro_com_atend = st.selectbox(
                "Com Atendimento",
                ["Todos", "Sim", "Não"]
            )
        
        with col12:
            filtro_com_check = st.selectbox(
                "Com Check",
                ["Todos", "Sim", "Não"]
            )
        
        # Quarta linha de filtros
        col13, col14, col15, col16 = st.columns(4)
        
        with col13:
            filtro_dirigindo = st.selectbox(
                "Dirigindo",
                ["Todos", "Sim", "Não"]
            )
        
        with col14:
            filtro_parado_ate1h = st.selectbox(
                "Parado até 1h",
                ["Todos", "Sim", "Não"]
            )
        
        with col15:
            filtro_parado1ate2h = st.selectbox(
                "Parado 1h a 2h",
                ["Todos", "Sim", "Não"]
            )
        
        with col16:
            filtro_parado_acima2h = st.selectbox(
                "Parado acima 2h",
                ["Todos", "Sim", "Não"]
            )
        
        # Quinta linha de filtros
        col17, col18, col19, col20 = st.columns(4)
        
        with col17:
            filtro_jornada_acm80 = st.selectbox(
                "Jornada acima 80%",
                ["Todos", "Sim", "Não"]
            )
        
        with col18:
            filtro_jornada_exced = st.selectbox(
                "Jornada Excedida",
                ["Todos", "Sim", "Não"]
            )
        
        with col19:
            filtro_sem_folga_acm7d = st.selectbox(
                "Sem folga a partir 8d",
                ["Todos", "Sim", "Não"]
            )
        
        with col20:
            filtro_sem_folga_acm12d = st.selectbox(
                "Sem folga a partir de 12d",
                ["Todos", "Sim", "Não"]
            )
        
        # Sexta linha de filtros
        col21, col22, col23, col24 = st.columns(4)
        
        with col21:
            filtro_doc_vencendo = st.selectbox(
                "Doc Vencendo",
                ["Todos", "Sim", "Não"]
            )
        
        with col22:
            filtro_doc_vencido = st.selectbox(
                "Doc Vencido",
                ["Todos", "Sim", "Não"]
            )
        
        with col23:
            filtro_associacao_clientes = st.selectbox(
                "Associação a Clientes",
                ["Todos", "Sim", "Não"]
            )
        
        with col24:
            filtro_interj_menor8 = st.selectbox(
                "Interjornada < 8h",
                ["Todos", "Sim", "Não"]
            )
        
        # Sétima linha de filtros
        col25, col26, col27, col28 = st.columns(4)
        
        with col25:
            filtro_interj_maior8 = st.selectbox(
                "Interjornada > 8h",
                ["Todos", "Sim", "Não"]
            )
        
        # Aplicar filtros
        dados_filtrados = gerenciador.dados.copy()
        
        # Aplicar todos os filtros
        if filtro_empresa != "Todas":
            dados_filtrados = dados_filtrados[dados_filtrados['empresa'] == filtro_empresa]
        
        if filtro_filial != "Todas":
            dados_filtrados = dados_filtrados[dados_filtrados['filial'] == filtro_filial]
        
        if filtro_categoria != "Todas":
            dados_filtrados = dados_filtrados[dados_filtrados['categoria'] == filtro_categoria]
        
        if filtro_veiculo != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['com-veiculo'] == filtro_veiculo]
        
        if filtro_disponibilidade != "Todas":
            dados_filtrados = dados_filtrados[dados_filtrados['disponibilidade'] == filtro_disponibilidade]
        
        if filtro_ferias != "Todas":
            dados_filtrados = dados_filtrados[dados_filtrados['ferias'] == filtro_ferias]
        
        if filtro_licenca != "Todas":
            dados_filtrados = dados_filtrados[dados_filtrados['licenca'] == filtro_licenca]
        
        if filtro_folga != "Todas":
            dados_filtrados = dados_filtrados[dados_filtrados['folga'] == filtro_folga]
        
        if filtro_sobreaviso != "Todas":
            dados_filtrados = dados_filtrados[dados_filtrados['sobreaviso'] == filtro_sobreaviso]
        
        if filtro_atestado != "Todas":
            dados_filtrados = dados_filtrados[dados_filtrados['atestado'] == filtro_atestado]
        
        if filtro_com_atend != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['com-atend'] == filtro_com_atend]
        
        if filtro_com_check != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['com-check'] == filtro_com_check]
        
        if filtro_dirigindo != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['dirigindo'] == filtro_dirigindo]
        
        if filtro_parado_ate1h != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['parado-ate1h'] == filtro_parado_ate1h]
        
        if filtro_parado1ate2h != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['parado1ate2h'] == filtro_parado1ate2h]
        
        if filtro_parado_acima2h != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['parado-acima2h'] == filtro_parado_acima2h]
        
        if filtro_jornada_acm80 != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['jornada-acm80'] == filtro_jornada_acm80]
        
        if filtro_jornada_exced != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['jornada-exced'] == filtro_jornada_exced]
        
        if filtro_sem_folga_acm7d != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['sem-folga-acm7d'] == filtro_sem_folga_acm7d]
        
        if filtro_sem_folga_acm12d != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['sem-folga-acm12d'] == filtro_sem_folga_acm12d]
        
        if filtro_doc_vencendo != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['doc-vencendo'] == filtro_doc_vencendo]
        
        if filtro_doc_vencido != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['doc-vencido'] == filtro_doc_vencido]
        
        if filtro_associacao_clientes != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['associacao-clientes'] == filtro_associacao_clientes]
        
        if filtro_interj_menor8 != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['interj-menor8'] == filtro_interj_menor8]
        
        if filtro_interj_maior8 != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['interj-maior8'] == filtro_interj_maior8]
        
        st.subheader(f"📊 Resultados ({len(dados_filtrados)} motoristas)")
        st.dataframe(dados_filtrados, use_container_width=True)
        
        # Botão de download
        if not dados_filtrados.empty:
            csv = dados_filtrados.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"motoristas_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
    else:
        st.info("Nenhum motorista cadastrado.")

# PÁGINAS PARA CLIENTES
elif pagina == "🏢 Cadastrar Cliente":
    st.title("🏢 Cadastrar Novo Cliente")
    
    # Garante que os dados estão carregados
    if gerenciador.dados is None:
        gerenciador.carregar_dados()
    
    # Verifica se há dados de motoristas antes de prosseguir
    if gerenciador.dados is not None and not gerenciador.dados.empty:
        # Busca os usuários dos motoristas para o dropdown
        try:
            usuarios_motoristas = gerenciador.obter_usuarios_motoristas()
        except Exception as e:
            st.error(f"Erro ao carregar usuários dos motoristas: {e}")
            usuarios_motoristas = []
        
        with st.form("form_cliente"):
            st.subheader("Informações do Cliente")
            col1, col2 = st.columns(2)
            
            with col1:
                cliente = st.text_input("Nome do Cliente*")
                # Dropdown com os usuários dos motoristas
                usuario_selecionado = st.selectbox("Usuário do Motorista*", [""] + usuarios_motoristas)
                # Mostra o nome do motorista associado ao usuário selecionado
                if usuario_selecionado:
                    try:
                        nome_motorista = gerenciador.obter_nome_por_usuario(usuario_selecionado)
                        if nome_motorista:
                            st.info(f"**Motorista associado:** {nome_motorista}")
                        else:
                            st.warning("Usuário não encontrado na tabela de motoristas")
                    except Exception as e:
                        st.error(f"Erro ao buscar motorista: {e}")
            
            with col2:
                empresa = st.selectbox("Empresa*", ["EXPRESSO", "LOGIKA"])
                filial = st.selectbox("Filial*", ["MEA", "RIO", "CXA", "VIX", "SPO", "LGK", "NPA"])
                status = st.selectbox("Status*", ["ATIVO", "INATIVO"])
            
            submitted = st.form_submit_button("💾 Cadastrar Cliente")
            
            if submitted:
                if cliente and usuario_selecionado and empresa:
                    # Obtém o nome do motorista automaticamente
                    try:
                        nome_motorista = gerenciador.obter_nome_por_usuario(usuario_selecionado)
                    except Exception as e:
                        st.error(f"Erro ao obter nome do motorista: {e}")
                        nome_motorista = ""
                    
                    dados_cliente = {
                        'cliente': cliente,
                        'nome': nome_motorista,
                        'usuario': usuario_selecionado,
                        'empresa': empresa,
                        'filial': filial,
                        'status': status
                    }
                    
                    if gerenciador.adicionar_cliente(dados_cliente):
                        st.success("✅ Cliente cadastrado com sucesso!")
                        st.balloons()
                    else:
                        st.error("❌ Erro ao cadastrar cliente")
                else:
                    st.warning("⚠️ Preencha os campos obrigatórios (Cliente, Usuário do Motorista, Empresa)")
    else:
        st.warning("⚠️ Não há motoristas cadastrados. É necessário cadastrar motoristas antes de associar clientes.")
        st.info("Vá para a página '👥 Cadastrar Motorista' para adicionar motoristas primeiro.")

# Página: Editar Cliente
elif pagina == "✏️ Editar Cliente":
    st.title("✏️ Editar Cliente")
    
    # Garante que os dados estão carregados
    if gerenciador.dados is None:
        gerenciador.carregar_dados()
    
    if gerenciador.tem_dados_clientes() and gerenciador.dados is not None and not gerenciador.dados.empty:
        cliente_selecionado = st.selectbox(
            "Selecione o cliente para editar",
            gerenciador.dados_clientes['cliente'].tolist()
        )
        
        if cliente_selecionado:
            index = gerenciador.dados_clientes[gerenciador.dados_clientes['cliente'] == cliente_selecionado].index[0]
            cliente_data = gerenciador.dados_clientes.iloc[index]
            
            # Busca os usuários dos motoristas para o dropdown
            try:
                usuarios_motoristas = gerenciador.obter_usuarios_motoristas()
            except Exception as e:
                st.error(f"Erro ao carregar usuários dos motoristas: {e}")
                usuarios_motoristas = []
            
            with st.form("form_edicao_cliente"):
                st.subheader("Informações do Cliente")
                col1, col2 = st.columns(2)
                
                with col1:
                    cliente = st.text_input("Nome do Cliente*", value=cliente_data.get('cliente', ''))
                    # Encontra o índice correto para o dropdown de usuários
                    usuario_atual = cliente_data.get('usuario', '')
                    opcoes_usuarios = [""] + usuarios_motoristas
                    indice_atual = opcoes_usuarios.index(usuario_atual) if usuario_atual in opcoes_usuarios else 0
                    usuario_selecionado = st.selectbox("Usuário do Motorista*", opcoes_usuarios, index=indice_atual)
                    
                    # Mostra o nome do motorista associado ao usuário selecionado
                    if usuario_selecionado:
                        try:
                            nome_motorista = gerenciador.obter_nome_por_usuario(usuario_selecionado)
                            if nome_motorista:
                                st.info(f"**Motorista associado:** {nome_motorista}")
                            else:
                                st.warning("Usuário não encontrado na tabela de motoristas")
                        except Exception as e:
                            st.error(f"Erro ao buscar motorista: {e}")
                
                with col2:
                    empresa = st.selectbox("Empresa*", ["EXPRESSO", "LOGIKA"],
                                         index=["EXPRESSO", "LOGIKA"].index(cliente_data.get('empresa', 'EXPRESSO')))
                    filial = st.selectbox("Filial*", ["MEA", "RIO", "CXA", "VIX", "SPO", "LGK", "NPA"],
                                        index=["MEA", "RIO", "CXA", "VIX", "SPO", "LGK", "NPA"].index(cliente_data.get('filial', 'SPO')))
                    status = st.selectbox("Status*", ["ATIVO", "INATIVO"],
                                        index=["ATIVO", "INATIVO"].index(cliente_data.get('status', 'ATIVO')))
                
                submitted = st.form_submit_button("💾 Atualizar Cliente")
                
                if submitted:
                    if cliente and usuario_selecionado and empresa:
                        # Obtém o nome do motorista automaticamente
                        try:
                            nome_motorista = gerenciador.obter_nome_por_usuario(usuario_selecionado)
                        except Exception as e:
                            st.error(f"Erro ao obter nome do motorista: {e}")
                            nome_motorista = ""
                        
                        dados_atualizados = {
                            'cliente': cliente,
                            'nome': nome_motorista,
                            'usuario': usuario_selecionado,
                            'empresa': empresa,
                            'filial': filial,
                            'status': status
                        }
                        
                        if gerenciador.atualizar_cliente(index, dados_atualizados):
                            st.success("✅ Cliente atualizado com sucesso!")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao atualizar cliente")
                    else:
                        st.warning("⚠️ Preencha os campos obrigatórios")
    else:
        st.warning("⚠️ Não há motoristas ou clientes cadastrados.")

# Página: Excluir Cliente
elif pagina == "🗑️ Excluir Cliente":
    st.title("🗑️ Excluir Cliente")
    
    if gerenciador.tem_dados_clientes():
        cliente_selecionado = st.selectbox(
            "Selecione o cliente para excluir",
            gerenciador.dados_clientes['cliente'].tolist()
        )
        
        if cliente_selecionado:
            index = gerenciador.dados_clientes[gerenciador.dados_clientes['cliente'] == cliente_selecionado].index[0]
            cliente_data = gerenciador.dados_clientes.iloc[index]
            
            st.warning("⚠️ Confirma a exclusão deste cliente?")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.write(f"**Cliente:** {cliente_data.get('cliente', '')}")
                st.write(f"**Motorista:** {cliente_data.get('nome', '')}")
                st.write(f"**Usuário:** {cliente_data.get('usuario', '')}")
                st.write(f"**Empresa:** {cliente_data.get('empresa', '')}")
                st.write(f"**Status:** {cliente_data.get('status', '')}")
            
            col1, col2, col3 = st.columns(3)
            with col2:
                if st.button("🗑️ Confirmar Exclusão", type="primary"):
                    if gerenciador.excluir_cliente(index):
                        st.success("✅ Cliente excluído com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao excluir cliente")
    else:
        st.info("Nenhum cliente cadastrado.")

# Página: Lista de Clientes
elif pagina == "📋 Lista de Clientes":
    st.title("📋 Lista de Clientes")
    
    if gerenciador.tem_dados_clientes():
        # Filtros
        st.subheader("🔍 Filtros")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            valores_cliente = obter_valores_unicos('cliente', gerenciador.dados_clientes)
            filtro_cliente = st.selectbox("Cliente", ["Todos"] + valores_cliente)
        
        with col2:
            valores_motorista = obter_valores_unicos('nome', gerenciador.dados_clientes)
            filtro_motorista = st.selectbox("Motorista", ["Todos"] + valores_motorista)
        
        with col3:
            valores_empresa = obter_valores_unicos('empresa', gerenciador.dados_clientes)
            filtro_empresa = st.selectbox("Empresa", ["Todas"] + valores_empresa)
        
        with col4:
            filtro_status = st.selectbox("Status", ["Todos", "ATIVO", "INATIVO"])
        
        # Aplicar filtros
        dados_filtrados = gerenciador.dados_clientes.copy()
        
        if filtro_cliente != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['cliente'] == filtro_cliente]
        
        if filtro_motorista != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['nome'] == filtro_motorista]
        
        if filtro_empresa != "Todas":
            dados_filtrados = dados_filtrados[dados_filtrados['empresa'] == filtro_empresa]
        
        if filtro_status != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['status'] == filtro_status]
        
        st.subheader(f"📊 Resultados ({len(dados_filtrados)} clientes)")
        st.dataframe(dados_filtrados, use_container_width=True)
        
        # Botão de download
        if not dados_filtrados.empty:
            csv = dados_filtrados.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"clientes_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
    else:
        st.info("Nenhum cliente cadastrado.")

# Página: Gerenciar HTML
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
    
    # Navegação rápida no final
    st.markdown("---")
    
    if gerenciador_html.arquivos_html:
        st.success("💡 **Dica Rápida:** Você pode visualizar seus arquivos HTML na página principal 'Arquivos HTML'")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Ir para Visualização Principal", use_container_width=True):
                st.session_state.pagina = "📄 Arquivos HTML"
                st.rerun()
        
        with col2:
            if st.button("🏠 Voltar ao Início", use_container_width=True):
                st.session_state.pagina = "📄 Arquivos HTML"
                st.rerun()

# Informações de atualização no sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("🔄 Atualização")
if gerenciador.ultima_atualizacao:
    st.sidebar.write(f"Última atualização: {gerenciador.ultima_atualizacao.strftime('%d/%m/%Y %H:%M')}")

if st.sidebar.button("🔄 Atualizar Agora"):
    gerenciador.carregar_dados()
    st.session_state.ultima_atualizacao = datetime.now()
    st.rerun()

# Seção de Arquivos HTML no Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("🌐 Arquivos HTML")

if gerenciador_html.arquivos_html:
    st.sidebar.success(f"📁 {len(gerenciador_html.arquivos_html)} arquivo(s)")
    
    # Mostrar apenas os primeiros 3 arquivos para não poluir
    for i, arquivo in enumerate(gerenciador_html.arquivos_html[:3]):
        if st.sidebar.button(f"📄 {arquivo}", key=f"sidebar_{i}"):
            st.session_state.pagina = "📄 Arquivos HTML"
            st.session_state.arquivo_sidebar = arquivo
            st.rerun()
    
    if len(gerenciador_html.arquivos_html) > 3:
        st.sidebar.info(f"... e mais {len(gerenciador_html.arquivos_html) - 3} arquivos")
else:
    st.sidebar.info("📭 Nenhum arquivo")

# Botões de ação rápida no sidebar
col_sidebar1, col_sidebar2 = st.sidebar.columns(2)

with col_sidebar1:
    if st.button("👁️ Visualizar", use_container_width=True):
        st.session_state.pagina = "📄 Arquivos HTML"
        st.rerun()

with col_sidebar2:
    if st.button("⚙️ Gerenciar", use_container_width=True):
        st.session_state.pagina = "🌐 Gerenciar HTML"
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("Sistema atualizado automaticamente a cada 1 hora")