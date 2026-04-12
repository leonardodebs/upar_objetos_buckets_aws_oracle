import os
import boto3
import requests
from botocore.config import Config

def upload_arquivo_para_oci(local_file, bucket, object_key, oci_config=None, gui_callback=None):
    """
    Faz upload usando um link pré-assinado e a lib 'requests' para evitar bugs de cabeçalho do Boto3 na OCI.
    """
    if not os.path.exists(local_file):
        return False, "O arquivo selecionado não foi encontrado no sistema local."

    try:
        # 1. Configura o Client original para gerar a assinatura v4 (padrão OCI)
        endpoint = f"https://{oci_config.get('OCI_NAMESPACE')}.compat.objectstorage.{oci_config.get('OCI_REGION')}.oraclecloud.com"
        s3_config = Config(
            s3={'addressing_style': 'path'},
            signature_version='s3v4'
        )
        s3 = boto3.client(
            's3',
            region_name=oci_config.get('OCI_REGION'),
            endpoint_url=endpoint,
            aws_access_key_id=oci_config.get('OCI_ACCESS_KEY_ID'),
            aws_secret_access_key=oci_config.get('OCI_SECRET_ACCESS_KEY'),
            config=s3_config
        )

        # 2. Gera uma URL pré-assinada para o upload (Válida por 10 minutos)
        url = s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': bucket,
                'Key': object_key,
                'ContentType': 'application/octet-stream'
            },
            ExpiresIn=600
        )

        # 3. Faz o upload real usando a lib 'requests', que é a mais estável com cabeçalhos na OCI
        file_size = os.path.getsize(local_file)
        
        with open(local_file, 'rb') as f:
            # O requests envia o Content-Length automático e gerencia o stream sem chunked encoding por padrão
            # Essencial para arquivos pesados (> 10GB) não serem recusados pela OCI.
            response = requests.put(
                url, 
                data=f, 
                headers={
                    'Content-Type': 'application/octet-stream',
                    'Content-Length': str(file_size)
                }
            )
            
            if response.status_code in [200, 201]:
                if gui_callback:
                    gui_callback(100.0)
                return True, ""
            else:
                return False, f"Erro OCI ({response.status_code}): {response.text}"

    except Exception as e:
        return False, f"Erro inesperado: {str(e)}"
