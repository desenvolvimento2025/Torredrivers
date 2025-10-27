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
                                         index=["EXPRESSO", "LOGIKA"].index(motorista_data.get('empresa', 'EXPRESSO')) if motorista_data.get('empresa', 'EXPRESSO') in ["EXPRESSO", "LOGIKA"] else 0)
                    filial = st.selectbox("Filial*", ["MEA", "RIO", "CXA", "VIX", "SPO", "LGK", "NPA"],
                                        index=["MEA", "RIO", "CXA", "VIX", "SPO", "LGK", "NPA"].index(motorista_data.get('filial', 'SPO')) if motorista_data.get('filial', 'SPO') in ["MEA", "RIO", "CXA", "VIX", "SPO", "LGK", "NPA"] else 0)
                
                with col2:
                    status = st.selectbox("Status*", ["ATIVO", "INATIVO"],
                                        index=["ATIVO", "INATIVO"].index(motorista_data.get('status', 'ATIVO')) if motorista_data.get('status', 'ATIVO') in ["ATIVO", "INATIVO"] else 0)
                    categoria = st.selectbox("Categoria CNH", ["A", "B", "C", "D", "E"],
                                           index=["A", "B", "C", "D", "E"].index(motorista_data.get('categoria', 'B')) if motorista_data.get('categoria', 'B') in ["A", "B", "C", "D", "E"] else 1)
                    placa1 = st.text_input("Placa Principal", value=motorista_data.get('placa1', ''))
                    placa2 = st.text_input("Placa Secundária", value=motorista_data.get('placa2', ''))
                    placa3 = st.text_input("Placa Terciária", value=motorista_data.get('placa3', ''))
                
                st.subheader("Status do Motorista")
                col3, col4 = st.columns(2)
                
                with col3:
                    disponibilidade = st.selectbox("Disponibilidade*", ["Trabalhando", "Interjornada", "Indisponíveis"],
                                                 index=["Trabalhando", "Interjornada", "Indisponíveis"].index(motorista_data.get('disponibilidade', 'Trabalhando')) if motorista_data.get('disponibilidade', 'Trabalhando') in ["Trabalhando", "Interjornada", "Indisponíveis"] else 0)
                    ferias = st.selectbox("Férias*", ["Sim", "Não"],
                                        index=["Sim", "Não"].index(motorista_data.get('ferias', 'Não')) if motorista_data.get('ferias', 'Não') in ["Sim", "Não"] else 1)
                    licenca = st.selectbox("Licença*", ["Sim", "Não"],
                                         index=["Sim", "Não"].index(motorista_data.get('licenca', 'Não')) if motorista_data.get('licenca', 'Não') in ["Sim", "Não"] else 1)
                    folga = st.selectbox("Folga*", ["Sim", "Não"],
                                       index=["Sim", "Não"].index(motorista_data.get('folga', 'Não')) if motorista_data.get('folga', 'Não') in ["Sim", "Não"] else 1)
                
                with col4:
                    sobreaviso = st.selectbox("Sobreaviso*", ["Sim", "Não"],
                                            index=["Sim", "Não"].index(motorista_data.get('sobreaviso', 'Não')) if motorista_data.get('sobreaviso', 'Não') in ["Sim", "Não"] else 1)
                    atestado = st.selectbox("Atestado*", ["Sim", "Não"],
                                          index=["Sim", "Não"].index(motorista_data.get('atestado', 'Não')) if motorista_data.get('atestado', 'Não') in ["Sim", "Não"] else 1)
                    
                    # CORREÇÃO PARA CAMPOS COM VALORES VAZIOS
                    com_atend_valor = motorista_data.get('com-atend', '')
                    com_atend_opcoes = ["", "Sim", "Não"]
                    com_atend_index = com_atend_opcoes.index(com_atend_valor) if com_atend_valor in com_atend_opcoes else 0
                    com_atend = st.selectbox("Com Atendimento", com_atend_opcoes, index=com_atend_index)
                    
                    com_veiculo_valor = motorista_data.get('com-veiculo', '')
                    com_veiculo_opcoes = ["", "Sim", "Não"]
                    com_veiculo_index = com_veiculo_opcoes.index(com_veiculo_valor) if com_veiculo_valor in com_veiculo_opcoes else 0
                    com_veiculo = st.selectbox("Com Veículo", com_veiculo_opcoes, index=com_veiculo_index)
                
                st.subheader("Status Operacional")
                col5, col6 = st.columns(2)
                
                with col5:
                    # CORREÇÃO PARA CAMPOS COM VALORES VAZIOS
                    com_check_valor = motorista_data.get('com-check', '')
                    com_check_opcoes = ["", "Sim", "Não"]
                    com_check_index = com_check_opcoes.index(com_check_valor) if com_check_valor in com_check_opcoes else 0
                    com_check = st.selectbox("Com Check", com_check_opcoes, index=com_check_index)
                    
                    # CORREÇÃO ESPECÍFICA PARA O CAMPO "dirigindo" (linha 745)
                    dirigindo_valor = motorista_data.get('dirigindo', '')
                    dirigindo_opcoes = ["", "Sim", "Não"]
                    dirigindo_index = dirigindo_opcoes.index(dirigindo_valor) if dirigindo_valor in dirigindo_opcoes else 0
                    dirigindo = st.selectbox("Dirigindo", dirigindo_opcoes, index=dirigindo_index)
                    
                    parado_ate1h_valor = motorista_data.get('parado-ate1h', '')
                    parado_ate1h_opcoes = ["", "Sim", "Não"]
                    parado_ate1h_index = parado_ate1h_opcoes.index(parado_ate1h_valor) if parado_ate1h_valor in parado_ate1h_opcoes else 0
                    parado_ate1h = st.selectbox("Parado até 1h", parado_ate1h_opcoes, index=parado_ate1h_index)
                    
                    parado1ate2h_valor = motorista_data.get('parado1ate2h', '')
                    parado1ate2h_opcoes = ["", "Sim", "Não"]
                    parado1ate2h_index = parado1ate2h_opcoes.index(parado1ate2h_valor) if parado1ate2h_valor in parado1ate2h_opcoes else 0
                    parado1ate2h = st.selectbox("Parado 1h a 2h", parado1ate2h_opcoes, index=parado1ate2h_index)
                
                with col6:
                    parado_acima2h_valor = motorista_data.get('parado-acima2h', '')
                    parado_acima2h_opcoes = ["", "Sim", "Não"]
                    parado_acima2h_index = parado_acima2h_opcoes.index(parado_acima2h_valor) if parado_acima2h_valor in parado_acima2h_opcoes else 0
                    parado_acima2h = st.selectbox("Parado acima 2h", parado_acima2h_opcoes, index=parado_acima2h_index)
                    
                    jornada_acm80_valor = motorista_data.get('jornada-acm80', '')
                    jornada_acm80_opcoes = ["", "Sim", "Não"]
                    jornada_acm80_index = jornada_acm80_opcoes.index(jornada_acm80_valor) if jornada_acm80_valor in jornada_acm80_opcoes else 0
                    jornada_acm80 = st.selectbox("Jornada acima 80%", jornada_acm80_opcoes, index=jornada_acm80_index)
                    
                    jornada_exced_valor = motorista_data.get('jornada-exced', '')
                    jornada_exced_opcoes = ["", "Sim", "Não"]
                    jornada_exced_index = jornada_exced_opcoes.index(jornada_exced_valor) if jornada_exced_valor in jornada_exced_opcoes else 0
                    jornada_exced = st.selectbox("Jornada Excedida", jornada_exced_opcoes, index=jornada_exced_index)
                
                st.subheader("Jornada e Documentação")
                col7, col8 = st.columns(2)
                
                with col7:
                    sem_folga_acm7d_valor = motorista_data.get('sem-folga-acm7d', '')
                    sem_folga_acm7d_opcoes = ["", "Sim", "Não"]
                    sem_folga_acm7d_index = sem_folga_acm7d_opcoes.index(sem_folga_acm7d_valor) if sem_folga_acm7d_valor in sem_folga_acm7d_opcoes else 0
                    sem_folga_acm7d = st.selectbox("Sem folga a partir 8d", sem_folga_acm7d_opcoes, index=sem_folga_acm7d_index)
                    
                    sem_folga_acm12d_valor = motorista_data.get('sem-folga-acm12d', '')
                    sem_folga_acm12d_opcoes = ["", "Sim", "Não"]
                    sem_folga_acm12d_index = sem_folga_acm12d_opcoes.index(sem_folga_acm12d_valor) if sem_folga_acm12d_valor in sem_folga_acm12d_opcoes else 0
                    sem_folga_acm12d = st.selectbox("Sem folga a partir de 12d", sem_folga_acm12d_opcoes, index=sem_folga_acm12d_index)
                    
                    doc_vencendo_valor = motorista_data.get('doc-vencendo', '')
                    doc_vencendo_opcoes = ["", "Sim", "Não"]
                    doc_vencendo_index = doc_vencendo_opcoes.index(doc_vencendo_valor) if doc_vencendo_valor in doc_vencendo_opcoes else 0
                    doc_vencendo = st.selectbox("Doc Vencendo", doc_vencendo_opcoes, index=doc_vencendo_index)
                    
                    doc_vencido_valor = motorista_data.get('doc-vencido', '')
                    doc_vencido_opcoes = ["", "Sim", "Não"]
                    doc_vencido_index = doc_vencido_opcoes.index(doc_vencido_valor) if doc_vencido_valor in doc_vencido_opcoes else 0
                    doc_vencido = st.selectbox("Doc Vencido", doc_vencido_opcoes, index=doc_vencido_index)
                
                with col8:
                    localiz_atual = st.text_input("Última localiz pelo veículo", value=motorista_data.get('localiz-atual', ''))
                    
                    associacao_clientes_valor = motorista_data.get('associacao-clientes', '')
                    associacao_clientes_opcoes = ["", "Sim", "Não"]
                    associacao_clientes_index = associacao_clientes_opcoes.index(associacao_clientes_valor) if associacao_clientes_valor in associacao_clientes_opcoes else 0
                    associacao_clientes = st.selectbox("Associação a Clientes", associacao_clientes_opcoes, index=associacao_clientes_index)
                    
                    interj_menor8_valor = motorista_data.get('interj-menor8', '')
                    interj_menor8_opcoes = ["", "Sim", "Não"]
                    interj_menor8_index = interj_menor8_opcoes.index(interj_menor8_valor) if interj_menor8_valor in interj_menor8_opcoes else 0
                    interj_menor8 = st.selectbox("Interjornada < 8h", interj_menor8_opcoes, index=interj_menor8_index)
                    
                    interj_maior8_valor = motorista_data.get('interj-maior8', '')
                    interj_maior8_opcoes = ["", "Sim", "Não"]
                    interj_maior8_index = interj_maior8_opcoes.index(interj_maior8_valor) if interj_maior8_valor in interj_maior8_opcoes else 0
                    interj_maior8 = st.selectbox("Interjornada > 8h", interj_maior8_opcoes, index=interj_maior8_index)
                
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
                            'com-check': com_check,
                            'dirigindo': dirigindo,
                            'parado-ate1h': parado_ate1h,
                            'parado1ate2h': parado1ate2h,
                            'parado-acima2h': parado_acima2h,
                            'jornada-acm80': jornada_acm80,
                            'jornada-exced': jornada_exced,
                            'sem-folga-acm7d': sem_folga_acm7d,
                            'sem-folga-acm12d': sem_folga_acm12d,
                            'doc-vencendo': doc_vencendo,
                            'doc-vencido': doc_vencido,
                            'localiz-atual': localiz_atual,
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