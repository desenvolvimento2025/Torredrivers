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

# ESTRUTURA EXATA DA SUA TABELA - MESMA ORDEM E NOMES
ESTRUTURA_COLUNAS = [
    'nome', 'usuario', 'grupo', 'empresa', 'filial', 'status', 'status1', 'status2', 'status3',
    'com-atend', 'sem-atend', 'com-veiculo', 'sem-veiculo', 'com-check', 'sem-check', 'dirigindo', 'parado',
    'parado-ate1h', 'parado1ate2h', 'parado-acima2h', 'jornada-acm80', 'jornada-exced', 'sem-folga-acm7d',
    'sem-folga-acm12d', 'categoria', 'doc-vencendo', 'doc-vencido', 'localiz-atual', 'agenda-pro',
    'agenda-anda', 'agenda-con', 'projeto-pro', 'projeto-anda', 'projeto-con', 'interj-menor8',
    'interj-maior8', 'placa1', 'placa2', 'placa3', 'status-log1', 'status-log2'
]

COLUNAS_PRINCIPAIS = [
    'nome', 'usuario', 'grupo', 'empresa', 'filial', 'status', 
    'categoria', 'placa1', 'placa2', 'placa3', 'localiz-atual'
]

# Classe para gerenciamento de dados
class GerenciadorMotoristas:
    def __init__(self):
        self.arquivo_excel = "tabela-motoristas.xlsx"
        self.ultima_atualizacao = None
        self.dados = None
        
    def carregar_dados(self):
        """Carrega dados do arquivo Excel"""
        try:
            if os.path.exists(self.arquivo_excel):
                self.dados = pd.read_excel(self.arquivo_excel, sheet_name='motoristas')
                # Garante que todas as colunas existam na ordem correta
                for coluna in ESTRUTURA_COLUNAS:
                    if coluna not in self.dados.columns:
                        self.dados[coluna] = ""
                # Reordena as colunas conforme a estrutura
                self.dados = self.dados[ESTRUTURA_COLUNAS]
                self.ultima_atualizacao = datetime.now()
                return True
            else:
                # Cria dataframe vazio com a estrutura exata
                self.dados = pd.DataFrame(columns=ESTRUTURA_COLUNAS)
                self.salvar_dados()
                return True
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
            return False
    
    def salvar_dados(self):
        """Salva dados no arquivo Excel mantendo a estrutura"""
        try:
            # Garante a ordem correta das colunas
            if not self.dados.empty:
                for coluna in ESTRUTURA_COLUNAS:
                    if coluna not in self.dados.columns:
                        self.dados[coluna] = ""
                self.dados = self.dados[ESTRUTURA_COLUNAS]
            
            with pd.ExcelWriter(self.arquivo_excel, engine='openpyxl') as writer:
                self.dados.to_excel(writer, sheet_name='motoristas', index=False)
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

# Inicialização do gerenciador
@st.cache_resource
def get_gerenciador():
    return GerenciadorMotoristas()

gerenciador = get_gerenciador()

# Sidebar para navegação
st.sidebar.title("🚗 Sistema de Motoristas")
pagina = st.sidebar.selectbox(
    "Navegação",
    ["📊 Dashboard", "👥 Cadastrar Motorista", "📤 Importar Excel", "✏️ Editar Motorista", "🗑️ Excluir Motorista", "📋 Lista Completa"]
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

# Página: Dashboard
if pagina == "📊 Dashboard":
    st.title("📊 Dashboard de Motoristas")
    
    if gerenciador.dados is not None and not gerenciador.dados.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_motoristas = len(gerenciador.dados)
            st.metric("Total de Motoristas", total_motoristas)
        
        with col2:
            ativos = len(gerenciador.dados[gerenciador.dados['status'] == 'Ativo'])
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
            grupo = st.text_input("Grupo")
            empresa = st.text_input("Empresa*")
            filial = st.text_input("Filial")
        
        with col2:
            status = st.selectbox("Status*", ["Ativo", "Inativo", "Férias", "Afastado"])
            categoria = st.selectbox("Categoria CNH", ["A", "B", "C", "D", "E"])
            placa1 = st.text_input("Placa Principal")
            placa2 = st.text_input("Placa Secundária")
            placa3 = st.text_input("Placa Terciária")
        
        st.subheader("Status Operacional")
        col3, col4 = st.columns(2)
        
        with col3:
            com_atend = st.selectbox("Com Atendimento", ["", "Sim", "Não"])
            sem_atend = st.selectbox("Sem Atendimento", ["", "Sim", "Não"])
            com_veiculo = st.selectbox("Com Veículo", ["", "Sim", "Não"])
            sem_veiculo = st.selectbox("Sem Veículo", ["", "Sim", "Não"])
            com_check = st.selectbox("Com Check", ["", "Sim", "Não"])
            sem_check = st.selectbox("Sem Check", ["", "Sim", "Não"])
        
        with col4:
            dirigindo = st.selectbox("Dirigindo", ["", "Sim", "Não"])
            parado = st.selectbox("Parado", ["", "Sim", "Não"])
            parado_ate1h = st.selectbox("Parado até 1h", ["", "Sim", "Não"])
            parado1ate2h = st.selectbox("Parado 1h a 2h", ["", "Sim", "Não"])
            parado_acima2h = st.selectbox("Parado acima 2h", ["", "Sim", "Não"])
        
        st.subheader("Jornada e Documentação")
        col5, col6 = st.columns(2)
        
        with col5:
            jornada_acm80 = st.selectbox("Jornada até 80%", ["", "Sim", "Não"])
            jornada_exced = st.selectbox("Jornada Excedida", ["", "Sim", "Não"])
            sem_folga_acm7d = st.selectbox("Sem folga até 7d", ["", "Sim", "Não"])
            sem_folga_acm12d = st.selectbox("Sem folga até 12d", ["", "Sim", "Não"])
            doc_vencendo = st.selectbox("Doc Vencendo", ["", "Sim", "Não"])
            doc_vencido = st.selectbox("Doc Vencido", ["", "Sim", "Não"])
        
        with col6:
            localiz_atual = st.text_input("Localização Atual")
            agenda_pro = st.text_input("Agenda Próxima")
            agenda_anda = st.text_input("Agenda Andamento")
            agenda_con = st.text_input("Agenda Concluída")
            projeto_pro = st.text_input("Projeto Próximo")
            projeto_anda = st.text_input("Projeto Andamento")
            projeto_con = st.text_input("Projeto Concluído")
        
        st.subheader("Informações Adicionais")
        col7, col8 = st.columns(2)
        
        with col7:
            interj_menor8 = st.text_input("Interjornada < 8h")
            interj_maior8 = st.text_input("Interjornada > 8h")
            status_log1 = st.text_input("Status Log 1")
            status_log2 = st.text_input("Status Log 2")
        
        with col8:
            status1 = st.text_input("Status 1")
            status2 = st.text_input("Status 2")
            status3 = st.text_input("Status 3")
        
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
                    
                    # Status operacional
                    'com-atend': com_atend,
                    'sem-atend': sem_atend,
                    'com-veiculo': com_veiculo,
                    'sem-veiculo': sem_veiculo,
                    'com-check': com_check,
                    'sem-check': sem_check,
                    'dirigindo': dirigindo,
                    'parado': parado,
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
                    
                    # Localização e agenda
                    'localiz-atual': localiz_atual,
                    'agenda-pro': agenda_pro,
                    'agenda-anda': agenda_anda,
                    'agenda-con': agenda_con,
                    
                    # Projetos
                    'projeto-pro': projeto_pro,
                    'projeto-anda': projeto_anda,
                    'projeto-con': projeto_con,
                    
                    # Interjornada
                    'interj-menor8': interj_menor8,
                    'interj-maior8': interj_maior8,
                    
                    # Status adicionais
                    'status1': status1,
                    'status2': status2,
                    'status3': status3,
                    'status-log1': status_log1,
                    'status-log2': status_log2
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
        'empresa': 'Transportes ABC',
        'status': 'Ativo',
        'categoria': 'D',
        'filial': 'São Paulo',
        'com-veiculo': 'Sim',
        'doc-vencido': 'Não'
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
                    grupo = st.text_input("Grupo", value=motorista_data.get('grupo', ''))
                    empresa = st.text_input("Empresa*", value=motorista_data.get('empresa', ''))
                    filial = st.text_input("Filial", value=motorista_data.get('filial', ''))
                
                with col2:
                    status = st.selectbox(
                        "Status*", 
                        ["Ativo", "Inativo", "Férias", "Afastado"],
                        index=["Ativo", "Inativo", "Férias", "Afastado"].index(motorista_data.get('status', 'Ativo'))
                    )
                    categoria = st.selectbox(
                        "Categoria CNH", 
                        ["A", "B", "C", "D", "E"],
                        index=["A", "B", "C", "D", "E"].index(motorista_data.get('categoria', 'B'))
                    )
                    placa1 = st.text_input("Placa Principal", value=motorista_data.get('placa1', ''))
                    placa2 = st.text_input("Placa Secundária", value=motorista_data.get('placa2', ''))
                    placa3 = st.text_input("Placa Terciária", value=motorista_data.get('placa3', ''))
                
                st.subheader("Status Operacional")
                col3, col4 = st.columns(2)
                
                with col3:
                    com_atend = st.selectbox(
                        "Com Atendimento", 
                        ["", "Sim", "Não"],
                        index=["", "Sim", "Não"].index(motorista_data.get('com-atend', ''))
                    )
                    sem_atend = st.selectbox(
                        "Sem Atendimento", 
                        ["", "Sim", "Não"],
                        index=["", "Sim", "Não"].index(motorista_data.get('sem-atend', ''))
                    )
                    com_veiculo = st.selectbox(
                        "Com Veículo", 
                        ["", "Sim", "Não"],
                        index=["", "Sim", "Não"].index(motorista_data.get('com-veiculo', ''))
                    )
                    sem_veiculo = st.selectbox(
                        "Sem Veículo", 
                        ["", "Sim", "Não"],
                        index=["", "Sim", "Não"].index(motorista_data.get('sem-veiculo', ''))
                    )
                    com_check = st.selectbox(
                        "Com Check", 
                        ["", "Sim", "Não"],
                        index=["", "Sim", "Não"].index(motorista_data.get('com-check', ''))
                    )
                    sem_check = st.selectbox(
                        "Sem Check", 
                        ["", "Sim", "Não"],
                        index=["", "Sim", "Não"].index(motorista_data.get('sem-check', ''))
                    )
                
                with col4:
                    dirigindo = st.selectbox(
                        "Dirigindo", 
                        ["", "Sim", "Não"],
                        index=["", "Sim", "Não"].index(motorista_data.get('dirigindo', ''))
                    )
                    parado = st.selectbox(
                        "Parado", 
                        ["", "Sim", "Não"],
                        index=["", "Sim", "Não"].index(motorista_data.get('parado', ''))
                    )
                    parado_ate1h = st.selectbox(
                        "Parado até 1h", 
                        ["", "Sim", "Não"],
                        index=["", "Sim", "Não"].index(motorista_data.get('parado-ate1h', ''))
                    )
                    parado1ate2h = st.selectbox(
                        "Parado 1h a 2h", 
                        ["", "Sim", "Não"],
                        index=["", "Sim", "Não"].index(motorista_data.get('parado1ate2h', ''))
                    )
                    parado_acima2h = st.selectbox(
                        "Parado acima 2h", 
                        ["", "Sim", "Não"],
                        index=["", "Sim", "Não"].index(motorista_data.get('parado-acima2h', ''))
                    )
                
                st.subheader("Informações Adicionais")
                col5, col6 = st.columns(2)
                
                with col5:
                    localiz_atual = st.text_input("Localização Atual", value=motorista_data.get('localiz-atual', ''))
                    doc_vencendo = st.selectbox(
                        "Doc Vencendo", 
                        ["", "Sim", "Não"],
                        index=["", "Sim", "Não"].index(motorista_data.get('doc-vencendo', ''))
                    )
                    doc_vencido = st.selectbox(
                        "Doc Vencido", 
                        ["", "Sim", "Não"],
                        index=["", "Sim", "Não"].index(motorista_data.get('doc-vencido', ''))
                    )
                    status1 = st.text_input("Status 1", value=motorista_data.get('status1', ''))
                    status2 = st.text_input("Status 2", value=motorista_data.get('status2', ''))
                    status3 = st.text_input("Status 3", value=motorista_data.get('status3', ''))
                
                with col6:
                    status_log1 = st.text_input("Status Log 1", value=motorista_data.get('status-log1', ''))
                    status_log2 = st.text_input("Status Log 2", value=motorista_data.get('status-log2', ''))
                
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
                            'com-atend': com_atend,
                            'sem-atend': sem_atend,
                            'com-veiculo': com_veiculo,
                            'sem-veiculo': sem_veiculo,
                            'com-check': com_check,
                            'sem-check': sem_check,
                            'dirigindo': dirigindo,
                            'parado': parado,
                            'parado-ate1h': parado_ate1h,
                            'parado1ate2h': parado1ate2h,
                            'parado-acima2h': parado_acima2h,
                            'doc-vencendo': doc_vencendo,
                            'doc-vencido': doc_vencido,
                            'localiz-atual': localiz_atual,
                            'status1': status1,
                            'status2': status2,
                            'status3': status3,
                            'status-log1': status_log1,
                            'status-log2': status_log2
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
                ["Todas"] + gerenciador.dados['empresa'].unique().tolist()
            )
        
        with col2:
            filtro_status = st.selectbox(
                "Status",
                ["Todos"] + gerenciador.dados['status'].unique().tolist()
            )
        
        with col3:
            filtro_categoria = st.selectbox(
                "Categoria",
                ["Todas"] + gerenciador.dados['categoria'].unique().tolist()
            )
        
        with col4:
            filtro_veiculo = st.selectbox(
                "Com Veículo",
                ["Todos", "Sim", "Não"]
            )
        
        # Aplicar filtros
        dados_filtrados = gerenciador.dados.copy()
        
        if filtro_empresa != "Todas":
            dados_filtrados = dados_filtrados[dados_filtrados['empresa'] == filtro_empresa]
        
        if filtro_status != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['status'] == filtro_status]
        
        if filtro_categoria != "Todas":
            dados_filtrados = dados_filtrados[dados_filtrados['categoria'] == filtro_categoria]
        
        if filtro_veiculo != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['com-veiculo'] == filtro_veiculo]
        
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

# Informações de atualização no sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("🔄 Atualização")
if gerenciador.ultima_atualizacao:
    st.sidebar.write(f"Última atualização: {gerenciador.ultima_atualizacao.strftime('%d/%m/%Y %H:%M')}")

if st.sidebar.button("🔄 Atualizar Agora"):
    gerenciador.carregar_dados()
    st.session_state.ultima_atualizacao = datetime.now()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("Sistema atualizado automaticamente a cada 1 hora")