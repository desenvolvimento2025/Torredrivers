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
            
            # Atualiza o campo 'associacao-clientes' do motorista para 'Sim'
            usuario_motorista = dados_cliente.get('usuario', '')
            if usuario_motorista:
                self.atualizar_associacao_motorista(usuario_motorista, 'Sim')
            
            return self.salvar_dados()
        except Exception as e:
            st.error(f"Erro ao adicionar cliente: {e}")
            return False
    
    def atualizar_cliente(self, index, dados_cliente):
        """Atualiza cliente existente"""
        try:
            # Obtém o usuário atual antes da atualização
            usuario_antigo = self.dados_clientes.iloc[index]['usuario']
            
            for coluna, valor in dados_cliente.items():
                if coluna in self.dados_clientes.columns:
                    self.dados_clientes.at[index, coluna] = valor
            
            # Obtém o novo usuário após a atualização
            usuario_novo = dados_cliente.get('usuario', '')
            
            # Se o usuário mudou, atualiza ambos os motoristas
            if usuario_antigo != usuario_novo:
                # Remove associação do motorista antigo
                if usuario_antigo:
                    self.atualizar_associacao_motorista(usuario_antigo, 'Não')
                # Adiciona associação ao novo motorista
                if usuario_novo:
                    self.atualizar_associacao_motorista(usuario_novo, 'Sim')
            
            return self.salvar_dados()
        except Exception as e:
            st.error(f"Erro ao atualizar cliente: {e}")
            return False
    
    def excluir_cliente(self, index):
        """Exclui cliente"""
        try:
            # Obtém o usuário do motorista associado antes de excluir
            usuario_motorista = self.dados_clientes.iloc[index]['usuario']
            
            self.dados_clientes = self.dados_clientes.drop(index).reset_index(drop=True)
            
            # Atualiza o campo 'associacao-clientes' do motorista para 'Não'
            if usuario_motorista:
                self.atualizar_associacao_motorista(usuario_motorista, 'Não')
            
            return self.salvar_dados()
        except Exception as e:
            st.error(f"Erro ao excluir cliente: {e}")
            return False

    def tem_dados_clientes(self):
        """Verifica se existem dados de clientes"""
        return self.dados_clientes is not None and not self.dados_clientes.empty

    # MÉTODOS CORRIGIDOS E ADICIONADOS
    def obter_usuarios_motoristas(self):
        """Obtém lista de usuários únicos dos motoristas"""
        try:
            if self.dados is not None and not self.dados.empty and 'usuario' in self.dados.columns:
                # Remove valores NaN e converte para string
                usuarios = self.dados['usuario'].dropna().astype(str)
                # Remove valores vazios e 'nan'
                usuarios = [u.strip() for u in usuarios.unique() if u.strip() and u.lower() != 'nan']
                return sorted(usuarios)
            return []
        except Exception as e:
            st.error(f"Erro ao obter usuários dos motoristas: {e}")
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

    def atualizar_associacao_motorista(self, usuario, valor):
        """Atualiza o campo 'associacao-clientes' do motorista"""
        try:
            if self.dados is not None and not self.dados.empty and 'usuario' in self.dados.columns:
                # Encontra o índice do motorista pelo usuário
                usuario_str = str(usuario).strip()
                self.dados['usuario'] = self.dados['usuario'].fillna('').astype(str)
                indices = self.dados[self.dados['usuario'].str.strip() == usuario_str].index
                
                if not indices.empty:
                    index_motorista = indices[0]
                    self.dados.at[index_motorista, 'associacao-clientes'] = valor
                    return True
            return False
        except Exception as e:
            st.error(f"Erro ao atualizar associação do motorista: {e}")
            return False

# Inicialização do gerenciador
@st.cache_resource
def get_gerenciador():
    return GerenciadorMotoristas()

gerenciador = get_gerenciador()

# Sidebar para navegação
st.sidebar.title("🚗 Sistema de Motoristas")
pagina = st.sidebar.selectbox(
    "Navegação",
    ["📊 Dashboard", "👥 Cadastrar Motorista", "📤 Importar Excel", "✏️ Editar Motorista", "🗑️ Excluir Motorista", "📋 Lista Completa", 
     "🏢 Cadastrar Cliente", "✏️ Editar Cliente", "🗑️ Excluir Cliente", "📋 Lista de Clientes"]
)

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
                
                st.subheader("Status Operacional")
                col5, col6 = st.columns(2)
                
                with col5:
                    com_check = st.selectbox("Com Check", ["", "Sim", "Não"],
                                           index=["", "Sim", "Não"].index(motorista_data.get('com-check', '')))
                    dirigindo = st.selectbox("Dirigindo", ["", "Sim", "Não"],
                                           index=["", "Sim", "Não"].index(motorista_data.get('dirigindo', '')))
                    parado_ate1h = st.selectbox("Parado até 1h", ["", "Sim", "Não"],
                                              index=["", "Sim", "Não"].index(motorista_data.get('parado-ate1h', '')))
                    parado1ate2h = st.selectbox("Parado 1h a 2h", ["", "Sim", "Não"],
                                              index=["", "Sim", "Não"].index(motorista_data.get('parado1ate2h', '')))
                
                with col6:
                    parado_acima2h = st.selectbox("Parado acima 2h", ["", "Sim", "Não"],
                                                index=["", "Sim", "Não"].index(motorista_data.get('parado-acima2h', '')))
                    jornada_acm80 = st.selectbox("Jornada acima 80%", ["", "Sim", "Não"],
                                               index=["", "Sim", "Não"].index(motorista_data.get('jornada-acm80', '')))
                    jornada_exced = st.selectbox("Jornada Excedida", ["", "Sim", "Não"],
                                               index=["", "Sim", "Não"].index(motorista_data.get('jornada-exced', '')))
                
                st.subheader("Jornada e Documentação")
                col7, col8 = st.columns(2)
                
                with col7:
                    sem_folga_acm7d = st.selectbox("Sem folga a partir 8d", ["", "Sim", "Não"],
                                                 index=["", "Sim", "Não"].index(motorista_data.get('sem-folga-acm7d', '')))
                    sem_folga_acm12d = st.selectbox("Sem folga a partir de 12d", ["", "Sim", "Não"],
                                                  index=["", "Sim", "Não"].index(motorista_data.get('sem-folga-acm12d', '')))
                    doc_vencendo = st.selectbox("Doc Vencendo", ["", "Sim", "Não"],
                                              index=["", "Sim", "Não"].index(motorista_data.get('doc-vencendo', '')))
                    doc_vencido = st.selectbox("Doc Vencido", ["", "Sim", "Não"],
                                             index=["", "Sim", "Não"].index(motorista_data.get('doc-vencido', '')))
                
                with col8:
                    localiz_atual = st.text_input("Última localiz pelo veículo", value=motorista_data.get('localiz-atual', ''))
                    associacao_clientes = st.selectbox("Associação a Clientes", ["", "Sim", "Não"],
                                                     index=["", "Sim", "Não"].index(motorista_data.get('associacao-clientes', '')))
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
                            'com-check': com_check,
                            'dirigindo': dirigindo,
                            'parado-ate1h': parado_ate1h,
                            'parado1ate2h': parado1ate2h,
                            'parado-acima2h': parado_acima2h,
                            'jornada-acm80': jornada_acm80,
                            'jornada-exced': jornada_exced,
                            'sem-folga-acm7d': sem_folga_acm7d,
                            'sem-folga-acm12d': sem_folga_acm12d,
                            'doc-vencendo': doc_vencendo,
                            'doc-vencido': doc_vencido,
                            'localiz-atual': localiz_atual,
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
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Dados do Motorista")
                st.write(f"**Nome:** {motorista_data.get('nome', '')}")
                st.write(f"**Usuário:** {motorista_data.get('usuario', '')}")
                st.write(f"**Empresa:** {motorista_data.get('empresa', '')}")
                st.write(f"**Status:** {motorista_data.get('status', '')}")
            
            with col2:
                st.subheader("Confirmação")
                confirmacao = st.text_input("Digite 'EXCLUIR' para confirmar")
                
                if st.button("🗑️ Excluir Permanentemente", type="primary"):
                    if confirmacao == "EXCLUIR":
                        if gerenciador.excluir_motorista(index):
                            st.success("✅ Motorista excluído com sucesso!")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao excluir motorista")
                    else:
                        st.error("❌ Digite 'EXCLUIR' para confirmar a exclusão")
    else:
        st.info("Nenhum motorista cadastrado.")

# Página: Lista Completa
elif pagina == "📋 Lista Completa":
    st.title("📋 Lista Completa de Motoristas")
    
    if gerenciador.dados is not None and not gerenciador.dados.empty:
        # Filtros
        st.subheader("🔍 Filtros")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            filtro_empresa = st.selectbox(
                "Empresa",
                ["Todas"] + obter_valores_unicos('empresa', gerenciador.dados)
            )
        
        with col2:
            filtro_status = st.selectbox(
                "Status",
                ["Todos"] + obter_valores_unicos('status', gerenciador.dados)
            )
        
        with col3:
            filtro_filial = st.selectbox(
                "Filial",
                ["Todas"] + obter_valores_unicos('filial', gerenciador.dados)
            )
        
        with col4:
            filtro_disponibilidade = st.selectbox(
                "Disponibilidade",
                ["Todas"] + obter_valores_unicos('disponibilidade', gerenciador.dados)
            )
        
        # Aplicar filtros
        dados_filtrados = gerenciador.dados.copy()
        
        if filtro_empresa != "Todas":
            dados_filtrados = dados_filtrados[dados_filtrados['empresa'] == filtro_empresa]
        
        if filtro_status != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['status'] == filtro_status]
        
        if filtro_filial != "Todas":
            dados_filtrados = dados_filtrados[dados_filtrados['filial'] == filtro_filial]
        
        if filtro_disponibilidade != "Todas":
            dados_filtrados = dados_filtrados[dados_filtrados['disponibilidade'] == filtro_disponibilidade]
        
        # Mostrar estatísticas dos filtros
        st.info(f"📊 Mostrando {len(dados_filtrados)} de {len(gerenciador.dados)} motoristas")
        
        # Seleção de colunas para exibição
        st.subheader("👁️ Colunas para Exibição")
        
        colunas_selecionadas = st.multiselect(
            "Selecione as colunas para exibir",
            options=COLUNAS_PRINCIPAIS,
            default=COLUNAS_PRINCIPAIS[:8]  # Primeiras 8 colunas por padrão
        )
        
        if not colunas_selecionadas:
            colunas_selecionadas = COLUNAS_PRINCIPAIS[:8]
        
        # Tabela de dados
        st.subheader("📊 Dados dos Motoristas")
        st.dataframe(dados_filtrados[colunas_selecionadas], use_container_width=True)
        
        # Botão de download
        st.subheader("📥 Exportar Dados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Download como CSV
            csv = dados_filtrados[colunas_selecionadas].to_csv(index=False)
            st.download_button(
                label="📄 Baixar como CSV",
                data=csv,
                file_name=f"motoristas_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Download como Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                dados_filtrados[colunas_selecionadas].to_excel(writer, sheet_name='motoristas', index=False)
            
            st.download_button(
                label="📊 Baixar como Excel",
                data=buffer.getvalue(),
                file_name=f"motoristas_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.ms-excel"
            )
    
    else:
        st.info("Nenhum motorista cadastrado ainda.")

# PÁGINAS DE CLIENTES

# Página: Cadastrar Cliente
elif pagina == "🏢 Cadastrar Cliente":
    st.title("🏢 Cadastrar Novo Cliente")
    
    # Carrega os dados primeiro
    if gerenciador.dados is None:
        gerenciador.carregar_dados()
    
    # Verifica se há motoristas cadastrados
    if gerenciador.dados is not None and not gerenciador.dados.empty:
        # Obtém a lista de usuários dos motoristas
        usuarios_motoristas = gerenciador.obter_usuarios_motoristas()
        
        with st.form("form_cliente"):
            st.subheader("Informações do Cliente")
            col1, col2 = st.columns(2)
            
            with col1:
                cliente = st.text_input("Cliente*")
                nome = st.text_input("Nome*")
                usuario = st.selectbox(
                    "Usuário do Motorista*",
                    options=[""] + usuarios_motoristas,
                    help="Selecione o usuário do motorista associado a este cliente"
                )
            
            with col2:
                empresa = st.selectbox("Empresa*", ["EXPRESSO", "LOGIKA"])
                filial = st.selectbox("Filial*", ["MEA", "RIO", "CXA", "VIX", "SPO", "LGK", "NPA"])
                status = st.selectbox("Status*", ["ATIVO", "INATIVO"])
            
            # Mostra o nome do motorista se um usuário for selecionado
            if usuario:
                nome_motorista = gerenciador.obter_nome_por_usuario(usuario)
                if nome_motorista:
                    st.info(f"**Motorista associado:** {nome_motorista}")
                else:
                    st.warning("Usuário não encontrado na base de motoristas")
            
            submitted = st.form_submit_button("💾 Cadastrar Cliente")
            
            if submitted:
                if cliente and nome and usuario and empresa:
                    dados_cliente = {
                        'cliente': cliente,
                        'nome': nome,
                        'usuario': usuario,
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
                    st.warning("⚠️ Preencha os campos obrigatórios (Cliente, Nome, Usuário, Empresa)")
    else:
        st.warning("⚠️ Não há motoristas cadastrados. Cadastre motoristas primeiro.")

# Página: Editar Cliente
elif pagina == "✏️ Editar Cliente":
    st.title("✏️ Editar Cliente")
    
    if gerenciador.tem_dados_clientes():
        cliente_selecionado = st.selectbox(
            "Selecione o cliente para editar",
            gerenciador.dados_clientes['cliente'].tolist()
        )
        
        if cliente_selecionado:
            index = gerenciador.dados_clientes[gerenciador.dados_clientes['cliente'] == cliente_selecionado].index[0]
            cliente_data = gerenciador.dados_clientes.iloc[index]
            
            # Carrega os usuários disponíveis dos motoristas
            usuarios_motoristas = gerenciador.obter_usuarios_motoristas()
            
            with st.form("form_edicao_cliente"):
                st.subheader("Informações do Cliente")
                col1, col2 = st.columns(2)
                
                with col1:
                    cliente = st.text_input("Cliente*", value=cliente_data.get('cliente', ''))
                    nome = st.text_input("Nome*", value=cliente_data.get('nome', ''))
                    
                    # Encontra o índice do usuário atual na lista
                    usuario_atual = cliente_data.get('usuario', '')
                    indice_usuario = 0
                    if usuario_atual in usuarios_motoristas:
                        indice_usuario = usuarios_motoristas.index(usuario_atual) + 1
                    
                    usuario = st.selectbox(
                        "Usuário do Motorista*",
                        options=[""] + usuarios_motoristas,
                        index=indice_usuario
                    )
                
                with col2:
                    empresa = st.selectbox("Empresa*", ["EXPRESSO", "LOGIKA"],
                                         index=["EXPRESSO", "LOGIKA"].index(cliente_data.get('empresa', 'EXPRESSO')))
                    filial = st.selectbox("Filial*", ["MEA", "RIO", "CXA", "VIX", "SPO", "LGK", "NPA"],
                                        index=["MEA", "RIO", "CXA", "VIX", "SPO", "LGK", "NPA"].index(cliente_data.get('filial', 'SPO')))
                    status = st.selectbox("Status*", ["ATIVO", "INATIVO"],
                                        index=["ATIVO", "INATIVO"].index(cliente_data.get('status', 'ATIVO')))
                
                # Mostra o nome do motorista se um usuário for selecionado
                if usuario:
                    nome_motorista = gerenciador.obter_nome_por_usuario(usuario)
                    if nome_motorista:
                        st.info(f"**Motorista associado:** {nome_motorista}")
                    else:
                        st.warning("Usuário não encontrado na base de motoristas")
                
                submitted = st.form_submit_button("💾 Atualizar Cliente")
                
                if submitted:
                    if cliente and nome and usuario and empresa:
                        dados_atualizados = {
                            'cliente': cliente,
                            'nome': nome,
                            'usuario': usuario,
                            'empresa': empresa,
                            'filial': filial,
                            'status': status
                        }
                        
                        if gerenciador.atualizar_cliente(index, dados_atualizados):
                            st.success("✅ Cliente atualizado com sucesso!")
                            st.balloons()
                        else:
                            st.error("❌ Erro ao atualizar cliente")
                    else:
                        st.warning("⚠️ Preencha os campos obrigatórios (Cliente, Nome, Usuário, Empresa)")
    else:
        st.info("Nenhum cliente cadastrado para editar.")

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
            
            st.warning("⚠️ **Atenção:** Esta ação não pode ser desfeita!")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Dados do Cliente")
                st.write(f"**Cliente:** {cliente_data.get('cliente', '')}")
                st.write(f"**Nome:** {cliente_data.get('nome', '')}")
                st.write(f"**Usuário do Motorista:** {cliente_data.get('usuario', '')}")
                st.write(f"**Empresa:** {cliente_data.get('empresa', '')}")
                st.write(f"**Status:** {cliente_data.get('status', '')}")
            
            with col2:
                st.subheader("Confirmação")
                confirmacao = st.text_input("Digite 'EXCLUIR' para confirmar")
                
                if st.button("🗑️ Excluir Permanentemente", type="primary"):
                    if confirmacao == "EXCLUIR":
                        if gerenciador.excluir_cliente(index):
                            st.success("✅ Cliente excluído com sucesso!")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao excluir cliente")
                    else:
                        st.error("❌ Digite 'EXCLUIR' para confirmar a exclusão")
    else:
        st.info("Nenhum cliente cadastrado.")

# Página: Lista de Clientes
elif pagina == "📋 Lista de Clientes":
    st.title("📋 Lista de Clientes")
    
    if gerenciador.tem_dados_clientes():
        # Filtros
        st.subheader("🔍 Filtros")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filtro_empresa = st.selectbox(
                "Empresa",
                ["Todas"] + obter_valores_unicos('empresa', gerenciador.dados_clientes)
            )
        
        with col2:
            filtro_status = st.selectbox(
                "Status",
                ["Todos"] + obter_valores_unicos('status', gerenciador.dados_clientes)
            )
        
        with col3:
            filtro_filial = st.selectbox(
                "Filial",
                ["Todas"] + obter_valores_unicos('filial', gerenciador.dados_clientes)
            )
        
        # Aplicar filtros
        dados_filtrados = gerenciador.dados_clientes.copy()
        
        if filtro_empresa != "Todas":
            dados_filtrados = dados_filtrados[dados_filtrados['empresa'] == filtro_empresa]
        
        if filtro_status != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['status'] == filtro_status]
        
        if filtro_filial != "Todas":
            dados_filtrados = dados_filtrados[dados_filtrados['filial'] == filtro_filial]
        
        # Mostrar estatísticas dos filtros
        st.info(f"📊 Mostrando {len(dados_filtrados)} de {len(gerenciador.dados_clientes)} clientes")
        
        # Tabela de dados
        st.subheader("📊 Dados dos Clientes")
        st.dataframe(dados_filtrados, use_container_width=True)
        
        # Botão de download
        st.subheader("📥 Exportar Dados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Download como CSV
            csv = dados_filtrados.to_csv(index=False)
            st.download_button(
                label="📄 Baixar como CSV",
                data=csv,
                file_name=f"clientes_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Download como Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                dados_filtrados.to_excel(writer, sheet_name='clientes', index=False)
            
            st.download_button(
                label="📊 Baixar como Excel",
                data=buffer.getvalue(),
                file_name=f"clientes_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.ms-excel"
            )
    
    else:
        st.info("Nenhum cliente cadastrado ainda.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Desenvolvido por**  
    Sistema de Gestão de Motoristas  
    Versão 2.0
    """
)

# Atualização automática dos dados
if st.sidebar.button("🔄 Atualizar Dados"):
    gerenciador.carregar_dados()
    st.success("✅ Dados atualizados!")
    st.rerun()

# Informações do sistema
if gerenciador.ultima_atualizacao:
    st.sidebar.info(f"📅 Última atualização: {gerenciador.ultima_atualizacao.strftime('%d/%m/%Y %H:%M')}")