import os
import subprocess
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, Canvas, scrolledtext
import configparser
from pywinauto import Desktop
import pygetwindow as gw

# Inicializa a variável global yggdrasil_process
yggdrasil_process = None

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

# Função para minimizar a janela do Yggdrasil
def minimize_window():
    time.sleep(2)  # Aguarda a janela abrir
    folder_name = os.path.basename(yggdrasil_path.get())
    windows = gw.getWindowsWithTitle(folder_name)
    if windows:
        for window in windows:
            window.minimize()
    else:
        # Use pywinauto to minimize the window if pygetwindow doesn't find it
        app = Desktop(backend="uia").window(title=folder_name)
        app.minimize()

# Função para iniciar o Yggdrasil
def start_yggdrasil():
    global yggdrasil_process
    path = yggdrasil_path.get()
    if not path:
        messagebox.showwarning("Warning", "Please select the Yggdrasil directory first!")
        return

    yggdrasil_exe = os.path.join(path, "yggdrasil.exe")
    yggdrasil_conf = os.path.join(path, "yggdrasil.conf")

    try:
        yggdrasil_process = subprocess.Popen([yggdrasil_exe, '--useconffile', yggdrasil_conf], cwd=path,
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        threading.Thread(target=read_output, daemon=True).start()
        threading.Thread(target=minimize_window, daemon=True).start()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start Yggdrasil: {e}")

# Função para ler a saída do processo
def read_output():
    for line in yggdrasil_process.stdout:
        update_output(line)
    for line in yggdrasil_process.stderr:
        update_output(line)

# Função para parar o Yggdrasil
def stop_yggdrasil():
    global yggdrasil_process
    try:
        if yggdrasil_process:
            yggdrasil_process.terminate()
            yggdrasil_process.wait()
            yggdrasil_process = None
            update_light('red')
        messagebox.showinfo("Info", "Yggdrasil stopped successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to stop Yggdrasil: {e}")

# Função para checar se o Yggdrasil está rodando
def check_yggdrasil_status():
    global yggdrasil_process
    while True:
        time.sleep(1)
        if yggdrasil_process and yggdrasil_process.poll() is None:
            update_light('green')
        else:
            update_light('red')

# Função para atualizar a cor da luz
def update_light(color):
    canvas.itemconfig(light, fill=color)

# Função para atualizar o quadro de saída
def update_output(output):
    output_text.configure(state='normal')
    output_text.insert(tk.END, output)
    output_text.configure(state='disabled')
    output_text.see(tk.END)

# Função para alternar o estado do Yggdrasil
def toggle_yggdrasil(event):
    if yggdrasil_process and yggdrasil_process.poll() is None:
        stop_yggdrasil()
    else:
        start_yggdrasil()

# Configuração da janela principal do Tkinter
root = tk.Tk()
root.title("Yggdrasil Control Panel")

yggdrasil_path = tk.StringVar(value=load_config())

# Botões e entradas da interface
tk.Label(root, text="Yggdrasil Directory:").pack(pady=5)
tk.Entry(root, textvariable=yggdrasil_path, width=50).pack(padx=10)
tk.Button(root, text="Select Directory", command=select_directory).pack(pady=5)

# Canvas para a luz indicadora
canvas = Canvas(root, width=40, height=40)
canvas.pack(pady=10)
light = canvas.create_oval(5, 5, 35, 35, fill='red')
canvas.tag_bind(light, '<Button-1>', toggle_yggdrasil)

# Quadro de saída
output_text = scrolledtext.ScrolledText(root, width=80, height=20, state='disabled')
output_text.pack(pady=5, padx=10)

# Thread para checar o status do Yggdrasil
thread = threading.Thread(target=check_yggdrasil_status, daemon=True)
thread.start()

# Inicialização da janela
root.mainloop()
