# ☁️ UparObjetos (AWS-OCI)

Ferramenta com interface gráfica para upload de arquivos pesados (como backups de banco de dados SQL e pacotes ZIP) para o **Oracle Cloud Infrastructure (OCI) Object Storage**.

Originalmente desenvolvido para AWS S3, este projeto foi migrado e otimizado para a OCI S3 Compatibility API, resolvendo erros comuns de cabeçalhos e tamanhos de arquivos.

## 🚀 Funcionalidades
- **Interface Gráfica Simples**: Seleção de arquivos via explorador do Windows.
- **Upload Híbrido**: Usa chaves de compatibilidade S3 da Oracle com método de link pré-assinado (garante estabilidade para arquivos de 10GB+).
- **Sem Prefixo Obrigatório**: Permite subir arquivos tanto em "pastas" virtuais quanto na raiz do bucket.
- **Seguro**: Armazena as chaves localmente em arquivo `.env` (ignorado pelo Git).

## 🛠️ Requisitos
- **Python 3.10+**
- Dependências: `boto3`, `requests`, `python-dotenv`, `ttkthemes`

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
No primeiro uso, vá na aba **Configurações** e preencha com suas **Customer Secret Keys** da Oracle Cloud.
> **Nota**: Não se esqueça de usar o **Namespace** correto do seu Tenancy e a **Região** (ex: sa-vinhedo-1).

---

