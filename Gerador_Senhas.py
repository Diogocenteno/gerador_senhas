# %% Gerador de Senhas e Criptografador de Arquivos (Versão Aprimorada)

import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from cryptography.fernet import Fernet, InvalidToken
import os
import sys  # Adicionado para lidar com os caminhos do PyInstaller
from ttkthemes import ThemedTk

# --- Função para encontrar recursos (ícone) ---
def resource_path(relative_path):
    """ Obtém o caminho absoluto para o recurso, funciona para dev e para PyInstaller """
    try:
        # PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- Configuração de Tema Persistente ---
CONFIG_FILE = os.path.join(os.path.expanduser('~'), '.gerador_senhas_tema.cfg')
DEFAULT_THEME = "arc"

def save_theme_config(theme_name):
    """Salva o nome do tema escolhido no arquivo de configuração."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            f.write(theme_name)
    except IOError:
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
    Uma aplicação de desktop aprimorada para gerar, gerenciar e salvar senhas e arquivos seguros.
    Melhorias:
    - Interface mais limpa e organizada com `grid`.
    - Feedback visual instantâneo para a senha gerada (com força e cor).
    - Botão para copiar a última senha gerada.
    - Indicador de força de senha com cores na lista.
    - Limpeza automática da área de transferência por segurança.
    - Layout responsivo e mais agradável.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Gerador e Criptografador Seguro v2.0")

        # --- Definir Ícone da Janela e Barra de Tarefas ---
        try:
            # O nome do arquivo ('CADEADO.png') deve ser o mesmo que você usa no comando PyInstaller --add-data
            # Exemplo: --add-data="caminho/para/CADEADO.png;."
            icon_path = resource_path("CADEADO.png")
            icon_image = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(True, icon_image)
        except Exception as e:
            print(f"Aviso: Não foi possível carregar o ícone da janela '{icon_path}'. Erro: {e}")
            # A aplicação continuará funcionando sem o ícone.

        self.root.geometry("700x750")
        self.root.resizable(True, True)
        self.root.minsize(650, 700)

        # --- Estilo e Cores ---
        self.style = ttk.Style()
        self.forca_cores = {
            "Muito Fraca": "#d9534f",
            "Fraca": "#f0ad4e",
            "Média": "#5bc0de",
            "Forte": "#5cb85c",
            "Muito Forte": "#2e6da4"
        }
        self.configure_styles()

        # --- Dados ---
        self.senhas_geradas = []
        self.letras = list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')
        self.numeros = list('0123456789')
        self.caracteres_especiais = list('!@#$%^&*()_+-=[]{}|;:\'",.<>?/`~\\')
        
        # Variáveis de controle
        self.caminho_arquivo_senhas = tk.StringVar()
        self.caminho_arquivo_chave = tk.StringVar()
        self._caminho_completo_senhas = ""
        self._caminho_completo_chave = ""

        self.caminho_arquivo_a_criptografar = tk.StringVar()
        self.caminho_arquivo_a_descriptografar = tk.StringVar()
        self.caminho_chave_para_descriptografar = tk.StringVar()

        self.create_widgets()

    def configure_styles(self):
        """Configura os estilos dos widgets ttk."""
        theme_bg = self.style.lookup('TFrame', 'background')
        self.root.configure(bg=theme_bg)
        self.style.configure("TButton", padding=6, relief="flat", font=("Segoe UI", 10))
        self.style.configure("TLabel", background=theme_bg, font=("Segoe UI", 10))
        self.style.configure("TCheckbutton", background=theme_bg, font=("Segoe UI", 10))
        self.style.configure("TRadiobutton", background=theme_bg, font=("Segoe UI", 10))
        self.style.configure("TLabelframe.Label", background=theme_bg, font=("Segoe UI", 11, "bold"))
        self.style.configure("Result.TLabel", font=("Courier New", 14, "bold"), padding=5)
        self.style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))

    def create_menu(self):
        """Cria a barra de menu superior."""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        arquivo_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Arquivo", menu=arquivo_menu)
        arquivo_menu.add_command(label="Descriptografar Senhas...", command=lambda: self.notebook.select(self.tab_descriptografar_senhas))
        arquivo_menu.add_command(label="Criptografar/Descriptografar Arquivos...", command=lambda: self.notebook.select(self.tab_arquivos))
        arquivo_menu.add_separator()
        arquivo_menu.add_command(label="Sair", command=self.root.destroy)

        tema_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Temas", menu=tema_menu)
        temas_disponiveis = sorted(self.root.get_themes())
        for tema in temas_disponiveis:
            tema_menu.add_command(label=tema, command=lambda t=tema: self.change_theme(t))

    def change_theme(self, theme_name):
        """Muda o tema da aplicação."""
        try:
            self.root.set_theme(theme_name)
            self.configure_styles() # Re-aplica os estilos para o novo tema
            save_theme_config(theme_name)
        except tk.TclError:
            messagebox.showerror("Erro de Tema", f"Não foi possível carregar o tema '{theme_name}'.")

    def create_widgets(self):
        """Cria e organiza os widgets na janela principal."""
        self.create_menu()
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        main_frame.rowconfigure(2, weight=1) # A linha da lista de senhas irá expandir
        main_frame.columnconfigure(0, weight=1)

        # --- Frame Superior: Notebook com as abas de geração ---
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.tab_simples = ttk.Frame(self.notebook, padding="15")
        self.tab_custom = ttk.Frame(self.notebook, padding="15")
        self.tab_multiplas = ttk.Frame(self.notebook, padding="15")
        self.tab_descriptografar_senhas = ttk.Frame(self.notebook, padding="15")
        self.tab_arquivos = ttk.Frame(self.notebook, padding="15")

        self.notebook.add(self.tab_simples, text="⚡ Gerar Senha Rápida")
        self.notebook.add(self.tab_custom, text="⚙️ Senha Customizável")
        self.notebook.add(self.tab_multiplas, text="📋 Múltiplas Senhas")
        self.notebook.add(self.tab_descriptografar_senhas, text="🔑 Descriptografar Senhas")
        self.notebook.add(self.tab_arquivos, text="📁 Criptografar Arquivos")

        self.create_tab_nivel()
        self.create_tab_customizavel()
        self.create_tab_multiplas()
        self.create_tab_descriptografar_senhas()
        self.create_tab_arquivos()

        # --- Frame de Resultado Imediato ---
        result_frame = ttk.LabelFrame(main_frame, text="Última Senha Gerada", padding="10")
        result_frame.grid(row=1, column=0, sticky="ew", pady=10)
        result_frame.columnconfigure(0, weight=1)

        self.last_password_var = tk.StringVar(value="Sua senha aparecerá aqui...")
        self.last_password_label = ttk.Label(result_frame, textvariable=self.last_password_var, style="Result.TLabel", anchor="center")
        self.last_password_label.grid(row=0, column=0, sticky="ew")

        self.strength_var = tk.StringVar()
        self.strength_label = ttk.Label(result_frame, textvariable=self.strength_var, font=("Segoe UI", 10, "bold"), anchor="center")
        self.strength_label.grid(row=1, column=0)

        copy_button = ttk.Button(result_frame, text="Copiar Última Senha", command=self.copiar_ultima_senha, style="Accent.TButton")
        copy_button.grid(row=0, column=1, rowspan=2, padx=(10, 0), sticky="ns")

        # --- Frame Inferior: Lista de senhas geradas ---
        list_frame = ttk.LabelFrame(main_frame, text="Histórico da Sessão", padding="10")
        list_frame.grid(row=2, column=0, sticky="nsew", pady=5)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        
        listbox_scrollbar = ttk.Scrollbar(list_frame)
        listbox_scrollbar.grid(row=0, column=1, sticky="ns")
        self.password_listbox = tk.Listbox(list_frame, yscrollcommand=listbox_scrollbar.set, font=("Courier New", 12), selectbackground="#0078d4", selectforeground="white")
        self.password_listbox.grid(row=0, column=0, sticky="nsew")
        listbox_scrollbar.config(command=self.password_listbox.yview)

        # --- Frame de Ações da Lista ---
        actions_frame = ttk.Frame(main_frame)
        actions_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        actions_frame.columnconfigure((0, 1, 2, 3), weight=1)
        ttk.Button(actions_frame, text="Copiar Selecionada", command=self.copiar_senha_selecionada).grid(row=0, column=0, sticky="ew", padx=2)
        ttk.Button(actions_frame, text="Salvar Criptografado...", command=self.salvar_senhas_criptografadas).grid(row=0, column=1, sticky="ew", padx=2)
        ttk.Button(actions_frame, text="Salvar como Texto...", command=self.salvar_senhas_nao_criptografadas).grid(row=0, column=2, sticky="ew", padx=2)
        ttk.Button(actions_frame, text="Limpar Histórico", command=self.deletar_senhas).grid(row=0, column=3, sticky="ew", padx=2)

    # --- Métodos de criação de Abas (Refatorados com Grid) ---
    def create_tab_nivel(self):
        self.nivel_var = tk.StringVar(value="M")
        niveis = { "Básico": "B", "Médio": "M", "Avançado": "A", "Especialista": "D" }
        descricoes = { "B": "(Apenas 8 letras)", "M": "(10 letras e números)", "A": "(14 caracteres com especiais)", "D": "(20 caracteres, máxima complexidade)" }
        ttk.Label(self.tab_simples, text="Escolha um nível de complexidade:", style="Header.TLabel").pack(anchor="w", pady=(0, 10))
        for texto, valor in niveis.items():
            ttk.Radiobutton(self.tab_simples, text=f"{texto: <12} {descricoes[valor]}", variable=self.nivel_var, value=valor).pack(anchor="w", pady=3, padx=10)
        ttk.Button(self.tab_simples, text="Gerar Senha Rápida", command=self.gerar_por_nivel, style="Accent.TButton").pack(pady=20, ipadx=10)

    def create_tab_customizavel(self):
        self.tab_custom.columnconfigure(1, weight=1)
        
        ttk.Label(self.tab_custom, text="Tamanho:").grid(row=0, column=0, sticky="w", pady=5)
        self.tamanho_var = ttk.Entry(self.tab_custom, width=10)
        self.tamanho_var.grid(row=0, column=1, sticky="w", pady=5)
        self.tamanho_var.insert(0, "16")

        # Checkbox para 'apenas letras'
        self.apenas_letras_var = tk.BooleanVar(value=False)
        apenas_letras_cb = ttk.Checkbutton(self.tab_custom, text="Gerar senha apenas com letras", variable=self.apenas_letras_var, command=self.toggle_character_options)
        apenas_letras_cb.grid(row=1, column=0, columnspan=2, sticky="w", pady=3)

        self.incluir_num_var = tk.BooleanVar(value=True)
        self.numeros_cb = ttk.Checkbutton(self.tab_custom, text="Incluir Números (0-9)", variable=self.incluir_num_var)
        self.numeros_cb.grid(row=2, column=0, columnspan=2, sticky="w", pady=3)
        
        self.incluir_especiais_var = tk.BooleanVar(value=True)
        self.especiais_cb = ttk.Checkbutton(self.tab_custom, text="Incluir Caracteres Especiais (!@#$%)", variable=self.incluir_especiais_var)
        self.especiais_cb.grid(row=3, column=0, columnspan=2, sticky="w", pady=3)
        
        self.sem_repeticao_var = tk.BooleanVar()
        ttk.Checkbutton(self.tab_custom, text="Sem Repetição de Caracteres", variable=self.sem_repeticao_var).grid(row=4, column=0, columnspan=2, sticky="w", pady=3)

        ttk.Label(self.tab_custom, text="Palavras-chave (opcional):").grid(row=5, column=0, columnspan=2, sticky="w", pady=(10, 2))
        self.palavras_var = ttk.Entry(self.tab_custom)
        self.palavras_var.grid(row=6, column=0, columnspan=2, sticky="ew", pady=2)

        ttk.Button(self.tab_custom, text="Gerar Senha Customizada", command=self.gerar_customizavel, style="Accent.TButton").grid(row=7, column=0, columnspan=2, pady=20, ipadx=10)

    def create_tab_multiplas(self):
        self.tab_multiplas.columnconfigure(1, weight=1)

        ttk.Label(self.tab_multiplas, text="Quantidade:").grid(row=0, column=0, sticky="w", pady=5)
        self.quantidade_var = ttk.Entry(self.tab_multiplas, width=10)
        self.quantidade_var.grid(row=0, column=1, sticky="w")
        self.quantidade_var.insert(0, "5")

        ttk.Label(self.tab_multiplas, text="Tamanho:").grid(row=1, column=0, sticky="w", pady=5)
        self.tamanho_multiplas_var = ttk.Entry(self.tab_multiplas, width=10)
        self.tamanho_multiplas_var.grid(row=1, column=1, sticky="w")
        self.tamanho_multiplas_var.insert(0, "16")

        ttk.Label(self.tab_multiplas, text="Complexidade:").grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 5))
        self.nivel_multiplas_var = tk.StringVar(value="A")
        niveis_frame = ttk.Frame(self.tab_multiplas)
        niveis_frame.grid(row=3, column=0, columnspan=2, sticky="w")
        ttk.Radiobutton(niveis_frame, text="Básico", variable=self.nivel_multiplas_var, value="B").pack(side="left", padx=5)
        ttk.Radiobutton(niveis_frame, text="Médio", variable=self.nivel_multiplas_var, value="M").pack(side="left", padx=5)
        ttk.Radiobutton(niveis_frame, text="Avançado", variable=self.nivel_multiplas_var, value="A").pack(side="left", padx=5)
        
        ttk.Button(self.tab_multiplas, text="Gerar Múltiplas Senhas", command=self.gerar_multiplas_senhas, style="Accent.TButton").grid(row=4, column=0, columnspan=2, pady=25, ipadx=10)

    def create_tab_descriptografar_senhas(self):
        self.tab_descriptografar_senhas.columnconfigure(1, weight=1)
        self.tab_descriptografar_senhas.rowconfigure(2, weight=1)

        ttk.Button(self.tab_descriptografar_senhas, text="Selecionar Arquivo de Senhas (.txt)", command=self.selecionar_arquivo_senhas).grid(row=0, column=0, sticky='ew', padx=(0,5), pady=5)
        ttk.Label(self.tab_descriptografar_senhas, textvariable=self.caminho_arquivo_senhas, relief="sunken", anchor="w").grid(row=0, column=1, sticky='ew', pady=5)
        
        ttk.Button(self.tab_descriptografar_senhas, text="Selecionar Arquivo de Chave (.key)", command=self.selecionar_arquivo_chave).grid(row=1, column=0, sticky='ew', padx=(0,5), pady=5)
        ttk.Label(self.tab_descriptografar_senhas, textvariable=self.caminho_arquivo_chave, relief="sunken", anchor="w").grid(row=1, column=1, sticky='ew', pady=5)
        
        ttk.Button(self.tab_descriptografar_senhas, text="Descriptografar Senhas", command=self.executar_descriptografia_senhas, style="Accent.TButton").grid(row=4, column=0, columnspan=2, pady=10)
        
        list_frame = ttk.LabelFrame(self.tab_descriptografar_senhas, text="Senhas Descriptografadas", padding="10")
        list_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=10)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.decrypted_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Courier New", 12))
        self.decrypted_listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar.config(command=self.decrypted_listbox.yview)
        
        ttk.Button(self.tab_descriptografar_senhas, text="Copiar Senha Selecionada", command=self.copiar_senha_descriptografada).grid(row=3, column=0, columnspan=2, pady=(5,0))
    
    def create_tab_arquivos(self):
        notebook_arquivos = ttk.Notebook(self.tab_arquivos)
        notebook_arquivos.pack(pady=10, expand=True, fill="both")
        
        tab_cript = ttk.Frame(notebook_arquivos, padding="15")
        tab_descript = ttk.Frame(notebook_arquivos, padding="15")
        notebook_arquivos.add(tab_cript, text="Criptografar Arquivo")
        notebook_arquivos.add(tab_descript, text="Descriptografar Arquivo")

        # Aba de Criptografia
        tab_cript.columnconfigure(1, weight=1)
        ttk.Label(tab_cript, text="Selecione um arquivo para criptografar:").grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))
        ttk.Button(tab_cript, text="Selecionar Arquivo...", command=self.selecionar_arquivo_para_criptografar).grid(row=1, column=0, sticky='ew', padx=(0, 5))
        ttk.Label(tab_cript, textvariable=self.caminho_arquivo_a_criptografar, relief="sunken", anchor="w").grid(row=1, column=1, sticky='ew')
        ttk.Button(tab_cript, text="Criptografar Arquivo Selecionado", command=self.executar_criptografia_arquivo, style="Accent.TButton").grid(row=2, column=0, columnspan=2, pady=20)

        # Aba de Descriptografia
        tab_descript.columnconfigure(1, weight=1)
        ttk.Label(tab_descript, text="Selecione os arquivos para descriptografar:").grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))
        ttk.Button(tab_descript, text="Arquivo Criptografado (.enc)...", command=self.selecionar_arquivo_para_descriptografar).grid(row=1, column=0, sticky='ew', pady=2, padx=(0, 5))
        ttk.Label(tab_descript, textvariable=self.caminho_arquivo_a_descriptografar, relief="sunken", anchor="w").grid(row=1, column=1, sticky='ew', pady=2)
        ttk.Button(tab_descript, text="Arquivo de Chave (.key)...", command=self.selecionar_chave_para_descriptografar).grid(row=2, column=0, sticky='ew', pady=2, padx=(0, 5))
        ttk.Label(tab_descript, textvariable=self.caminho_chave_para_descriptografar, relief="sunken", anchor="w").grid(row=2, column=1, sticky='ew', pady=2)
        ttk.Button(tab_descript, text="Descriptografar Arquivo", command=self.executar_descriptografia_arquivo, style="Accent.TButton").grid(row=3, column=0, columnspan=2, pady=20)


    # --- Lógica de Geração ---
    def toggle_character_options(self):
        """Ativa/desativa as opções de caracteres com base na seleção 'apenas letras'."""
        if self.apenas_letras_var.get():
            # Se 'apenas letras' estiver marcado, desmarca e desativa as outras opções
            self.incluir_num_var.set(False)
            self.incluir_especiais_var.set(False)
            self.numeros_cb.config(state="disabled")
            self.especiais_cb.config(state="disabled")
        else:
            # Se 'apenas letras' for desmarcado, reativa as outras opções e restaura o padrão
            self.numeros_cb.config(state="normal")
            self.especiais_cb.config(state="normal")
            self.incluir_num_var.set(True)
            self.incluir_especiais_var.set(True)

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
        config = { "B": {"tamanho": 8, "num": False, "esp": False}, "M": {"tamanho": 10, "num": True, "esp": False}, "A": {"tamanho": 14, "num": True, "esp": True}, "D": {"tamanho": 20, "num": True, "esp": True} }
        c = config[nivel]
        senha = self.gerar_senha(c["tamanho"], usar_numeros=c["num"], usar_especiais=c["esp"])
        if senha: self.adicionar_senha_lista(senha)

    def gerar_customizavel(self):
        try:
            tamanho = int(self.tamanho_var.get())
            if not (4 <= tamanho <= 100): raise ValueError
        except ValueError:
            messagebox.showerror("Erro de Validação", "O tamanho deve ser um número entre 4 e 100.")
            return

        palavras = self.palavras_var.get().strip().split()
        tamanho_palavras = sum(len(p) for p in palavras)
        if tamanho_palavras >= tamanho:
            messagebox.showerror("Erro", "O tamanho total das palavras-chave não pode ser maior ou igual ao tamanho da senha.")
            return

        tamanho_aleatorio = tamanho - tamanho_palavras
        senha_aleatoria = self.gerar_senha(tamanho_aleatorio, usar_numeros=self.incluir_num_var.get(), usar_especiais=self.incluir_especiais_var.get(), sem_repeticao=self.sem_repeticao_var.get())
        
        if senha_aleatoria:
            senha_final_lista = list(senha_aleatoria + ''.join(palavras))
            random.shuffle(senha_final_lista)
            senha_final = ''.join(senha_final_lista)
            self.adicionar_senha_lista(senha_final)
            
    def gerar_multiplas_senhas(self):
        try:
            quantidade = int(self.quantidade_var.get())
            tamanho = int(self.tamanho_multiplas_var.get())
            if not (1 <= quantidade <= 100 and 4 <= tamanho <= 100): raise ValueError
        except ValueError:
            messagebox.showerror("Erro de Validação", "A quantidade deve ser entre 1-100 e o tamanho entre 4-100.")
            return

        nivel = self.nivel_multiplas_var.get()
        config = { "B": {"num": False, "esp": False}, "M": {"num": True, "esp": False}, "A": {"num": True, "esp": True} }
        c = config[nivel]
        
        novas_senhas = [self.gerar_senha(tamanho, usar_numeros=c["num"], usar_especiais=c["esp"]) for _ in range(quantidade)]
        if novas_senhas:
            for s in novas_senhas: 
                if s: self.adicionar_senha_lista(s, update_ui=False)
            self.update_password_listbox()
            messagebox.showinfo("Sucesso", f"{len(novas_senhas)} senhas geradas com sucesso!")

    # --- Funções Auxiliares e de UI ---
    def avaliar_forca(self, senha):
        score = 0
        if len(senha) >= 8: score += 1
        if len(senha) >= 12: score += 1
        if any(c in self.numeros for c in senha): score += 1
        if any(c in self.caracteres_especiais for c in senha): score += 1
        if any(c.islower() for c in senha) and any(c.isupper() for c in senha): score += 1
        
        if score <= 1: return "Muito Fraca"
        if score == 2: return "Fraca"
        if score == 3: return "Média"
        if score == 4: return "Forte"
        return "Muito Forte"
    
    def adicionar_senha_lista(self, senha, update_ui=True):
        forca = self.avaliar_forca(senha)
        self.senhas_geradas.append({"senha": senha, "forca": forca})
        self.last_password_var.set(senha)
        self.strength_var.set(forca)
        self.strength_label.config(foreground=self.forca_cores.get(forca, "black"))
        if update_ui: self.update_password_listbox()
            
    def update_password_listbox(self):
        self.password_listbox.delete(0, tk.END)
        for i, item in enumerate(self.senhas_geradas):
            self.password_listbox.insert(tk.END, f"{item['senha']:<30} | Força: {item['forca']}")
            cor = self.forca_cores.get(item['forca'], "black")
            self.password_listbox.itemconfig(i, {'fg': cor})
        self.password_listbox.yview_moveto(1) # Rola para o final
            
    def copiar_para_clipboard(self, texto):
        self.root.clipboard_clear()
        self.root.clipboard_append(texto)
        messagebox.showinfo("Copiado", f"'{texto}'\nCopiado para a área de transferência!\n\n(Será limpo em 30 segundos por segurança)", parent=self.root)
        self.root.after(30000, self.root.clipboard_clear) # Limpa o clipboard após 30s

    def copiar_ultima_senha(self):
        senha = self.last_password_var.get()
        if senha and "Sua senha" not in senha:
            self.copiar_para_clipboard(senha)
        else:
            messagebox.showwarning("Aviso", "Nenhuma senha foi gerada ainda.")

    def copiar_senha_selecionada(self):
        try:
            selected_index = self.password_listbox.curselection()[0]
            senha_para_copiar = self.senhas_geradas[selected_index]['senha']
            self.copiar_para_clipboard(senha_para_copiar)
        except IndexError:
            messagebox.showwarning("Aviso", "Nenhuma senha selecionada na lista.")

    def deletar_senhas(self):
        if not self.senhas_geradas:
            messagebox.showinfo("Informação", "O histórico de senhas já está vazio.")
            return
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja apagar todas as senhas do histórico da sessão?"):
            self.senhas_geradas.clear()
            self.update_password_listbox()
            self.last_password_var.set("Sua senha aparecerá aqui...")
            self.strength_var.set("")
            messagebox.showinfo("Sucesso", "Histórico da sessão limpo.")

    # --- Funções de Salvamento e Descriptografia ---
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
        if not self._caminho_completo_senhas or not self._caminho_completo_chave:
            messagebox.showerror("Erro", "Por favor, selecione o arquivo de senhas e o arquivo de chave.")
            return
        try:
            with open(self._caminho_completo_chave, 'rb') as f_chave: chave = f_chave.read()
            cipher = Fernet(chave)
            with open(self._caminho_completo_senhas, 'r') as f_senhas: senhas_criptografadas = f_senhas.readlines()
            
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
            senha_para_copiar = self.decrypted_listbox.get(self.decrypted_listbox.curselection()[0])
            self.copiar_para_clipboard(senha_para_copiar)
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
                for i, item in enumerate(self.senhas_geradas): f.write(f"{i + 1}: {item['senha']} (Força: {item['forca']})\n")
            messagebox.showinfo("Sucesso", f"Senhas salvas (sem criptografia) em: {os.path.basename(caminho_arquivo)}")
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo: {e}")

    # --- Funções de Criptografia de Arquivos (mantidas, mas agora dentro de uma UI melhor) ---
    def selecionar_arquivo_para_criptografar(self):
        arquivo = filedialog.askopenfilename(title="Selecionar arquivo para criptografar")
        if arquivo: self.caminho_arquivo_a_criptografar.set(arquivo)
    
    def executar_criptografia_arquivo(self):
        caminho_original = self.caminho_arquivo_a_criptografar.get()
        if not caminho_original:
            messagebox.showerror("Erro", "Nenhum arquivo selecionado para criptografar.")
            return
        
        nome_base = os.path.basename(caminho_original)
        caminho_criptografado = filedialog.asksaveasfilename(title="Salvar arquivo criptografado como...", initialfile=f"{nome_base}.enc", defaultextension=".enc", filetypes=[("Arquivo Criptografado", "*.enc")])
        if not caminho_criptografado: return

        caminho_chave = filedialog.asksaveasfilename(title="Salvar arquivo da CHAVE como...", initialfile=f"{nome_base}.key", defaultextension=".key", filetypes=[("Arquivo de Chave", "*.key")])
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
        if arquivo: self.caminho_arquivo_a_descriptografar.set(arquivo)

    def selecionar_chave_para_descriptografar(self):
        arquivo = filedialog.askopenfilename(title="Selecionar arquivo de chave (.key)", filetypes=[("Arquivo de Chave", "*.key")])
        if arquivo: self.caminho_chave_para_descriptografar.set(arquivo)

    def executar_descriptografia_arquivo(self):
        caminho_criptografado = self.caminho_arquivo_a_descriptografar.get()
        caminho_chave = self.caminho_chave_para_descriptografar.get()
        if not caminho_criptografado or not caminho_chave:
            messagebox.showerror("Erro", "Selecione o arquivo criptografado e o arquivo de chave.")
            return

        nome_base = os.path.basename(caminho_criptografado)
        nome_sugerido = nome_base[:-4] if nome_base.endswith('.enc') else f"descriptografado_{nome_base}"
        
        caminho_descriptografado = filedialog.asksaveasfilename(title="Salvar arquivo descriptografado como...", initialfile=nome_sugerido, filetypes=[("Todos os arquivos", "*.*")])
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
    # Para executar este script, você precisa instalar as bibliotecas:
    # pip install cryptography ttkthemes
    root = ThemedTk()
    initial_theme = load_theme_config()
    if initial_theme in root.get_themes():
        root.set_theme(initial_theme)
    else:
        root.set_theme(DEFAULT_THEME)
        save_theme_config(DEFAULT_THEME)
    
    # Adiciona um estilo para botões de destaque
    style = ttk.Style()
    style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'))

    app = PasswordGeneratorApp(root)
    root.mainloop()


