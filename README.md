🔐 Gerador de Senhas com Interface Gráfica
Aplicativo Python com GUI em Tkinter para geração de senhas seguras. Suporta níveis predefinidos, personalização completa, múltiplas senhas e criptografia com cryptography. Ideal para quem quer segurança sem complicação.

🚀 Funcionalidades
Geração por Nível:

Básico (6 letras)

Médio (8 letras + números)

Avançado (12 com especiais)

Muito Avançado (20 caracteres)

![Captura de tela 2025-05-27 094818](https://github.com/user-attachments/assets/eaf5bd90-f039-40ec-90bc-3b5524ca6b4d)

Geração Customizável:

Define o tamanho

Adiciona números/caracteres especiais

Sem repetição de caracteres

Adição de palavras específicas

Outros Recursos:

Avaliação de força da senha

Geração em lote

Salvamento em .txt (criptografado ou simples)

Cópia automática para clipboard

Interface moderna com tema ttkthemes

🛠️ Tecnologias Usadas
Tkinter + ttkthemes – GUI

random – Geração aleatória

cryptography.fernet – Criptografia simétrica

os, filedialog, messagebox – utilidades do sistema

💻 Como Executar
Instale as dependências:

pip install cryptography ttkthemes
Rode o script:

python gerador_senhas.py
📁 Estrutura de Saída
Arquivo .txt com senhas criptografadas (contém a chave de descriptografia).

Arquivo simples salvo na Área de Trabalho (sem criptografia).

⚠️ Observações
A chave de criptografia não é armazenada – se perder, já era.

A criptografia é opcional e só ocorre ao salvar com o botão "Salvar Senhas".

🧠 Autor
Script criado para fins educacionais e de produtividade pessoal. Faça bom uso e não reutilize senhas fracas.
