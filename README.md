# Projet de Gestion d'École Django

Ce projet est une application web de gestion d'école développée avec le framework Django. Il permet de gérer les élèves, les professeurs, le personnel administratif, les classes, les notes, le finance, l'élaboration de l'emploi du temps, la génération de bulletin, l'édition de cahier de texte et bien plus encore.

## Prérequis

Avant de lancer le projet, assurez-vous d'avoir les éléments suivants installés :

* Python (version 3.13 recommandée)
* pip (gestionnaire de paquets Python)

## Installation

1.  Clonez le dépôt :

    ```bash
    git clone https://github.com/Orden-Ktn/GestSchool.git
    ```

2.  Accédez au répertoire du projet :

    ```bash
    cd GestSchool
    ```

3.  Créez un environnement virtuel (recommandé) :

    ```bash
    python -m venv venv
    ```

4.  Activez l'environnement virtuel :

    * Sur Windows :

        ```bash
        venv\Scripts\activate
        ```

    * Sur macOS et Linux :

        ```bash
        source venv/bin/activate
        ```

5.  Installez les dépendances du projet à partir du fichier `requirements.txt` :

    ```bash
    pip install -r requirements.txt
    ```

6.  Appliquez les migrations :

    ```bash
    python manage.py migrate
    ```


7.  Lancez le serveur de développement :

    ```bash
    python manage.py runserver
    ```

8.  Accédez à l'application dans votre navigateur à l'adresse `http://127.0.0.1:8000/gestschool_app`.

## Informations de connexion de test

Les informations de connexion de test de base sont fournies dans le fichier `identifiant.txt`. Veuillez utiliser ces informations pour explorer l'application.

## Fonctionnalités principales

* Gestion des élèves (ajout, modification, suppression)
* Gestion des professeurs (ajout, modification, suppression)
* Gestion des classes (ajout, modification, attribution de professeur, ajout d'emploi)
* Gestion des notes (ajout, modification, suppression)
* Interface d'administration Django
* Tableau de bord avec statistiques
* Gestion des matières
* Ajout de contenu dasn le cahier de texte
* Gestion des trimestres
* Gestion des années scolaires
* Gestion des utilisateurs (personnel, professeurs)

## Contributions

Les contributions sont les bienvenues ! Si vous souhaitez contribuer à ce projet, veuillez suivre les étapes suivantes :

1.  Forkez le dépôt.
2.  Créez une branche pour votre fonctionnalité ou correction de bug.
3.  Effectuez vos modifications.
4.  Effectuez un commit de vos modifications.
5.  Effectuez un push vers votre branche.
6.  Créez une pull request.
