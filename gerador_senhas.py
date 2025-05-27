#%%

import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from cryptography.fernet import Fernet
import os
from ttkthemes import ThemedTk

# Configurações de estilo
FONTE_PRINCIPAL = ("Arial", 12)
COR_FUNDO = "#f0f0f0"
COR_BOTAO = "#4CAF50"
COR_TEXTO_BOTAO = "white"

# Caracteres disponíveis
letras = list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')
numeros = list('0123456789')
caracteres_especiais = list('!@#$%^&*()_+-=[]{}|;:\'",.<>?/`~\\')

# Funções de geração de senha
def gerar_senhas_por_niveis(nivel):
    if nivel == "B":
        return ''.join(random.choice(letras) for _ in range(6))
    elif nivel == "M":
        listas_somadas = letras + numeros
        return ''.join(random.choice(listas_somadas) for _ in range(8))
    elif nivel == "A":
        listas_somadas = letras + numeros + caracteres_especiais
        return ''.join(random.choice(listas_somadas) for _ in range(12))
    elif nivel == "D":
        listas_somadas = letras + numeros + caracteres_especiais
        return ''.join(random.choice(listas_somadas) for _ in range(20))

def gerar_senhas_customizavel(tamanho, incluir_num, incluir_especiais, palavras, sem_repeticao):
    listas_somadas = letras.copy()
    if incluir_num:
        listas_somadas += numeros
    if incluir_especiais:
        listas_somadas += caracteres_especiais

    tamanho_palavras = sum(len(palavra) for palavra in palavras)
    tamanho_aleatorio = tamanho - tamanho_palavras

    if sem_repeticao:
        try:
            senha_aleatoria = gerar_senha_sem_repeticao(listas_somadas, tamanho_aleatorio)
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
            return None
    else:
        senha_aleatoria = ''.join(random.choice(listas_somadas) for _ in range(tamanho_aleatorio))

    senha_com_palavras = senha_aleatoria + ''.join(palavras)
    senha_final = ''.join(random.sample(senha_com_palavras, len(senha_com_palavras)))
    return senha_final

def gerar_senha_sem_repeticao(caracteres, tamanho):
    if tamanho > len(caracteres):
        raise ValueError("O tamanho da senha não pode ser maior que o número de caracteres disponíveis.")
    return ''.join(random.sample(caracteres, tamanho))

def avaliar_forca(senha):
    if len(senha) < 8:
        return "Fraca"
    if len(senha) <= 12:
        if any(char in numeros for char in senha) or any(char in caracteres_especiais for char in senha):
            return "Média"
        return "Fraca"
    else:
        if any(char in numeros for char in senha) and any(char in caracteres_especiais for char in senha):
            return "Forte"
        return "Média"

# Funções de criptografia
def gerar_chave():
    return Fernet.generate_key()

def criptografar_senha(senha, chave):
    cipher_suite = Fernet(chave)
    return cipher_suite.encrypt(senha.encode()).decode()

def descriptografar_senha(senha_criptografada, chave):
    cipher_suite = Fernet(chave)
    return cipher_suite.decrypt(senha_criptografada.encode()).decode()

# Lista de senhas geradas
senhas_geradas = []

# Funções auxiliares
def copiar_para_clipboard(senha):
    janela.clipboard_clear()
    janela.clipboard_append(senha)
    messagebox.showinfo("Copiar", "Senha copiada para a área de transferência!")

def salvar_senhas():
    if not senhas_geradas:
        messagebox.showinfo("Erro", "Nenhuma senha gerada para salvar.")
        return

    arquivo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Arquivos de texto", "*.txt")])
    if arquivo:
        try:
            chave = gerar_chave()
            senhas_criptografadas = [criptografar_senha(senha, chave) for senha in senhas_geradas]

            with open(arquivo, "w") as f:
                f.write(f"Chave de criptografia: {chave.decode()}\n\n")
                for i, senha in enumerate(senhas_criptografadas):
                    f.write(f"{i + 1}: {senha}\n")

            messagebox.showinfo("Sucesso", f"Senhas criptografadas salvas com sucesso em: {arquivo}")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao salvar o arquivo: {e}")

def salvar_senhas_area_trabalho():
    if not senhas_geradas:
        messagebox.showinfo("Erro", "Nenhuma senha gerada para salvar.")
        return

    try:
        area_trabalho = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        arquivo = os.path.join(area_trabalho, "senhas_geradas.txt")

        with open(arquivo, "w") as f:
            for i, senha in enumerate(senhas_geradas):
                f.write(f"{i + 1}: {senha}\n")

        messagebox.showinfo("Sucesso", f"Senhas salvas com sucesso na área de trabalho: {arquivo}")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao salvar o arquivo: {e}")

def deletar_senhas():
    global senhas_geradas
    senhas_geradas = []
    messagebox.showinfo("Deletar Senhas", "Todas as senhas foram deletadas com sucesso!")

def gerar_multiplas_senhas():
    try:
        quantidade = int(quantidade_var.get())
        tamanho = int(tamanho_multiplas_var.get())
    except ValueError:
        messagebox.showerror("Erro", "A quantidade e o tamanho devem ser números inteiros.")
        return

    nivel = nivel_var.get()
    for _ in range(quantidade):
        senha = gerar_senhas_por_niveis(nivel)
        try:
            if len(senha) < tamanho:
                senha = gerar_senha_sem_repeticao(letras + numeros + caracteres_especiais, tamanho)
            elif len(senha) > tamanho:
                senha = senha[:tamanho]
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
            return

        forca = avaliar_forca(senha)
        senhas_geradas.append(senha)

    messagebox.showinfo("Sucesso", f"{quantidade} senhas geradas com sucesso!")

def gerar_por_nivel():
    nivel = nivel_var.get()
    if nivel not in ("B", "M", "A", "D"):
        messagebox.showerror("Erro", "Selecione um nível válido.")
        return

    senha = gerar_senhas_por_niveis(nivel)
    forca = avaliar_forca(senha)
    senhas_geradas.append(senha)
    exibir_senha(senha, forca)

def gerar_customizavel():
    try:
        tamanho = int(tamanho_var.get())
    except ValueError:
        messagebox.showerror("Erro", "Tamanho deve ser um número inteiro.")
        return

    incluir_num = incluir_num_var.get()
    incluir_especiais = incluir_especiais_var.get()
    sem_repeticao = sem_repeticao_var.get()

    palavras_input = palavras_var.get().strip()
    palavras = palavras_input.split() if palavras_input else []

    senha = gerar_senhas_customizavel(tamanho, incluir_num, incluir_especiais, palavras, sem_repeticao)
    if senha:
        forca = avaliar_forca(senha)
        senhas_geradas.append(senha)
        exibir_senha(senha, forca)

def listar_senhas():
    if not senhas_geradas:
        messagebox.showinfo("Senhas Geradas", "Nenhuma senha gerada ainda.")
    else:
        senhas = "\n".join(f"{i + 1}: {senha}" for i, senha in enumerate(senhas_geradas))
        messagebox.showinfo("Senhas Geradas", senhas)

def exibir_senha(senha, forca):
    top = tk.Toplevel(janela)
    top.title("Senha Gerada")
    top.geometry("300x150")
    top.configure(bg=COR_FUNDO)

    tk.Label(top, text=f"Senha: {senha}", font=FONTE_PRINCIPAL, bg=COR_FUNDO).pack(pady=10)
    tk.Label(top, text=f"Força: {forca}", font=FONTE_PRINCIPAL, bg=COR_FUNDO).pack(pady=5)
    tk.Button(top, text="Copiar", command=lambda: copiar_para_clipboard(senha), bg=COR_BOTAO, fg=COR_TEXTO_BOTAO, font=FONTE_PRINCIPAL).pack()
    tk.Button(top, text="Fechar", command=top.destroy, bg=COR_BOTAO, fg=COR_TEXTO_BOTAO, font=FONTE_PRINCIPAL).pack(pady=5)

def sair():
    janela.destroy()

# Interface gráfica
janela = ThemedTk(theme="arc")  # Usando um tema moderno
janela.title("Gerador de Senhas")
janela.geometry("500x750")
janela.configure(bg=COR_FUNDO)

# Menu superior
menu_superior = tk.Menu(janela)
janela.config(menu=menu_superior)

menu_arquivo = tk.Menu(menu_superior, tearoff=0)
menu_superior.add_cascade(label="Arquivo", menu=menu_arquivo)
menu_arquivo.add_command(label="Sair", command=sair)

menu_ajuda = tk.Menu(menu_superior, tearoff=0)
menu_superior.add_cascade(label="Ajuda", menu=menu_ajuda)
menu_ajuda.add_command(label="Sobre", command=lambda: messagebox.showinfo("Sobre", "Gerador de Senhas Seguras\nVersão 1.0"))

# Frame de geração por nível
frame_nivel = ttk.LabelFrame(janela, text="Gerar Senha por Nível", padding=10)
frame_nivel.pack(pady=10, fill="x", padx=10)

nivel_var = tk.StringVar(value="B")
ttk.Radiobutton(frame_nivel, text="Básico (6 letras)", variable=nivel_var, value="B").pack(anchor="w")
ttk.Radiobutton(frame_nivel, text="Médio (8 letras e números)", variable=nivel_var, value="M").pack(anchor="w")
ttk.Radiobutton(frame_nivel, text="Avançado (12 caracteres, incluindo especiais)", variable=nivel_var, value="A").pack(anchor="w")
ttk.Radiobutton(frame_nivel, text="Muito Avançado (20 caracteres, incluindo tudo)", variable=nivel_var, value="D").pack(anchor="w")

ttk.Button(frame_nivel, text="Gerar Senha", command=gerar_por_nivel).pack(pady=5)

# Frame de geração customizável
frame_customizavel = ttk.LabelFrame(janela, text="Gerar Senha Customizável", padding=10)
frame_customizavel.pack(pady=10, fill="x", padx=10)

ttk.Label(frame_customizavel, text="Tamanho:").pack(anchor="w")
tamanho_var = ttk.Entry(frame_customizavel)
tamanho_var.pack(fill="x")

incluir_num_var = tk.BooleanVar()
ttk.Checkbutton(frame_customizavel, text="Incluir Números", variable=incluir_num_var).pack(anchor="w")

incluir_especiais_var = tk.BooleanVar()
ttk.Checkbutton(frame_customizavel, text="Incluir Caracteres Especiais", variable=incluir_especiais_var).pack(anchor="w")

sem_repeticao_var = tk.BooleanVar()
ttk.Checkbutton(frame_customizavel, text="Sem Repetição de Caracteres", variable=sem_repeticao_var).pack(anchor="w")

ttk.Label(frame_customizavel, text="Palavras (opcional):").pack(anchor="w")
palavras_var = ttk.Entry(frame_customizavel)
palavras_var.pack(fill="x")

ttk.Button(frame_customizavel, text="Gerar Senha", command=gerar_customizavel).pack(pady=5)

# Frame de múltiplas senhas
frame_multiplas = ttk.LabelFrame(janela, text="Gerar Múltiplas Senhas", padding=10)
frame_multiplas.pack(pady=10, fill="x", padx=10)

ttk.Label(frame_multiplas, text="Quantidade de senhas:").pack(anchor="w")
quantidade_var = ttk.Entry(frame_multiplas)
quantidade_var.pack(fill="x")

ttk.Label(frame_multiplas, text="Tamanho da senha:").pack(anchor="w")
tamanho_multiplas_var = ttk.Entry(frame_multiplas)
tamanho_multiplas_var.pack(fill="x")

ttk.Button(frame_multiplas, text="Gerar Múltiplas Senhas", command=gerar_multiplas_senhas).pack(pady=5)

# Botões de ação
frame_acoes = ttk.Frame(janela)
frame_acoes.pack(pady=10, fill="x", padx=10)

ttk.Button(frame_acoes, text="Listar Senhas", command=listar_senhas).pack(side="left", padx=5)
ttk.Button(frame_acoes, text="Salvar Senhas", command=salvar_senhas).pack(side="left", padx=5)
ttk.Button(frame_acoes, text="Salvar na Área de Trabalho", command=salvar_senhas_area_trabalho).pack(side="left", padx=5)
ttk.Button(frame_acoes, text="Deletar Senhas", command=deletar_senhas).pack(side="left", padx=5)

# Botão de sair
ttk.Button(janela, text="Sair", command=sair).pack(pady=10)

# Iniciar o Tkinter loop
janela.mainloop()