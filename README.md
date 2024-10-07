BOT DISCORD PFP

📚 Description

Le Bot Discord PinteCord est un BOT conçu pour gérer les pièces jointes sur Discord, y compris les images et vidéos. Il prend en charge la combinaison d'images, la conversion de vidéos MP4 en GIF, et l'envoi de photos de profil aléatoires des utilisateurs. Ce bot permet de poster rapidement des photos de profils sans réalisé de commandes, dans un embed associé à un bouton pour télécharger en HD.

🛠️ Installation

Prérequis
Avant de commencer, assurez-vous d'avoir installé Git et Python 3.8+. Vous devez également disposer d'un token de bot Discord.

```sh

git clone https://github.com/deveiops/pintecord.git
cd pintecord-bot
pip install -r requirements.txt

```

⚙️ Configuration

Ajoutez un fichier .env à la racine du projet avec les informations suivantes :

```sh
DISCORD_TOKEN= ton token de bot
LOG_CHANNEL_ID= ID de channel des logs
EXEMPT_CHANNEL_ID= channel qui sera bypass des upload photo ( genre channel admin ) 
PROFILE_PIC_CHANNEL_ID= ID du channel ou le bot enverra des photos aléatoire
TARGET_GUILD_ID= l'id de ton serveur ou y'aura le bot, pour éviter les bug si le bot est sur plusieurs serv
DOUBLE_IMAGE_CHANNEL_ID= ID de ton channel pour les pp lié
````

🎯 Utilisation

Pas besoin de faire de commandes avec ce bot, une fois qu'il est actif, vous pouvez envoyer des photos/gif rapidement dans un channel, 10 par 10 et le bot se chargera de les repost dans un embed avec un bouton de téléchargement en HD, il supprimera vos messages.


![Pintecord](https://github.com/deveIops/pintecord/blob/main/Pintecord.jpg)

