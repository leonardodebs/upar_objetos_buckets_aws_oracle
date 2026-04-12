import os
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import set_key, load_dotenv
from ttkthemes import ThemedTk

from oci_uploader import upload_arquivo_para_oci

# Localiza o diretório base e o arquivo .env (especial para PyInstaller)
if getattr(sys, "frozen", False):
    # Se rodando via executável, procura os arquivos extraídos na pasta temporária (_MEIPASS)
    # ou na pasta do executável se estiver fora dela.
    BASE_DIR = Path(sys._MEIPASS)
    ENV_PATH = BASE_DIR / ".env"
    
    # Caso o .env não esteja dentro do pacote (backup para carregar da pasta do exe)
    if not ENV_PATH.exists():
        ENV_PATH = Path(sys.executable).parent / ".env"
else:
    # Se rodando via script normal
    BASE_DIR = Path(__file__).parent
    ENV_PATH = BASE_DIR / ".env"

def _carregar_env():
    """Lê (ou relê) o .env e retorna um dict com as chaves incluindo OCI."""
    load_dotenv(ENV_PATH, override=True)
    return {
        "OCI_NAMESPACE":         os.getenv("OCI_NAMESPACE", ""),
        "OCI_REGION":            os.getenv("OCI_REGION", ""),
        "OCI_BUCKET_NAME":       os.getenv("OCI_BUCKET_NAME", ""),
        "OCI_ACCESS_KEY_ID":     os.getenv("OCI_ACCESS_KEY_ID", ""),
        "OCI_SECRET_ACCESS_KEY": os.getenv("OCI_SECRET_ACCESS_KEY", ""),
    }


class FileUploaderGUI:
    def __init__(self):
        self.window = ThemedTk(theme="arc")
        self.window.title("☁️ Uploader OCI — Oracle Cloud")
        self.window.geometry("540x470")
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

        ttk.Label(f, text="Credenciais da Oracle Cloud", font=("Arial", 13, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 14)
        )

        campos = [
            ("Namespace (OCI):",            "OCI_NAMESPACE",         False),
            ("Região:",                     "OCI_REGION",            False),
            ("Nome do Bucket:",             "OCI_BUCKET_NAME",       False),
            ("Access Key (Customer):",      "OCI_ACCESS_KEY_ID",     False),
            ("Secret Key (Customer):",      "OCI_SECRET_ACCESS_KEY", True),
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
        self.lbl_val_status.grid(row=7, column=0, columnspan=2, sticky="w", pady=(10, 0))

        # Botão Validar
        self.btn_validar = ttk.Button(
            f,
            text="🔍  Validar Conexão OCI",
            command=self._iniciar_validacao,
            width=22,
        )
        self.btn_validar.grid(row=8, column=0, columnspan=2, pady=(12, 0))

    # ---- Aba Upload ----
    def _build_tab_upload(self):
        f = self.tab_upload

        ttk.Label(f, text="Upload para Oracle Object Storage", font=("Arial", 13, "bold")).pack(
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

        # Destino OCI
        ttk.Label(f, text="Destino na OCI (chave/prefixo):", font=("Arial", 9)).pack(anchor="w")
        self.entry_object_key = ttk.Entry(f, font=("Arial", 10), width=55)
        self.entry_object_key.insert(0, "")
        self.entry_object_key.pack(anchor="w", pady=(2, 14))

        # Botão Upload
        self.btn_upload = ttk.Button(
            f, text="🚀  Enviar para OCI", command=self.enviar_para_oci, width=22
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

        # Footer
        footer = tk.Frame(f, bg="#f8f9fa")
        footer.pack(fill="x", side="bottom", pady=(10, 0))
        tk.Label(
            footer, text="UparOCI v1.0 • Oracle Object Storage", 
            font=("Arial", 8), fg="#999", bg="#f8f9fa"
        ).pack()

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
            text="⏳ Validando conexão com a OCI…", foreground="#1a6fc4"
        )

        threading.Thread(
            target=self._validar_credenciais,
            args=(valores,),
            daemon=True,
        ).start()

    def _validar_credenciais(self, v):
        """Executa em thread separada: testa head_bucket."""
        try:
            endpoint = f"https://{v['OCI_NAMESPACE']}.compat.objectstorage.{v['OCI_REGION']}.oraclecloud.com"
            # Configuração de compatibilidade OCI
            s3_config = boto3.session.Config(
                s3={'addressing_style': 'path'},
                signature_version='s3v4'
            )
            s3 = boto3.client(
                "s3",
                region_name=v["OCI_REGION"],
                endpoint_url=endpoint,
                aws_access_key_id=v["OCI_ACCESS_KEY_ID"],
                aws_secret_access_key=v["OCI_SECRET_ACCESS_KEY"],
                config=s3_config
            )
            s3.head_bucket(Bucket=v["OCI_BUCKET_NAME"])
            self.window.after(0, self._validacao_ok, v["OCI_BUCKET_NAME"], v["OCI_REGION"])
        except NoCredentialsError:
            self.window.after(0, self._validacao_erro, "Credenciais inválidas ou ausentes.")
        except ClientError as e:
            codigo = e.response["Error"]["Code"]
            if codigo in ("403", "NoSuchBucket"):
                msg = "Bucket OCI não encontrado ou sem permissão de acesso (Access Denied)."
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
            prefixo = self.entry_object_key.get().rstrip("/")
            if prefixo:
                destino = f"{prefixo}/{nome}"
            else:
                destino = nome
            self.entry_object_key.delete(0, tk.END)
            self.entry_object_key.insert(0, destino)

    def enviar_para_oci(self):
        if not self.selected_file:
            messagebox.showerror("Erro", "Nenhum arquivo foi selecionado.")
            return

        object_key = self.entry_object_key.get().strip()
        if not object_key:
            messagebox.showerror("Erro", "O campo de destino OCI não pode estar vazio.")
            return

        env = _carregar_env()
        bucket = env["OCI_BUCKET_NAME"]

        self.btn_upload.state(["disabled"])
        self.btn_selecionar.state(["disabled"])
        self.progress_bar["value"] = 0
        self.lbl_status.config(text="Enviando…", foreground="#1a6fc4")

        threading.Thread(
            target=self._executar_upload,
            args=(object_key, bucket),
            daemon=True,
        ).start()

    def _executar_upload(self, object_key, bucket):
        try:
            env = _carregar_env()
            resultado = upload_arquivo_para_oci(
                self.selected_file,
                bucket,
                object_key,
                oci_config=env,
                gui_callback=self._atualizar_progresso,
            )
            
            if isinstance(resultado, tuple):
                sucesso, erro_msg = resultado
            else:
                sucesso = resultado
                erro_msg = "Erro desconhecido ao processar upload."
            
            # Notifica finalização
            self.window.after(0, self._finalizar_upload, sucesso, erro_msg)
        except Exception as e:
            # Em caso de crash na thread, avisa a finalização como erro
            self.window.after(0, self._finalizar_upload, False, f"Erro Fatal: {str(e)}")

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

    def _finalizar_upload(self, sucesso: bool, erro_msg: str = ""):
        self.btn_upload.state(["!disabled"])
        self.btn_selecionar.state(["!disabled"])
        self.entry_object_key.state(["!disabled"])
        
        if sucesso:
            self.progress_bar["value"] = 100
            self.lbl_status.config(
                text="✅ Upload concluído com sucesso!", foreground="#2a9d2a"
            )
            
            messagebox.showinfo("Sucesso", "Upload concluído com sucesso! ✅")
        else:
            self.progress_bar["value"] = 0
            self.lbl_status.config(text="❌ Falha no upload.", foreground="#cc0000")
            
            msg_exibicao = erro_msg if erro_msg else "Falha no upload. Verifique as credenciais e tente novamente."
            messagebox.showerror("Erro de Upload", msg_exibicao)


    # ------------------------------------------------------------------ #

    # ------------------------------------------------------------------ #
    def iniciar(self):
        self.window.mainloop()
