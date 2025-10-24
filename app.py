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

# ESTRUTURA PARA TABELA CLIENTES
ESTRUTURA_CLIENTES = [
    'Cliente', 'Nome', 'Usuario'
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
                    # Reordena as colunas conforme a estrutura
                    self.dados_clientes = self.dados_clientes[ESTRUTURA_CLIENTES]
                except:
                    # Se não existir a sheet de clientes, cria uma vazia
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
            if not self.dados.empty:
                for coluna in ESTRUTURA_COLUNAS:
                    if coluna not in self.dados.columns:
                        self.dados[coluna] = ""
                self.dados = self.dados[ESTRUTURA_COLUNAS]
            
            # Garante a ordem correta das colunas para clientes
            if not self.dados_clientes.empty:
                for coluna in ESTRUTURA_CLIENTES:
                    if coluna not in self.dados_clientes.columns:
                        self.dados_clientes[coluna] = ""
                self.dados_clientes = self.dados_clientes[ESTRUTURA_CLIENTES]
            
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
            if not self.dados.empty:
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

    # MÉTODOS PARA GERENCIAR CLIENTES
    def obter_lista_motoristas(self):
        """Obtém lista de motoristas para seleção"""
        if self.dados is not None and not self.dados.empty:
            motoristas = []
            for _, row in self.dados.iterrows():
                nome = row.get('nome', '')
                usuario = row.get('usuario', '')
                if nome and usuario:
                    motoristas.append({'nome': nome, 'usuario': usuario})
            return motoristas
        return []

    def adicionar_cliente(self, dados_cliente):
        """Adiciona novo cliente"""
        try:
            dados_completos = {}
            for coluna in ESTRUTURA_CLIENTES:
                dados_completos[coluna] = dados_cliente.get(coluna, "")
            
            novo_registro = pd.DataFrame([dados_completos])
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

# Inicialização do gerenciador
@st.cache_resource
def get_gerenciador():
    return GerenciadorMotoristas()

gerenciador = get_gerenciador()

# Sidebar para navegação
st.sidebar.title("🚗 Sistema de Motoristas")
pagina = st.sidebar.selectbox(
    "Navegação",
    ["📊 Dashboard", "👥 Cadastrar Motorista", "📤 Importar Excel", "✏️ Editar Motorista", "🗑️ Excluir Motorista", "📋 Lista Completa", "👥 Gerenciar Clientes"]
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
        if coluna in dados.columns:
            valores = dados[coluna].unique().tolist()
            # Remove valores NaN/None
            valores = [v for v in valores if pd.notna(v) and v != ""]
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
                            'doc-vencendo': doc_vencendo,
                            'doc-vencido': doc_vencido,
                            'localiz-atual': localiz_atual,
                            'associacao-clientes': associacao_clientes,
                            'interj-menor8': interj_menor8,
                            'interj-maior8': interj_maior8
                        }
                        
                        if gerenciador.atualizar_motorista(index, dados_atualizados):
                            st.success("✅ Motorista atualizado com sucesso!")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao atualizar motorista")
                    else:
                        st.warning("⚠️ Preencha os campos obrigatórios")
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
            
            st.warning("⚠️ Confirma a exclusão deste motorista?")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.write(f"**Nome:** {motorista_data.get('nome', '')}")
                st.write(f"**Usuário:** {motorista_data.get('usuario', '')}")
                st.write(f"**Empresa:** {motorista_data.get('empresa', '')}")
                st.write(f"**Status:** {motorista_data.get('status', '')}")
            
            col1, col2, col3 = st.columns(3)
            with col2:
                if st.button("🗑️ Confirmar Exclusão", type="primary"):
                    if gerenciador.excluir_motorista(index):
                        st.success("✅ Motorista excluído com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao excluir motorista")
    else:
        st.info("Nenhum motorista cadastrado para excluir.")

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
        
        # Estatísticas dos filtros
        st.info(f"📊 Mostrando {len(dados_filtrados)} de {len(gerenciador.dados)} motoristas")
        
        # Seleção de colunas para exibição
        st.subheader("👁️ Colunas para Exibição")
        colunas_selecionadas = st.multiselect(
            "Selecione as colunas para exibir",
            options=COLUNAS_PRINCIPAIS,
            default=COLUNAS_PRINCIPAIS
        )
        
        if not colunas_selecionadas:
            colunas_selecionadas = ['nome', 'usuario', 'empresa', 'status']
        
        # Exibir dados
        if not dados_filtrados.empty:
            dados_exibicao = dados_filtrados[colunas_selecionadas]
            st.dataframe(dados_exibicao, use_container_width=True)
            
            # Botão de download
            st.subheader("📥 Download dos Dados Filtrados")
            col1, col2 = st.columns(2)
            
            with col1:
                # Download como CSV
                csv = dados_exibicao.to_csv(index=False)
                st.download_button(
                    label="💾 Baixar como CSV",
                    data=csv,
                    file_name=f"motoristas_filtrados_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Download como Excel
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    dados_exibicao.to_excel(writer, sheet_name='motoristas', index=False)
                
                st.download_button(
                    label="📊 Baixar como Excel",
                    data=buffer.getvalue(),
                    file_name=f"motoristas_filtrados_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.ms-excel"
                )
        else:
            st.warning("Nenhum motorista encontrado com os filtros aplicados.")
    else:
        st.info("Nenhum motorista cadastrado.")

# Página: Gerenciar Clientes
elif pagina == "👥 Gerenciar Clientes":
    st.title("👥 Gerenciar Clientes")
    
    # Carrega dados dos clientes
    gerenciador.carregar_dados()
    
    # Subpáginas para clientes
    subpagina_cliente = st.sidebar.selectbox(
        "Operações",
        ["📋 Lista de Clientes", "➕ Cadastrar Cliente", "✏️ Editar Cliente", "🗑️ Excluir Cliente"]
    )
    
    # Obtém lista de motoristas para seleção
    lista_motoristas = gerenciador.obter_lista_motoristas()
    
    if subpagina_cliente == "📋 Lista de Clientes":
        st.subheader("📋 Lista de Clientes Cadastrados")
        
        if gerenciador.dados_clientes is not None and not gerenciador.dados_clientes.empty:
            st.dataframe(gerenciador.dados_clientes, use_container_width=True)
            
            # Estatísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Clientes", len(gerenciador.dados_clientes))
            with col2:
                clientes_unicos = gerenciador.dados_clientes['Cliente'].nunique()
                st.metric("Clientes Únicos", clientes_unicos)
            with col3:
                motoristas_associados = gerenciador.dados_clientes['Nome'].nunique()
                st.metric("Motoristas Associados", motoristas_associados)
        else:
            st.info("Nenhum cliente cadastrado ainda.")
    
    elif subpagina_cliente == "➕ Cadastrar Cliente":
        st.subheader("➕ Cadastrar Novo Cliente")
        
        with st.form("form_cliente"):
            cliente = st.text_input("Nome do Cliente*")
            
            # Seleção do motorista
            if lista_motoristas:
                nomes_motoristas = [f"{m['nome']} ({m['usuario']})" for m in lista_motoristas]
                motorista_selecionado = st.selectbox(
                    "Selecione o Motorista*",
                    nomes_motoristas,
                    help="Lista de motoristas cadastrados no sistema"
                )
                
                # Extrai nome e usuário do motorista selecionado
                if motorista_selecionado:
                    nome_motorista = motorista_selecionado.split(" (")[0]
                    usuario_motorista = motorista_selecionado.split(" (")[1].replace(")", "")
                else:
                    nome_motorista = ""
                    usuario_motorista = ""
            else:
                st.warning("Nenhum motorista cadastrado no sistema. Cadastre motoristas primeiro.")
                nome_motorista = ""
                usuario_motorista = ""
            
            submitted = st.form_submit_button("💾 Cadastrar Cliente")
            
            if submitted:
                if cliente and nome_motorista and usuario_motorista:
                    dados_cliente = {
                        'Cliente': cliente,
                        'Nome': nome_motorista,
                        'Usuario': usuario_motorista
                    }
                    
                    if gerenciador.adicionar_cliente(dados_cliente):
                        st.success("✅ Cliente cadastrado com sucesso!")
                        st.balloons()
                    else:
                        st.error("❌ Erro ao cadastrar cliente")
                else:
                    st.warning("⚠️ Preencha todos os campos obrigatórios")
    
    elif subpagina_cliente == "✏️ Editar Cliente":
        st.subheader("✏️ Editar Cliente")
        
        if gerenciador.dados_clientes is not None and not gerenciador.dados_clientes.empty:
            # Seleção do cliente para editar
            clientes_lista = [f"{row['Cliente']} - {row['Nome']} ({row['Usuario']})" 
                            for _, row in gerenciador.dados_clientes.iterrows()]
            
            cliente_selecionado = st.selectbox(
                "Selecione o cliente para editar",
                clientes_lista
            )
            
            if cliente_selecionado:
                index = clientes_lista.index(cliente_selecionado)
                cliente_data = gerenciador.dados_clientes.iloc[index]
                
                with st.form("form_editar_cliente"):
                    cliente = st.text_input("Nome do Cliente*", value=cliente_data.get('Cliente', ''))
                    
                    # Seleção do motorista
                    if lista_motoristas:
                        nomes_motoristas = [f"{m['nome']} ({m['usuario']})" for m in lista_motoristas]
                        motorista_atual = f"{cliente_data.get('Nome', '')} ({cliente_data.get('Usuario', '')})"
                        
                        if motorista_atual in nomes_motoristas:
                            index_motorista = nomes_motoristas.index(motorista_atual)
                        else:
                            index_motorista = 0
                            
                        motorista_selecionado = st.selectbox(
                            "Selecione o Motorista*",
                            nomes_motoristas,
                            index=index_motorista
                        )
                        
                        # Extrai nome e usuário do motorista selecionado
                        if motorista_selecionado:
                            nome_motorista = motorista_selecionado.split(" (")[0]
                            usuario_motorista = motorista_selecionado.split(" (")[1].replace(")", "")
                        else:
                            nome_motorista = ""
                            usuario_motorista = ""
                    else:
                        st.warning("Nenhum motorista cadastrado no sistema.")
                        nome_motorista = cliente_data.get('Nome', '')
                        usuario_motorista = cliente_data.get('Usuario', '')
                    
                    submitted = st.form_submit_button("💾 Atualizar Cliente")
                    
                    if submitted:
                        if cliente and nome_motorista and usuario_motorista:
                            dados_cliente = {
                                'Cliente': cliente,
                                'Nome': nome_motorista,
                                'Usuario': usuario_motorista
                            }
                            
                            if gerenciador.atualizar_cliente(index, dados_cliente):
                                st.success("✅ Cliente atualizado com sucesso!")
                                st.rerun()
                            else:
                                st.error("❌ Erro ao atualizar cliente")
                        else:
                            st.warning("⚠️ Preencha todos os campos obrigatórios")
        else:
            st.info("Nenhum cliente cadastrado para editar.")
    
    elif subpagina_cliente == "🗑️ Excluir Cliente":
        st.subheader("🗑️ Excluir Cliente")
        
        if gerenciador.dados_clientes is not None and not gerenciador.dados_clientes.empty:
            # Seleção do cliente para excluir
            clientes_lista = [f"{row['Cliente']} - {row['Nome']} ({row['Usuario']})" 
                            for _, row in gerenciador.dados_clientes.iterrows()]
            
            cliente_selecionado = st.selectbox(
                "Selecione o cliente para excluir",
                clientes_lista
            )
            
            if cliente_selecionado:
                index = clientes_lista.index(cliente_selecionado)
                cliente_data = gerenciador.dados_clientes.iloc[index]
                
                st.warning("⚠️ Confirma a exclusão deste cliente?")
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.write(f"**Cliente:** {cliente_data.get('Cliente', '')}")
                    st.write(f"**Motorista:** {cliente_data.get('Nome', '')}")
                    st.write(f"**Usuário:** {cliente_data.get('Usuario', '')}")
                
                col1, col2, col3 = st.columns(3)
                with col2:
                    if st.button("🗑️ Confirmar Exclusão", type="primary"):
                        if gerenciador.excluir_cliente(index):
                            st.success("✅ Cliente excluído com sucesso!")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao excluir cliente")
        else:
            st.info("Nenhum cliente cadastrado para excluir.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Desenvolvido por**  
    Sistema de Gestão de Motoristas  
    Versão 2.0 - Com Módulo de Clientes
    """
)

# Atualização automática de dados
if gerenciador.ultima_atualizacao:
    tempo_atualizacao = datetime.now() - gerenciador.ultima_atualizacao
    if tempo_atualizacao.total_seconds() > 300:  # 5 minutos
        gerenciador.carregar_dados()
        st.sidebar.info("🔄 Dados atualizados automaticamente")