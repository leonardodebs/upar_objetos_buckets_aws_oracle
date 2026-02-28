# 🆙 UparS3 — AWS File Uploader

Aplicativo profissional com interface gráfica (GUI) moderna para **upload de arquivos** para buckets **S3 da AWS**. Desenvolvido para ser leve, rápido e fácil de distribuir.

---

## 🚀 Novidades da Versão Estável
- **Interface em Abas:** Separação clara entre configurações e ferramentas de upload.
- **Validação em Tempo Real:** Botão para testar suas chaves AWS antes de iniciar o envio.
- **Motor Assíncrono:** Upload processado em segundo plano para que a interface nunca congele.
- **Barra de Progresso Visual:** Feedback instantâneo do percentual de envio na janela.
- **Distribuição Fácil:** Gerado um executável único (`.exe`) que roda em qualquer Windows sem precisar de Python.

---

## 📦 Funcionalidades Detalhadas

1.  **Aba Configurações:**
    - Gerenciamento de chaves AWS (Access Key, Secret Key, Região e Bucket).
    - Persistência automática em arquivo `.env` local.
    - Indicador visual de conexão (Validação ok/falha).
2.  **Aba Upload:**
    - Seleção intuitiva de arquivos locais.
    - Sugestão inteligente de destino no S3 (Prefixos).
    - Barra de progresso resiliente com refresh forçado de UI.
    - Notificações de sucesso/erro via pop-ups nativos.

---

## 🛠️ Como usar o Executável (Para Usuários)

Se você recebeu apenas o arquivo **`UparS3_Stable.exe`**:
1. Abra o arquivo.
2. Na aba **Configurações**, insira as credenciais da AWS e o nome do bucket.
3. Clique em **Validar Conexão**.
4. Uma vez validado, a aba **Upload** será liberada para uso.

---

## 💻 Desenvolvimento (Para Programadores)

### Pré-requisitos
- Python 3.10+
- Bibliotecas: `boto3`, `python-dotenv`, `ttkthemes`

### Instalação e Execução
```bash
pip install -r requirements.txt
python main.py
```

### Gerar novo Executável
```bash
python -m PyInstaller --noconfirm --name UparS3_Stable --onefile --windowed main.py
```

---

## 🔧 Estrutura do Projeto
```
upar_aws/
├── main.py              # Ponto de entrada
├── gui.py               # Lógica da interface (Tkinter + ThemedTk)
├── s3_uploader.py       # Motor de upload (Boto3 + Callbacks)
├── dist/                # Pasta contendo o executável gerado
├── requirements.txt     # Dependências do projeto
└── .env                 # Arquivo local de credenciais (gerado pelo app)
```

---

Feito com 💻 por Leonardo Pereira Debs.
