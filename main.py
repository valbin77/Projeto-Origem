import tkinter as tk
from tkinter import messagebox
import sqlite3
import bcrypt
from functools import partial

# Conectar ao banco de dados
conn = sqlite3.connect("lanchonete.db")
c = conn.cursor()

# Criar tabelas se não existirem
c.execute('''CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    validade TEXT,
    preco TEXT
)''')
c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE,
    senha TEXT
)''')
conn.commit()


def limpar_frames():
    frame_cadastro_produto.pack_forget()
    frame_visualizar_produtos.pack_forget()


def cadastrar_usuario():
    usuario = entry_novo_usuario.get()
    senha = entry_nova_senha.get()

    if usuario and senha:
        senha_hashed = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        try:
            c.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (usuario, senha_hashed))
            conn.commit()
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            cadastro_window.destroy()  # Fechar a janela de cadastro
            entry_usuario.delete(0, tk.END)
            entry_senha.delete(0, tk.END)
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Usuário já existe!")
    else:
        messagebox.showwarning("Atenção", "Preencha todos os campos!")


def abrir_tela_cadastro():
    global cadastro_window, entry_novo_usuario, entry_nova_senha

    cadastro_window = tk.Toplevel(login_window)
    cadastro_window.title("Cadastrar Usuário")
    cadastro_window.geometry("300x200")

    tk.Label(cadastro_window, text="Novo Usuário").pack()
    entry_novo_usuario = tk.Entry(cadastro_window)
    entry_novo_usuario.pack()
    tk.Label(cadastro_window, text="Nova Senha").pack()
    entry_nova_senha = tk.Entry(cadastro_window, show="*")
    entry_nova_senha.pack()
    tk.Button(cadastro_window, text="Cadastrar", command=cadastrar_usuario).pack(pady=10)


def verificar_login():
    usuario = entry_usuario.get()
    senha = entry_senha.get()

    c.execute("SELECT senha FROM usuarios WHERE usuario=?", (usuario,))
    resultado = c.fetchone()
    if resultado and bcrypt.checkpw(senha.encode('utf-8'), resultado[0]):
        login_window.destroy()
        abrir_menu_principal()
    else:
        messagebox.showerror("Erro", "Usuário ou senha incorretos!")


def abrir_menu_principal():
    global menu_window, frame_cadastro_produto, frame_visualizar_produtos, entry_nome, entry_validade, entry_preco, entry_pesquisar
    menu_window = tk.Tk()
    menu_window.title("Menu Principal")
    menu_window.geometry("400x400")

    menu_frame = tk.Frame(menu_window)
    menu_frame.pack(anchor="w", padx=10, pady=5)

    tk.Button(menu_frame, text="Cadastrar Produto", command=abrir_cadastro_produto).pack(side="left", padx=5)
    tk.Button(menu_frame, text="Visualizar Produtos", command=abrir_visualizar_produtos).pack(side="left", padx=5)

    frame_cadastro_produto = tk.Frame(menu_window)
    frame_visualizar_produtos = tk.Frame(menu_window)


def abrir_cadastro_produto():
    limpar_frames()
    frame_cadastro_produto.pack()

    global entry_nome, entry_validade, entry_preco
    for widget in frame_cadastro_produto.winfo_children():
        widget.destroy()

    tk.Label(frame_cadastro_produto, text="Nome").pack()
    entry_nome = tk.Entry(frame_cadastro_produto)
    entry_nome.pack()
    tk.Label(frame_cadastro_produto, text="Validade").pack()
    entry_validade = tk.Entry(frame_cadastro_produto)
    entry_validade.pack()
    tk.Label(frame_cadastro_produto, text="Preço").pack()
    entry_preco = tk.Entry(frame_cadastro_produto)
    entry_preco.pack()
    tk.Button(frame_cadastro_produto, text="Salvar", command=salvar_dados).pack(pady=10)


def abrir_visualizar_produtos():
    limpar_frames()
    frame_visualizar_produtos.pack()

    global entry_pesquisar
    for widget in frame_visualizar_produtos.winfo_children():
        widget.destroy()

    tk.Label(frame_visualizar_produtos, text="Pesquisar Produto").pack()
    entry_pesquisar = tk.Entry(frame_visualizar_produtos)
    entry_pesquisar.pack()
    tk.Button(frame_visualizar_produtos, text="Pesquisar", command=pesquisar_produtos).pack(pady=5)

    exibir_produtos()


def exibir_produtos(produtos=None):
    if produtos is None:
        c.execute("SELECT * FROM produtos")
        produtos = c.fetchall()

    for widget in frame_visualizar_produtos.winfo_children()[3:]:
        widget.destroy()

    for produto in produtos:
        frame = tk.Frame(frame_visualizar_produtos)
        frame.pack()
        tk.Label(frame, text=f"ID: {produto[0]} - Nome: {produto[1]} - Validade: {produto[2]} - Preço: {produto[3]}").pack(side="left")
        tk.Button(frame, text="Editar", command=partial(editar_produto, produto[0])).pack(side="right")
        tk.Button(frame, text="Excluir", command=partial(excluir_produto, produto[0])).pack(side="right")


def pesquisar_produtos():
    termo_pesquisa = entry_pesquisar.get()

    if termo_pesquisa.isdigit():  # Se o termo de pesquisa for um número, pesquisar pelo ID
        c.execute("SELECT * FROM produtos WHERE id=?", (termo_pesquisa,))
    else:  # Caso contrário, pesquisar pelo nome
        c.execute("SELECT * FROM produtos WHERE nome LIKE ?", ('%' + termo_pesquisa + '%',))

    produtos = c.fetchall()
    exibir_produtos(produtos)


def salvar_dados():
    nome = entry_nome.get()
    validade = entry_validade.get()
    preco = entry_preco.get()

    if nome and validade and preco:
        c.execute("INSERT INTO produtos (nome, validade, preco) VALUES (?,?,?)", (nome, validade, preco))
        conn.commit()
        messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
        entry_nome.delete(0, tk.END)
        entry_validade.delete(0, tk.END)
        entry_preco.delete(0, tk.END)
    else:
        messagebox.showwarning("Atenção", "Preencha todos os campos!")


def editar_produto(produto_id):
    limpar_frames()
    frame_cadastro_produto.pack()

    c.execute("SELECT * FROM produtos WHERE id=?", (produto_id,))
    produto = c.fetchone()

    if produto:
        global entry_nome, entry_validade, entry_preco

        for widget in frame_cadastro_produto.winfo_children():
            widget.destroy()

        tk.Label(frame_cadastro_produto, text="Nome").pack()
        entry_nome = tk.Entry(frame_cadastro_produto)
        entry_nome.insert(0, produto[1])
        entry_nome.pack()

        tk.Label(frame_cadastro_produto, text="Validade").pack()
        entry_validade = tk.Entry(frame_cadastro_produto)
        entry_validade.insert(0, produto[2])
        entry_validade.pack()

        tk.Label(frame_cadastro_produto, text="Preço").pack()
        entry_preco = tk.Entry(frame_cadastro_produto)
        entry_preco.insert(0, produto[3])
        entry_preco.pack()

        tk.Button(frame_cadastro_produto, text="Salvar", command=partial(salvar_edicao, produto_id)).pack(pady=10)


def salvar_edicao(produto_id):
    nome = entry_nome.get()
    validade = entry_validade.get()
    preco = entry_preco.get()

    if nome and validade and preco:
        c.execute("UPDATE produtos SET nome=?, validade=?, preco=? WHERE id=?", (nome, validade, preco, produto_id))
        conn.commit()
        messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
        limpar_frames()
        abrir_visualizar_produtos()
    else:
        messagebox.showwarning("Atenção", "Preencha todos os campos!")


def excluir_produto(produto_id):
    resposta = messagebox.askyesno("Confirmação", "Tem certeza que deseja excluir este produto?")
    if resposta:
        c.execute("DELETE FROM produtos WHERE id=?", (produto_id,))
        conn.commit()
        messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
        abrir_visualizar_produtos()


# Tela de login
login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("300x200")

frame_login = tk.Frame(login_window)
frame_login.pack()

tk.Label(frame_login, text="Usuário").pack()
entry_usuario = tk.Entry(frame_login)
entry_usuario.pack()
tk.Label(frame_login, text="Senha").pack()
entry_senha = tk.Entry(frame_login, show="*")
entry_senha.pack()
tk.Button(frame_login, text="Entrar", command=verificar_login).pack(pady=5)
tk.Button(frame_login, text="Cadastrar Usuário", command=abrir_tela_cadastro).pack(pady=5)

login_window.mainloop()