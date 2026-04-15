import os
import time
import csv
import re
import shutil
import pdfplumber
from pypdf import PdfReader, PdfWriter
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Tradutor de meses bonitinho
MAPA_MESES = {
    "JANEIRO": "01 - Janeiro", "FEVEREIRO": "02 - Fevereiro", "MARCO": "03 - Marco",
    "MARÇO": "03 - Marco", "ABRIL": "04 - Abril", "MAIO": "05 - Maio",
    "JUNHO": "06 - Junho", "JULHO": "07 - Julho", "AGOSTO": "08 - Agosto",
    "SETEMBRO": "09 - Setembro", "OUTUBRO": "10 - Outubro",
    "NOVEMBRO": "11 - Novembro", "DEZEMBRO": "12 - Dezembro"
}

# Configurações de pastas
RAIZ_REDE = "./REDE_IML" 
PASTA_SCANNER = "./pasta_scanner" 
PASTA_BACKUP = "./arquivos_processados"

def carregar_servidores():
    servidores = {}
    caminho_csv = "servidores.csv"
    if os.path.exists(caminho_csv):
        with open(caminho_csv, mode='r', encoding='utf-8') as arquivo:
            leitor = csv.reader(arquivo)
            next(leitor) 
            for linha in leitor:
                if len(linha) == 2:
                    matricula, nome = linha
                    servidores[matricula.strip()] = nome.strip()
    return servidores

def buscar_pasta_do_servidor(raiz_rede, matricula_base):
    if not os.path.exists(raiz_rede): return None
    for nome_pasta in os.listdir(raiz_rede):
        caminho_pasta = os.path.join(raiz_rede, nome_pasta)
        if os.path.isdir(caminho_pasta):
            # Limpeza trator para comparar com a pasta da rede
            pasta_limpa = nome_pasta.upper().replace(".", "").replace("-", "").replace("X", "")
            if matricula_base in pasta_limpa:
                return caminho_pasta
    return None

class VigiaDePasta(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.lower().endswith('.pdf'): return
        caminho_arquivo = event.src_path
        nome_original = os.path.basename(caminho_arquivo)
        print(f"\n🔎 Arquivo detectado no scanner: {nome_original}")
        time.sleep(2) 

        try:
            lista_servidores = carregar_servidores()
            
            with pdfplumber.open(caminho_arquivo) as pdf_leitor:
                leitor_fatiador = PdfReader(caminho_arquivo)
                
                for num_pagina, pagina in enumerate(pdf_leitor.pages):
                    texto = pagina.extract_text() or ""
                    texto_upper = texto.upper()
                    texto_limpo = texto_upper.replace(".", "").replace("-", "").replace("X", "")
                    
                    dono_encontrado = None
                    matricula_dono = None
                    
                    # 1. Busca por Matrícula ou Nome
                    for matricula, nome in lista_servidores.items():
                        m_base = matricula.upper().replace("X", "").replace(".", "").replace("-", "")
                        if m_base in texto_limpo or nome.upper() in texto_upper:
                            dono_encontrado = nome.strip().title()
                            matricula_dono = m_base
                            break 
                    
                    if dono_encontrado:
                        # 2. Identifica o Mês/Ano (Texto como JANEIRO/2026)
                        padrao_data = r"\b(JANEIRO|FEVEREIRO|MAR[CÇ]O|ABRIL|MAIO|JUNHO|JULHO|AGOSTO|SETEMBRO|OUTUBRO|NOVEMBRO|DEZEMBRO)[\s/DE]*([12]\d{3})\b"
                        busca_data = re.search(padrao_data, texto_upper)
                        
                        if busca_data:
                            mes_txt = busca_data.group(1).replace("Ç", "C")
                            ano_doc = busca_data.group(2)
                            nome_mes = MAPA_MESES[mes_txt]
                        else:
                            # Plano B: Data do sistema
                            agora = datetime.now()
                            mes_n = agora.strftime("%m")
                            meses_b = ["", "01 - Janeiro", "02 - Fevereiro", "03 - Marco", "04 - Abril", "05 - Maio", "06 - Junho", "07 - Julho", "08 - Agosto", "09 - Setembro", "10 - Outubro", "11 - Novembro", "12 - Dezembro"]
                            nome_mes = meses_b[int(mes_n)]
                            ano_doc = agora.strftime("%Y")

                        # 3. Organização de Pastas
                        pasta_serv = buscar_pasta_do_servidor(RAIZ_REDE, matricula_dono)
                        if not pasta_serv:
                            pasta_serv = os.path.join(RAIZ_REDE, f"{dono_encontrado} - Matricula {matricula_dono}")
                        
                        p_destino = os.path.join(pasta_serv, ano_doc)
                        os.makedirs(p_destino, exist_ok=True)
                        
                        # 4. SALVAMENTO (Novo Padrão: 01 - Janeiro 2026 - Pag 1.pdf)
                        nome_f = f"{nome_mes} {ano_doc} - Pag {num_pagina+1}.pdf"
                        c_final = os.path.join(p_destino, nome_f)
                        
                        escritor = PdfWriter()
                        escritor.add_page(leitor_fatiador.pages[num_pagina])
                        with open(c_final, "wb") as f: escritor.write(f)
                        
                        print(f"   ✅ [PÁG {num_pagina+1}] Salvo para: {dono_encontrado}")
                    else:
                        print(f"   ❌ [PÁG {num_pagina+1}] Erro: Servidor não identificado.")

            # Mover original para backup
            os.makedirs(PASTA_BACKUP, exist_ok=True)
            shutil.move(caminho_arquivo, os.path.join(PASTA_BACKUP, nome_original))
            print("🚀 Tudo pronto! Arquivo movido para a pasta de processados.")

        except Exception as e:
            print(f"💥 ERRO AO PROCESSAR: {e}")

if not os.path.exists(PASTA_SCANNER): os.makedirs(PASTA_SCANNER)
observer = Observer()
observer.schedule(VigiaDePasta(), PASTA_SCANNER, recursive=False)
observer.start()
print("👀 Monitor V7.4 Ativado (Clean Name). Aguardando documentos...")
try:
    while True: time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
