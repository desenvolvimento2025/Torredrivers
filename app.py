import streamlit as st
import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime, timedelta
import time
import io
import base64

# Configuração da página
st.set_page_config(
    page_title="Sistema de Motoristas",
    page_icon="🚗",
    layout="wide"
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

# Inicialização do gerenciador (sem cache para simplificar)
gerenciador = GerenciadorMotoristas()

# Sidebar para navegação
st.sidebar.title("🚗 Sistema de Motoristas")
pagina = st.sidebar.selectbox(
    "Navegação",
    ["📊 Dashboard", "👥 Cadastrar Motorista", "📤 Importar Excel", "✏️ Editar Motorista", "🗑️ Excluir Motorista", "📋 Lista Completa", 
     "🏢 Cadastrar Cliente", "✏️ Editar Cliente", "🗑️ Excluir Cliente", "📋 Lista de Clientes"]
)

# Carrega dados
if gerenciador.dados is None:
    gerenciador.carregar_dados()

# Página: Dashboard
if pagina == "📊 Dashboard":
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
        
        st.success("✅ Dashboard carregado com sucesso!")
        
    else:
        st.info("Nenhum motorista cadastrado ainda.")
        st.info("Use a página '👥 Cadastrar Motorista' para adicionar o primeiro motorista.")

# Página: Cadastrar Motorista
elif pagina == "👥 Cadastrar Motorista":
    st.title("👥 Cadastrar Novo Motorista")
    
    with st.form("form_cadastro"):
        st.subheader("Informações Básicas")
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome completo*")
            usuario = st.text_input("Usuário*")
            empresa = st.selectbox("Empresa*", ["EXPRESSO", "LOGIKA"])
            filial = st.selectbox("Filial*", ["MEA", "RIO", "CXA", "VIX", "SPO", "LGK", "NPA"])
        
        with col2:
            status = st.selectbox("Status*", ["ATIVO", "INATIVO"])
            categoria = st.selectbox("Categoria CNH", ["A", "B", "C", "D", "E"])
            placa1 = st.text_input("Placa Principal")
        
        submitted = st.form_submit_button("💾 Cadastrar Motorista")
        
        if submitted:
            if nome and usuario and empresa:
                dados_motorista = {
                    'nome': nome,
                    'usuario': usuario,
                    'grupo': 'Motorista',
                    'empresa': empresa,
                    'filial': filial,
                    'status': status,
                    'categoria': categoria,
                    'placa1': placa1,
                    'disponibilidade': 'Trabalhando',
                    'ferias': 'Não',
                    'licenca': 'Não',
                    'folga': 'Não',
                    'sobreaviso': 'Não',
                    'atestado': 'Não',
                    'com-veiculo': 'Sim'
                }
                
                # Preenche campos faltantes
                for coluna in ESTRUTURA_COLUNAS:
                    if coluna not in dados_motorista:
                        dados_motorista[coluna] = ""
                
                if gerenciador.adicionar_motorista(dados_motorista):
                    st.success("✅ Motorista cadastrado com sucesso!")
                else:
                    st.error("❌ Erro ao cadastrar motorista")
            else:
                st.warning("⚠️ Preencha os campos obrigatórios (Nome, Usuário, Empresa)")

# Página: Importar Excel
elif pagina == "📤 Importar Excel":
    st.title("📤 Importar Dados via Excel")
    st.info("Funcionalidade de importação Excel")
    st.write("Esta página permite importar dados de motoristas a partir de arquivos Excel.")

# Página: Editar Motorista
elif pagina == "✏️ Editar Motorista":
    st.title("✏️ Editar Motorista")
    
    if gerenciador.dados is not None and not gerenciador.dados.empty:
        st.selectbox("Selecione o motorista para editar", gerenciador.dados['nome'].tolist())
        st.info("Formulário de edição carregado")
    else:
        st.info("Nenhum motorista cadastrado para editar.")

# Página: Excluir Motorista
elif pagina == "🗑️ Excluir Motorista":
    st.title("🗑️ Excluir Motorista")
    
    if gerenciador.dados is not None and not gerenciador.dados.empty:
        st.selectbox("Selecione o motorista para excluir", gerenciador.dados['nome'].tolist())
        st.info("Formulário de exclusão carregado")
    else:
        st.info("Nenhum motorista cadastrado para excluir.")

# Página: Lista Completa
elif pagina == "📋 Lista Completa":
    st.title("📋 Lista Completa de Motoristas")
    
    if gerenciador.dados is not None and not gerenciador.dados.empty:
        st.dataframe(gerenciador.dados, use_container_width=True)
        st.success(f"✅ Mostrando {len(gerenciador.dados)} motoristas")
    else:
        st.info("Nenhum motorista cadastrado.")

# PÁGINAS PARA CLIENTES
elif pagina == "🏢 Cadastrar Cliente":
    st.title("🏢 Cadastrar Novo Cliente")
    st.info("Formulário de cadastro de cliente")
    st.write("Esta página permite cadastrar novos clientes associados a motoristas.")

elif pagina == "✏️ Editar Cliente":
    st.title("✏️ Editar Cliente")
    st.info("Formulário de edição de cliente")

elif pagina == "🗑️ Excluir Cliente":
    st.title("🗑️ Excluir Cliente")
    st.info("Formulário de exclusão de cliente")

elif pagina == "📋 Lista de Clientes":
    st.title("📋 Lista de Clientes")
    st.info("Lista completa de clientes")

# Adicionando métodos faltantes à classe
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

# Adiciona o método à classe
GerenciadorMotoristas.adicionar_motorista = adicionar_motorista

# Informações no sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("🔄 Sistema")
if gerenciador.ultima_atualizacao:
    st.sidebar.write(f"Última atualização: {gerenciador.ultima_atualizacao.strftime('%d/%m/%Y %H:%M')}")

if st.sidebar.button("🔄 Atualizar Dados"):
    gerenciador.carregar_dados()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("Sistema de Gestão de Motoristas")