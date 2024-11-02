# Analyseur de Données

## 📑 Table des Matières

1. [📘 Description du Projet](#-description-du-projet)
2. [⚙️ Installation et Configuration](#️-installation-et-configuration)
3. [🧩 Utilisation](#-utilisation)
4. [🛠️ Technologies Utilisées](#️-technologies-utilisées)
5. [📊 Exemples de Code](#-exemples-de-code)
6. [👥 Contributeurs](#-contributeurs)
7. [🤝 Contribution](#-contribution)
8. [🚀 Améliorations Futures](#-améliorations-futures)

## ⚙️ Installation et Configuration

### Prérequis

- Python 3.8+
- pip (gestionnaire de paquets Python)
- Django (version 5.0+)
- Librairies supplémentaires : pandas, matplotlib, seaborn, openpyxl, reportlab

## 📘 Description du Projet

Analyseur de Données est une application web construite avec Django pour analyser des fichiers de données (CSV et Excel). Elle permet aux utilisateurs de télécharger des fichiers, de calculer des statistiques descriptives (moyenne, médiane, mode, variance, etc.), d’analyser les corrélations, et de télécharger les résultats en formats CSV ou PDF. Des visualisations de données (histogrammes et régressions) sont également incluses pour aider les utilisateurs à interpréter les relations entre les variables.

### Étapes d’installation

1. Clonez le dépôt

    ```sh
    git clone <https://github.com/yourusername/analyseur_donnees.git>
    cd analyseur_donnees
    ```

2. Installez les dépendances

    ```sh
    pip install -r requirements.txt
    ```

3. Configurez les paramètres du projet
    - Créez un fichier `.env` ou configurez les paramètres dans `settings.py` pour inclure votre `SECRET_KEY`, et configurez `DEBUG`, `STATIC_ROOT`, et `MEDIA_ROOT`.
    - Configurez `MAILGUN_API_KEY` et `MAILGUN_DOMAIN` si vous utilisez Mailgun pour les notifications par e-mail.

    Exemple :

    ```python
    # settings.py

    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')
    ```

4. Exécutez les migrations

    ```sh
    python manage.py migrate
    ```

5. Collectez les fichiers statiques

    ```sh
    python manage.py collectstatic
    ```

6. Créez un superutilisateur pour accéder à l’administration Django

    ```sh
    python manage.py createsuperuser
    ```

7. Lancez le serveur

    ```sh
    python manage.py runserver
    ```

    Le site sera accessible à <http://127.0.0.1:8000/>.

## 🧩 Utilisation

### Fonctionnalités principales

- **Page d’accueil** : Permet aux utilisateurs de naviguer vers la page de profil, l’historique des analyses ou le formulaire d’upload.
- **Téléchargement de Fichiers** : Les utilisateurs peuvent télécharger des fichiers CSV ou Excel pour analyse.
- **Personnalisation de l’Analyse** : Les utilisateurs peuvent sélectionner les statistiques descriptives à calculer et les colonnes à analyser.
- **Visualisations** : Des histogrammes et des régressions linéaires sont générés pour aider à la visualisation des données.
- **Historique des Analyses** : Affiche un tableau des fichiers analysés avec leurs statistiques et des liens pour télécharger les résultats en CSV ou PDF.

### Navigation

1. **Page d’Accueil** :
    - Accédez aux options de téléchargement, à votre profil ou à l’historique des analyses.
2. **Télécharger un Fichier** :
    - Choisissez un fichier (CSV ou Excel) et soumettez-le pour analyse.
    - Configurez les statistiques souhaitées avant de lancer l’analyse.
3. **Historique des Analyses** :
    - Consultez toutes les analyses passées, avec un lien pour télécharger chaque fichier analysé.
    - Téléchargez les résultats en format CSV ou PDF.
4. **Profil** :
    - Mettez à jour votre adresse e-mail et gérez vos informations de profil.

## 🛠️ Technologies Utilisées

- **Backend** : Django (avec les applications intégrées comme Django Admin et les templates)
- **Frontend** : HTML, CSS (Bootstrap pour le style et la mise en page)
- **Analyse et Visualisation de Données** :
  - Pandas : Pour le chargement et la manipulation des fichiers CSV/Excel.
  - Matplotlib et Seaborn : Pour les visualisations de données (histogrammes, heatmaps, régressions).
- **Autres Bibliothèques** :
  - ReportLab : Pour la génération de rapports PDF.
  - Openpyxl : Pour la manipulation des fichiers Excel.

## 📊 Exemples de Code

### Exemple d’une Vue pour le Téléchargement de Fichier

```python
@login_required
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            # Lecture et traitement du fichier
            df = pd.read_excel(file, engine='openpyxl') if file.name.endswith('.xlsx') else pd.read_csv(file)
            # Calcul des statistiques et sauvegarde des résultats
            ...
            messages.success(request, f"Analyse de {file.name} terminée.")
            return redirect('analysis_history')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})
```

## 👥 Contributeurs

Ce projet est réalisé en binôme par :

- [Mohamed Lakssir](https://github.com/thejokers69)
- [Houssam Aoun](https://github.com/AuroreTBF)

## 🤝 Contribution

Si vous souhaitez contribuer à ce projet, veuillez suivre les étapes suivantes :

1. Forkez le dépôt sur votre compte GitHub.
2. Clonez votre fork en local :

    ```sh
    git clone https://github.com/thejokers69/analyseur_donnees.git
    cd analyseur_donnees
    ```

3. Utilisez votre branche dédiée : Une branche a été spécialement créée pour faciliter votre contribution sans affecter le travail principal. Utilisez la branche `feature-houssam` pour faire vos modifications.
    - Récupérez la branche `feature-houssam` :

    ```sh
    git fetch origin feature-houssam
    git checkout feature-houssam
    ```

4. Travaillez sur la branche `feature-houssam` : Ajoutez vos fonctionnalités ou corrigez les bogues dans cette branche.
5. Commitez vos modifications :

    ```sh
    git add .
    git commit -m "Ajout de [votre fonctionnalité ou correction]"
    ```

6. Poussez votre branche vers GitHub :

    ```sh
    git push origin feature-houssam
    ```

7. Ouvrez une Pull Request (PR) vers la branche principale (`master`) pour que vos modifications soient révisées et fusionnées dans le projet principal.

⚠️ Important : Assurez-vous de rester synchronisé avec les dernières modifications en tirant les mises à jour de `master` dans votre branche `feature-houssam` si nécessaire. Pour cela :

    ```sh
    git checkout feature-houssam
    git pull origin master
    ```

Note pour Houssam Aoun : Utilisez uniquement la branche `feature-houssam` pour vos modifications afin de faciliter la gestion du projet et éviter les conflits avec la branche principale `master`.

Voici comment structurer la section 🚀 Améliorations Futures dans le README.md pour suggérer des axes d’amélioration du projet et orienter les contributeurs sur des fonctionnalités ou optimisations à venir :

## 🚀 Améliorations Futures

Le projet Analyseur de Données peut être étendu avec de nouvelles fonctionnalités et améliorations pour offrir une meilleure expérience utilisateur et enrichir les capacités d’analyse. Voici quelques idées pour les futures améliorations :

- **• 🔍 Analyse Avancée** : Ajouter des options pour des analyses plus poussées, comme l’analyse multivariée, les régressions polynomiales, et l’intégration de méthodes de machine learning pour les prédictions basées sur les données.
- **• 🔒 Sécurité des Fichiers et Gestion des Permissions** : Mettre en place des validations avancées pour les fichiers uploadés afin d’éviter les erreurs. Envisager l’ajout d’un contrôle d’accès basé sur les rôles pour sécuriser les informations sensibles et permettre une gestion des utilisateurs plus fine.
- **• 🎨 Interface Utilisateur Améliorée** : Intégrer davantage de styles CSS et améliorer la mise en page avec des animations et des effets visuels modernes pour rendre l’interface plus conviviale et intuitive. Ajouter également une compatibilité mobile pour une utilisation sur divers appareils.
- **• 📧 Notifications par E-mail** : Activer les notifications par e-mail pour informer les utilisateurs lorsque leur analyse est terminée. Cela pourrait inclure un système de rappel pour les utilisateurs réguliers, les mises à jour de nouvelles fonctionnalités, et les alertes pour les analyses importantes.
- **• 📈 Options de Visualisation Avancées** : Intégrer davantage de visualisations de données comme les graphiques en barres, en secteurs, et les nuages de points pour offrir une vue plus complète des données. Permettre également aux utilisateurs de personnaliser les graphiques (par exemple, choisir les couleurs, les types de graphiques).
- **• 💾 Support des Bases de Données** : Permettre aux utilisateurs de charger des données directement depuis une base de données (comme PostgreSQL, MySQL), en plus des fichiers CSV/Excel. Cela facilitera l’analyse de grandes quantités de données sans avoir à gérer manuellement des fichiers.
- **• 📜 Documentation Améliorée** : Ajouter une documentation plus complète pour aider les développeurs et les utilisateurs finaux. Cela pourrait inclure un guide API pour les futures extensions et des tutoriels pour montrer comment utiliser les fonctionnalités avancées de l’application.
- **• 🌐 Internationalisation (i18n)** : Ajouter le support pour plusieurs langues afin que l’application puisse être utilisée par une audience internationale. Utiliser les fonctionnalités d’internationalisation de Django pour traduire l’interface utilisateur.
- **• 📲 Application Mobile** : Créer une version mobile ou une PWA (Progressive Web App) pour que les utilisateurs puissent accéder aux analyses et résultats directement depuis leurs appareils mobiles.

Ces idées visent à élargir les capacités de l’application et à renforcer sa convivialité, sa sécurité et son efficacité. Elles permettent aussi de définir des axes de développement pour les contributeurs intéressés par ce projet.

