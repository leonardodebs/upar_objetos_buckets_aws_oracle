import os
import threading
import boto3
from botocore.exceptions import ClientError, EndpointConnectionError

class ProgressPercentage:
    """
    Callback chamado pelo boto3 a cada chunk transferido.
    Atualiza um callback opcional para atualizar a GUI.
    """

    def __init__(self, filename, gui_callback=None):
        self._filename = filename
        self._size = os.path.getsize(filename)
        self._seen_so_far = 0
        self._gui_callback = gui_callback
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            if self._gui_callback and self._size > 0:
                try:
                    percentage = (self._seen_so_far / self._size) * 100
                    self._gui_callback(percentage)
                except Exception:
                    pass  # Ignora erros no callback da GUI em segundo plano

def upload_arquivo_para_s3(local_file, bucket, s3_key, aws_config=None, gui_callback=None):
    """
    Faz upload de um arquivo local para o S3.
    """
    if not os.path.exists(local_file):
        return False, "O arquivo selecionado não foi encontrado no sistema local."

    try:
        if aws_config:
            s3 = boto3.client(
                's3',
                region_name=aws_config.get('AWS_REGION'),
                aws_access_key_id=aws_config.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=aws_config.get('AWS_SECRET_ACCESS_KEY'),
            )
        else:
            s3 = boto3.client('s3')

        progress = ProgressPercentage(local_file, gui_callback)
        s3.upload_file(local_file, bucket, s3_key, Callback=progress)
        return True, ""

    except EndpointConnectionError:
        erro = "Erro de rede: Verifique sua conexão com a internet ou se um firewall está bloqueando o acesso."
        return False, erro
    except PermissionError:
        erro = "Erro de permissão: Certifique-se de que o arquivo não está sendo usado por outro programa."
        return False, erro
    except ClientError as e:
        codigo = e.response.get("Error", {}).get("Code", "Desconhecido")
        erro = f"Recusado pelo S3 (Código {codigo}): Verifique se o bucket existe e se as permissões de gravação estão corretas."
        return False, erro
    except Exception as e:
        erro = f"Erro inesperado no upload: {str(e)}"
        # Tenta imprimir apenas se estiver em ambiente de terminal
        try:
            print(f"❌ Erro no upload: {e}")
        except:
            pass
        return False, erro
