import socket
from pynput.mouse import Button, Controller

# Configuration du serveur
HOST = '0.0.0.0'  # Écouter sur toutes les interfaces réseau
PORT = 65432  # Port d'écoute
mouse = Controller()

# Créer un socket TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("Le serveur est en attente de connexions...")

    while True:  # Boucle principale pour accepter de nouvelles connexions
        try:
            conn, addr = s.accept()  # Attendre une connexion
            with conn:
                print('Connecté par', addr)
                while True:  # Boucle pour recevoir des données de la connexion
                    data = conn.recv(1024)  # Recevoir les données
                    if not data:
                        print("Connexion interrompue.")
                        break  # Sortir de la boucle si la connexion est perdue

                    # Convertir les données en texte et supprimer les espaces superflus
                    message = data.decode().strip()

                    # Vérifier le type de commande reçue
                    if message == "CLICK_LEFT":
                        # Clic gauche
                        mouse.click(Button.left, 1)
                        print("Clic gauche effectué.")
                    elif message == "CLICK_RIGHT":
                        # Clic droit
                        mouse.click(Button.right, 1)
                        print("Clic droit effectué.")
                    else:
                        # Sinon, on s'attend à recevoir des coordonnées au format "x,y"
                        coordinates = message.split(',')
                        if len(coordinates) == 2:
                            try:
                                x = float(coordinates[0])
                                y = float(coordinates[1])
                                mouse.position = (x, y)
                                print(f"Déplacement de la souris à : {x}, {y}")
                            except ValueError:
                                print("Erreur de conversion des coordonnées.")

        except Exception as e:
            print(f"Erreur dans la connexion : {e}")
            # On peut décider de faire une pause ou une autre action ici avant de continuer à écouter
