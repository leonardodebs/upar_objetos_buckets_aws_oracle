import os
import threading
import boto3
from botocore.exceptions import ClientError

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
        return False

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
        return True

    except Exception as e:
        # Tenta imprimir apenas se estiver em ambiente de terminal
        try:
            print(f"❌ Erro no upload: {e}")
        except:
            pass
        return False
