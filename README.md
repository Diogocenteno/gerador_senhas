🔐 Gerador de Senhas com Interface Gráfica
Aplicativo Python com GUI em Tkinter para geração de senhas seguras. Suporta níveis predefinidos, personalização completa, múltiplas senhas e criptografia com cryptography. Ideal para quem quer segurança sem complicação.

<img width="781" height="863" alt="Captura de tela 2025-09-03 114933" src="https://github.com/user-attachments/assets/1dccd9d3-dcb8-4a28-aa2a-fb9cbc235de3" />


Este commit inicial introduz uma aplicação de desktop completa para a geração e gerenciamento seguro de senhas, além de funcionalidades para criptografia e descriptografia de arquivos.

A interface gráfica, desenvolvida com Tkinter e aprimorada com ttkthemes, oferece uma experiência de usuário intuitiva e personalizável.

Principais funcionalidades implementadas:

Geração de Senhas:

Geração baseada em níveis de complexidade pré-definidos (Básico a Especialista).

Opção de senha customizável, permitindo ao usuário definir tamanho, conjunto de caracteres (letras, números, especiais) e palavras-chave.

Capacidade de gerar múltiplas senhas em lote.

Avaliação da força de cada senha gerada.

Criptografia e Gerenciamento:

Salva listas de senhas de forma segura, utilizando criptografia simétrica (Fernet).

Permite salvar as senhas em texto simples (com aviso de segurança).

Ferramenta dedicada para descriptografar arquivos de senhas previamente salvos, exigindo o arquivo de chave correspondente.

Módulo para criptografar e descriptografar qualquer tipo de arquivo, gerando um arquivo de dados (.enc) e um de chave (.key).

Interface e Usabilidade:

Interface organizada em abas para separar as diferentes funcionalidades.

Suporte a múltiplos temas visuais, com a escolha do usuário sendo salva em um arquivo de configuração para persistência.

Lista dinâmica para exibir as senhas geradas na sessão atual.

Ações rápidas como "Copiar para a área de transferência", "Salvar" e "Limpar lista".

Janela redimensionável com barra de rolagem para garantir a usabilidade em diferentes tamanhos de tela.
