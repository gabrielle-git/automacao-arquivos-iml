# 📑 Fatiador de Documentos Inteligente (IML/PCDF)

### 🚀 O Problema
No Instituto de Medicina Legal, o processo de arquivamento de folhas de ponto era manual. A rotina exigia fatiar PDFs únicos com dezenas de páginas, separando servidor por servidor, e renomeando cada arquivo com um padrão rigoroso. Um trabalho braçal que consumia horas da equipe.

### 💡 A Solução
Desenvolvi um script de automação em **Python** que atua como um vigilante de pastas em tempo real. O fluxo funciona assim:
1. **Detecção Automática:** O `watchdog` identifica instantaneamente quando o scanner joga um novo arquivo na rede.
2. **Leitura e Extração:** O `pdfplumber` lê o conteúdo da página, localizando o nome ou matrícula do servidor cruzando com uma base de dados.
3. **Mineração de Datas:** Expressões Regulares (Regex) caçam o mês e o ano de competência diretamente no texto.
4. **Roteamento Inteligente:** O documento é fatiado (`pypdf`) e salvo direto na pasta do ano do servidor correto, seguindo a padronização (ex: `04 - Abril 2026 - Pag 1.pdf`).

### 🛠️ Tecnologias Utilizadas
- **Linguagem:** Python 3.12 (Ambiente Linux Debian)
- **Bibliotecas Principais:** `watchdog`, `pdfplumber`, `pypdf`
- **Lógica e Dados:** Expressões Regulares (Regex) e Dicionários CSV

### 📈 Impacto
Transformação de um processo operacional exaustivo em uma automação de 5 segundos. Redução a zero das falhas humanas de digitação e garantia de 100% de padronização na rede do instituto.
