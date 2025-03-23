import mysql.connector
 
class BancoDeDados:
    def __init__(self):
        self.conexao = mysql.connector.connect(
            host="localhost",
            port=3307,
            user="root",
            password="root",
            database="infinity-desafio"
        )
        self.cursor = self.conexao.cursor()
        print("Conexão com o banco foi estabelecida com sucesso!")
        self.criar_tabelas()
 
    def criar_tabelas(self):
        comando_criar_produtos = """
            CREATE TABLE IF NOT EXISTS produtos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                descricao TEXT,
                quantidade INT NOT NULL,
                preco DECIMAL(10, 2) NOT NULL
            )
        """
        self.cursor.execute(comando_criar_produtos)
 
        comando_criar_vendas = """
            CREATE TABLE IF NOT EXISTS vendas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                produto_id INT,
                quantidade INT NOT NULL,
                data_venda DATETIME NOT NULL,
                FOREIGN KEY (produto_id) REFERENCES produtos(id)
            )
        """
        self.cursor.execute(comando_criar_vendas)
        self.conexao.commit()
        print("Tabelas criadas/verificadas com sucesso!")
 
class Sistema:
    def __init__(self):
        self.bd = BancoDeDados()
 
 
    def adicionar_produto(self, novo_produto):
        if not novo_produto.nome or novo_produto.qtde < 0 or novo_produto.preco <= 0:
            print("Dados do produto inválidos")
            return None
 
        comando = """
            INSERT INTO produtos (nome, descricao, quantidade, preco)
            VALUES (%s, %s, %s, %s)
        """
        dados = (novo_produto.nome, novo_produto.descricao, novo_produto.qtde, novo_produto.preco)
        self.bd.cursor.execute(comando, dados)
        self.bd.conexao.commit()
        novo_id = self.bd.cursor.lastrowid
        print(f"Produto {novo_produto.nome} adicionado com sucesso!")
        return novo_id
 
    def listar_produtos(self):
        self.bd.cursor.execute("SELECT * FROM produtos")
        produtos = []
        for produto in self.bd.cursor.fetchall():
            produtos.append(
                Produto(
                    id=produto[0],
                    nome=produto[1],
                    descricao=produto[2],
                    qtde=produto[3],
                    preco=produto[4]
                )
            )
        if not produtos:
            print("Nenhum produto cadastrado!")
 
        return produtos
 
    def editar_produto(self):
        produtos = self.listar_produtos()
        if not produtos:
            print("Não há produtos para editar!")
            return

        print("\n---------EDITAR PRODUTO----------")
        id_produto = int(input("Digite o ID do produto que deseja editar: "))
        
        produto_encontrado = None
        for produto in produtos:
            if produto.id == id_produto:
                produto_encontrado = produto
                break

        if not produto_encontrado:
            print("Produto não encontrado!")
            return

        print(f"\nEditando produto: {produto_encontrado.nome}")
        novo_nome = input("Digite o novo nome (ou pressione Enter para manter o atual): ")
        nova_descricao = input("Digite a nova descrição (ou pressione Enter para manter a atual): ")
        nova_qtde = input("Digite a nova quantidade (ou pressione Enter para manter a atual): ")
        novo_preco = input("Digite o novo preço (ou pressione Enter para manter o atual): ")

        # Mantém os valores atuais se nenhum novo valor for fornecido
        if not novo_nome:
            novo_nome = produto_encontrado.nome
        if not nova_descricao:
            nova_descricao = produto_encontrado.descricao
        if not nova_qtde:
            nova_qtde = produto_encontrado.qtde
        else:
            nova_qtde = int(nova_qtde)
        if not novo_preco:
            novo_preco = produto_encontrado.preco
        else:
            novo_preco = float(novo_preco)

        # Validações
        if nova_qtde < 0 or novo_preco <= 0:
            print("Dados inválidos! Quantidade não pode ser negativa e preço deve ser maior que zero.")
            return

        comando = """
            UPDATE produtos 
            SET nome = %s, descricao = %s, quantidade = %s, preco = %s
            WHERE id = %s
        """
        dados = (novo_nome, nova_descricao, nova_qtde, novo_preco, id_produto)
        self.bd.cursor.execute(comando, dados)
        self.bd.conexao.commit()
        print(f"Produto {novo_nome} atualizado com sucesso!")
 
    def deletar_produto(self):
        if not (produtos := self.listar_produtos()):
            print("Não há produtos para deletar!")
            return

        try:
            id_produto = int(input("\nDigite o ID do produto para deletar: "))
            if not any(p.id == id_produto for p in produtos):
                print("Produto não encontrado!")
                return

            self.bd.cursor.execute("DELETE FROM produtos WHERE id = %s", (id_produto,))
            self.bd.conexao.commit()
            print("Produto deletado com sucesso!")
        except ValueError:
            print("ID inválido!")
 
    def registrar_venda(self):
        produtos = self.listar_produtos()
        if not produtos:
            print("Não há produtos disponíveis para venda!")
            return

        try:
            id_produto = int(input("\nDigite o ID do produto: "))
            produto = next((p for p in produtos if p.id == id_produto), None)
            
            if not produto:
                print("Produto não encontrado!")
                return

            quantidade = int(input("Digite a quantidade a vender: "))
            if quantidade <= 0:
                print("Quantidade inválida!")
                return

            if quantidade > produto.qtde:
                print("Quantidade insuficiente em estoque!")
                return

            comando = """
                INSERT INTO vendas (produto_id, quantidade, data_venda)
                VALUES (%s, %s, NOW())
            """
            self.bd.cursor.execute(comando, (id_produto, quantidade))
            
            # Atualiza o estoque
            comando_update = """
                UPDATE produtos 
                SET quantidade = quantidade - %s 
                WHERE id = %s
            """
            self.bd.cursor.execute(comando_update, (quantidade, id_produto))
            
            self.bd.conexao.commit()
            print(f"Venda registrada com sucesso! Total: R$ {produto.preco * quantidade:.2f}")
        except ValueError:
            print("Dados inválidos!")

    def listar_vendas(self):
        comando = """
            SELECT v.*, p.nome as produto_nome, p.preco as preco_unitario
            FROM vendas v
            JOIN produtos p ON v.produto_id = p.id
            ORDER BY v.data_venda DESC
        """
        self.bd.cursor.execute(comando)
        vendas = []
        
        for venda in self.bd.cursor.fetchall():
            vendas.append({
                'id': venda[0],
                'produto_id': venda[1],
                'quantidade': venda[2],
                'data_venda': venda[3],
                'produto_nome': venda[4],
                'preco_unitario': venda[5],
                'total': venda[2] * venda[5]
            })
        
        if not vendas:
            print("Nenhuma venda registrada!")
            return

        print("\n---------VENDAS REGISTRADAS----------")
        for venda in vendas:
            print(f"ID: {venda['id']}")
            print(f"Produto: {venda['produto_nome']}")
            print(f"Quantidade: {venda['quantidade']}")
            print(f"Preço Unitário: R$ {venda['preco_unitario']:.2f}")
            print(f"Total: R$ {venda['total']:.2f}")
            print(f"Data: {venda['data_venda']}")
            print("----------------------\n")

    def editar_venda(self):
        if not (vendas := self.listar_vendas()):
            return

        try:
            id_venda = int(input("\nDigite o ID da venda para editar: "))
            comando = "SELECT * FROM vendas WHERE id = %s"
            self.bd.cursor.execute(comando, (id_venda,))
            venda = self.bd.cursor.fetchone()
            
            if not venda:
                print("Venda não encontrada!")
                return

            nova_quantidade = int(input("Digite a nova quantidade: "))
            if nova_quantidade <= 0:
                print("Quantidade inválida!")
                return

            # Verifica estoque disponível
            self.bd.cursor.execute("SELECT quantidade FROM produtos WHERE id = %s", (venda[1],))
            estoque_atual = self.bd.cursor.fetchone()[0]
            diferenca = nova_quantidade - venda[2]

            if estoque_atual + venda[2] < nova_quantidade:
                print("Quantidade insuficiente em estoque!")
                return

            # Atualiza a venda
            comando = "UPDATE vendas SET quantidade = %s WHERE id = %s"
            self.bd.cursor.execute(comando, (nova_quantidade, id_venda))
            
            # Atualiza o estoque
            comando = "UPDATE produtos SET quantidade = quantidade - %s WHERE id = %s"
            self.bd.cursor.execute(comando, (diferenca, venda[1]))
            
            self.bd.conexao.commit()
            print("Venda atualizada com sucesso!")
        except ValueError:
            print("Dados inválidos!")

    def deletar_venda(self):
        if not (vendas := self.listar_vendas()):
            return

        try:
            id_venda = int(input("\nDigite o ID da venda para deletar: "))
            comando = "SELECT * FROM vendas WHERE id = %s"
            self.bd.cursor.execute(comando, (id_venda,))
            venda = self.bd.cursor.fetchone()
            
            if not venda:
                print("Venda não encontrada!")
                return

            # Restaura o estoque
            comando = "UPDATE produtos SET quantidade = quantidade + %s WHERE id = %s"
            self.bd.cursor.execute(comando, (venda[2], venda[1]))
            
            # Deleta a venda
            comando = "DELETE FROM vendas WHERE id = %s"
            self.bd.cursor.execute(comando, (id_venda,))
            
            self.bd.conexao.commit()
            print("Venda deletada com sucesso!")
        except ValueError:
            print("ID inválido!")

class Produto:
    def __init__(self, nome, descricao, qtde, preco, id=None):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.qtde = qtde
        self.preco = preco
 
class Venda:
    def __init__(self, id, produto_id, qtde, data_venda):
        self.id = id
        self.produto_id = produto_id
        self.qtde = qtde
        self.data_venda = data_venda
 
sistema = Sistema()
while True:
    print("------------ESTOQUE v0.1-------------")
    print("1 - Adicionar novo produto")
    print("2 - Listar produtos")
    print("3 - Editar produto")
    print("4 - Deletar produto")
    print("5 - Registrar venda")
    print("6 - Listar vendas")
    print("7 - Editar venda")
    print("8 - Deletar venda")
    print("9 - Sair")
    op = int(input("-> "))
    if op == 1:
        nome = input("Digite o nome do produto: ")
        descricao = input("Digite a descrição do produto: ")
        qtde = int(input("Digite a quantidade do produto: "))
        preco = float(input("Digite o preço do produto: "))
        novo_produto = Produto(nome, descricao, qtde, preco)
        sistema.adicionar_produto(novo_produto)
    elif op == 2:
        produtos = sistema.listar_produtos()
        print("---------PRODUTOS CADASTRADOS----------")
        for produto in produtos:
            print(f"ID: {produto.id}")
            print(f"Nome: {produto.nome}")
            print(f"Quantidade em estoque: {produto.qtde}")
            print(f"Preço Unitário: {produto.preco}")
            print(f"Descrição: {produto.descricao}")
            print("----------------------\n")
    elif op == 3:
        sistema.editar_produto()
    elif op == 4:
        sistema.deletar_produto()
    elif op == 5:
        sistema.registrar_venda()
    elif op == 6:
        sistema.listar_vendas()
    elif op == 7:
        sistema.editar_venda()
    elif op == 8:
        sistema.deletar_venda()
    elif op == 9:
        print("Desligando o sistema...")
        break