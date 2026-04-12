# ADR — Architecture Decision Record

## ADR-001: Upload Híbrido AWS S3 e OCI

**Título:** Suporte a múltiplos provedores de object storage  
**Data:** 2026-04-12  
**Status:** Proposto  
**Responsável:** Equipe Infra

---

## Contexto

A organização utiliza tanto **Amazon S3** quanto **Oracle Cloud Infrastructure (OCI)** para armazenamento de objetos. existía a necessidade de uma ferramenta unificada ou de ferramentas separadas para fazer upload de arquivos pesados (backups, pacotes ZIP) para ambos os provedores.

---

## Decisão

Realizar a implementação de dois projetos separados:

1. **upar_aws/** — Uploader nativo para AWS S3 usando boto3
2. **upar_oci/** — Uploader para OCI usando S3 Compatibility API com requests (para evitar bugs de cabeçalho)

A decisão por projetos separados foi tomada para:
- Manter código limpo e específico por provider
- Evitar complexidade de configuração poliglota
- Facilitar manutenção e debugging independente

---

## Alternativas Consideradas

| Alternativa | Descrição | Rejeição |
|-------------|-----------|---------|
| API único com flag | Single application com parâmetro `--provider` | Maior complexidade de código |
| SDK poliglota | Usar SDK oficial da OCI + boto3 no mesmo código | Overhead de dependências |
| CLI apenas | Interface por linha de comando | Usuários não técnicos precisam de GUI |

---

## Implementação

### AWS S3 (`upar_aws/`)
- boto3 com upload_file nativo
- Interface Tk com progresso em tempo real
- Validação de credenciais via head_bucket

### OCI (`upar_oci/`)
- boto3 para gerar presigned URL (assinatura v4)
- requests para upload real (resolve problemas de Content-Length com arquivos 10GB+)
- Interface similar à versão AWS

---

## Consequências

### Positivas
- Facilidade de uso para operadores não técnicos
- Upload estável para arquivos grandes
- Credenciais armazenadas localmente em .env (não versionado)

### Negativas
- Duplicação de código de interface (GUI)
- Necessidade de manter duas bases de código

---

## Referências

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [OCI Object Storage S3 Compatibility](https://docs.oracle.com/iaas/Content/Object/Tasks/usingamazonapip.htm)