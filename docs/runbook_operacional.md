# Runbook: Operação e Troubleshooting — Upar Objetos

**Última atualização:** 2026-04-18  
**Responsável:** Time de Infraestrutura / DevOps  
**Tempo estimado:** 5-10 minutos  
**Impacto:** Operacional (Upload de dados)

---

## 1. Objetivo
Este runbook descreve os procedimentos para configurar, validar e utilizar as ferramentas de upload para AWS e OCI, além de fornecer passos para resolução de problemas comuns.

## 2. Pré-requisitos
- [ ] Credenciais de acesso (Access Key / Secret Key) com permissão de `PutObject` e `ListBucket`.
- [ ] Endereço da região e nome do bucket destino.
- [ ] Python 3.10 ou superior (caso esteja executando via script).

## 3. Procedimento Operacional

### Passo 1 — Configuração Inicial
1. Abra a aplicação escolhida (`upar_aws` ou `upar_oci`).
2. Navegue até a aba **Configurações**.
3. Preencha todos os campos conforme indicado.
   - *Nota: O OCI exige o 'Namespace' que pode ser encontrado no console da Oracle.*
4. Clique em **Validar Conexão**. Só é possível prosseguir se o status ficar verde (Sucesso).

### Passo 2 — Upload de Arquivos
1. Vá para a aba **Upload**.
2. Clique em **Escolher Arquivo** e selecione o documento (Backup, ZIP, etc).
3. Defina o caminho de destino no bucket (Ex: `backups/2026/04/banco.zip`).
4. Clique em **Enviar**. Acompanhe a barra de progresso.

---

## 4. Troubleshooting (Resolução de Problemas)

### Problema: Falha na Validação (403 Forbidden)
- **Causa:** Credenciais incorretas ou falta de permissão IAM no bucket.
- **Solução:** Verifique se as chaves não possuem espaços extras. Confirme se a política de acesso (Bucket Policy) permite a ação `s3:GetBucketLocation` ou `s3:ListBucket`.

### Problema: Upload trava em 0% ou falha no meio do processo
- **Causa:** Instabilidade de rede ou expiração de token.
- **Solução:** Reinicie a aplicação. Se o arquivo for maior que 10GB e estiver na OCI, certifique-se de estar usando o módulo `upar_oci`, que é otimizado para este volume.

### Problema: "Namespace not found" (OCI)
- **Causa:** Namespace incorreto na configuração.
- **Solução:** Pegue o Namespace exato no console OCI em: *Profile -> Tenancy: [Nome] -> Object Storage Namespace*.

## 5. Rollback
Não há necessidade de procedimentos de rollback técnico para a aplicação, pois ela não altera o estado do servidor local. Para "cancelar" um upload em progresso, basta fechar a janela da aplicação.
