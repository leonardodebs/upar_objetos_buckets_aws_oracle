# Runbook — Upar Objetos

## Propósito

Procedimento operacional para hacer upload de arquivos pesados para AWS S3 ou Oracle Cloud Infrastructure usando a ferramenta Upar Objetos.

---

## AWS S3

### 1. Preparar Ambiente

```bash
cd upar_aws
pip install -r requirements.txt
```

### 2. Executar Aplicativo

```bash
python main.py
```

### 3. Configurar Credenciais

Na aba **Configurações**, preencha:

| Campo | Exemplo |
|-------|---------|
| Região | `us-east-1` |
| Bucket S3 | `meu-bucket-backups` |
| Access Key ID | `AKIAIOSFODNN7EXAMPLE` |
| Secret Access Key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |

Clique em **"Validar Conexão"**.

### 4. Realizar Upload

1. Acesse a aba **Upload**
2. Clique em **"Escolher Arquivo"**
3. Selecione o arquivo no explorador
4. Verifique/adjust o destino no S3 (prefixo/chave)
5. Clique em **"Enviar para S3"**
6. Aguarde a transferência completa

### 5. Verificar Resultado

- Barra verde 100% = sucesso
- Mensagem de erro = verifique credenciais e tente novamente

---

## Oracle Cloud (OCI)

### 1. Preparar Ambiente

```bash
cd upar_oci
pip install -r requirements.txt
```

### 2. Obter Credenciais OCI

1. Acesse o Console Oracle Cloud
2.Identity > Customer Secret Keys
3.Crie uma nova chave e copie:
- Access Key ID
- Secret Access Key
- Namespace (do seu Tenancy)

### 3. Executar Aplicativo

```bash
python main.py
```

### 4. Configurar Credenciais

Na aba **Configurações**, preencha:

| Campo | Exemplo |
|-------|---------|
| Región OCI | `sa-vinhedo-1` |
| Namespace | `idnsexample123` |
| Bucket | `backups-prod` |
| Access Key ID | `ocid1.secretkey ExampleKeyID` |
| Secret Access Key | `ChaveSecreta+Exemplo` |

Clique em **"Validar Conexão"**.

### 5. Realizar Upload

1. Acesse a aba **Upload**
2. Clique em **"Escolher Arquivo"**
3. Selecione o arquivo
4. Defina o destino (prefixo/objeto)
5. Clique em **"Enviar para OCI"**
6. Aguarde a conclusão

---

## Solução de Problemas

| Erro | Solução |
|------|---------|
| Credenciais inválidas | Verifique Access Key e Secret Key |
| Bucket não encontrado | Confirme o nome do bucket e permissões IAM |
| Timeout no upload | Verifique conexão de rede ou use rede mais estável |
| Erro de cabeçalho (OCI) | Já tratado pela lib requests (não use boto3 direto) |

---

## Recuperação

Em caso de falha no upload:
1.删ione o arquivo parcialmente enviado no bucket
2. Verifique o arquivo local (tamanho intacto)
3. Tente novamente

---

## Logs

O aplicativo exibe erros na interface. Para logs detallados, execute em terminal:

```bash
python -u main.py 2>&1 | tee upload.log
```