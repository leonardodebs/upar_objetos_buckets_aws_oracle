import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv

def test_conexao_aws():
    # Carrega as variáveis do .env (se existir)
    load_dotenv()
    
    try:
        # Pega as credenciais das variáveis de ambiente
        s3 = boto3.client(
            's3',
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        response = s3.list_buckets()
        print("✅ Conectado com sucesso! Buckets encontrados:")
        for bucket in response['Buckets']:
            print(" -", bucket['Name'])
    except NoCredentialsError:
        print("❌ Credenciais não encontradas.")
    except ClientError as e:
        print(f"❌ Erro ao conectar: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_conexao_aws()
