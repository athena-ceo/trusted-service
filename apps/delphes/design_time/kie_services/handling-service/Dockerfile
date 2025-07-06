# Utilise une image Java légère officielle
FROM eclipse-temurin:17-jre-alpine

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le dossier Quarkus packagé dans l'image
COPY target/quarkus-app/ ./quarkus-app/

# Exposer le port utilisé par Quarkus (7070)
EXPOSE 7070

# Commande de lancement
CMD ["java", "-Dquarkus.http.port=7070", "-jar", "quarkus-app/quarkus-run.jar"]