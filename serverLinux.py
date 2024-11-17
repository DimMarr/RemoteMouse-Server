import os
import socket
import tkinter as tk
from tkinter import ttk
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Controller as KeyboardController, Key
import threading

HOST = '0.0.0.0'
PORT = 65432
mouse = MouseController()
keyboard = KeyboardController()
sensibility = 50

# Création de l'interface Tkinter
root = tk.Tk()
root.title("Serveur de contrôle souris")
root.geometry("600x500")

# Création des cadres pour chaque type de donnée
frame_client = ttk.LabelFrame(root, text="Informations du client")
frame_client.pack(fill="x", padx=10, pady=5)

frame_coords = ttk.LabelFrame(root, text="Coordonnées")
frame_coords.pack(fill="x", padx=10, pady=5)

frame_click = ttk.LabelFrame(root, text="Clic de souris")
frame_click.pack(fill="x", padx=10, pady=5)

frame_volume = ttk.LabelFrame(root, text="Volume")
frame_volume.pack(fill="x", padx=10, pady=5)

frame_errors = ttk.LabelFrame(root, text="Erreurs")
frame_errors.pack(fill="x", padx=10, pady=5)

frame_key = ttk.LabelFrame(root, text="Actions clavier")
frame_key.pack(fill="x", padx=10, pady=5)

# Widgets pour afficher les valeurs
label_client = tk.Label(frame_client, text="Aucune connexion", font=("Impact", 12))
label_client.pack(padx=10, pady=5)

label_coords = tk.Label(frame_coords, text="Aucune donnée", font=("Impact", 12))
label_coords.pack(padx=10, pady=5)

label_click = tk.Label(frame_click, text="Aucune donnée", font=("Impact", 12))
label_click.pack(padx=10, pady=5)

label_volume = tk.Label(frame_volume, text="Aucune donnée", font=("Impact", 12))
label_volume.pack(padx=10, pady=5)

label_errors = tk.Label(frame_errors, text="Pas d'erreurs", font=("Impact", 12), fg="red")
label_errors.pack(padx=10, pady=5)

label_key = tk.Label(frame_key, text="Aucune donnée", font=("Impact", 12))
label_key.pack(padx=10, pady=5)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Fonction pour mettre à jour le texte dans les widgets
def update_label(label, text, color=None):
    label.config(text=text)
    if color:
        label.config(fg=color)

def handle_key_action(message):
    """Handle key actions based on the message."""
    try:
        key_attr = getattr(Key, message.lower())
        keyboard.press(key_attr)
        keyboard.release(key_attr)
        update_label(label_key, f"Touche pressée : {message}")
    except Exception as e:
        error_message = f"Erreur d'action clavier : {e}"
        update_label(label_errors, error_message)

def server_loop():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        while True:
            try:
                conn, addr = s.accept()
                with conn:
                    client_ip, client_port = addr
                    client_info = f"Client connecté : IP={client_ip}, Port={client_port}"
                    update_label(label_client, client_info, color="blue")

                    previousY = screen_height / 2
                    previousX = screen_width / 2

                    while True:
                        try:
                            data = conn.recv(1024)
                            if not data:
                                print("Connexion interrompue.")
                                update_label(label_client, "Aucune connexion", color="black")
                                break

                            tabMessage = data.decode().strip().split('_')
                            typeMessage = tabMessage[0]
                            message = tabMessage[1]

                            if typeMessage == "CLICK":
                                if message == "LEFT":
                                    typeClick = tabMessage[2]
                                    if typeClick == "UP":
                                        mouse.release(Button.left)
                                        update_label(label_click, "Clic gauche relâché")
                                    elif typeClick == "DOWN":
                                        mouse.press(Button.left)
                                        update_label(label_click, "Clic gauche appuyé")
                                    elif typeClick == "ONE":
                                        mouse.click(Button.left, 1)
                                        update_label(label_click, "Clic gauche effectué")
                                elif message == "RIGHT":
                                    mouse.click(Button.right, 1)
                                    update_label(label_click, "Clic droit effectué")
                            elif typeMessage == "VOLUME":
                                if message == "UP":
                                    os.system("amixer -D pulse sset Master 5%+")
                                    update_label(label_volume, "Volume augmenté")
                                elif message == "DOWN":
                                    os.system("amixer -D pulse sset Master 5%-")
                                    update_label(label_volume, "Volume diminué")
                            elif typeMessage == "ALIGN":
                                mouse.position = (screen_width / 2, screen_height / 2)
                                previousX = screen_width / 2
                                previousY = screen_height / 2
                            elif typeMessage == "KEY":
                                handle_key_action(message)
                                print(tabMessage)
                            elif typeMessage == "COORD":
                                coordinates = message.split(',')
                                if len(coordinates) == 2:
                                    try:
                                        gyroX = float(coordinates[0])
                                        gyroY = float(coordinates[1])

                                        newX = previousX - (gyroX * sensibility)
                                        newY = previousY - (gyroY * sensibility)

                                        mouse.position = (newX, newY)

                                        previousX = newX
                                        previousY = newY

                                        update_label(label_coords, f"X: {newX:.2f}, Y: {newY:.2f}")
                                    except ValueError:
                                        error_message = f"Erreur de conversion : {tabMessage}"
                                        update_label(label_errors, error_message)
                                        print(error_message)
                                else:
                                    error_message = f"Données incorrectes : {tabMessage}"
                                    update_label(label_errors, error_message)
                                    print(error_message)
                        except Exception as e:
                            error_message = f"Erreur : {e}"
                            update_label(label_errors, error_message)
                            print(error_message)
                            break
            except Exception as e:
                print(f"Erreur dans la connexion : {e}")

# Lancer le serveur dans un thread séparé
def start_server():
    server_thread = threading.Thread(target=server_loop, daemon=True)
    server_thread.start()

# Démarrage du serveur
start_server()

# Lancement de l'interface Tkinter
root.mainloop()
