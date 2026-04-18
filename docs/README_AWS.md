# ☁️ Upar Objetos (AWS)

Ferramenta com interface gráfica para upload de arquivos pesados (backups de banco de dados, pacotes ZIP, etc.) para o **Amazon S3**.

## 🚀 Funcionalidades

- **Interface Gráfica**: Seleção de arquivos via explorador do Windows
- **Upload com Progresso**: Exibe porcentaje de upload em tempo real
- **Suporte a Arquivos Grandes**: Funciona com arquivos de qualquer tamanho
- **Seguro**: Armazena chaves localmente em arquivo `.env` (ignorado pelo Git)

## 🛠️ Requisitos

- Python 3.10+
- Dependências: `boto3`

## ⚙️ Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/seu-repo/upar-objetos.git
   cd upar-objetos
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute o aplicativo:
   ```bash
   python main.py
   ```

## 🔐 Configuração

No primeiro uso, configure suas credenciais AWS na aba **Configurações**:
- AWS Access Key ID
- AWS Secret Access Key
- Região (ex: us-east-1)

---
*Cloud Infra*