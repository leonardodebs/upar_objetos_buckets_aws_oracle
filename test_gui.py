import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # Importando o ttk para usar a Progressbar
import os  # Importando o módulo os para usar getsize
from s3_uploader import upload_arquivo_para_s3
from config import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

# Função para selecionar o arquivo e fazer o upload
def selecionar_arquivo():
    global file_size  # Tornar o file_size global
    local_file = filedialog.askopenfilename(title="Selecione o arquivo", filetypes=[("All Files", "*.*")])
    if local_file:
        file_name = local_file.split('/')[-1]  # Pega o nome do arquivo
        s3_key = f"uploads/{file_name}"  # Define o caminho do arquivo no S3
        print(f"Arquivo selecionado: {local_file}")
        
        # Definir o tamanho do arquivo
        file_size = os.path.getsize(local_file)
        
        # Inicia o upload
        sucesso = upload_arquivo_para_s3(local_file, bucket_name, s3_key, progress_callback)
        if sucesso:
            messagebox.showinfo("Sucesso", "Arquivo enviado com sucesso!")
        else:
            messagebox.showerror("Erro", "Falha ao enviar o arquivo.")

# Atualiza a barra de progresso
def progress_callback(bytes_transferred):
    progress = (bytes_transferred / file_size) * 100
    progress_bar['value'] = progress
    window.update_idletasks()  # Atualiza a interface gráfica

# Criando a interface gráfica
window = tk.Tk()
window.title("Envio de Arquivo para S3")
window.geometry("400x200")

# Barra de progresso (agora do ttk)
progress_bar = ttk.Progressbar(window, length=300, mode='determinate', maximum=100)
progress_bar.pack(pady=20)

# Botão para selecionar o arquivo
button_select = tk.Button(window, text="Selecionar Arquivo", command=selecionar_arquivo)
button_select.pack(pady=10)

# Defina o nome do seu bucket S3 aqui
bucket_name = "meu-bucket-de-backups-leonardodebs"

# Inicia a interface gráfica
window.mainloop()
