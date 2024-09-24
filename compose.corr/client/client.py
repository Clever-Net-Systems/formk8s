#!/usr/bin/env python3


import os
import mysql.connector
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()

        try:
            # Connexion à la base de données
            mydb = mysql.connector.connect(
                user=os.environ["MYSQL_USER"],
                password=os.environ["MYSQL_PASSWORD"],
                host=os.environ["MYSQL_HOST"],
                database=os.environ["MYSQL_DB"]
            )
            mycursor = mydb.cursor()

            # Exécuter une requête pour récupérer toutes les colonnes de la table `user`
            mycursor.execute("SELECT User FROM user")
            myresult = mycursor.fetchall()

            # Itérer sur chaque ligne récupérée
            for user in myresult:
                for index, column in enumerate(user):
                    # Afficher le type de chaque colonne
                    self.wfile.write(f"Colonne coucou {index}: {str(column)}\n".encode('utf-8'))

        except mysql.connector.Error as err:
            # Gérer les erreurs de connexion ou de requête
            self.wfile.write(f"Erreur de base de données: {err}".encode('utf-8'))

        finally:
            # Assurez-vous de fermer la connexion à la base de données
            if mydb.is_connected():
                mycursor.close()
                mydb.close()

# Démarrer le serveur HTTP
httpd = HTTPServer(('', int(os.getenv('PORT', 8000))), SimpleHTTPRequestHandler)
httpd.serve_forever()

