# Página: Cadastrar Cliente
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
        
        # Inicializa variáveis no session_state se não existirem
        if 'dados_sincronizados' not in st.session_state:
            st.session_state.dados_sincronizados = {}
        if 'usuario_selecionado' not in st.session_state:
            st.session_state.usuario_selecionado = ""
        
        with st.form("form_cliente"):
            st.subheader("Informações do Cliente")
            col1, col2 = st.columns(2)
            
            with col1:
                cliente = st.text_input("Nome do Cliente*")
                
                # Dropdown para selecionar usuário do motorista
                usuario_selecionado = st.selectbox(
                    "Usuário do Motorista*", 
                    [""] + usuarios_motoristas,
                    key="usuario_select"
                )
                
                # Atualiza dados quando usuário é selecionado
                if usuario_selecionado and usuario_selecionado != st.session_state.usuario_selecionado:
                    st.session_state.usuario_selecionado = usuario_selecionado
                    if gerenciador.validar_usuario_motorista(usuario_selecionado):
                        st.session_state.dados_sincronizados = gerenciador.sincronizar_dados_cliente(usuario_selecionado)
                    else:
                        st.session_state.dados_sincronizados = {}
                
                # Mostra informações do motorista associado
                if usuario_selecionado:
                    if gerenciador.validar_usuario_motorista(usuario_selecionado):
                        nome_motorista = gerenciador.obter_nome_por_usuario(usuario_selecionado)
                        st.success(f"✅ **Motorista associado:** {nome_motorista}")
                        
                        # Mostra dados sincronizados
                        dados = st.session_state.dados_sincronizados
                        if dados:
                            st.info(f"""
                            🏢 **Empresa:** {dados.get('empresa', 'N/A')}  
                            🏷️ **Filial:** {dados.get('filial', 'N/A')}  
                            📊 **Status:** {dados.get('status', 'N/A')}
                            """)
                    else:
                        st.error("❌ Usuário não encontrado na tabela de motoristas")
            
            with col2:
                # CAMPOS AUTOMATICAMENTE PREENCHIDOS com base no motorista
                empresa = st.text_input(
                    "Empresa*", 
                    value=st.session_state.dados_sincronizados.get('empresa', ''),
                    key="empresa_field"
                )
                
                filial = st.text_input(
                    "Filial*", 
                    value=st.session_state.dados_sincronizados.get('filial', ''),
                    key="filial_field"
                )
                
                # Para status, usamos selectbox mas com valor padrão do motorista
                status_options = ["ATIVO", "INATIVO"]
                status_default = st.session_state.dados_sincronizados.get('status', 'ATIVO')
                status_index = status_options.index(status_default) if status_default in status_options else 0
                
                status = st.selectbox(
                    "Status*", 
                    status_options,
                    index=status_index,
                    key="status_field"
                )
            
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
                        # Limpa o session_state após cadastro bem-sucedido
                        st.session_state.dados_sincronizados = {}
                        st.session_state.usuario_selecionado = ""
                    else:
                        st.error("❌ Erro ao cadastrar cliente")
                else:
                    st.warning("⚠️ Preencha os campos obrigatórios (Cliente, Usuário do Motorista, Empresa)")
    
    else:
        st.warning("⚠️ Não há motoristas cadastrados. É necessário cadastrar motoristas antes de associar clientes.")
        st.info("Vá para a página '👥 Cadastrar Motorista' para adicionar motoristas primeiro.")

# Também preciso atualizar o método sincronizar_dados_cliente para garantir que funciona corretamente: