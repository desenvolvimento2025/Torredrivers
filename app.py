# PÁGINAS PARA CLIENTES - VERSÃO CORRIGIDA
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
        if 'usuario_selecionado_atual' not in st.session_state:
            st.session_state.usuario_selecionado_atual = ""
        
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
                
                # Sincroniza dados quando usuário é selecionado (fora do contexto de submit)
                if usuario_selecionado and usuario_selecionado != st.session_state.usuario_selecionado_atual:
                    st.session_state.usuario_selecionado_atual = usuario_selecionado
                    if gerenciador.validar_usuario_motorista(usuario_selecionado):
                        st.session_state.dados_sincronizados = gerenciador.sincronizar_dados_cliente(usuario_selecionado)
                    else:
                        st.session_state.dados_sincronizados = {}
                
                # Mostra informações do motorista associado (apenas visual)
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
                else:
                    st.info("🔍 Selecione um usuário do motorista para preencher automaticamente os dados")
            
            with col2:
                # CAMPOS AUTOMATICAMENTE PREENCHIDOS com base no motorista
                empresa_value = st.session_state.dados_sincronizados.get('empresa', '')
                filial_value = st.session_state.dados_sincronizados.get('filial', '')
                status_value = st.session_state.dados_sincronizados.get('status', 'ATIVO')
                
                empresa = st.text_input(
                    "Empresa*", 
                    value=empresa_value,
                    key="empresa_field"
                )
                
                filial = st.text_input(
                    "Filial*", 
                    value=filial_value,
                    key="filial_field"
                )
                
                # Para status, usamos selectbox mas com valor padrão do motorista
                status_options = ["ATIVO", "INATIVO"]
                status_index = status_options.index(status_value) if status_value in status_options else 0
                
                status = st.selectbox(
                    "Status*", 
                    status_options,
                    index=status_index,
                    key="status_field"
                )
            
            # BOTÃO DE SUBMIT CORRETO
            submitted = st.form_submit_button("💾 Cadastrar Cliente")
            
            if submitted:
                if cliente and usuario_selecionado and empresa:
                    # Validação final antes do cadastro
                    if not gerenciador.validar_usuario_motorista(usuario_selecionado):
                        st.error("❌ Usuário do motorista não encontrado. Verifique o usuário selecionado.")
                    else:
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
                            st.session_state.usuario_selecionado_atual = ""
                        else:
                            st.error("❌ Erro ao cadastrar cliente")
                else:
                    st.warning("⚠️ Preencha os campos obrigatórios (Cliente, Usuário do Motorista, Empresa)")
    
    else:
        st.warning("⚠️ Não há motoristas cadastrados. É necessário cadastrar motoristas antes de associar clientes.")
        st.info("Vá para a página '👥 Cadastrar Motorista' para adicionar motoristas primeiro.")

# Página: Editar Cliente - VERSÃO CORRIGIDA
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
            
            # Inicializa variáveis no session_state se não existirem
            if 'dados_sincronizados_edicao' not in st.session_state:
                st.session_state.dados_sincronizados_edicao = {}
            if 'usuario_selecionado_edicao' not in st.session_state:
                st.session_state.usuario_selecionado_edicao = cliente_data.get('usuario', '')
            
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
                    
                    # Sincroniza dados quando usuário é selecionado (fora do contexto de submit)
                    if usuario_selecionado and usuario_selecionado != st.session_state.usuario_selecionado_edicao:
                        st.session_state.usuario_selecionado_edicao = usuario_selecionado
                        if gerenciador.validar_usuario_motorista(usuario_selecionado):
                            st.session_state.dados_sincronizados_edicao = gerenciador.sincronizar_dados_cliente(usuario_selecionado)
                        else:
                            st.session_state.dados_sincronizados_edicao = {}
                    
                    # Mostra informações do motorista associado (apenas visual)
                    if usuario_selecionado:
                        if gerenciador.validar_usuario_motorista(usuario_selecionado):
                            nome_motorista = gerenciador.obter_nome_por_usuario(usuario_selecionado)
                            st.success(f"✅ **Motorista associado:** {nome_motorista}")
                            
                            # Mostra dados sincronizados
                            dados = st.session_state.dados_sincronizados_edicao
                            if dados:
                                st.info(f"""
                                🏢 **Empresa:** {dados.get('empresa', 'N/A')}  
                                🏷️ **Filial:** {dados.get('filial', 'N/A')}  
                                📊 **Status:** {dados.get('status', 'N/A')}
                                """)
                        else:
                            st.error("❌ Usuário não encontrado na tabela de motoristas")
                    else:
                        st.info("🔍 Selecione um usuário do motorista para preencher automaticamente os dados")
                
                with col2:
                    # CAMPOS AUTOMATICAMENTE PREENCHIDOS com base no motorista
                    empresa_value = st.session_state.dados_sincronizados_edicao.get('empresa', cliente_data.get('empresa', ''))
                    filial_value = st.session_state.dados_sincronizados_edicao.get('filial', cliente_data.get('filial', ''))
                    status_value = st.session_state.dados_sincronizados_edicao.get('status', cliente_data.get('status', 'ATIVO'))
                    
                    empresa = st.text_input(
                        "Empresa*", 
                        value=empresa_value,
                        key="empresa_field_edicao"
                    )
                    
                    filial = st.text_input(
                        "Filial*", 
                        value=filial_value,
                        key="filial_field_edicao"
                    )
                    
                    # Para status, usamos selectbox mas com valor padrão do motorista
                    status_options = ["ATIVO", "INATIVO"]
                    status_index = status_options.index(status_value) if status_value in status_options else 0
                    
                    status = st.selectbox(
                        "Status*", 
                        status_options,
                        index=status_index,
                        key="status_field_edicao"
                    )
                
                # BOTÃO DE SUBMIT CORRETO
                submitted = st.form_submit_button("💾 Atualizar Cliente")
                
                if submitted:
                    if cliente and usuario_selecionado and empresa:
                        # Validação final antes da atualização
                        if not gerenciador.validar_usuario_motorista(usuario_selecionado):
                            st.error("❌ Usuário do motorista não encontrado. Verifique o usuário selecionado.")
                        else:
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