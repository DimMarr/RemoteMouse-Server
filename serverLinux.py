import os
import socket
import tkinter as tk
from pynput.mouse import Button, Controller

HOST = '0.0.0.0'
PORT = 65432
mouse = Controller()
sensibility = 50

root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("Le serveur est en attente de connexions...")

    while True:
        try:
            conn, addr = s.accept()
            with conn:
                print('Connecté par', addr)
                previousY = screen_height / 2
                previousX = screen_width / 2
                while True:
                    data = conn.recv(1024)
                    if not data:
                        print("Connexion interrompue.")
                        break

                    tabMessage = data.decode().strip().split('_')
                    typeMessage = tabMessage[0]
                    message = tabMessage[1]

                    if typeMessage == "CLICK":
                        if message == "LEFT":
                            typeClick = tabMessage[2]
                            if typeClick == "UP":
                                mouse.release(Button.left)
                            elif typeClick == "DOWN":
                                mouse.press(Button.left)
                        elif message == "RIGHT":
                            mouse.click(Button.right, 1)
                        print("Clic effectué.")
                    elif typeMessage == "VOLUME":
                        if message == "UP":
                            os.system("amixer -D pulse sset Master 5%+")
                        elif message == "DOWN":
                            os.system("amixer -D pulse sset Master 5%-")
                        print("Volume modifié")
                    elif typeMessage == "COORD":
                        coordinates = message.split(',')
                        if len(coordinates) == 2:
                            try:
                                gyroX = float(coordinates[0])
                                gyroY = float(coordinates[1])

                                newX = previousX - (gyroX * sensibility)
                                newY = previousY - (gyroY * sensibility)

                                if newX < 0:
                                    newX = 0
                                elif newX > screen_width:
                                    newX = screen_width
                                if newY < 0:
                                    newY = 0

                                mouse.position = (newX, newY)

                                previousX = newX
                                previousY = newY

                                print(f"Déplacement de la souris à : {newX}, {newY}")
                            except ValueError:
                                print("Erreur de conversion des coordonnées.")

        except Exception as e:
            print(f"Erreur dans la connexion : {e}")
