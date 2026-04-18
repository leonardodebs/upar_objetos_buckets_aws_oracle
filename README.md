# Upar Objetos — AWS & Oracle Cloud

![Arquitetura do Projeto](stack.png)

Ferramenta desktop com interface gráfica para upload de arquivos pesados (backups de banco de dados, pacotes ZIP, etc.) para **Amazon S3** ou **Oracle Cloud Infrastructure (OCI) Object Storage**.

## Funcionalidades

- Interface gráfica com Seleção de arquivos via explorador do Windows
- Progresso de upload em tempo real
- Suporte a arquivos de qualquer tamanho (testado com 10GB+)
- Armazenamento seguro de credenciais em arquivo .env
- Compatível com AWS S3 e OCI S3 Compatibility API

## Requisitos
- Python 3.10+
- Windows (GUI baseada em Tk)

## Instalação

```bash
pip install -r requirements.txt
```

## Uso — AWS S3

```bash
cd upar_aws
python main.py
```

Configure as credenciais na aba Configurações:
- AWS Region (ex: us-east-1)
- Bucket Name
- Access Key ID
- Secret Access Key

Clique em "Validar Conexão" e depois avance para a aba Upload.

## Uso — Oracle Cloud (OCI)

```bash
cd upar_oci
python main.py
```

Configure as credenciais na aba Configurações:
- OCI Region (ex: sa-vinhedo-1)
- Namespace
- Bucket Name
- Access Key ID
- Secret Access Key

Clique em "Validar Conexão" e depois avance para a aba Upload.

## Estrutura do Projeto

```
.
├── upar_aws/           # Aplicativo para AWS S3
│   ├── gui.py         # Interface gráfica
│   ├── s3_uploader.py # Lógica de upload S3
│   └── main.py        # Ponto de entrada
├── upar_oci/          # Aplicativo para OCI
│   ├── gui.py         # Interface gráfica
│   ├── oci_uploader.py # Lógica de upload OCI
│   └── main.py        # Ponto de entrada
├── requirements.txt   # Dependências comuns
└── README.md         # Este arquivo
```

## Build — Executável

```bash
# AWS
cd upar_aws
pyinstaller UparAWS.spec

# OCI
cd upar_oci
pyinstaller UparOCI.spec
```

Os executáveis ficarão em `upar_aws/dist/` e `upar_oci/dist/`.

---

## 📚 Documentação Adicional
Para detalhes técnicos e guias avançados, consulte a pasta [docs/](./docs):
- [Arquitetura Detalhada](./docs/arquitetura.md)