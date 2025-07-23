import customtkinter as ctk
import bcrypt
import json
from datetime import datetime
import os

# Configurações
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('green')
app = ctk.CTk()
app.title('Sistema de Login Seguro')
app.geometry('500x500')
app.resizable(False, False)

# Constantes
MAX_TENTATIVAS = 5
tentativas = 0
ARQUIVO_USUARIOS = "usuarios.json"
LOG_ARQUIVO = "log_acessos.txt"

usuario_logado = None  # Variável global para armazenar usuário logado

# Carrega ou cria arquivo de usuários
def carregar_usuarios():
    if not os.path.exists(ARQUIVO_USUARIOS) or os.stat(ARQUIVO_USUARIOS).st_size == 0:
        with open(ARQUIVO_USUARIOS, "w") as f:
            json.dump({}, f)
        return {}

    try:
        with open(ARQUIVO_USUARIOS, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Se o conteúdo estiver inválido, substitui por dicionário vazio
        with open(ARQUIVO_USUARIOS, "w") as f:
            json.dump({}, f)
        return {}

def salvar_usuarios(dados):
    with open(ARQUIVO_USUARIOS, "w") as f:
        json.dump(dados, f, indent=4)

usuarios = carregar_usuarios()

# Logs
def registrar_tentativa(usuario, sucesso):
    with open(LOG_ARQUIVO, "a") as f:
        horario = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "SUCESSO" if sucesso else "FALHA"
        f.write(f"[{horario}] Usuário: {usuario} | Status: {status}\n")

# Tela de login
def mostrar_tela_login():
    global campo_usuario, campo_senha, resultado_login, progresso, botao_login, tentativas

    tentativas = 0  # resetar tentativas ao mostrar login

    for widget in app.winfo_children():
        widget.destroy()

    ctk.CTkLabel(app, text='Usuário:', font=('Arial', 14)).pack(pady=(20, 5))
    campo_usuario = ctk.CTkEntry(app, placeholder_text='Digite seu usuário')
    campo_usuario.pack(pady=5, padx=20, fill='x')

    ctk.CTkLabel(app, text='Senha:', font=('Arial', 14)).pack(pady=5)
    campo_senha = ctk.CTkEntry(app, placeholder_text='Digite sua senha', show='*')
    campo_senha.pack(pady=5, padx=20, fill='x')

    botao_login = ctk.CTkButton(app, text='Login', command=validar_login, height=40)
    botao_login.pack(pady=10)

    ctk.CTkButton(app, text="Cadastrar novo usuário", command=abrir_tela_cadastro).pack(pady=5)

    resultado_login = ctk.CTkLabel(app, text='', font=('Arial', 12))
    resultado_login.pack(pady=10)

    progresso = ctk.CTkProgressBar(app, mode='indeterminate')
    progresso.pack_forget()

# Validação login
def validar_login():
    global tentativas, usuario_logado
    usuario = campo_usuario.get().strip()
    senha = campo_senha.get().encode()

    if not usuario or not senha:
        resultado_login.configure(text='Preencha todos os campos!', text_color='orange')
        return

    if tentativas >= MAX_TENTATIVAS:
        resultado_login.configure(text='Muitas tentativas. Tente mais tarde.', text_color='orange')
        botao_login.configure(state='disabled')
        return

    if usuario in usuarios:
        senha_hash = usuarios[usuario]["senha"].encode()
        if bcrypt.checkpw(senha, senha_hash):
            registrar_tentativa(usuario, True)
            resultado_login.configure(text='Login realizado com sucesso!', text_color='green')
            progresso.pack(pady=10)
            progresso.start()
            usuario_logado = usuario
            app.after(3000, lambda: [progresso.stop(), progresso.pack_forget(), abrir_nova_tela()])
            return

    tentativas += 1
    registrar_tentativa(usuario, False)
    resultado_login.configure(text='Usuário ou senha incorretos!', text_color='red')

# Cadastro de novo usuário
def abrir_tela_cadastro():
    for widget in app.winfo_children():
        widget.destroy()

    def cadastrar_usuario():
        novo_usuario = entrada_usuario.get().strip()
        nova_senha = entrada_senha.get()
        confirmar_senha = entrada_confirma.get()

        if not novo_usuario or not nova_senha or not confirmar_senha:
            aviso_cadastro.configure(text="Preencha todos os campos!", text_color="orange")
            return

        if novo_usuario in usuarios:
            aviso_cadastro.configure(text="Usuário já existe!", text_color="red")
            return

        if nova_senha != confirmar_senha:
            aviso_cadastro.configure(text="Senhas não coincidem!", text_color="red")
            return

        senha_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()).decode()
        usuarios[novo_usuario] = {
            "senha": senha_hash,
            "criado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        salvar_usuarios(usuarios)
        aviso_cadastro.configure(text="Usuário cadastrado com sucesso!", text_color="green")

    ctk.CTkLabel(app, text="Cadastro de Novo Usuário", font=('Arial', 18)).pack(pady=10)

    entrada_usuario = ctk.CTkEntry(app, placeholder_text="Novo usuário")
    entrada_usuario.pack(pady=5, padx=20, fill='x')

    entrada_senha = ctk.CTkEntry(app, placeholder_text="Nova senha", show="*")
    entrada_senha.pack(pady=5, padx=20, fill='x')

    entrada_confirma = ctk.CTkEntry(app, placeholder_text="Confirmar senha", show="*")
    entrada_confirma.pack(pady=5, padx=20, fill='x')

    botao_salvar = ctk.CTkButton(app, text="Salvar", command=cadastrar_usuario)
    botao_salvar.pack(pady=15)

    aviso_cadastro = ctk.CTkLabel(app, text="", font=('Arial', 12))
    aviso_cadastro.pack()

    botao_voltar = ctk.CTkButton(app, text="Voltar para login", command=mostrar_tela_login)
    botao_voltar.pack(pady=10)

# Sistema de dados
def abrir_nova_tela():
    for widget in app.winfo_children():
        widget.destroy()

    boas_vindas = ctk.CTkLabel(
        app,
        text=f'Bem-vindo ao Sistema de Dados, {usuario_logado}',
        font=('Arial', 18)
    )
    boas_vindas.pack(pady=20)

    def mostrar_usuarios():
        # Remove se já estiver mostrado
        for widget in app.winfo_children():
            if getattr(widget, "_id_", "") == "lista_usuarios":
                widget.destroy()

        texto_lista = "Usuários cadastrados:\n\n"
        for nome, dados in usuarios.items():
            criado_em = dados.get("criado_em", "Desconhecida")
            texto_lista += f"• {nome} (cadastrado em: {criado_em})\n"

        lista_label = ctk.CTkLabel(
            app,
            text=texto_lista,
            font=('Arial', 14),
            justify="left"
        )
        lista_label._id_ = "lista_usuarios"
        lista_label.pack(pady=10)

        botao_voltar = ctk.CTkButton(
            app,
            text="Ocultar lista",
            command=abrir_nova_tela
        )
        botao_voltar._id_ = "lista_usuarios"
        botao_voltar.pack(pady=10)

    botao_listar = ctk.CTkButton(
        app,
        text='Listar todos os usuários',
        command=mostrar_usuarios
    )
    botao_listar.pack(pady=20)

    # Botão de logout
    botao_logout = ctk.CTkButton(app, text='Logout', command=mostrar_tela_login)
    botao_logout.pack(pady=(10, 5))

    # Excluir usuário atual (com restrição para "admin")
    def excluir_usuario():
        for widget in app.winfo_children():
            widget.destroy()

        if usuario_logado == "admin":
            ctk.CTkLabel(app, text="O usuário 'admin' não pode ser excluído.", font=('Arial', 14), text_color="red").pack(pady=40)
            ctk.CTkButton(app, text="Voltar", command=abrir_nova_tela).pack(pady=10)
            return

        def confirmar_exclusao():
            del usuarios[usuario_logado]
            salvar_usuarios(usuarios)
            mostrar_tela_login()

        ctk.CTkLabel(app, text=f"Tem certeza que deseja excluir a conta '{usuario_logado}'?", font=('Arial', 14)).pack(pady=40)
        ctk.CTkButton(app, text='Confirmar exclusão', fg_color='red', command=confirmar_exclusao).pack(pady=10)
        ctk.CTkButton(app, text='Cancelar', command=abrir_nova_tela).pack()

    botao_excluir = ctk.CTkButton(app, text='Excluir minha conta', command=excluir_usuario, fg_color='darkred')
    botao_excluir.pack(pady=5)

# Inicializa tela
mostrar_tela_login()
app.mainloop()
