# Página: Lista Completa
elif pagina == "📋 Lista Completa":
    st.title("📋 Lista Completa de Motoristas")
    
    if gerenciador.dados is not None and not gerenciador.dados.empty:
        # Filtros - Layout com múltiplas linhas para organizar todos os filtros
        st.subheader("🔍 Filtros")
        
        # Função auxiliar para obter opções únicas de uma coluna
        def obter_opcoes(coluna, padrao="Todas"):
            try:
                if coluna in gerenciador.dados.columns:
                    valores_unicos = [v for v in gerenciador.dados[coluna].unique() if pd.notna(v) and v != ""]
                    return [padrao] + sorted(valores_unicos)
                else:
                    return [padrao]
            except:
                return [padrao]
        
        # Primeira linha de filtros
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            filtro_empresa = st.selectbox(
                "Empresa",
                obter_opcoes('empresa')
            )
        
        with col2:
            filtro_filial = st.selectbox(
                "Filial",
                obter_opcoes('filial')
            )
        
        with col3:
            filtro_categoria = st.selectbox(
                "Categoria",
                obter_opcoes('categoria')
            )
        
        with col4:
            filtro_veiculo = st.selectbox(
                "Com Veículo",
                ["Todos", "Sim", "Não"]
            )
        
        # Segunda linha de filtros
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            # Filtro de disponibilidade com valores específicos
            opcoes_disponibilidade = ["Todas", "Trabalhando", "Interjornada", "Indisponíveis"]
            # Adiciona valores existentes no banco que não estão na lista padrão
            valores_existentes = obter_opcoes('disponibilidade', "Todas")[1:]  # Remove "Todas"
            for valor in valores_existentes:
                if valor not in opcoes_disponibilidade:
                    opcoes_disponibilidade.append(valor)
            
            filtro_disponibilidade = st.selectbox(
                "Disponibilidade",
                opcoes_disponibilidade
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
        
        # Função auxiliar para aplicar filtros
        def aplicar_filtro(coluna, valor_filtro, valor_todos="Todos"):
            if valor_filtro != valor_todos:
                if coluna in dados_filtrados.columns:
                    if valor_filtro in ["Sim", "Não"]:
                        return dados_filtrados[coluna] == valor_filtro
                    else:
                        return dados_filtrados[coluna] == valor_filtro
            return pd.Series([True] * len(dados_filtrados))
        
        # Aplica todos os filtros
        filtros = [
            aplicar_filtro('empresa', filtro_empresa, "Todas"),
            aplicar_filtro('filial', filtro_filial, "Todas"),
            aplicar_filtro('categoria', filtro_categoria, "Todas"),
            aplicar_filtro('com-veiculo', filtro_veiculo),
            aplicar_filtro('disponibilidade', filtro_disponibilidade, "Todas"),
            aplicar_filtro('ferias', filtro_ferias, "Todas"),
            aplicar_filtro('licenca', filtro_licenca, "Todas"),
            aplicar_filtro('folga', filtro_folga, "Todas"),
            aplicar_filtro('sobreaviso', filtro_sobreaviso, "Todas"),
            aplicar_filtro('atestado', filtro_atestado, "Todas"),
            aplicar_filtro('com-atend', filtro_com_atend),
            aplicar_filtro('com-check', filtro_com_check),
            aplicar_filtro('dirigindo', filtro_dirigindo),
            aplicar_filtro('parado-ate1h', filtro_parado_ate1h),
            aplicar_filtro('parado1ate2h', filtro_parado1ate2h),
            aplicar_filtro('parado-acima2h', filtro_parado_acima2h),
            aplicar_filtro('jornada-acm80', filtro_jornada_acm80),
            aplicar_filtro('jornada-exced', filtro_jornada_exced),
            aplicar_filtro('sem-folga-acm7d', filtro_sem_folga_acm7d),
            aplicar_filtro('sem-folga-acm12d', filtro_sem_folga_acm12d),
            aplicar_filtro('doc-vencendo', filtro_doc_vencendo),
            aplicar_filtro('doc-vencido', filtro_doc_vencido),
            aplicar_filtro('associacao-clientes', filtro_associacao_clientes),
            aplicar_filtro('interj-menor8', filtro_interj_menor8),
            aplicar_filtro('interj-maior8', filtro_interj_maior8)
        ]
        
        # Combina todos os filtros
        for filtro in filtros:
            if isinstance(filtro, pd.Series) and len(filtro) == len(dados_filtrados):
                dados_filtrados = dados_filtrados[filtro]
        
        st.subheader(f"📊 Resultados ({len(dados_filtrados)} motoristas)")
        
        # Renomear as colunas para exibição conforme a aba "Cadastrar Motorista"
        dados_exibicao = dados_filtrados.copy()
        
        # Mapeamento dos nomes das colunas para exibição - EXATAMENTE como na aba de cadastro
        mapeamento_colunas = {
            'nome': 'Nome completo*',
            'usuario': 'Usuário*',
            'grupo': 'Grupo*',
            'empresa': 'Empresa*',
            'filial': 'Filial*',
            'status': 'Status*',
            'disponibilidade': 'Disponibilidade*',
            'ferias': 'Férias*',
            'licenca': 'Licença*',
            'folga': 'Folga*',
            'sobreaviso': 'Sobreaviso*',
            'atestado': 'Atestado*',
            'com-atend': 'Com Atendimento',
            'com-veiculo': 'Com Veículo',
            'com-check': 'Com Check',
            'dirigindo': 'Dirigindo',
            'parado-ate1h': 'Parado até 1h',
            'parado1ate2h': 'Parado 1h a 2h',
            'parado-acima2h': 'Parado acima 2h',
            'jornada-acm80': 'Jornada acima 80%',
            'jornada-exced': 'Jornada Excedida',
            'sem-folga-acm7d': 'Sem folga a partir 8d',
            'sem-folga-acm12d': 'Sem folga a partir de 12d',
            'categoria': 'Categoria CNH',
            'doc-vencendo': 'Doc Vencendo',
            'doc-vencido': 'Doc Vencido',
            'localiz-atual': 'Última localiz pelo veículo',
            'associacao-clientes': 'Associação a Clientes',
            'interj-menor8': 'Interjornada < 8h',
            'interj-maior8': 'Interjornada > 8h',
            'placa1': 'Placa Principal',
            'placa2': 'Placa Secundária',
            'placa3': 'Placa Terciária'
        }
        
        # Renomear as colunas para exibição
        dados_exibicao = dados_exibicao.rename(columns=mapeamento_colunas)
        
        st.dataframe(dados_exibicao, use_container_width=True)
        
        # Botão de download (mantém nomes originais para o CSV)
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