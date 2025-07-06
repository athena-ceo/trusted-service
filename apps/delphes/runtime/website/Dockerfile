# Utilise une image Python légère
FROM python:3.11-slim

# Crée un dossier pour l'app
WORKDIR /app

# Copie le site statique dans l'image
COPY . /app/website/

# Expose le port 8080
EXPOSE 8080

# Commande de lancement du serveur HTTP Python
CMD ["python", "-m", "http.server", "8080", "--directory", "website"]