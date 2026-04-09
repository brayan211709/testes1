import sqlite3
import getpass

def conectar():
    return sqlite3.connect('sisvenda.db')

def inicializar_sistema():
    conn = conectar()
    cursor = conn.cursor()
    
    # Tabela de Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    ''')
    
    # Tabela de Clientes (NOVA)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE,
            telefone TEXT
        )
    ''')
    
    # Criar admin padrão
    try:
        cursor.execute('INSERT INTO usuarios (username, senha) VALUES (?, ?)', ('admin', '123'))
    except sqlite3.IntegrityError:
        pass
        
    cursor.execute('CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY, nome TEXT, preco REAL, estoque INTEGER)')
    cursor.execute('CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY, data TIMESTAMP DEFAULT CURRENT_TIMESTAMP, total REAL)')
    
    conn.commit()
    conn.close()

def login():
    print("\n--- ACESSO AO SISTEMA ---")
    usuario = input("Usuário: ")
    senha = input("Senha: ") 
    
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE username = ? AND senha = ?', (usuario, senha))
    user = cursor.fetchone()
    conn.close()
    
    return user is not None

# --- Funções de Clientes ---

def cadastrar_cliente():
    print("\n--- NOVO CADASTRO DE CLIENTE ---")
    nome = input("Nome completo: ")
    cpf = input("CPF (apenas números): ")
    telefone = input("Telefone: ")
    
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO clientes (nome, cpf, telefone) VALUES (?, ?, ?)', (nome, cpf, telefone))
        conn.commit()
        print(f"\n[OK] Cliente {nome} cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        print("\n[ERRO] Este CPF já está cadastrado.")
    finally:
        conn.close()

def listar_clientes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clientes')
    clientes = cursor.fetchall()
    
    print("\n--- LISTA DE CLIENTES ---")
    if not clientes:
        print("Nenhum cliente cadastrado.")
    for c in clientes:
        print(f"ID: {c[0]} | Nome: {c[1]} | CPF: {c[2]} | Tel: {c[3]}")
    conn.close()

# --- Funções de Negócio ---

def cadastrar_produto():
    nome = input("Nome do produto: ")
    preco = float(input("Preço: "))
    estoque = int(input("Quantidade em estoque: "))
    
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)', (nome, preco, estoque))
    conn.commit()
    conn.close()
    print(f"\n[OK] {nome} cadastrado!")

def listar_produtos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM produtos')
    produtos = cursor.fetchall()
    print("\n--- ESTOQUE ATUAL ---")
    for p in produtos:
        print(f"ID: {p[0]} | {p[1]} | R$ {p[2]:.2f} | Qtd: {p[3]}")
    conn.close()

def nova_venda():
    listar_produtos()
    try:
        id_p = int(input("\nID do produto: "))
        qtd = int(input("Quantidade: "))
        
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('SELECT nome, preco, estoque FROM produtos WHERE id = ?', (id_p,))
        res = cursor.fetchone()
        
        if res and res[2] >= qtd:
            total = res[1] * qtd
            cursor.execute('UPDATE produtos SET estoque = estoque - ? WHERE id = ?', (qtd, id_p))
            cursor.execute('INSERT INTO vendas (total) VALUES (?)', (total,))
            conn.commit()
            print(f"\n[SUCESSO] Venda de {res[0]} concluída! Total: R$ {total:.2f}")
        else:
            print("\n[ERRO] Estoque insuficiente ou ID inválido.")
        conn.close()
    except ValueError:
        print("\n[ERRO] Entrada inválida.")

# --- Menu Principal ---

def menu():
    while True:
        print("\n=== SISVENDA - MENU PRINCIPAL ===")
        print("1. Nova Venda")
        print("2. Cadastrar Produto")
        print("3. Listar Estoque")
        print("4. Cadastrar Cliente")  # Nova opção
        print("5. Listar Clientes")    # Nova opção
        print("6. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            nova_venda()
        elif opcao == '2':
            cadastrar_produto()
        elif opcao == '3':
            listar_produtos()
        elif opcao == '4':
            cadastrar_cliente()
        elif opcao == '5':
            listar_clientes()
        elif opcao == '6':
            print("Encerrando...")
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    inicializar_sistema()
    
    tentativas = 3
    while tentativas > 0:
        if login():
            menu()
            break
        else:
            tentativas -= 1
            print(f"Login incorreto! Tentativas restantes: {tentativas}")
    
    if tentativas == 0:
        print("Acesso bloqueado.")