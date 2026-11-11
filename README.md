# SmartQueue Sénégal — Plateforme intelligente de gestion des files d'attente

Application web Django pour permettre aux usagers de prendre un ticket numérique et de suivre leur position dans une file d'attente. Le projet est une base fonctionnelle de démonstration, extensible pour les SMS, WhatsApp et e-mails.

## 1. Prérequis
- Python 3.10 ou plus récent
- Visual Studio Code
- Une connexion Internet pour installer Django

## 2. Installation dans VS Code
Ouvrez le dossier `SmartQueue_Senegal` dans VS Code, puis ouvrez le terminal intégré.

### Windows
```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Ubuntu / Linux / machine virtuelle
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Ouvrez ensuite http://127.0.0.1:8000/ .
Administration : http://127.0.0.1:8000/admin/

## 3. Fonctions incluses
- Inscription et connexion des utilisateurs
- Liste des établissements et détails d'un établissement
- Création d'un ticket numérique
- Calcul de la position dans la file
- Tableau de bord avec statistiques simples
- Gestion des établissements et tickets depuis l'administration Django
- Interface responsive avec CSS

## 4. Notifications
Les notifications sont préparées comme point d'extension. Pour envoyer réellement des SMS, WhatsApp ou des e-mails, configurez un fournisseur (par exemple un service SMS/WhatsApp) et ses identifiants dans des variables d'environnement. Ne mettez jamais de clés secrètes dans le code source.

## 5. Parcours de démonstration
1. Créez un compte ou connectez-vous.
2. Connectez-vous à `/admin/` avec le superutilisateur.
3. Ajoutez un établissement dans **Établissements**.
4. Retournez à l'accueil, ouvrez cet établissement et prenez un ticket.
5. Consultez **Mes tickets** pour voir votre ticket et sa position.

## 6. Remarque
La base de données par défaut est SQLite pour faciliter les premiers tests. Pour un déploiement réel, utilisez PostgreSQL, HTTPS, une configuration de secrets sécurisée, des sauvegardes, des tests et un fournisseur de notifications.
