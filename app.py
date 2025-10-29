# Página: Arquivos HTML (PÁGINA PRINCIPAL SIMPLIFICADA)
if pagina == "📄 Arquivos HTML":
    # Atualizar lista de arquivos
    gerenciador_html.carregar_arquivos()
    
    if gerenciador_html.arquivos_html:
        # Seletor de arquivos discreto no topo
        if len(gerenciador_html.arquivos_html) > 1:
            arquivo_selecionado = st.selectbox(
                "Selecione o relatório:",
                gerenciador_html.arquivos_html,
                index=0,
                label_visibility="collapsed"
            )
        else:
            arquivo_selecionado = gerenciador_html.arquivos_html[0]
        
        # Botões de ação compactos em uma linha
        col1, col2, col3, col4 = st.columns([1, 1, 1, 7])
        
        with col1:
            # Download do arquivo
            conteudo_html = gerenciador_html.obter_conteudo_html(arquivo_selecionado)
            if conteudo_html:
                st.download_button(
                    label="📥",
                    data=conteudo_html,
                    file_name=arquivo_selecionado,
                    mime="text/html",
                    help="Baixar arquivo HTML",
                    use_container_width=True
                )
        
        with col2:
            # Ver código fonte
            if st.button("📝", help="Ver código fonte", use_container_width=True):
                st.session_state.mostrar_codigo_fonte = not st.session_state.get('mostrar_codigo_fonte', False)
                st.rerun()
        
        with col3:
            # Atualizar lista
            if st.button("🔄", help="Atualizar lista", use_container_width=True):
                gerenciador_html.carregar_arquivos()
                st.rerun()
        
        with col4:
            st.write(f"**Visualizando:** {arquivo_selecionado}")
        
        # Obter conteúdo do arquivo
        conteudo_html = gerenciador_html.obter_conteudo_html(arquivo_selecionado)
        
        if conteudo_html:
            # Renderizar HTML em tela cheia
            st.markdown("---")
            
            # Altura máxima para tela cheia (quase toda a tela)
            altura = 900
            
            # Renderizar HTML diretamente em tela cheia
            st.components.v1.html(conteudo_html, height=altura, scrolling=True)
            
            # Mostrar código fonte se solicitado (em expander para não atrapalhar a visualização)
            if st.session_state.get('mostrar_codigo_fonte', False):
                with st.expander("📝 Código Fonte do Relatório", expanded=True):
                    st.code(conteudo_html, language='html')
        
        else:
            st.error("❌ Não foi possível carregar o conteúdo do relatório")
    
    else:
        # Tela quando não há arquivos - ainda mais minimalista
        st.markdown("""
        <div style='
            text-align: center; 
            padding: 100px 20px; 
            background-color: #f8f9fa; 
            border-radius: 10px;
            border: 2px dashed #dee2e6;
            margin: 20px 0;
        '>
            <h3 style='color: #6c757d; margin-bottom: 30px;'>📭 Nenhum Relatório Encontrado</h3>
            <p style='color: #6c757d; font-size: 16px; margin-bottom: 40px;'>
                Importe seu primeiro relatório HTML para visualizá-lo aqui.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botão centralizado e discreto
        col_empty1, col_empty2, col_empty3 = st.columns([1, 2, 1])
        
        with col_empty2:
            if st.button("📤 Importar Primeiro Relatório", type="primary", use_container_width=True):
                st.session_state.pagina = "🌐 Gerenciar HTML"
                st.rerun()