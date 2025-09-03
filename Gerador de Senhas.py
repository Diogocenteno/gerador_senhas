# %% Gerador de Senhas e Criptografador de Arquivos

import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from cryptography.fernet import Fernet, InvalidToken
import os
from ttkthemes import ThemedTk

# --- Configuração de Tema Persistente ---
CONFIG_FILE = os.path.join(os.path.expanduser('~'), '.gerador_senhas_tema.cfg')
DEFAULT_THEME = "arc"

def save_theme_config(theme_name):
    """Salva o nome do tema escolhido no arquivo de configuração."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            f.write(theme_name)
    except IOError:
        # Falha silenciosa se não for possível salvar. Não é um erro crítico.
        print(f"Aviso: Não foi possível salvar a configuração do tema em {CONFIG_FILE}")

def load_theme_config():
    """Carrega o nome do tema do arquivo de configuração."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                theme_name = f.read().strip()
                return theme_name if theme_name else DEFAULT_THEME
        except IOError:
            return DEFAULT_THEME
    return DEFAULT_THEME
# -----------------------------------------

class PasswordGeneratorApp:
    """
    Uma aplicação de desktop para gerar, gerenciar e salvar senhas e arquivos seguros.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Gerador e Criptografador Seguro")
        self.root.geometry("630x600")
        self.root.resizable(True, True) # Permite que a janela seja redimensionada
        self.root.minsize(630, 650)     # Define um tamanho mínimo para a janela

        # Estilo
        self.style = ttk.Style()
        theme_bg = self.style.lookup('TFrame', 'background')
        self.root.configure(bg=theme_bg)
        self.style.configure("TButton", padding=6, relief="flat", font=("Arial", 10))
        self.style.configure("TLabel", background=theme_bg, font=("Arial", 10))
        self.style.configure("TCheckbutton", background=theme_bg)
        self.style.configure("TRadiobutton", background=theme_bg)

        # Dados
        self.senhas_geradas = []
        self.letras = list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')
        self.numeros = list('0123456789')
        self.caracteres_especiais = list('!@#$%^&*()_+-=[]{}|;:\'",.<>?/`~\\')
        
        # Variáveis para a aba de descriptografia de senhas
        self.caminho_arquivo_senhas = tk.StringVar()
        self.caminho_arquivo_chave = tk.StringVar()
        self._caminho_completo_senhas = ""
        self._caminho_completo_chave = ""

        # Variáveis para a aba de criptografia de arquivos
        self.caminho_arquivo_a_criptografar = tk.StringVar()
        self.caminho_arquivo_a_descriptografar = tk.StringVar()
        self.caminho_chave_para_descriptografar = tk.StringVar()

        self.create_widgets()

    def create_menu(self):
        """Cria a barra de menu superior com opções de arquivo e temas."""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # Menu Arquivo
        arquivo_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Arquivo", menu=arquivo_menu)
        arquivo_menu.add_command(label="Descriptografar Senhas...", command=self.ir_para_aba_descriptografar_senhas)
        arquivo_menu.add_command(label="Criptografar Arquivos...", command=self.ir_para_aba_arquivos)
        arquivo_menu.add_separator()
        arquivo_menu.add_command(label="Sair", command=self.root.destroy)

        # Menu de Temas
        tema_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Temas", menu=tema_menu)
        temas_disponiveis = sorted(self.root.get_themes())
        if temas_disponiveis:
            for tema in temas_disponiveis:
                tema_menu.add_command(label=tema, command=lambda t=tema: self.change_theme(t))
        else:
            tema_menu.add_command(label="Nenhum tema encontrado", state="disabled")

    def change_theme(self, theme_name):
        """Muda o tema da aplicação e atualiza as cores dos widgets."""
        try:
            self.root.set_theme(theme_name)
            theme_bg = self.style.lookup('TFrame', 'background')
            self.root.configure(bg=theme_bg)
            self.style.configure("TLabel", background=theme_bg)
            self.style.configure("TCheckbutton", background=theme_bg)
            self.style.configure("TRadiobutton", background=theme_bg)
            save_theme_config(theme_name)
        except tk.TclError:
            messagebox.showerror("Erro de Tema", f"Não foi possível carregar o tema '{theme_name}'.")

    def create_widgets(self):
        """Cria e organiza os widgets na janela principal."""
        self.create_menu()

        # --- Container principal com barra de rolagem ---
        # 1. Cria um Canvas que ocupará a janela
        main_canvas = tk.Canvas(self.root, highlightthickness=0)
        
        # 2. Cria a barra de rolagem vertical
        v_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        
        # 3. Cria o frame que conterá todos os outros widgets (será rolável)
        scrollable_frame = ttk.Frame(main_canvas, padding="10")

        # 4. Configura o binding para atualizar a região de rolagem quando o tamanho do frame mudar
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(
                scrollregion=main_canvas.bbox("all")
            )
        )

        # 5. Coloca o frame rolável dentro do Canvas
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # 6. Informa ao Canvas qual é o comando da barra de rolagem
        main_canvas.configure(yscrollcommand=v_scrollbar.set)

        # 7. Empacota a barra de rolagem e o canvas na janela principal
        v_scrollbar.pack(side="right", fill="y")
        main_canvas.pack(side="left", fill="both", expand=True)
        
        # --- Fim da configuração da rolagem. Todo o conteúdo agora vai no 'scrollable_frame' ---

        self.notebook = ttk.Notebook(scrollable_frame)
        self.notebook.pack(pady=10, expand=True, fill="both")

        # Abas
        self.tab_simples = ttk.Frame(self.notebook, padding="10")
        self.tab_custom = ttk.Frame(self.notebook, padding="10")
        self.tab_multiplas = ttk.Frame(self.notebook, padding="10")
        self.tab_descriptografar_senhas = ttk.Frame(self.notebook, padding="10")
        self.tab_arquivos = ttk.Frame(self.notebook, padding="10")

        self.notebook.add(self.tab_simples, text="Gerar Senha")
        self.notebook.add(self.tab_custom, text="Senha Customizável")
        self.notebook.add(self.tab_multiplas, text="Múltiplas Senhas")
        self.notebook.add(self.tab_descriptografar_senhas, text="Descriptografar Senhas")
        self.notebook.add(self.tab_arquivos, text="Criptografar Arquivos")

        self.create_tab_nivel()
        self.create_tab_customizavel()
        self.create_tab_multiplas()
        self.create_tab_descriptografar_senhas()
        self.create_tab_arquivos()

        list_frame = ttk.LabelFrame(scrollable_frame, text="Senhas Geradas (Sessão Atual)", padding="10")
        list_frame.pack(fill="both", expand=True, pady=5)
        
        # Renomeada a variável para evitar conflito com a scrollbar principal
        listbox_scrollbar = ttk.Scrollbar(list_frame)
        listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.password_listbox = tk.Listbox(list_frame, yscrollcommand=listbox_scrollbar.set, font=("Courier New", 12))
        self.password_listbox.pack(fill="both", expand=True)
        listbox_scrollbar.config(command=self.password_listbox.yview)

        actions_frame = ttk.Frame(scrollable_frame)
        actions_frame.pack(fill=tk.X, pady=10)
        actions_frame.columnconfigure((0, 1, 2, 3), weight=1)
        ttk.Button(actions_frame, text="Copiar Selecionada", command=self.copiar_senha_selecionada).grid(row=0, column=0, sticky="ew", padx=2)
        ttk.Button(actions_frame, text="Salvar Criptografado", command=self.salvar_senhas_criptografadas).grid(row=0, column=1, sticky="ew", padx=2)
        ttk.Button(actions_frame, text="Salvar (Texto Simples)", command=self.salvar_senhas_nao_criptografadas).grid(row=0, column=2, sticky="ew", padx=2)
        ttk.Button(actions_frame, text="Limpar Tudo", command=self.deletar_senhas).grid(row=0, column=3, sticky="ew", padx=2)

    # --- Métodos de criação de Abas ---
    def create_tab_nivel(self):
        self.nivel_var = tk.StringVar(value="M")
        niveis = { "Básico": "B", "Médio": "M", "Avançado": "A", "Especialista": "D" }
        descricoes = { "B": "(6 letras)", "M": "(8 letras e números)", "A": "(12 caracteres, incluindo especiais)", "D": "(20 caracteres, incluindo tudo)" }
        for texto, valor in niveis.items():
            ttk.Radiobutton(self.tab_simples, text=f"{texto} {descricoes[valor]}", variable=self.nivel_var, value=valor).pack(anchor="w", pady=2)
        ttk.Button(self.tab_simples, text="Gerar Senha", command=self.gerar_por_nivel).pack(pady=10)

    def create_tab_customizavel(self):
        ttk.Label(self.tab_custom, text="Tamanho:").pack(anchor="w")
        self.tamanho_var = ttk.Entry(self.tab_custom)
        self.tamanho_var.pack(fill="x", pady=2)
        self.tamanho_var.insert(0, "12")
        self.incluir_num_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.tab_custom, text="Incluir Números", variable=self.incluir_num_var).pack(anchor="w")
        self.incluir_especiais_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.tab_custom, text="Incluir Caracteres Especiais", variable=self.incluir_especiais_var).pack(anchor="w")
        self.sem_repeticao_var = tk.BooleanVar()
        ttk.Checkbutton(self.tab_custom, text="Sem Repetição de Caracteres", variable=self.sem_repeticao_var).pack(anchor="w")
        ttk.Label(self.tab_custom, text="Palavras-chave (opcional, separadas por espaço):").pack(anchor="w")
        self.palavras_var = ttk.Entry(self.tab_custom)
        self.palavras_var.pack(fill="x", pady=2)
        ttk.Button(self.tab_custom, text="Gerar Senha Customizada", command=self.gerar_customizavel).pack(pady=20)

    def create_tab_multiplas(self):
        ttk.Label(self.tab_multiplas, text="Quantidade de senhas:").pack(anchor="w")
        self.quantidade_var = ttk.Entry(self.tab_multiplas)
        self.quantidade_var.pack(fill="x", pady=2)
        self.quantidade_var.insert(0, "5")
        ttk.Label(self.tab_multiplas, text="Tamanho de cada senha:").pack(anchor="w", pady=(10,0))
        self.tamanho_multiplas_var = ttk.Entry(self.tab_multiplas)
        self.tamanho_multiplas_var.pack(fill="x", pady=2)
        self.tamanho_multiplas_var.insert(0, "12")
        ttk.Label(self.tab_multiplas, text="Usar Nível de Complexidade:").pack(anchor="w", pady=(10,0))
        self.nivel_multiplas_var = tk.StringVar(value="A")
        ttk.Radiobutton(self.tab_multiplas, text="Básico", variable=self.nivel_multiplas_var, value="B").pack(anchor="w")
        ttk.Radiobutton(self.tab_multiplas, text="Médio", variable=self.nivel_multiplas_var, value="M").pack(anchor="w")
        ttk.Radiobutton(self.tab_multiplas, text="Avançado", variable=self.nivel_multiplas_var, value="A").pack(anchor="w")
        ttk.Radiobutton(self.tab_multiplas, text="Especialista", variable=self.nivel_multiplas_var, value="D").pack(anchor="w")
        ttk.Button(self.tab_multiplas, text="Gerar Múltiplas Senhas", command=self.gerar_multiplas_senhas).pack(pady=20)

    def create_tab_descriptografar_senhas(self):
        frame_selecao = ttk.Frame(self.tab_descriptografar_senhas)
        frame_selecao.pack(fill='x', pady=5)
        ttk.Button(frame_selecao, text="Selecionar Arquivo de Senhas (.txt)", command=self.selecionar_arquivo_senhas).grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        ttk.Label(frame_selecao, textvariable=self.caminho_arquivo_senhas, relief="sunken", anchor="w").grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        ttk.Button(frame_selecao, text="Selecionar Arquivo de Chave (.key)", command=self.selecionar_arquivo_chave).grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        ttk.Label(frame_selecao, textvariable=self.caminho_arquivo_chave, relief="sunken", anchor="w").grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        frame_selecao.columnconfigure(1, weight=1)
        ttk.Button(self.tab_descriptografar_senhas, text="Descriptografar Senhas", command=self.executar_descriptografia_senhas).pack(pady=10)
        list_frame = ttk.LabelFrame(self.tab_descriptografar_senhas, text="Senhas Descriptografadas", padding="10")
        list_frame.pack(fill="both", expand=True, pady=5)
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.decrypted_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Courier New", 12))
        self.decrypted_listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.decrypted_listbox.yview)
        actions_frame_dec = ttk.Frame(self.tab_descriptografar_senhas)
        actions_frame_dec.pack(fill='x', pady=(5, 0))
        ttk.Button(actions_frame_dec, text="Copiar Senha Selecionada", command=self.copiar_senha_descriptografada).pack(expand=True)
    
    def create_tab_arquivos(self):
        """Cria a UI para a aba de criptografia de arquivos."""
        notebook_arquivos = ttk.Notebook(self.tab_arquivos)
        notebook_arquivos.pack(pady=10, expand=True, fill="both")
        
        tab_cript = ttk.Frame(notebook_arquivos, padding="10")
        tab_descript = ttk.Frame(notebook_arquivos, padding="10")
        notebook_arquivos.add(tab_cript, text="Criptografar Arquivo")
        notebook_arquivos.add(tab_descript, text="Descriptografar Arquivo")

        # --- Aba de Criptografia de Arquivo ---
        tab_cript.columnconfigure(1, weight=1) # Faz a coluna do Label expandir
        ttk.Label(tab_cript, text="Selecione um arquivo para criptografar:").grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        ttk.Button(tab_cript, text="Selecionar Arquivo...", command=self.selecionar_arquivo_para_criptografar).grid(row=1, column=0, sticky='ew', padx=(0, 5))
        ttk.Label(tab_cript, textvariable=self.caminho_arquivo_a_criptografar, relief="sunken", anchor="w").grid(row=1, column=1, sticky='ew')
        
        ttk.Button(tab_cript, text="Criptografar Arquivo Selecionado", command=self.executar_criptografia_arquivo).grid(row=2, column=0, columnspan=2, pady=20)


        # --- Aba de Descriptografia de Arquivo ---
        tab_descript.columnconfigure(1, weight=1) # Faz a coluna do Label expandir
        ttk.Label(tab_descript, text="Selecione os arquivos para descriptografar:").grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        ttk.Button(tab_descript, text="Arquivo Criptografado (.enc)...", command=self.selecionar_arquivo_para_descriptografar).grid(row=1, column=0, sticky='ew', pady=2, padx=(0, 5))
        ttk.Label(tab_descript, textvariable=self.caminho_arquivo_a_descriptografar, relief="sunken", anchor="w").grid(row=1, column=1, sticky='ew', pady=2)
        
        ttk.Button(tab_descript, text="Arquivo de Chave (.key)...", command=self.selecionar_chave_para_descriptografar).grid(row=2, column=0, sticky='ew', pady=2, padx=(0, 5))
        ttk.Label(tab_descript, textvariable=self.caminho_chave_para_descriptografar, relief="sunken", anchor="w").grid(row=2, column=1, sticky='ew', pady=2)
        
        ttk.Button(tab_descript, text="Descriptografar Arquivo", command=self.executar_descriptografia_arquivo).grid(row=3, column=0, columnspan=2, pady=20)


    # --- Lógica de Geração ---
    def gerar_senha(self, tamanho, usar_letras=True, usar_numeros=True, usar_especiais=True, sem_repeticao=False):
        caracteres = []
        if usar_letras: caracteres.extend(self.letras)
        if usar_numeros: caracteres.extend(self.numeros)
        if usar_especiais: caracteres.extend(self.caracteres_especiais)
        if not caracteres:
            messagebox.showerror("Erro", "Nenhum conjunto de caracteres selecionado.")
            return None
        if sem_repeticao:
            if tamanho > len(caracteres):
                messagebox.showerror("Erro de Geração", f"Não é possível gerar uma senha de tamanho {tamanho} sem repetição com os caracteres selecionados (máx: {len(caracteres)}).")
                return None
            return ''.join(random.sample(caracteres, tamanho))
        else:
            return ''.join(random.choice(caracteres) for _ in range(tamanho))

    def gerar_por_nivel(self):
        nivel = self.nivel_var.get()
        config = { "B": {"tamanho": 6, "num": False, "esp": False}, "M": {"tamanho": 8, "num": True, "esp": False}, "A": {"tamanho": 12, "num": True, "esp": True}, "D": {"tamanho": 20, "num": True, "esp": True} }
        c = config[nivel]
        senha = self.gerar_senha(c["tamanho"], usar_numeros=c["num"], usar_especiais=c["esp"])
        if senha: self.adicionar_senha_lista(senha)

    def gerar_customizavel(self):
        try:
            tamanho = int(self.tamanho_var.get())
            if tamanho <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "O tamanho deve ser um número inteiro positivo.")
            return
        palavras = self.palavras_var.get().strip().split()
        tamanho_palavras = sum(len(p) for p in palavras)
        if tamanho_palavras >= tamanho:
            messagebox.showerror("Erro", "O tamanho total das palavras-chave não pode ser maior ou igual ao tamanho da senha.")
            return
        tamanho_aleatorio = tamanho - tamanho_palavras
        senha_aleatoria = self.gerar_senha(tamanho_aleatorio, usar_numeros=self.incluir_num_var.get(), usar_especiais=self.incluir_especiais_var.get(), sem_repeticao=self.sem_repeticao_var.get())
        if senha_aleatoria:
            senha_com_palavras = senha_aleatoria + ''.join(palavras)
            senha_final_lista = list(senha_com_palavras)
            random.shuffle(senha_final_lista)
            senha_final = ''.join(senha_final_lista)
            self.adicionar_senha_lista(senha_final)
            
    def gerar_multiplas_senhas(self):
        try:
            quantidade = int(self.quantidade_var.get())
            tamanho = int(self.tamanho_multiplas_var.get())
            if quantidade <= 0 or tamanho <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "A quantidade e o tamanho devem ser números inteiros positivos.")
            return
        nivel = self.nivel_multiplas_var.get()
        config = { "B": {"num": False, "esp": False}, "M": {"num": True, "esp": False}, "A": {"num": True, "esp": True}, "D": {"num": True, "esp": True} }
        c = config[nivel]
        novas_senhas = []
        for _ in range(quantidade):
            senha = self.gerar_senha(tamanho, usar_numeros=c["num"], usar_especiais=c["esp"])
            if senha: novas_senhas.append(senha)
        if novas_senhas:
            for s in novas_senhas: self.adicionar_senha_lista(s, update_ui=False)
            self.update_password_listbox()
            messagebox.showinfo("Sucesso", f"{len(novas_senhas)} senhas geradas com sucesso!")

    # --- Funções Auxiliares e de UI ---
    def ir_para_aba_descriptografar_senhas(self):
        self.notebook.select(self.tab_descriptografar_senhas)
    
    def ir_para_aba_arquivos(self):
        self.notebook.select(self.tab_arquivos)

    def avaliar_forca(self, senha):
        score = 0
        if len(senha) >= 8: score += 1
        if len(senha) >= 12: score += 1
        if any(c in self.numeros for c in senha): score += 1
        if any(c in self.caracteres_especiais for c in senha): score += 1
        if any(c.islower() for c in senha) and any(c.isupper() for c in senha): score += 1
        if score <= 2: return "Fraca"
        if score <= 3: return "Média"
        if score <= 4: return "Forte"
        return "Muito Forte"
    
    def adicionar_senha_lista(self, senha, update_ui=True):
        forca = self.avaliar_forca(senha)
        self.senhas_geradas.append({"senha": senha, "forca": forca})
        if update_ui: self.update_password_listbox()
            
    def update_password_listbox(self):
        self.password_listbox.delete(0, tk.END)
        for item in self.senhas_geradas:
            self.password_listbox.insert(tk.END, f"{item['senha']:<30} | Força: {item['forca']}")
            
    def copiar_para_clipboard(self, texto, window):
        window.clipboard_clear()
        window.clipboard_append(texto)
        messagebox.showinfo("Copiado", "Copiado para a área de transferência!", parent=window)

    def copiar_senha_selecionada(self):
        try:
            selected_index = self.password_listbox.curselection()[0]
            senha_para_copiar = self.senhas_geradas[selected_index]['senha']
            self.copiar_para_clipboard(senha_para_copiar, self.root)
        except IndexError:
            messagebox.showwarning("Aviso", "Nenhuma senha selecionada na lista.")

    def deletar_senhas(self):
        if not self.senhas_geradas:
            messagebox.showinfo("Informação", "A lista de senhas já está vazia.")
            return
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja apagar todas as senhas da lista?"):
            self.senhas_geradas.clear()
            self.update_password_listbox()
            messagebox.showinfo("Sucesso", "Todas as senhas foram removidas da lista.")

    # --- Funções de Salvamento e Descriptografia de Senhas ---
    def salvar_senhas_criptografadas(self):
        if not self.senhas_geradas:
            messagebox.showwarning("Aviso", "Nenhuma senha para salvar.")
            return
        arquivo_senhas = filedialog.asksaveasfilename(title="Salvar arquivo de senhas", defaultextension=".txt", filetypes=[("Arquivos de Texto Criptografados", "*.txt")])
        if not arquivo_senhas: return
        arquivo_chave = filedialog.asksaveasfilename(title="Salvar arquivo da CHAVE DE CRIPTOGRAFIA", defaultextension=".key", filetypes=[("Arquivo de Chave", "*.key")])
        if not arquivo_chave: return
        if os.path.abspath(arquivo_senhas) == os.path.abspath(arquivo_chave):
            messagebox.showerror("Erro de Segurança", "O arquivo de senhas e o arquivo da chave não podem ser o mesmo. Operação cancelada.")
            return
        try:
            chave = Fernet.generate_key()
            cipher = Fernet(chave)
            with open(arquivo_senhas, "w") as f:
                for item in self.senhas_geradas:
                    senha_criptografada = cipher.encrypt(item['senha'].encode()).decode()
                    f.write(f"{senha_criptografada}\n")
            with open(arquivo_chave, "wb") as f: f.write(chave)
            messagebox.showinfo("Sucesso!", f"Senhas salvas em: {os.path.basename(arquivo_senhas)}\nChave salva em: {os.path.basename(arquivo_chave)}\n\nATENÇÃO: Guarde o arquivo da chave em um local SEGURO e SEPARADO.")
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Ocorreu um erro: {e}")

    def selecionar_arquivo_senhas(self):
        arquivo = filedialog.askopenfilename(title="Abrir arquivo de senhas", filetypes=[("Arquivos de Texto", "*.txt")])
        if arquivo:
            self.caminho_arquivo_senhas.set(os.path.basename(arquivo))
            self._caminho_completo_senhas = arquivo

    def selecionar_arquivo_chave(self):
        arquivo = filedialog.askopenfilename(title="Abrir arquivo de CHAVE", filetypes=[("Arquivo de Chave", "*.key")])
        if arquivo:
            self.caminho_arquivo_chave.set(os.path.basename(arquivo))
            self._caminho_completo_chave = arquivo
    
    def executar_descriptografia_senhas(self):
        arquivo_senhas = self._caminho_completo_senhas
        arquivo_chave = self._caminho_completo_chave
        if not arquivo_senhas or not arquivo_chave:
            messagebox.showerror("Erro", "Por favor, selecione o arquivo de senhas e o arquivo de chave primeiro.")
            return
        try:
            with open(arquivo_chave, 'rb') as f_chave: chave = f_chave.read()
            cipher = Fernet(chave)
            with open(arquivo_senhas, 'r') as f_senhas: senhas_criptografadas = f_senhas.readlines()
            self.decrypted_listbox.delete(0, tk.END)
            for s_cript in senhas_criptografadas:
                s_descript = cipher.decrypt(s_cript.strip().encode()).decode()
                self.decrypted_listbox.insert(tk.END, s_descript)
            if not senhas_criptografadas: messagebox.showinfo("Informação", "O arquivo de senhas está vazio.")
        except (InvalidToken, ValueError, TypeError):
            messagebox.showerror("Erro de Descriptografia", "Falha ao descriptografar. Verifique se a chave corresponde ao arquivo de senhas.")
            self.decrypted_listbox.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {e}")
            self.decrypted_listbox.delete(0, tk.END)

    def copiar_senha_descriptografada(self):
        try:
            selected_index = self.decrypted_listbox.curselection()[0]
            senha_para_copiar = self.decrypted_listbox.get(selected_index)
            self.copiar_para_clipboard(senha_para_copiar, self.root)
        except IndexError:
            messagebox.showwarning("Aviso", "Nenhuma senha selecionada na lista de descriptografados.")

    def salvar_senhas_nao_criptografadas(self):
        if not self.senhas_geradas:
            messagebox.showwarning("Aviso", "Nenhuma senha para salvar.")
            return
        caminho_arquivo = filedialog.asksaveasfilename(title="Salvar senhas como texto simples", defaultextension=".txt", filetypes=[("Arquivos de Texto", "*.txt")])
        if not caminho_arquivo: return
        try:
            with open(caminho_arquivo, "w") as f:
                f.write("--- Senhas Geradas (NÃO CRIPTOGRAFADAS) ---\n\nAVISO: Este arquivo não é seguro.\n\n")
                for i, item in enumerate(self.senhas_geradas): f.write(f"{i + 1}: {item['senha']}\n")
            messagebox.showinfo("Sucesso", f"Senhas salvas (sem criptografia) em: {os.path.basename(caminho_arquivo)}")
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo: {e}")

    # --- Funções de Criptografia de Arquivos ---
    def selecionar_arquivo_para_criptografar(self):
        arquivo = filedialog.askopenfilename(title="Selecionar arquivo para criptografar")
        if arquivo:
            self.caminho_arquivo_a_criptografar.set(arquivo)
    
    def executar_criptografia_arquivo(self):
        caminho_original = self.caminho_arquivo_a_criptografar.get()
        if not caminho_original:
            messagebox.showerror("Erro", "Nenhum arquivo selecionado para criptografar.")
            return
        
        nome_original_base = os.path.basename(caminho_original)
        nome_sugerido_cript = f"{nome_original_base}.enc"

        caminho_criptografado = filedialog.asksaveasfilename(
            title="Salvar arquivo criptografado como...",
            initialfile=nome_sugerido_cript,
            defaultextension=".enc",
            filetypes=[("Arquivo Criptografado", "*.enc")]
        )
        if not caminho_criptografado: return

        caminho_chave = filedialog.asksaveasfilename(
            title="Salvar arquivo da CHAVE como...",
            initialfile=f"{nome_original_base}.key",
            defaultextension=".key",
            filetypes=[("Arquivo de Chave", "*.key")]
        )
        if not caminho_chave: return

        try:
            with open(caminho_original, 'rb') as f: data = f.read()
            chave = Fernet.generate_key()
            cipher = Fernet(chave)
            data_criptografada = cipher.encrypt(data)
            with open(caminho_criptografado, 'wb') as f: f.write(data_criptografada)
            with open(caminho_chave, 'wb') as f: f.write(chave)
            messagebox.showinfo("Sucesso", "Arquivo criptografado com sucesso!\nLembre-se de guardar a chave em um local seguro.")
            self.caminho_arquivo_a_criptografar.set("")
        except Exception as e:
            messagebox.showerror("Erro na Criptografia", f"Ocorreu um erro: {e}")

    def selecionar_arquivo_para_descriptografar(self):
        arquivo = filedialog.askopenfilename(title="Selecionar arquivo criptografado (.enc)", filetypes=[("Arquivo Criptografado", "*.enc")])
        if arquivo:
            self.caminho_arquivo_a_descriptografar.set(arquivo)

    def selecionar_chave_para_descriptografar(self):
        arquivo = filedialog.askopenfilename(title="Selecionar arquivo de chave (.key)", filetypes=[("Arquivo de Chave", "*.key")])
        if arquivo:
            self.caminho_chave_para_descriptografar.set(arquivo)

    def executar_descriptografia_arquivo(self):
        caminho_criptografado = self.caminho_arquivo_a_descriptografar.get()
        caminho_chave = self.caminho_chave_para_descriptografar.get()
        if not caminho_criptografado or not caminho_chave:
            messagebox.showerror("Erro", "Selecione o arquivo criptografado e o arquivo de chave.")
            return

        # Sugere um nome de arquivo de saída baseado no nome do arquivo criptografado
        nome_base_criptografado = os.path.basename(caminho_criptografado)
        if nome_base_criptografado.endswith('.enc'):
            nome_sugerido = nome_base_criptografado[:-4]  # Remove a extensão .enc
        else:
            nome_sugerido = f"descriptografado_{nome_base_criptografado}"

        # Extrai a extensão original para usá-la como padrão
        _, ext_sugerida = os.path.splitext(nome_sugerido)
        if not ext_sugerida:
            filetypes = [("Todos os arquivos", "*.*")]
        else:
            filetypes = [(f"Arquivo ({ext_sugerida})", f"*{ext_sugerida}"), ("Todos os arquivos", "*.*")]

        caminho_descriptografado = filedialog.asksaveasfilename(
            title="Salvar arquivo descriptografado como...",
            initialfile=nome_sugerido,
            filetypes=filetypes,
            defaultextension=ext_sugerida
        )
        if not caminho_descriptografado: return
        
        try:
            with open(caminho_chave, 'rb') as f: chave = f.read()
            cipher = Fernet(chave)
            with open(caminho_criptografado, 'rb') as f: data_criptografada = f.read()
            data_descriptografada = cipher.decrypt(data_criptografada)
            with open(caminho_descriptografado, 'wb') as f: f.write(data_descriptografada)
            messagebox.showinfo("Sucesso", "Arquivo descriptografado com sucesso!")
            self.caminho_arquivo_a_descriptografar.set("")
            self.caminho_chave_para_descriptografar.set("")
        except (InvalidToken, ValueError, TypeError):
            messagebox.showerror("Erro de Descriptografia", "Falha ao descriptografar. Verifique se a chave corresponde ao arquivo.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    # Para executar este script, você precisa instalar as bibliotecas necessárias:
    # pip install cryptography ttkthemes
    root = ThemedTk()
    initial_theme = load_theme_config()
    if initial_theme in root.get_themes():
        root.set_theme(initial_theme)
    else:
        root.set_theme(DEFAULT_THEME)
        save_theme_config(DEFAULT_THEME)
    app = PasswordGeneratorApp(root)
    root.mainloop()

