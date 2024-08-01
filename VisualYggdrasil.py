import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import configparser

# Função para carregar a configuração do arquivo ini
def load_config():
    config = configparser.ConfigParser()
    config.read('conf.ini')
    if 'Yggdrasil' in config and 'path' in config['Yggdrasil']:
        return config['Yggdrasil']['path']
    return ""

# Função para salvar a configuração no arquivo ini
def save_config(path):
    config = configparser.ConfigParser()
    config['Yggdrasil'] = {'path': path}
    with open('conf.ini', 'w') as configfile:
        config.write(configfile)

# Função para selecionar o diretório do Yggdrasil
def select_directory():
    path = filedialog.askdirectory()
    if path:
        yggdrasil_path.set(path)
        save_config(path)

# Função para iniciar o Yggdrasil
def start_yggdrasil():
    path = yggdrasil_path.get()
    if not path:
        messagebox.showwarning("Warning", "Please select the Yggdrasil directory first!")
        return

    yggdrasil_exe = os.path.join(path, "yggdrasil.exe")
    yggdrasil_conf = os.path.join(path, "yggdrasil.conf")

    try:
        subprocess.Popen([yggdrasil_exe, '--useconffile', yggdrasil_conf], cwd=path)
        messagebox.showinfo("Info", "Yggdrasil started successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start Yggdrasil: {e}")

# Função para parar o Yggdrasil
def stop_yggdrasil():
    try:
        subprocess.run(['taskkill', '/f', '/im', 'yggdrasil.exe'], shell=True)
        messagebox.showinfo("Info", "Yggdrasil stopped successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to stop Yggdrasil: {e}")

# Configuração da janela principal do Tkinter
root = tk.Tk()
root.title("Yggdrasil Control Panel")

yggdrasil_path = tk.StringVar(value=load_config())

# Botões e entradas da interface
tk.Label(root, text="Yggdrasil Directory:").pack(pady=5)
tk.Entry(root, textvariable=yggdrasil_path, width=50).pack(padx=10)
tk.Button(root, text="Select Directory", command=select_directory).pack(pady=5)

tk.Button(root, text="Start Yggdrasil", command=start_yggdrasil).pack(pady=5)
tk.Button(root, text="Stop Yggdrasil", command=stop_yggdrasil).pack(pady=5)

# Inicialização da janela
root.mainloop()
