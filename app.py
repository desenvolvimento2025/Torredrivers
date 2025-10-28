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

# Página: Lista Completa - CORREÇÃO AQUI
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
    # ... (mantenha o código existente da edição de cliente)

# Página: Excluir Cliente
elif pagina == "🗑️ Excluir Cliente":
    # ... (mantenha o código existente da exclusão de cliente)

# Página: Lista de Clientes
elif pagina == "📋 Lista de Clientes":
    # ... (mantenha o código existente da lista de clientes)