# Projet 13 : Projet libre
--------------------------

# 1 Informations générales
--------------------------
Ce projet est le dernier projet de ma formation de développeur d'application en python auprès de l'établissement formateur OpenClassrooms.

## 1.1 Description du projet
-----------------------------
Le sujet du projet est libre mais il a pour but d'aider une communauté spécifique. J'ai donc décidé de créer une application de gestion des traductions Odoo afin d'aider la communauté des développeurs Odoo.
  

## 1.2 Fonctionnalités du projet
---------------------------------
Le projet aura plusieurs fonctionnalités principales, à savoir :
- Gestion de projet : possibilité de créer un projet, d'assigner des utilisateurs à des projets ainsi que leur attribuer un rôle etc...
- Gestion des traductions : Affichage, tri, modifications, suppression des traductions présentes dans les fichiers de traduction Odoo.

# 2 Prérequis pour l'utilisation du projet
-------------------------------------------

## 2.1 Langages utilisés
-------------------------
le langage de programmation utilisé dans ce projet est python.
Les langages pour la partie "web" sont le HTML, le CSS et le javascript   
Lien pour télécharger python : https://www.python.org/downloads/  
version de python lors du développement : 3.8
Le projet a été développé avec le framework python 'Django'.
Lien vers la documentation Django : https://docs.djangoproject.com/en/3.0/


## 2.2 librairies utilisées:
-----------------------------
Vous pouvez retrouver l'ensemble des librairies utilisées pour ce projet dans le
fichier requirements.txt et tout installer directement via ce fichier grâce à une
commande pip. 
  
# 3 Structure du projet
-------------------------
Il est à noter que le code associé au projet respecte la PEP8  
Le projet est structuré comme un projet Django 'classique', c'est à dire avec plusieurs applications au sein du projet principal.
Les différentes applications sont les suivantes :
- users : application gérant les utilisateurs du projet
- projects : application gérant la gestion des projets de traduction
- translations : application gérant les traductions odoo
- pages : application gérant les pages "statiques" : page "Home", page des mentions légales etc...
- translation_api : application faisant le lien avec l'api de traduction utilisé (version 2)
- search : application gérant certaines recherches spécifiques

Chaque application a en général un fichier models.py contenant les modèles de l'application, un fichier views.py contenant les views de l'application, un fichier tests.py contenant les tests des fonctions et méthodes de l'application et dans certains cas, un fichier managers.py lorsque les modèles de l'application avaient besoin de managers. Chaque application (ou presque) a aussi un fichier templates et static pour tous les fichiers statiques et les templates qui sont propre à l'application. 
Les commandes 'personnalisées' se situent dans des dossiers 'management/commands'.


# 4 Informations complémentaires
----------------------------------

## 4.1. Acteurs
----------------
développeur = Geoffrey Remacle

## 4.2. Utilisation d'API
--------------------------
Le projet utilisera une API de traduction mais cette fonctionnalité n'est pas encore présente.

## 4.3. Langue du code
-----------------------
les noms de classes, fonctions, variables, les commentaires, les docstrings,... sont écrits en anglais.

## 4.4 Déploiement
------------------
L'application est déployé avec Heroku
vous pouvez retrouver l'application à cette adresse : https://odoo-translations-gr.herokuapp.com/home

## 4.5 Utilisation de base de données
-------------------------------------
Le projet utilise une base de données PostGreSQL en production et en développement

## 4.6. Liens
--------------
Lien vers le repository github:  
https://github.com/GeoffreyRe/project_13
  
Lien vers la page de la formation "Développeur d'Application python":  
https://openclassrooms.com/fr/paths/68-developpeur-dapplication-python   