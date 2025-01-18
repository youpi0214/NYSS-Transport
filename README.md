# NYSS Transport

NYSS Transport est une application web centralisée visant à simplifier l'accès aux services de transport en commun au Québec. L'application permet aux usagers d'acheter et gérer leurs titres de transport de différentes compagnies via une seule plateforme, tout en offrant aux entreprises de transport un moyen efficace de distribuer leurs abonnements et tickets.

---

## Fonctionnalités

- **Achat centralisé** : Réservez et achetez vos billets et abonnements en quelques clics.
- **Gestion du portefeuille d'accès** : Visualisez et gérez vos tickets et abonnements actifs.
- **Intégration multi-compagnies** : Compatible avec plusieurs sociétés de transport québécoises (RTC, STM, STLévis, RTL).
- **Sécurisation des transactions** : Paiements sécurisés avec gestion des cartes de crédit.
- **Responsive Design** : Application accessible depuis un ordinateur, une tablette ou un mobile.

---
## Accès à l'application
Vous pouvez consulter le frontend de l'application ici : [NYSS Transport](https://nyss-transport.vercel.app/)

---

## Installation

### Prérequis
- MySQL installé et configuré.
- Node.js et npm installés.
- Git installé sur votre machine.

### Étapes
1. Clonez le dépôt :
   ```bash
   git clone https://github.com/youpi0214/NYSS-Transport.git
   ```
2. Naviguez vers le répertoire du projet :
   ```bash
   cd NYSS-Transport
   ```
3. Installez les dépendances :
   ```bash
   npm install
   ```
4. Configurez la base de données MySQL (script SQL disponible dans `/database`).
5. Démarrez le serveur pour le backend :
   ```bash
   python ???
   ```
6. Démarrez le serveur pour le frontend (dans le dossier `/Frontend`) :
   ```bash
   npm run dev
   ```
7. Accédez à l'application via votre navigateur à l'adresse fournit.

---

## Structure du projet

```
Backend/
├── API/            # Code source de l'API et tests
├── Database/       # Scripts SQL, serveur et gestion de la base de données
Frontend/
├── public/        # Fichiers statiques (logo)
├── src/           # Code source du frontend
├── index.html     # Page par défaut
├── package.json   # Dépendances Node.js
└── vite.config.js # Configuration du build
```

---

## Technologies utilisées

- **Backend** : Node.js, Express.js
- **Base de données** : MySQL
- **Frontend** : HTML, CSS, JavaScript

---

## Utiliser l'application

### Fonctionnalités principales :
1. **Inscription et Connexion**
    - Créez un compte usager ou administrateur.
    - Authentification sécurisée avec mot de passe hashé.
2. **Achat de tickets et abonnements**
    - Sélectionnez un titre de transport.
    - Ajoutez une carte de crédit et effectuez l'achat en ligne.
3. **Gestion des accès**
    - Consultez votre historique d’achats.
    - Ajoutez ou supprimez une carte de crédit.
4. **Administration** (Accès restreint)
    - Ajoutez de nouveaux titres de transport.
    - Gérez les abonnements des utilisateurs.

---

## Licence

Ce projet est sous licence **MIT**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## Remerciements

Ce projet a été réalisé dans le cadre du cours **GLO-2005 - Modèles et langages de base de données** à l'Université Laval. Un grand merci aux membres de l’équipe :

- **Nasma Chaoui**
- **Samy Khalfallah**
- **Yannick-André Ouamba**
- **Ahmed Sami**

Vidéo de présentation du projet : [Lien YouTube](https://youtu.be/1dXA18ASsaA)
