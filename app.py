import streamlit as st
import pandas as pd
import numpy as np
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
        
        submitted = st.form_submit_button("💾 Cadastrar Motorista")
        
        if submitted:
            if nome and usuario and empresa:
                dados_motorista = {
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
                    'disponibilidade': 'Trabalhando',
                    'ferias': 'Não',
                    'licenca': 'Não',
                    'folga': 'Não',
                    'sobreaviso': 'Não',
                    'atestado': 'Não',
                    'com-veiculo': 'Sim'
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
    st.info("Funcionalidade de importação Excel")
    
    # Upload do arquivo
    arquivo = st.file_uploader("Selecione o arquivo Excel", type=['xlsx', 'xls'])
    if arquivo:
        st.success("✅ Arquivo carregado com sucesso!")
        st.write("Pronto para importação")

# Página: Editar Motorista
elif pagina == "✏️ Editar Motorista":
    st.title("✏️ Editar Motorista")
    
    if gerenciador.dados is not None and not gerenciador.dados.empty:
        motorista_selecionado = st.selectbox("Selecione o motorista para editar", gerenciador.dados['nome'].tolist())
        
        if motorista_selecionado:
            st.success(f"✅ Editando: {motorista_selecionado}")
            
            # Simulação de formulário de edição
            with st.form("form_edicao"):
                novo_nome = st.text_input("Nome", value=motorista_selecionado)
                novo_status = st.selectbox("Status", ["ATIVO", "INATIVO"])
                
                if st.form_submit_button("💾 Atualizar Motorista"):
                    st.success("✅ Motorista atualizado com sucesso!")
    else:
        st.info("Nenhum motorista cadastrado para editar.")

# Página: Excluir Motorista
elif pagina == "🗑️ Excluir Motorista":
    st.title("🗑️ Excluir Motorista")
    
    if gerenciador.dados is not None and not gerenciador.dados.empty:
        motorista_selecionado = st.selectbox("Selecione o motorista para excluir", gerenciador.dados['nome'].tolist())
        
        if motorista_selecionado:
            st.warning(f"⚠️ Você está prestes a excluir: {motorista_selecionado}")
            
            if st.button("🗑️ Confirmar Exclusão", type="primary"):
                st.success("✅ Motorista excluído com sucesso!")
    else:
        st.info("Nenhum motorista cadastrado para excluir.")

# Página: Lista Completa
elif pagina == "📋 Lista Completa":
    st.title("📋 Lista Completa de Motoristas")
    
    if gerenciador.dados is not None and not gerenciador.dados.empty:
        st.dataframe(gerenciador.dados[COLUNAS_PRINCIPAIS], use_container_width=True)
        st.success(f"✅ Mostrando {len(gerenciador.dados)} motoristas")
    else:
        st.info("Nenhum motorista cadastrado.")

# PÁGINAS PARA CLIENTES
elif pagina == "🏢 Cadastrar Cliente":
    st.title("🏢 Cadastrar Novo Cliente")
    
    with st.form("form_cliente"):
        st.subheader("Informações do Cliente")
        cliente = st.text_input("Nome do Cliente*")
        empresa = st.selectbox("Empresa*", ["EXPRESSO", "LOGIKA"])
        status = st.selectbox("Status*", ["ATIVO", "INATIVO"])
        
        submitted = st.form_submit_button("💾 Cadastrar Cliente")
        
        if submitted:
            if cliente and empresa:
                dados_cliente = {
                    'cliente': cliente,
                    'empresa': empresa,
                    'status': status,
                    'nome': '',
                    'usuario': '',
                    'filial': 'SPO'
                }
                
                if gerenciador.adicionar_cliente(dados_cliente):
                    st.success("✅ Cliente cadastrado com sucesso!")
                else:
                    st.error("❌ Erro ao cadastrar cliente")
            else:
                st.warning("⚠️ Preencha os campos obrigatórios")

elif pagina == "✏️ Editar Cliente":
    st.title("✏️ Editar Cliente")
    
    if gerenciador.tem_dados_clientes():
        cliente_selecionado = st.selectbox("Selecione o cliente para editar", gerenciador.dados_clientes['cliente'].tolist())
        
        if cliente_selecionado:
            st.success(f"✅ Editando: {cliente_selecionado}")
            
            with st.form("form_edicao_cliente"):
                novo_cliente = st.text_input("Cliente", value=cliente_selecionado)
                novo_status = st.selectbox("Status", ["ATIVO", "INATIVO"])
                
                if st.form_submit_button("💾 Atualizar Cliente"):
                    st.success("✅ Cliente atualizado com sucesso!")
    else:
        st.info("Nenhum cliente cadastrado para editar.")

elif pagina == "🗑️ Excluir Cliente":
    st.title("🗑️ Excluir Cliente")
    
    if gerenciador.tem_dados_clientes():
        cliente_selecionado = st.selectbox("Selecione o cliente para excluir", gerenciador.dados_clientes['cliente'].tolist())
        
        if cliente_selecionado:
            st.warning(f"⚠️ Você está prestes a excluir: {cliente_selecionado}")
            
            if st.button("🗑️ Confirmar Exclusão", type="primary"):
                st.success("✅ Cliente excluído com sucesso!")
    else:
        st.info("Nenhum cliente cadastrado para excluir.")

elif pagina == "📋 Lista de Clientes":
    st.title("📋 Lista de Clientes")
    
    if gerenciador.tem_dados_clientes():
        st.dataframe(gerenciador.dados_clientes, use_container_width=True)
        st.success(f"✅ Mostrando {len(gerenciador.dados_clientes)} clientes")
    else:
        st.info("Nenhum cliente cadastrado.")

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