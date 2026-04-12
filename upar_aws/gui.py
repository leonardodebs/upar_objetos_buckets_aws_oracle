import os
import sys
import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import set_key, load_dotenv
from ttkthemes import ThemedTk

from s3_uploader import upload_arquivo_para_s3

# Localiza o diretório base e o arquivo .env (especial para PyInstaller)
if getattr(sys, "frozen", False):
    # Se rodando via executável, procura os arquivos extraídos na pasta temporária (_MEIPASS)
    BASE_DIR = Path(sys._MEIPASS)
    ENV_PATH = BASE_DIR / ".env"
    
    if not ENV_PATH.exists():
        ENV_PATH = Path(sys.executable).parent / ".env"
else:
    BASE_DIR = Path(__file__).parent
    ENV_PATH = BASE_DIR / ".env"


def _carregar_env():
    """Lê (ou relê) o .env e retorna um dict com as 4 chaves."""
    load_dotenv(ENV_PATH, override=True)
    return {
        "AWS_REGION":            os.getenv("AWS_REGION", ""),
        "BUCKET_NAME":           os.getenv("BUCKET_NAME", ""),
        "AWS_ACCESS_KEY_ID":     os.getenv("AWS_ACCESS_KEY_ID", ""),
        "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY", ""),
    }


class FileUploaderGUI:
    def __init__(self):
        self.window = ThemedTk(theme="arc")
        self.window.title("🆙 Uploader S3 — AWS")
        self.window.geometry("540x420")
        self.window.resizable(False, False)
        self.window.eval("tk::PlaceWindow %s center" % self.window.winfo_toplevel())

        self.selected_file = None
        self._credenciais_validadas = False

        self._build_ui()
        self._precarregar_credenciais()

    # ------------------------------------------------------------------ #
    #  Construção da Interface                                             #
    # ------------------------------------------------------------------ #
    def _build_ui(self):
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # ---------- Aba 1: Configurações ----------
        self.tab_config = ttk.Frame(self.notebook, padding=18)
        self.notebook.add(self.tab_config, text="  ⚙️  Configurações  ")
        self._build_tab_config()

        # ---------- Aba 2: Upload ----------
        self.tab_upload = ttk.Frame(self.notebook, padding=18)
        self.notebook.add(self.tab_upload, text="  🚀  Upload  ", state="disabled")
        self._build_tab_upload()

    # ---- Aba Configurações ----
    def _build_tab_config(self):
        f = self.tab_config

        ttk.Label(f, text="Credenciais AWS", font=("Arial", 13, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 14)
        )

        campos = [
            ("Região (AWS_REGION):",        "AWS_REGION",            False),
            ("Bucket S3 (BUCKET_NAME):",    "BUCKET_NAME",           False),
            ("Access Key ID:",              "AWS_ACCESS_KEY_ID",     False),
            ("Secret Access Key:",          "AWS_SECRET_ACCESS_KEY", True),
        ]

        self._entries = {}
        for i, (label, key, secret) in enumerate(campos, start=1):
            ttk.Label(f, text=label, font=("Arial", 9)).grid(
                row=i, column=0, sticky="w", pady=4
            )
            show = "*" if secret else ""
            entry = ttk.Entry(f, width=38, show=show, font=("Arial", 10))
            entry.grid(row=i, column=1, sticky="ew", padx=(10, 0), pady=4)
            self._entries[key] = entry

        f.columnconfigure(1, weight=1)

        # Status da validação
        self.lbl_val_status = ttk.Label(
            f, text="", font=("Arial", 9, "italic"), foreground="#777"
        )
        self.lbl_val_status.grid(row=6, column=0, columnspan=2, sticky="w", pady=(10, 0))

        # Botão Validar
        self.btn_validar = ttk.Button(
            f,
            text="🔍  Validar Conexão",
            command=self._iniciar_validacao,
            width=22,
        )
        self.btn_validar.grid(row=7, column=0, columnspan=2, pady=(12, 0))

    # ---- Aba Upload ----
    def _build_tab_upload(self):
        f = self.tab_upload

        ttk.Label(f, text="Upload para AWS S3", font=("Arial", 13, "bold")).pack(
            anchor="w", pady=(0, 14)
        )

        # Info do bucket ativo
        self.lbl_bucket_ativo = ttk.Label(
            f, text="", font=("Arial", 9, "italic"), foreground="#1a6fc4"
        )
        self.lbl_bucket_ativo.pack(anchor="w", pady=(0, 10))

        # Arquivo selecionado
        ttk.Label(f, text="Arquivo selecionado:", font=("Arial", 9)).pack(anchor="w")
        self.lbl_arquivo = ttk.Label(
            f,
            text="Nenhum arquivo escolhido",
            foreground="#888",
            font=("Arial", 9, "italic"),
            wraplength=470,
            justify="left",
        )
        self.lbl_arquivo.pack(anchor="w", pady=(2, 10))

        self.btn_selecionar = ttk.Button(
            f, text="📂  Escolher Arquivo", command=self.selecionar_arquivo, width=22
        )
        self.btn_selecionar.pack(pady=(0, 14))

        # Destino S3
        ttk.Label(f, text="Destino no S3 (chave/prefixo):", font=("Arial", 9)).pack(anchor="w")
        self.entry_s3_key = ttk.Entry(f, font=("Arial", 10), width=55)
        self.entry_s3_key.insert(0, "uploads/")
        self.entry_s3_key.pack(anchor="w", pady=(2, 14))

        # Botão Upload
        self.btn_upload = ttk.Button(
            f, text="🚀  Enviar para S3", command=self.enviar_para_s3, width=22
        )
        self.btn_upload.pack(pady=(0, 12))

        # Progressbar
        ttk.Label(f, text="Progresso:", font=("Arial", 9)).pack(anchor="w")
        self.progress_bar = ttk.Progressbar(
            f, orient="horizontal", length=470, mode="determinate", maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=(4, 6))

        self.lbl_status = ttk.Label(
            f, text="Pronto.", font=("Arial", 9, "italic"), foreground="#555"
        )
        self.lbl_status.pack(anchor="w")

        # --- Seção de Links (Inicia invisível/vazia) ---
        self.frame_links = ttk.LabelFrame(f, text=" 🔗 Links do Arquivo ", padding=10)
        
        # Link Público
        ttk.Label(self.frame_links, text="URL Pública:", font=("Arial", 8, "bold")).grid(row=0, column=0, sticky="w")
        self.ent_url_publica = ttk.Entry(self.frame_links, font=("Arial", 9), width=45)
        self.ent_url_publica.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        
        self.btn_copy_pub = ttk.Button(self.frame_links, text="📋", width=3, 
                                      command=lambda: self._copiar_texto(self.ent_url_publica.get()))
        self.btn_copy_pub.grid(row=1, column=1, padx=2)
        
        self.btn_open_pub = ttk.Button(self.frame_links, text="🌐", width=3,
                                      command=lambda: webbrowser.open(self.ent_url_publica.get()))
        self.btn_open_pub.grid(row=1, column=2, padx=2)

        # Link Console
        ttk.Label(self.frame_links, text="Console AWS:", font=("Arial", 8, "bold")).grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.ent_url_console = ttk.Entry(self.frame_links, font=("Arial", 9), width=45)
        self.ent_url_console.grid(row=3, column=0, sticky="ew", padx=(0, 5))
        
        self.btn_copy_con = ttk.Button(self.frame_links, text="📋", width=3,
                                      command=lambda: self._copiar_texto(self.ent_url_console.get()))
        self.btn_copy_con.grid(row=3, column=1, padx=2)
        
        self.btn_open_con = ttk.Button(self.frame_links, text="🛠️", width=3,
                                      command=lambda: webbrowser.open(self.ent_url_console.get()))
        self.btn_open_con.grid(row=3, column=2, padx=2)

        self.frame_links.columnconfigure(0, weight=1)
        # O frame só aparece após o primeiro upload de sucesso nesta sessão

    # ------------------------------------------------------------------ #
    #  Pré-carregar credenciais do .env                                   #
    # ------------------------------------------------------------------ #
    def _precarregar_credenciais(self):
        env = _carregar_env()
        for key, entry in self._entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, env.get(key, ""))

        # Se todas as credenciais já existem, marca como pronto para validar
        if all(env.values()):
            self.lbl_val_status.config(
                text="Credenciais carregadas do .env — clique em Validar para confirmar.",
                foreground="#888",
            )

    # ------------------------------------------------------------------ #
    #  Validação de Credenciais                                            #
    # ------------------------------------------------------------------ #
    def _iniciar_validacao(self):
        """Lê os campos, salva no .env e dispara validação em thread separada."""
        valores = {k: e.get().strip() for k, e in self._entries.items()}

        if not all(valores.values()):
            messagebox.showerror(
                "Campos incompletos",
                "Preencha todos os campos antes de validar.",
            )
            return

        # Salva no .env imediatamente
        ENV_PATH.touch(exist_ok=True)
        for k, v in valores.items():
            set_key(str(ENV_PATH), k, v)

        self.btn_validar.state(["disabled"])
        self.lbl_val_status.config(
            text="⏳ Validando conexão com a AWS…", foreground="#1a6fc4"
        )

        threading.Thread(
            target=self._validar_credenciais,
            args=(valores,),
            daemon=True,
        ).start()

    def _validar_credenciais(self, v):
        """Executa em thread separada: testa head_bucket."""
        try:
            s3 = boto3.client(
                "s3",
                region_name=v["AWS_REGION"],
                aws_access_key_id=v["AWS_ACCESS_KEY_ID"],
                aws_secret_access_key=v["AWS_SECRET_ACCESS_KEY"],
            )
            s3.head_bucket(Bucket=v["BUCKET_NAME"])
            self.window.after(0, self._validacao_ok, v["BUCKET_NAME"], v["AWS_REGION"])
        except NoCredentialsError:
            self.window.after(0, self._validacao_erro, "Credenciais inválidas ou ausentes.")
        except ClientError as e:
            codigo = e.response["Error"]["Code"]
            if codigo in ("403", "NoSuchBucket"):
                msg = "Bucket não encontrado ou sem permissão de acesso."
            else:
                msg = str(e)
            self.window.after(0, self._validacao_erro, msg)
        except Exception as e:
            self.window.after(0, self._validacao_erro, str(e))

    def _validacao_ok(self, bucket, region):
        self.btn_validar.state(["!disabled"])
        self.lbl_val_status.config(
            text=f"✅ Conexão validada! Bucket '{bucket}' ({region}) acessível.",
            foreground="#2a9d2a",
        )
        self._credenciais_validadas = True
        # Habilita a aba de Upload
        self.notebook.tab(self.tab_upload, state="normal")
        self.lbl_bucket_ativo.config(
            text=f"Bucket ativo: {bucket}  |  Região: {region}"
        )
        # Vai direto para a aba de upload
        self.notebook.select(self.tab_upload)

    def _validacao_erro(self, mensagem):
        self.btn_validar.state(["!disabled"])
        self.lbl_val_status.config(
            text=f"❌ {mensagem}", foreground="#cc0000"
        )
        self._credenciais_validadas = False
        self.notebook.tab(self.tab_upload, state="disabled")

    # ------------------------------------------------------------------ #
    #  Ações da Aba Upload                                                 #
    # ------------------------------------------------------------------ #
    def selecionar_arquivo(self):
        file_path = filedialog.askopenfilename(title="Selecione o arquivo")
        if file_path:
            self.selected_file = file_path
            self.lbl_arquivo.config(
                text=file_path, foreground="#222", font=("Arial", 9)
            )
            nome = os.path.basename(file_path)
            prefixo = self.entry_s3_key.get().rstrip("/") or "uploads"
            self.entry_s3_key.delete(0, tk.END)
            self.entry_s3_key.insert(0, f"{prefixo}/{nome}")

    def enviar_para_s3(self):
        if not self.selected_file:
            messagebox.showerror("Erro", "Nenhum arquivo foi selecionado.")
            return

        s3_key = self.entry_s3_key.get().strip()
        if not s3_key:
            messagebox.showerror("Erro", "O campo de destino S3 não pode estar vazio.")
            return

        env = _carregar_env()
        bucket = env["BUCKET_NAME"]

        self.btn_upload.state(["disabled"])
        self.btn_selecionar.state(["disabled"])
        self.progress_bar["value"] = 0
        self.lbl_status.config(text="Enviando…", foreground="#1a6fc4")

        threading.Thread(
            target=self._executar_upload,
            args=(s3_key, bucket),
            daemon=True,
        ).start()

    def _executar_upload(self, s3_key, bucket):
        try:
            env = _carregar_env()
            resultado = upload_arquivo_para_s3(
                self.selected_file,
                bucket,
                s3_key,
                aws_config=env,
                gui_callback=self._atualizar_progresso,
            )
            
            if isinstance(resultado, tuple):
                sucesso, erro_msg = resultado
            else:
                sucesso = resultado
                erro_msg = "Erro desconhecido ao processar upload."
            
            # Gera URLs se sucesso
            urls = None
            if sucesso:
                urls = self._gerar_urls(s3_key, bucket, env.get("AWS_REGION"))

            self.window.after(0, self._finalizar_upload, sucesso, urls, erro_msg)
        except Exception as e:
            # Em caso de crash na thread, avisa a finalização como erro
            self.window.after(0, self._finalizar_upload, False, None, f"Erro Fatal: {str(e)}")

    def _atualizar_progresso(self, percentual: float):
        self.window.after(0, self._set_progress, percentual)

    def _set_progress(self, percentual: float):
        try:
            self.progress_bar["value"] = percentual
            self.lbl_status.config(
                text=f"Enviando… {percentual:.1f}%", foreground="#1a6fc4"
            )
            self.window.update_idletasks() # Força refresh da GUI
        except:
            pass

    def _finalizar_upload(self, sucesso: bool, urls: dict = None, erro_msg: str = ""):
        self.btn_upload.state(["!disabled"])
        self.btn_selecionar.state(["!disabled"])
        self.entry_s3_key.state(["!disabled"])
        
        if sucesso:
            self.progress_bar["value"] = 100
            self.lbl_status.config(
                text="✅ Upload concluído com sucesso!", foreground="#2a9d2a"
            )
            
            if urls:
                self.ent_url_publica.delete(0, tk.END)
                self.ent_url_publica.insert(0, urls["publica"])
                self.ent_url_console.delete(0, tk.END)
                self.ent_url_console.insert(0, urls["console"])
                self.frame_links.pack(fill=tk.X, pady=(15, 0)) # Mostra o frame
            
            messagebox.showinfo("Sucesso", "Upload concluído com sucesso! ✅")
        else:
            self.progress_bar["value"] = 0
            self.lbl_status.config(text="❌ Falha no upload.", foreground="#cc0000")
            
            msg_exibicao = erro_msg if erro_msg else "Falha no upload. Verifique as credenciais e tente novamente."
            messagebox.showerror("Erro de Upload", msg_exibicao)

    def _gerar_urls(self, key, bucket, region):
        """Constrói as URLs de acesso ao objeto no S3."""
        # Sanitiza a key para URL (substitui espaços, etc)
        from urllib.parse import quote
        key_quoted = quote(key)
        
        url_publica = f"https://{bucket}.s3.{region}.amazonaws.com/{key_quoted}"
        url_console = f"https://s3.console.aws.amazon.com/s3/object/{bucket}?region={region}&prefix={key_quoted}"
        
        return {
            "publica": url_publica,
            "console": url_console
        }

    def _copiar_texto(self, texto):
        """Copia o texto para a área de transferência do Windows."""
        self.window.clipboard_clear()
        self.window.clipboard_append(texto)
        self.window.update() # Necessário em algumas versões do windows
        messagebox.showinfo("Copiado", "Link copiado para a área de transferência!")

    # ------------------------------------------------------------------ #
    def iniciar(self):
        self.window.mainloop()
