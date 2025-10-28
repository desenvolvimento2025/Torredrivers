class GerenciadorMotoristas:
    def __init__(self):
        self.motoristas = []
        self.usuarios_motoristas = {
            'motorista1': {'senha': 'senha123', 'cpf': '123.456.789-00'},
            'admin': {'senha': 'admin123', 'cpf': '111.222.333-44'},
            'driver': {'senha': 'driver123', 'cpf': '555.666.777-88'}
        }
    
    def validar_usuario_motorista(self, usuario, senha):
        """Valida as credenciais de um motorista"""
        if usuario in self.usuarios_motoristas:
            if self.usuarios_motoristas[usuario]['senha'] == senha:
                return True
        return False
    
    def cadastrar_motorista(self, nome, cpf, email, telefone, veiculo, usuario=None, senha=None):
        """Cadastra um novo motorista"""
        # Verificar se CPF já existe
        for motorista in self.motoristas:
            if motorista['cpf'] == cpf:
                raise ValueError("CPF já cadastrado")
        
        motorista = {
            'nome': nome,
            'cpf': cpf,
            'email': email,
            'telefone': telefone,
            'veiculo': veiculo,
            'ativo': True
        }
        
        self.motoristas.append(motorista)
        
        # Criar usuário de acesso se fornecido
        if usuario and senha:
            self.usuarios_motoristas[usuario] = {
                'senha': senha,
                'cpf': cpf
            }
        
        return motorista
    
    def buscar_motorista_por_cpf(self, cpf):
        """Busca motorista pelo CPF"""
        for motorista in self.motoristas:
            if motorista['cpf'] == cpf:
                return motorista
        return None
    
    def buscar_motorista_por_usuario(self, usuario):
        """Busca motorista pelo usuário"""
        if usuario in self.usuarios_motoristas:
            cpf = self.usuarios_motoristas[usuario]['cpf']
            return self.buscar_motorista_por_cpf(cpf)
        return None
    
    def listar_motoristas(self, apenas_ativos=True):
        """Retorna lista de motoristas"""
        if apenas_ativos:
            return [m for m in self.motoristas if m['ativo']]
        return self.motoristas
    
    def desativar_motorista(self, cpf):
        """Desativa um motorista pelo CPF"""
        motorista = self.buscar_motorista_por_cpf(cpf)
        if motorista:
            motorista['ativo'] = False
            return True
        return False
    
    def ativar_motorista(self, cpf):
        """Ativa um motorista pelo CPF"""
        motorista = self.buscar_motorista_por_cpf(cpf)
        if motorista:
            motorista['ativo'] = True
            return True
        return False
    
    def editar_motorista(self, cpf, **kwargs):
        """Edita informações de um motorista"""
        motorista = self.buscar_motorista_por_cpf(cpf)
        if motorista:
            for key, value in kwargs.items():
                if key in motorista and key != 'cpf':  # CPF não pode ser alterado
                    motorista[key] = value
            return True
        return False
    
    def criar_usuario_motorista(self, usuario, senha, cpf):
        """Cria usuário de acesso para motorista existente"""
        motorista = self.buscar_motorista_por_cpf(cpf)
        if not motorista:
            raise ValueError("Motorista não encontrado")
        
        if usuario in self.usuarios_motoristas:
            raise ValueError("Usuário já existe")
        
        self.usuarios_motoristas[usuario] = {
            'senha': senha,
            'cpf': cpf
        }
        return True


class SistemaTransporte:
    def __init__(self):
        self.gerenciador_motoristas = GerenciadorMotoristas()
    
    def menu_principal(self):
        """Menu principal do sistema"""
        while True:
            print("\n=== SISTEMA DE TRANSPORTE ===")
            print("1. Login Motorista")
            print("2. Cadastrar Motorista")
            print("3. Listar Motoristas")
            print("4. Sair")
            
            opcao = input("Escolha uma opção: ")
            
            if opcao == '1':
                self.login_motorista()
            elif opcao == '2':
                self.cadastrar_motorista()
            elif opcao == '3':
                self.listar_motoristas()
            elif opcao == '4':
                print("Saindo do sistema...")
                break
            else:
                print("Opção inválida!")
    
    def login_motorista(self):
        """Interface de login para motoristas"""
        print("\n--- LOGIN MOTORISTA ---")
        usuario = input("Usuário: ")
        senha = input("Senha: ")
        
        try:
            if self.gerenciador_motoristas.validar_usuario_motorista(usuario, senha):
                motorista = self.gerenciador_motoristas.buscar_motorista_por_usuario(usuario)
                if motorista:
                    print(f"\nLogin bem-sucedido! Bem-vindo, {motorista['nome']}!")
                    self.menu_motorista(motorista)
                else:
                    print("Motorista não encontrado!")
            else:
                print("Usuário ou senha inválidos!")
        except Exception as e:
            print(f"Erro durante validação: {e}")
    
    def cadastrar_motorista(self):
        """Interface para cadastrar novo motorista"""
        print("\n--- CADASTRAR MOTORISTA ---")
        nome = input("Nome completo: ")
        cpf = input("CPF: ")
        email = input("E-mail: ")
        telefone = input("Telefone: ")
        veiculo = input("Veículo (placa): ")
        
        criar_usuario = input("Deseja criar usuário de acesso? (s/n): ").lower()
        usuario = None
        senha = None
        
        if criar_usuario == 's':
            usuario = input("Usuário: ")
            senha = input("Senha: ")
        
        try:
            motorista = self.gerenciador_motoristas.cadastrar_motorista(
                nome, cpf, email, telefone, veiculo, usuario, senha
            )
            print(f"\nMotorista {motorista['nome']} cadastrado com sucesso!")
        except ValueError as e:
            print(f"Erro ao cadastrar: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")
    
    def listar_motoristas(self):
        """Lista todos os motoristas"""
        print("\n--- LISTA DE MOTORISTAS ---")
        motoristas = self.gerenciador_motoristas.listar_motoristas()
        
        if not motoristas:
            print("Nenhum motorista cadastrado.")
            return
        
        for i, motorista in enumerate(motoristas, 1):
            status = "Ativo" if motorista['ativo'] else "Inativo"
            print(f"{i}. {motorista['nome']} - CPF: {motorista['cpf']} - Status: {status}")
            print(f"   Veículo: {motorista['veiculo']} - Tel: {motorista['telefone']}")
            print(f"   E-mail: {motorista['email']}")
            print()
    
    def menu_motorista(self, motorista):
        """Menu do motorista após login"""
        while True:
            print(f"\n--- MENU MOTORISTA - {motorista['nome']} ---")
            print("1. Ver meus dados")
            print("2. Editar dados")
            print("3. Voltar ao menu principal")
            
            opcao = input("Escolha uma opção: ")
            
            if opcao == '1':
                self.ver_dados_motorista(motorista)
            elif opcao == '2':
                self.editar_dados_motorista(motorista)
            elif opcao == '3':
                break
            else:
                print("Opção inválida!")
    
    def ver_dados_motorista(self, motorista):
        """Exibe dados do motorista"""
        print("\n--- MEUS DADOS ---")
        print(f"Nome: {motorista['nome']}")
        print(f"CPF: {motorista['cpf']}")
        print(f"E-mail: {motorista['email']}")
        print(f"Telefone: {motorista['telefone']}")
        print(f"Veículo: {motorista['veiculo']}")
        print(f"Status: {'Ativo' if motorista['ativo'] else 'Inativo'}")
    
    def editar_dados_motorista(self, motorista):
        """Permite editar dados do motorista"""
        print("\n--- EDITAR DADOS ---")
        print("Deixe em branco para manter o valor atual")
        
        novo_email = input(f"Novo e-mail [{motorista['email']}]: ")
        novo_telefone = input(f"Novo telefone [{motorista['telefone']}]: ")
        novo_veiculo = input(f"Novo veículo [{motorista['veiculo']}]: ")
        
        updates = {}
        if novo_email:
            updates['email'] = novo_email
        if novo_telefone:
            updates['telefone'] = novo_telefone
        if novo_veiculo:
            updates['veiculo'] = novo_veiculo
        
        if updates:
            if self.gerenciador_motoristas.editar_motorista(motorista['cpf'], **updates):
                print("Dados atualizados com sucesso!")
            else:
                print("Erro ao atualizar dados!")
        else:
            print("Nenhuma alteração realizada.")


# Função principal
def main():
    sistema = SistemaTransporte()
    
    # Cadastrar alguns motoristas de exemplo
    try:
        sistema.gerenciador_motoristas.cadastrar_motorista(
            "João Silva", "123.456.789-00", "joao@email.com", 
            "(11) 99999-9999", "ABC-1234", "motorista1", "senha123"
        )
        sistema.gerenciador_motoristas.cadastrar_motorista(
            "Maria Santos", "111.222.333-44", "maria@email.com",
            "(11) 88888-8888", "XYZ-5678", "admin", "admin123"
        )
    except ValueError:
        pass  # Motoristas já cadastrados
    
    sistema.menu_principal()


if __name__ == "__main__":
    main()