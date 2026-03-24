FROM node:18-alpine

WORKDIR /app

# Copier les fichiers de configuration
COPY package*.json ./

# Installer les dépendances
RUN npm install

# Copier le code de l'application
COPY . .

# Expose le port
EXPOSE 3000

# Commande de démarrage
CMD ["npm", "start"]
