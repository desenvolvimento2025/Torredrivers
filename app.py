# Página: Lista Completa
elif pagina == "📋 Lista Completa":
    # ... (código existente da lista completa)

# PÁGINAS PARA CLIENTES - CORREÇÃO AQUI
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
                usuario_selecionado = st.selectbox("Selecione o Motorista*", [""] + usuarios_motoristas)
                
            with col2:
                # Espaço reservado para mostrar informações do motorista selecionado
                st.write("### Informações do Motorista")
                if usuario_selecionado:
                    try:
                        # Busca dados completos do motorista
                        motorista_data = gerenciador.dados[gerenciador.dados['usuario'] == usuario_selecionado].iloc[0]
                        nome_motorista = motorista_data.get('nome', '')
                        empresa_motorista = motorista_data.get('empresa', '')
                        filial_motorista = motorista_data.get('filial', '')
                        status_motorista = motorista_data.get('status', '')
                        
                        # Exibe os dados do motorista (somente leitura)
                        st.text_input("Nome do Motorista", value=nome_motorista, disabled=True)
                        st.text_input("Empresa", value=empresa_motorista, disabled=True)
                        st.text_input("Filial", value=filial_motorista, disabled=True)
                        st.text_input("Status", value=status_motorista, disabled=True)
                        
                    except Exception as e:
                        st.error(f"Erro ao buscar dados do motorista: {e}")
                        nome_motorista = ""
                        empresa_motorista = ""
                        filial_motorista = ""
                        status_motorista = ""
                else:
                    st.info("Selecione um motorista para ver suas informações")
                    nome_motorista = ""
                    empresa_motorista = ""
                    filial_motorista = ""
                    status_motorista = ""
            
            submitted = st.form_submit_button("💾 Cadastrar Cliente")
            
            if submitted:
                if cliente and usuario_selecionado:
                    # Obtém os dados completos do motorista selecionado
                    try:
                        motorista_data = gerenciador.dados[gerenciador.dados['usuario'] == usuario_selecionado].iloc[0]
                        nome_motorista = motorista_data.get('nome', '')
                        empresa_motorista = motorista_data.get('empresa', '')
                        filial_motorista = motorista_data.get('filial', '')
                        status_motorista = motorista_data.get('status', '')
                    except Exception as e:
                        st.error(f"Erro ao obter dados do motorista: {e}")
                        nome_motorista = ""
                        empresa_motorista = ""
                        filial_motorista = ""
                        status_motorista = ""
                    
                    dados_cliente = {
                        'cliente': cliente,
                        'nome': nome_motorista,  # Preenchido automaticamente da tabela motoristas
                        'usuario': usuario_selecionado,  # Preenchido automaticamente da tabela motoristas
                        'empresa': empresa_motorista,  # Preenchido automaticamente da tabela motoristas
                        'filial': filial_motorista,  # Preenchido automaticamente da tabela motoristas
                        'status': status_motorista  # Preenchido automaticamente da tabela motoristas
                    }
                    
                    if gerenciador.adicionar_cliente(dados_cliente):
                        st.success("✅ Cliente cadastrado com sucesso!")
                        st.balloons()
                    else:
                        st.error("❌ Erro ao cadastrar cliente")
                else:
                    st.warning("⚠️ Preencha os campos obrigatórios (Nome do Cliente e selecione um Motorista)")
    else:
        st.warning("⚠️ Não há motoristas cadastrados. É necessário cadastrar motoristas antes de associar clientes.")
        st.info("Vá para a página '👥 Cadastrar Motorista' para adicionar motoristas primeiro.")

# Página: Editar Cliente
elif pagina == "✏️ Editar Cliente":
    # ... (código existente da edição de cliente)

# Página: Excluir Cliente  
elif pagina == "🗑️ Excluir Cliente":
    # ... (código existente da exclusão de cliente)

# Página: Lista de Clientes
elif pagina == "📋 Lista de Clientes":
    # ... (código existente da lista de clientes)