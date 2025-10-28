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
                            'localiz-atual': localiz_atual,
                            'doc-vencendo': doc_vencendo,
                            'doc-vencido': doc_vencido,
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

# Página: Excluir Motorista - CORREÇÃO AQUI
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

# Página: Lista Completa
elif pagina == "📋 Lista Completa":
    st.title("📋 Lista Completa de Motoristas")
    
    if gerenciador.dados is not None and not gerenciador.dados.empty:
        # ... (mantenha todo o código existente da Lista Completa)
        pass
    else:
        st.info("Nenhum motorista cadastrado.")

# PÁGINAS PARA CLIENTES
elif pagina == "🏢 Cadastrar Cliente":
    st.title("🏢 Cadastrar Novo Cliente")
    
    # ... (mantenha todo o código existente do Cadastrar Cliente)
    pass

# Página: Editar Cliente
elif pagina == "✏️ Editar Cliente":
    # ... (mantenha todo o código existente da Editar Cliente)
    pass

# Página: Excluir Cliente
elif pagina == "🗑️ Excluir Cliente":
    # ... (mantenha todo o código existente da Excluir Cliente)
    pass

# Página: Lista de Clientes
elif pagina == "📋 Lista de Clientes":
    # ... (mantenha todo o código existente da Lista de Clientes)
    pass