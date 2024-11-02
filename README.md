Analyseur de Données

📘 Description du Projet

Analyseur de Données est une application web construite avec Django pour analyser des fichiers de données (CSV et Excel). Elle permet aux utilisateurs de télécharger des fichiers, de calculer des statistiques descriptives (moyenne, médiane, mode, variance, etc.), d’analyser les corrélations, et de télécharger les résultats en formats CSV ou PDF. Des visualisations de données (histogrammes et régressions) sont également incluses pour aider les utilisateurs à interpréter les relations entre les variables.

⚙️ Installation et Configuration

Prérequis

 • Python 3.8+
 • pip (gestionnaire de paquets Python)
 • Django (version 5.0+)
 • Librairies supplémentaires : pandas, matplotlib, seaborn, openpyxl, reportlab

Étapes d’installation

 1. Clonez le dépôt

git clone <https://github.com/yourusername/analyseur_donnees.git>
cd analyseur_donnees

 2. Installez les dépendances

pip install -r requirements.txt

 3. Configurez les paramètres du projet
 • Créez un fichier .env ou configurez les paramètres dans settings.py pour inclure votre SECRET_KEY, et configurez DEBUG, STATIC_ROOT, et MEDIA_ROOT.
 • Configurez MAILGUN_API_KEY et MAILGUN_DOMAIN si vous utilisez Mailgun pour les notifications par e-mail.
Exemple :

# settings.py

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')

 4. Exécutez les migrations

python manage.py migrate

 5. Collectez les fichiers statiques

python manage.py collectstatic

 6. Créez un superutilisateur pour accéder à l’administration Django

python manage.py createsuperuser

 7. Lancez le serveur

python manage.py runserver

Le site sera accessible à <http://127.0.0.1:8000/>.

🧩 Utilisation

Fonctionnalités principales

 • Page d’accueil : Permet aux utilisateurs de naviguer vers la page de profil, l’historique des analyses ou le formulaire d’upload.
 • Téléchargement de Fichiers : Les utilisateurs peuvent télécharger des fichiers CSV ou Excel pour analyse.
 • Personnalisation de l’Analyse : Les utilisateurs peuvent sélectionner les statistiques descriptives à calculer et les colonnes à analyser.
 • Visualisations : Des histogrammes et des régressions linéaires sont générés pour aider à la visualisation des données.
 • Historique des Analyses : Affiche un tableau des fichiers analysés avec leurs statistiques et des liens pour télécharger les résultats en CSV ou PDF.

Navigation

 1. Page d’Accueil :
 • Accédez aux options de téléchargement, à votre profil ou à l’historique des analyses.
 2. Télécharger un Fichier :
 • Choisissez un fichier (CSV ou Excel) et soumettez-le pour analyse.
 • Configurez les statistiques souhaitées avant de lancer l’analyse.
 3. Historique des Analyses :
 • Consultez toutes les analyses passées, avec un lien pour télécharger chaque fichier analysé.
 • Téléchargez les résultats en format CSV ou PDF.
 4. Profil :
 • Mettez à jour votre adresse e-mail et gérez vos informations de profil.

🛠️ Technologies Utilisées

 • Backend : Django (avec les applications intégrées comme Django Admin et les templates)
 • Frontend : HTML, CSS (Bootstrap pour le style et la mise en page)
 • Analyse et Visualisation de Données :
 • Pandas : Pour le chargement et la manipulation des fichiers CSV/Excel.
 • Matplotlib et Seaborn : Pour les visualisations de données (histogrammes, heatmaps, régressions).
 • Autres Bibliothèques :
 • ReportLab : Pour la génération de rapports PDF.
 • Openpyxl : Pour la manipulation des fichiers Excel.

📊 Exemples de Code

Exemple d’une Vue pour le Téléchargement de Fichier

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

Exemple de Configuration du Template analysis_history.html

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Historique des Analyses</title>
    <link rel="stylesheet" href="{% static 'custom.css' %}">
</head>
<body>
<div class="container mt-5">
    <h2 class="text-center mb-4">Historique des Analyses</h2>
    <table class="table table-bordered table-hover align-middle text-center mt-4">
        <thead class="table-dark">
            <tr>
                <th>Nom du Fichier</th>
                <th>Date d'Upload</th>
                <th>Moyenne</th>
                <th>Médiane</th>
                <th>Mode</th>
                <th>Variance</th>
                <th>Écart-type</th>
                <th>Étendue</th>
                <th>Fichier</th>
            </tr>
        </thead>
        <tbody>
            {% for analysis in user_analyses %}
            <tr>
                <td>{{ analysis.file_name }}</td>
                <td>{{ analysis.upload_date|date:"d M Y H:i" }}</td>
                <td>{{ analysis.mean }}</td>
                <td>{{ analysis.median }}</td>
                <td>{{ analysis.mode }}</td>
                <td>{{ analysis.variance }}</td>
                <td>{{ analysis.std_dev }}</td>
                <td>{{ analysis.data_range }}</td>
                <td>
                    <a href="{{ analysis.file.url }}" class="btn btn-sm btn-primary">Télécharger</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
</body>
</html>

🚀 Améliorations Futures

 • Analyse Avancée : Ajouter des options pour des analyses plus poussées (analyses multivariées, régressions polynomiales, etc.).
 • Sécurité des Fichiers : Ajouter une validation avancée pour les fichiers et un contrôle d’accès plus rigoureux.
 • Interface Utilisateur Améliorée : Intégrer davantage de styles CSS pour une expérience utilisateur plus moderne et intuitive.
 • Notifications par Email : Intégrer une notification par e-mail pour informer l’utilisateur lorsque l’analyse est terminée.

Ce README.md fournit une documentation complète pour que les utilisateurs puissent comprendre, installer et utiliser l’application. En cas de mise à jour du code ou d’ajout de nouvelles fonctionnalités, il est recommandé de mettre à jour ce document pour refléter les changements. 😄
