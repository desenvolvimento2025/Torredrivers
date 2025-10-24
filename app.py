# Página: Lista Completa
elif pagina == "📋 Lista Completa":
    st.title("📋 Lista Completa de Motoristas")
    
    if gerenciador.dados is not None and not gerenciador.dados.empty:
        # Filtros
        st.subheader("🔍 Filtros")
        
        # Primeira linha de filtros
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            filtro_empresa = st.selectbox(
                "Empresa",
                ["Todas"] + gerenciador.dados['empresa'].unique().tolist()
            )
        
        with col2:
            filtro_filial = st.selectbox(
                "Filial",
                ["Todas"] + gerenciador.dados['filial'].unique().tolist()
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
        
        # Segunda linha de filtros
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            filtro_disponibilidade = st.selectbox(
                "Disponibilidade",
                ["Todas"] + gerenciador.dados['disponibilidade'].unique().tolist()
            )
        
        with col6:
            filtro_ferias = st.selectbox(
                "Férias",
                ["Todos", "Sim", "Não"]
            )
        
        with col7:
            filtro_licenca = st.selectbox(
                "Licença",
                ["Todos", "Sim", "Não"]
            )
        
        with col8:
            filtro_folga = st.selectbox(
                "Folga",
                ["Todos", "Sim", "Não"]
            )
        
        # Terceira linha de filtros
        col9, col10, col11, col12 = st.columns(4)
        
        with col9:
            filtro_sobreaviso = st.selectbox(
                "Sobreaviso",
                ["Todos", "Sim", "Não"]
            )
        
        with col10:
            filtro_atestado = st.selectbox(
                "Atestado",
                ["Todos", "Sim", "Não"]
            )
        
        with col11:
            filtro_atendimento = st.selectbox(
                "Com atendimento",
                ["Todos", "Sim", "Não"]
            )
        
        with col12:
            filtro_check = st.selectbox(
                "Com check",
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
            filtro_jornada80 = st.selectbox(
                "Jornada acima 80%",
                ["Todos", "Sim", "Não"]
            )
        
        with col18:
            filtro_jornada_exced = st.selectbox(
                "Jornada Excedida",
                ["Todos", "Sim", "Não"]
            )
        
        with col19:
            filtro_folga8d = st.selectbox(
                "Sem folga a partir 8d",
                ["Todos", "Sim", "Não"]
            )
        
        with col20:
            filtro_folga12d = st.selectbox(
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
            filtro_associacao = st.selectbox(
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
        
        if filtro_ferias != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['ferias'] == filtro_ferias]
        
        if filtro_licenca != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['licenca'] == filtro_licenca]
        
        if filtro_folga != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['folga'] == filtro_folga]
        
        if filtro_sobreaviso != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['sobreaviso'] == filtro_sobreaviso]
        
        if filtro_atestado != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['atestado'] == filtro_atestado]
        
        if filtro_atendimento != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['com-atend'] == filtro_atendimento]
        
        if filtro_check != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['com-check'] == filtro_check]
        
        if filtro_dirigindo != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['dirigindo'] == filtro_dirigindo]
        
        if filtro_parado_ate1h != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['parado-ate1h'] == filtro_parado_ate1h]
        
        if filtro_parado1ate2h != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['parado1ate2h'] == filtro_parado1ate2h]
        
        if filtro_parado_acima2h != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['parado-acima2h'] == filtro_parado_acima2h]
        
        if filtro_jornada80 != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['jornada-acm80'] == filtro_jornada80]
        
        if filtro_jornada_exced != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['jornada-exced'] == filtro_jornada_exced]
        
        if filtro_folga8d != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['sem-folga-acm7d'] == filtro_folga8d]
        
        if filtro_folga12d != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['sem-folga-acm12d'] == filtro_folga12d]
        
        if filtro_doc_vencendo != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['doc-vencendo'] == filtro_doc_vencendo]
        
        if filtro_doc_vencido != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['doc-vencido'] == filtro_doc_vencido]
        
        if filtro_associacao != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['associacao-clientes'] == filtro_associacao]
        
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