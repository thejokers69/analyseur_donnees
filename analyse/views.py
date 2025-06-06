# /Users/thejoker/Documents/GitHub/analyseur_donnees/analyse/views.py
import os
import csv
import logging
import base64
from io import BytesIO
from scipy import stats 
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import kurtosis, skew
from scipy.sparse import csr_array
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from plotly.io import to_image
import plotly.express as px
from django.shortcuts import render, get_object_or_404
from .visualization_utils import create_correlation_heatmap, create_regression_plot
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .forms import EmailUpdateForm, UploadFileForm, AnalysisCustomizationForm
from .models import UploadedFile, AnalysisHistory
from .utils import load_data
from django.views.decorators.http import require_http_methods
from .utils import calculate_statistics
from .utils import (
    # correlation_analysis,
    linear_regression_analysis,
    probability_analysis,
    interactive_visualization,
    download_csv,
    download_pdf,
)
from scipy.stats import pearsonr
from django.http import Http404
logger = logging.getLogger(__name__)

# Custom login views
def custom_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect("analyse:home")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "workshop/login.html", {"form": form})


# Homepage view
@login_required
def home(request):
    uploaded_files = None
    if request.user.is_authenticated:
        uploaded_files = UploadedFile.objects.filter(user=request.user)
        logger.debug(f"Uploaded files for user {request.user.username}: {uploaded_files}")
        print(uploaded_files)
    return render(request, "workshop/home.html", {"uploaded_files": uploaded_files})


# Register view
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. You can now log in.")
            return redirect("analyse:home")
        else:
            print("Registration errors:", form.errors)
            messages.error(request, "Registration failed. Please check the form.")
    else:
        form = UserCreationForm()
    return render(request, "workshop/register.html", {"form": form})


# Profile view
@login_required
def profile(request):
    form = EmailUpdateForm(instance=request.user)
    if request.method == "POST":
        form = EmailUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre adresse e-mail a été mise à jour.")
            return redirect("analyse:profile")
    return render(request, "workshop/profile.html", {"form": form})


#  Vue Générique Exemple : some_view
@login_required
def some_view(request):
    some_id = request.GET.get("file_id")
    if not some_id:
        messages.error(request, "Aucun ID de fichier fourni.")
        return redirect("analyse:home")

    try:
        file = UploadedFile.objects.get(id=some_id, user=request.user)
    except UploadedFile.DoesNotExist:
        messages.error(request, "Fichier non trouvé.")
        return redirect("analyse:home")

    context = {
        "file_id": file.id,
        # Ajoutez d'autres variables de contexte si nécessaire
    }
    return render(request, "template.html", context)


# Upload file view
@login_required
def upload_file(request):
    customization_form = None
    dataframe = None

    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save(commit=False)
            uploaded_file.user = request.user
            uploaded_file.save()

            try:
                # Validation de la taille du fichier
                if uploaded_file.file.size > 10 * 1024 * 1024:  # 10 MB
                    messages.error(request, "File size exceeds 10 MB.")
                    uploaded_file.delete()
                    return redirect("analyse:upload")

                # Traitement du fichier
                file_extension = os.path.splitext(uploaded_file.file.name)[1].lower()
                try:
                    if file_extension in [".xls", ".xlsx"]:
                        dataframe = pd.read_excel(uploaded_file.file.open(), engine="openpyxl")
                    elif file_extension == ".csv":
                        dataframe = pd.read_csv(uploaded_file.file.open())
                    else:
                        raise ValueError("Unsupported file format.")
                except ValueError as ve:
                    messages.error(request, str(ve))
                    uploaded_file.delete()
                    return redirect("analyse:upload")
                except pd.errors.EmptyDataError:
                    messages.error(request, "The file is empty.")
                    uploaded_file.delete()
                    return redirect("analyse:upload")
                except pd.errors.ParserError:
                    messages.error(request, "Error parsing the file.")
                    uploaded_file.delete()
                    return redirect("analyse:upload")
                except Exception as e:
                    logger.error(f"Unexpected error during file processing: {str(e)}")
                    messages.error(request, "An unexpected error occurred. Please try again.")
                    uploaded_file.delete()
                    return redirect("analyse:upload")

                # Stockage des colonnes dans la session pour la personnalisation
                request.session[f"columns_{uploaded_file.id}"] = dataframe.columns.tolist()
                messages.success(request, f"File '{uploaded_file.file.name}' uploaded successfully.")

                # Initialisation du formulaire de personnalisation
                customization_form = AnalysisCustomizationForm(columns=dataframe.columns)
            except Exception as e:
                messages.error(request, f"An error occurred while processing the file: {str(e)}")
                uploaded_file.delete()
                return redirect("analyse:upload")
        else:
            messages.error(request, "Invalid form submission. Please try again.")
            logger.debug(f"Form errors: {form.errors}")


    else:
        form = UploadFileForm()

    return render(
        request,
        "workshop/upload.html",
        {
            "form": form,
            "customization_form": customization_form,
        },
    )


# Results view
@login_required
def results(request, file_id):
    try:
        uploaded_file = get_object_or_404(UploadedFile, id=file_id)
        file_path = uploaded_file.file.path

        # Load the file based on its format
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith((".xls", ".xlsx")):
            df = pd.read_excel(file_path, engine="openpyxl")
        else:
            messages.error(request, "Unsupported file format.")
            return redirect("analyse:upload")

        # Calculate statistics
        stats = calculate_statistics(df)

        # Identify numeric columns
        numeric_cols = df.select_dtypes(include="number").columns
        correlation_results = {}
        for col1 in numeric_cols:
            for col2 in numeric_cols:
                if col1 != col2:
                    corr, _ = pearsonr(df[col1], df[col2])
                    correlation_results[f"{col1} vs {col2}"] = round(corr, 2)

        # Linear regression (optional, based on numeric column availability)
        linear_regression_results = {}
        if len(numeric_cols) >= 2:
            X = df[numeric_cols[0]].values.reshape(-1, 1)
            y = df[numeric_cols[1]].values
            model = LinearRegression()
            model.fit(X, y)
            linear_regression_results = {
                "coefficient": model.coef_[0],
                "intercept": model.intercept_,
            }

        # Handle custom analysis form
        custom_analysis = None
        if request.method == "POST":
            x_column = request.POST.get("x_column")
            y_column = request.POST.get("y_column")
            if x_column in numeric_cols and y_column in numeric_cols:
                corr, _ = pearsonr(df[x_column], df[y_column])
                custom_analysis = {
                    "x_column": x_column,
                    "y_column": y_column,
                    "correlation": round(corr, 2),
                }
            else:
                custom_analysis = {"error": "Invalid columns selected for analysis."}

        # Context for the template
        context = {
            "mean": stats["mean"],
            "median": stats["median"],
            "mode": stats.get("mode", {}),
            "std_dev": stats["std_dev"],
            "file_id": file_id,
            "variance": stats.get("variance", {}),
            "range": stats.get("range", {}),
            "correlation_results": correlation_results,
            "linear_regression_results": linear_regression_results,
            "histograms": stats.get("histograms", {}),
            "custom_analysis": custom_analysis,
            "numeric_cols": numeric_cols,
        }
        return render(request, "workshop/results.html", context)

    except Exception as e:
        logger.error(f"Error in results view: {e}")
        messages.error(request, "An error occurred while processing the file.")
        return redirect("analyse:upload")




# Analysis History view
@login_required
def analysis_history(request):
    try:
        user_analyses = AnalysisHistory.objects.filter(user=request.user).order_by(
            "-upload_date"
        )
        # Vérifie que tous les champs JSON sont bien sérialisables
        for analysis in user_analyses:
            if not isinstance(analysis.mean, dict):
                analysis.mean = {}  # Valeur par défaut
            if not isinstance(analysis.median, dict):
                analysis.median = {}
            # Ajoute d'autres validations si nécessaire
        return render(
            request, "analysis/analysis_history.html", {"user_analyses": user_analyses}
        )
    except Exception as e:
        logger.error(f"Erreur dans analysis_history: {str(e)}")
        messages.error(request, "Une erreur est survenue.")
        return redirect("analyse:home")


# Download CSV
@login_required
def download_csv(request, analysis_id):
    analysis = get_object_or_404(AnalysisHistory, id=analysis_id, user=request.user)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="{analysis.file_name}_analysis.csv"'
    )

    writer = csv.writer(response)
    writer.writerow(["Metric", "Value"])  # Header row
    writer.writerow(["Mean", analysis.mean])
    writer.writerow(["Median", analysis.median])
    writer.writerow(["Mode", analysis.mode])
    writer.writerow(["Variance", analysis.variance])
    writer.writerow(["Standard Deviation", analysis.std_dev])
    writer.writerow(["Range", analysis.range_values])

    return response


# Download PDF
@login_required
def download_pdf(request, analysis_id):
    analysis = get_object_or_404(AnalysisHistory, id=analysis_id, user=request.user)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="{analysis.file_name}_analysis.pdf"'
    )

    pdf = canvas.Canvas(response, pagesize=A4)
    pdf.setTitle(f"Analysis Report - {analysis.file_name}")

    pdf.drawString(100, 800, f"Analysis Report for: {analysis.file_name}")
    pdf.drawString(
        100, 780, f"Upload Date: {analysis.upload_date.strftime('%d %B %Y, %H:%M')}"
    )
    pdf.drawString(100, 750, "Statistics:")
    pdf.drawString(120, 730, f"Mean: {analysis.mean}")
    pdf.drawString(120, 710, f"Median: {analysis.median}")
    pdf.drawString(120, 690, f"Mode: {analysis.mode}")
    pdf.drawString(120, 670, f"Variance: {analysis.variance}")
    pdf.drawString(120, 650, f"Standard Deviation: {analysis.std_dev}")
    pdf.drawString(120, 630, f"Range: {analysis.range_values}")

    y_position = 600
    if analysis.histograms:
        for column, image_path in analysis.histograms.items():
            pdf.drawString(100, y_position, f"Histogram for {column}:")
            pdf.drawImage(
                f"static/{image_path}", 100, y_position - 200, width=400, height=150
            )
            y_position -= 220
    else:
        pdf.drawString(100, y_position, "No histograms available for this analysis.")

    pdf.showPage()
    pdf.save()

    return response

# Data table
@login_required
def data_table_view(request, file_id):
    uploaded_file = get_object_or_404(UploadedFile, id=file_id)
    file_path = uploaded_file.file.path

    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith((".xls", ".xlsx")):
        df = pd.read_excel(file_path, engine="openpyxl")
    else:
        messages.error(request, "Unsupported file format.")
        return redirect("analyse:upload")

    data = df.values.tolist()
    columns = df.columns.tolist()

    return render(
        request, "visualization/data_table.html", {"data": data, "columns": columns}
    )

# correlation and regression visualization
@login_required
def correlation_and_regression_visualization(request, file_id):
    try:
        # Fetch the uploaded file
        uploaded_file = get_object_or_404(UploadedFile, id=file_id, user=request.user)
        file_path = uploaded_file.file.path

        # Check if the file exists on the server
        if not os.path.exists(file_path):
            messages.error(request, "The file is missing from the server.")
            logger.error(f"File not found at path: {file_path}")
            return redirect("analyse:upload")

        # Load the file data into a DataFrame
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path, engine="openpyxl")
        else:
            messages.error(request, "Unsupported file format. Please upload a CSV or Excel file.")
            logger.error(f"Unsupported file format: {file_path}")
            return redirect("analyse:upload")

        # Extract numeric columns
        numeric_columns = df.select_dtypes(include="number").columns.tolist()
        if not numeric_columns:
            messages.error(request, "The file does not contain any numeric columns.")
            logger.error("No numeric columns found in the uploaded file.")
            return redirect("analyse:upload")

        # Generate correlation heatmap and regression plot
        correlation_heatmap, regression_plot = None, None
        try:
            if numeric_columns:
                correlation_heatmap = create_correlation_heatmap(df)
            if len(numeric_columns) >= 2:
                regression_plot = create_regression_plot(df, numeric_columns[0], numeric_columns[1])
        except Exception as e:
            messages.error(request, "An error occurred while generating visualizations.")
            logger.error(f"Error generating visualizations: {e}")
            return redirect("analyse:upload")

        # Render the visualization template
        return render(request, "analysis/correlation_regression.html", {
            "correlation_heatmap": correlation_heatmap,
            "regression_plot": regression_plot,
            "numeric_columns": numeric_columns,
            "file_id": file_id,
        })

    except Exception as e:
        # Catch any unexpected errors
        messages.error(request, "An unexpected error occurred.")
        logger.error(f"Unexpected error in correlation_and_regression_visualization: {e}")
        return redirect("analyse:upload")





# # Correlation and regression analysis
# @login_required
# def correlation_analysis(request, file_id):
#     try:
#         logger.info(f"Récupération du fichier avec ID : {file_id}")
#         # Récupérer le fichier téléchargé
#         uploaded_file = get_object_or_404(UploadedFile, id=file_id, user=request.user)
#         file_path = uploaded_file.file.path
#         logger.info(f"Chemin du fichier : {file_path}")

#         # Charger le fichier dans un DataFrame
#         if file_path.endswith(".csv"):
#             df = pd.read_csv(file_path)
#         elif file_path.endswith((".xls", ".xlsx")):
#             df = pd.read_excel(file_path, engine="openpyxl")
#         else:
#             messages.error(request, "Format de fichier non supporté.")
#             return redirect("analyse:upload")
#         logger.info(f"Fichier chargé avec succès. Dimensions du DataFrame : {df.shape}")

#         # Vérifier la présence de données
#         if df.empty:
#             logger.warning("Le fichier est vide.")
#             messages.error(request, "Le fichier est vide.")
#             return redirect("analyse:upload")

#         # Vérifier la présence de colonnes numériques
#         numeric_columns = df.select_dtypes(include="number").columns
#         logger.info(f"Colonnes numériques trouvées : {list(numeric_columns)}")
#         if len(numeric_columns) < 2:
#             messages.error(
#                 request,
#                 "Le fichier ne contient pas suffisamment de colonnes numériques pour la corrélation.",
#             )
#             return redirect("analyse:upload")













# Visualization avec option
@login_required
def visualization_options(request, file_id):
    uploaded_file = get_object_or_404(UploadedFile, id=file_id)
    file_path = uploaded_file.file.path

    # Load the data
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path, engine="openpyxl")
    else:
        messages.error(request, "Unsupported file format.")
        return redirect("analyse:upload")

    numeric_columns = df.select_dtypes(include="number").columns.tolist()

    # Log numeric columns
    logger.debug(f"Numeric columns: {numeric_columns}")

    if not numeric_columns:
        messages.error(
            request,
            "Votre fichier ne contient pas de colonnes numériques pour la visualisation.",
        )
        return redirect("analyse:upload")

    if request.method == "POST":
        selected_columns = request.POST.getlist("columns")
        visualization_type = request.POST.get("visualization")
        visualization_type = visualization_type.replace('\r\n', '').replace('\n', '')

        # Log selected columns and visualization type
        sanitized_columns = [col.replace('\r\n', '').replace('\n', '') for col in selected_columns]
        logger.debug(f"Selected columns: {sanitized_columns}")
        logger.debug(f"Visualization type: {visualization_type}")

        if not selected_columns:
            messages.error(
                request, "Please select at least one column for visualization."
            )
            return redirect("analyse:visualization_options", file_id=file_id)

        df = df[selected_columns]

        plot_base64 = None
        if visualization_type == "histogram":
            for col in selected_columns:
                plt.figure()
                sns.histplot(df[col], kde=True)
                plt.title(f"Histogram of {col}")
                buffer = BytesIO()
                plt.savefig(buffer, format="png")
                plt.close()
                plot_base64 = base64.b64encode(buffer.getvalue()).decode()
                buffer.close()
        elif visualization_type == "correlation_heatmap":
            correlation_matrix = df.corr()
            plt.figure(figsize=(10, 8))
            sns.heatmap(
                correlation_matrix, annot=True, cmap="coolwarm", vmin=-1, vmax=1
            )
            buffer = BytesIO()
            plt.savefig(buffer, format="png")
            plt.close()
            plot_base64 = base64.b64encode(buffer.getvalue()).decode()
            buffer.close()
        elif visualization_type == "scatter":
            if len(selected_columns) == 2:
                plt.figure()
                sns.scatterplot(x=selected_columns[0], y=selected_columns[1], data=df)
                plt.title(
                    f"Scatter Plot: {selected_columns[0]} vs {selected_columns[1]}"
                )
                buffer = BytesIO()
                plt.savefig(buffer, format="png")
                plt.close()
                plot_base64 = base64.b64encode(buffer.getvalue()).decode()
                buffer.close()
            else:
                messages.error(request, "Scatter plots require exactly two columns.")
        elif visualization_type == "boxplot":
            for col in selected_columns:
                plt.figure()
                sns.boxplot(data=df[col])
                plt.title(f"Box Plot of {col}")
                buffer = BytesIO()
                plt.savefig(buffer, format="png")
                plt.close()
                plot_base64 = base64.b64encode(buffer.getvalue()).decode()
                buffer.close()
        elif visualization_type == "barchart":
            for col in selected_columns:
                plt.figure()
                df[col].value_counts().plot(kind="bar")
                plt.title(f"Bar Chart of {col}")
                buffer = BytesIO()
                plt.savefig(buffer, format="png")
                plt.close()
                plot_base64 = base64.b64encode(buffer.getvalue()).decode()
                buffer.close()
        elif visualization_type == "kde_plot":
            for col in selected_columns:
                plt.figure()
                sns.kdeplot(df[col], shade=True)
                plt.title(f"KDE Plot of {col}")
                buffer = BytesIO()
                plt.savefig(buffer, format="png")
                plt.close()
                plot_base64 = base64.b64encode(buffer.getvalue()).decode()
                buffer.close()
        elif visualization_type == "violin_plot":
            if len(selected_columns) == 1:
                plt.figure()
                sns.violinplot(data=df[selected_columns[0]])
                plt.title(f"Violin Plot of {selected_columns[0]}")
                buffer = BytesIO()
                plt.savefig(buffer, format="png")
                plt.close()
                plot_base64 = base64.b64encode(buffer.getvalue()).decode()
                buffer.close()

        return render(
            request,
            "visualization/visualization_result.html",
            {
                "plot_base64": plot_base64,
                "file_id": file_id,
                "visualization_type": visualization_type,
            },
        )

    return render(
        request,
        "visualization/visualization_options.html",
        {"uploaded_file": uploaded_file, "columns": numeric_columns},
    )


@login_required
def customize_analysis(request, file_id):
    uploaded_file = get_object_or_404(UploadedFile, id=file_id, user=request.user)
    file_extension = uploaded_file.file.name.split(".")[-1].lower()

    # Load data
    if file_extension == "csv":
        df = pd.read_csv(uploaded_file.file.path)
    else:
        df = pd.read_excel(uploaded_file.file.path, engine="openpyxl")

    if request.method == "POST":
        form = AnalysisCustomizationForm(request.POST, columns=df.columns)
        if form.is_valid():
            selected_columns = form.cleaned_data["columns"]
            selected_metrics = {
                "mean": form.cleaned_data["mean"],
                "median": form.cleaned_data["median"],
                "mode": form.cleaned_data["mode"],
                "variance": form.cleaned_data["variance"],
                "std_dev": form.cleaned_data["std_dev"],
            }

            # Filter DataFrame to selected columns
            df_filtered = df[selected_columns]

            # Perform selected analyses
            results = {}
            if selected_metrics["mean"]:
                results["mean"] = df_filtered.mean().to_dict()
            if selected_metrics["median"]:
                results["median"] = df_filtered.median().to_dict()
            if selected_metrics["mode"]:
                results["mode"] = df_filtered.mode().iloc[0].to_dict()
            if selected_metrics["variance"]:
                results["variance"] = df_filtered.var().to_dict()
            if selected_metrics["std_dev"]:
                results["std_dev"] = df_filtered.std().to_dict()

            # Save results in the database
            analysis = AnalysisHistory(
                user=request.user,
                file_name=uploaded_file.file.name,
                uploaded_file=uploaded_file,
                mean=results.get("mean"),
                median=results.get("median"),
                mode=results.get("mode"),
                variance=results.get("variance"),
                std_dev=results.get("std_dev"),
                range_values=(df_filtered.max() - df_filtered.min()).to_dict(),
                status=AnalysisHistory.Status.COMPLETED,
            )
            analysis.save()
            return render(
                request,
                "analysis/analysis_results.html",
                {"results": results, "file_name": uploaded_file.file.name},
            )
    else:
        form = AnalysisCustomizationForm(columns=df.columns)

    return render(
        request, "analysis/customize_analysis.html", {"form": form, "file_id": file_id}
    )


# Preview file view
@login_required
def preview_file(request, file_id):
    uploaded_file = get_object_or_404(UploadedFile, id=file_id)
    file_path = uploaded_file.file.path

    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith((".xls", ".xlsx")):
        df = pd.read_excel(file_path, engine="openpyxl")
    else:
        messages.error(request, "Unsupported file format.")
        return redirect("analyse:upload")

    data_html = df.to_html(classes="table table-striped table-bordered", index=False)

    return render(
        request, "preview/preview.html", {"data": data_html, "file_id": file_id}
    )

# Delete analysis
@login_required
def delete_analysis(request, analysis_id):
    analysis = get_object_or_404(AnalysisHistory, id=analysis_id, user=request.user)
    analysis.delete()
    messages.success(
        request, f"L'analyse pour le fichier {analysis.file_name} a été supprimée."
    )
    return redirect("analyse:analysis_history")


# Caclcul de probabilities
@login_required
def probability_analysis(request, file_id):
    uploaded_file = get_object_or_404(UploadedFile, id=file_id)
    file_path = uploaded_file.file.path

    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith((".xls", ".xlsx")):
        df = pd.read_excel(file_path, engine="openpyxl")
    else:
        messages.error(request, "Unsupported file format.")
        return redirect("analyse:upload")

    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    probabilities = {}

    if request.method == "POST":
        selected_column = request.POST.get("column")
        range_start = float(request.POST.get("range_start"))
        range_end = float(request.POST.get("range_end"))

        if selected_column in numeric_columns:
            column_data = df[selected_column].dropna()
            total_count = len(column_data)
            in_range_count = column_data.between(range_start, range_end).sum()
            probabilities[selected_column] = in_range_count / total_count

    return render(
        request,
        "analysis/probability_analysis.html",
        {"numeric_columns": numeric_columns, "probabilities": probabilities},
    )


# Les graphiques interactifs avec ploty


@login_required
def interactive_visualization(request, file_id):
    uploaded_file = get_object_or_404(UploadedFile, id=file_id)
    file_path = uploaded_file.file.path

    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith((".xls", ".xlsx")):
        df = pd.read_excel(file_path, engine="openpyxl")
    else:
        messages.error(request, "Unsupported file format.")
        return redirect("analyse:upload")

    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    plot_html = None

    if request.method == "POST":
        x_column = request.POST.get("x_column")
        y_column = request.POST.get("y_column")
        chart_type = request.POST.get("chart_type")

        if x_column in numeric_columns and y_column in numeric_columns:
            if chart_type == "scatter":
                fig = px.scatter(df, x=x_column, y=y_column, title="Scatter Plot")
            elif chart_type == "line":
                fig = px.line(df, x=x_column, y=y_column, title="Line Chart")
            elif chart_type == "bar":
                fig = px.bar(df, x=x_column, y=y_column, title="Bar Chart")

            plot_html = fig.to_html(full_html=False)

    return render(
        request,
        "visualization/interactive_visualization.html",
        {"numeric_columns": numeric_columns, "plot_html": plot_html},
    )


@login_required
def download_pdf_with_plotly(request, analysis_id):
    analysis = get_object_or_404(AnalysisHistory, id=analysis_id, user=request.user)

    # Example Plotly figure
    fig = px.bar(x=["A", "B", "C"], y=[10, 20, 30], title="Sample Plot")
    plot_image = to_image(fig, format="png")

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="{analysis.file_name}_interactive_analysis.pdf"'
    )

    pdf = canvas.Canvas(response, pagesize=A4)
    pdf.setTitle(f"Analysis Report - {analysis.file_name}")
    pdf.drawString(100, 800, "Interactive Analysis Report")
    pdf.drawImage(plot_image, 100, 600, width=400, height=200)
    pdf.showPage()
    pdf.save()

    return response


# Regression lineaire
@login_required
def linear_regression_analysis(request, file_id):
    uploaded_file = get_object_or_404(UploadedFile, id=file_id)
    file_path = uploaded_file.file.path

    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith((".xls", ".xlsx")):
        df = pd.read_excel(file_path, engine="openpyxl")
    else:
        messages.error(request, "Unsupported file format.")
        return redirect("analyse:upload")

    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    model_results = None

    if request.method == "POST":
        target_column = request.POST.get("target_column")
        features = request.POST.getlist("features")

        if target_column in numeric_columns and all(
            f in numeric_columns for f in features
        ):
            X = df[features]
            y = df[target_column]

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            model = LinearRegression()
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)

            model_results = {
                "coefficients": dict(zip(features, model.coef_)),
                "intercept": model.intercept_,
                "mean_squared_error": mean_squared_error(y_test, predictions),
            }

    return render(
        request,
        "linear_regression_analysis.html",
        {"numeric_columns": numeric_columns, "model_results": model_results},
    )


# Slice and indexing functions:
def slicing_and_indexing(request):
    global dataframe
    is_file_uploaded = dataframe is not None

    if not is_file_uploaded:
        return render(
            request,
            "visualization/slicing_indexing.html",
            {
                "is_file_uploaded": is_file_uploaded,
                "error": "No file uploaded yet. Please upload a CSV file first.",
            },
        )

    if request.method == "POST":
        # Obtenir les paramètres de la requête
        row_start = int(request.POST.get("row_start", 0))
        row_end = int(request.POST.get("row_end", len(dataframe) - 1))
        selected_cols = request.POST.getlist("columns")

        # Filtrer les données
        sliced_df = dataframe.loc[row_start:row_end, selected_cols]

        # Calcul des statistiques
        selected_stats = request.POST.getlist("stats")
        stats = {}
        if selected_stats:
            numeric_sliced_df = sliced_df.select_dtypes(include=[np.number])
            if "moyenne" in selected_stats:
                stats["Moyenne"] = numeric_sliced_df.mean().to_dict()
            if "mediane" in selected_stats:
                stats["Médiane"] = numeric_sliced_df.median().to_dict()
            if "variance" in selected_stats:
                stats["Variance"] = numeric_sliced_df.var().to_dict()
            if "std_dev" in selected_stats:
                stats["Écart Type"] = numeric_sliced_df.std().to_dict()
            if "range" in selected_stats:
                stats["Étendue"] = (
                    numeric_sliced_df.max() - numeric_sliced_df.min()
                ).to_dict()

        # Génération des graphiques
        plots = []
        for col in selected_cols:
            if col in sliced_df.select_dtypes(include=[np.number]).columns:
                fig, ax = plt.subplots()
                sns.histplot(sliced_df[col], kde=True, ax=ax)
                ax.set_title(f"Distribution de {col}")
                ax.set_xlabel(col)
                ax.set_ylabel("Fréquence")
                buffer = BytesIO()
                plt.savefig(buffer, format="png")
                buffer.seek(0)
                plots.append(base64.b64encode(buffer.getvalue()).decode())
                buffer.close()
                plt.close(fig)

        # Retourner les résultats
        return render(
            request,
            "visualization/slicing_indexing.html",
            {
                "columns": dataframe.columns,
                "row_numbers": range(len(dataframe)),
                "sliced_data": sliced_df.to_html(classes="table table-striped"),
                "stats": stats,
                "plots": plots,
                "is_file_uploaded": is_file_uploaded,
            },
        )

    # Retourner la vue initiale
    return render(
        request,
        "visualization/slicing_indexing.html",
        {
            "columns": dataframe.columns,
            "row_numbers": range(len(dataframe)),
            "data": dataframe.to_html(classes="table table-striped"),
            "is_file_uploaded": is_file_uploaded,
        },
    )


# Handle missing values
@login_required
def missing_values_analysis(request, file_id):
    uploaded_file = get_object_or_404(UploadedFile, id=file_id)
    df = pd.read_csv(uploaded_file.file.path)

    if request.method == "POST":
        strategy = request.POST.get("missing_value_strategy")
        if strategy == "drop":
            df = df.dropna()
        elif strategy == "mean":
            df = df.fillna(df.mean())
        elif strategy == "median":
            df = df.fillna(df.median())

        # Save the cleaned data back
        df.to_csv(uploaded_file.file.path, index=False)
        messages.success(request, "Missing values handled successfully!")
        return redirect("analyse:data_preview", file_id=file_id)

    return render(
        request,
        "analysis/missing_values.html",
        {"file_id": file_id, "columns": df.columns},
    )


# Data preview and Editing
@csrf_exempt
@login_required
def update_cell(request, file_id):
    if request.method == "POST":
        uploaded_file = get_object_or_404(UploadedFile, id=file_id)
        df = pd.read_csv(uploaded_file.file.path)

        row_index = int(request.POST.get("row"))
        column_name = request.POST.get("column")
        new_value = request.POST.get("value")

        df.at[row_index, column_name] = new_value
        df.to_csv(uploaded_file.file.path, index=False)
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error", "message": "Invalid request."})



# Delete file uploaded
@require_http_methods(["DELETE"])
@login_required
def delete_file(request, file_id):
    try:
        uploaded_file = get_object_or_404(UploadedFile, id=file_id, user=request.user)
        uploaded_file.delete()
        return JsonResponse({"status": "success"})
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        return JsonResponse({"status": "error", "message": "An internal error has occurred."}, status=500)
#Houssam aoun (Sa partie)
# Example View for Correlation Analysis
# @login_required
# def correlation_view(request, file_id):
#     uploaded_file = get_object_or_404(UploadedFile, id=file_id, user=request.user)
#     file_path = uploaded_file.file.path

#     try:
#         if file_path.endswith(".csv"):
#             df = pd.read_csv(file_path)
#         elif file_path.endswith(".xlsx"):
#             df = pd.read_excel(file_path, engine="openpyxl")
#         else:
#             raise ValueError("Unsupported file format.")
        
#         col1 = request.GET.get("col1")
#         col2 = request.GET.get("col2")
#         result = correlation_analysis(df, col1, col2)

#     except Exception as e:
#         messages.error(request, f"Error: {str(e)}")
#         return redirect("analyse:upload")

#     return JsonResponse(result)

# Example View for Interactive Visualization
def visualization_view(request):
    data = pd.read_csv("path_to_your_csv_file.csv")
    x = request.GET.get("x")
    y = request.GET.get("y")
    chart_type = request.GET.get("chart_type", "scatter")
    html_chart = interactive_visualization(data, x, y, chart_type)
    return HttpResponse(html_chart)

# Example View for Exporting CSV
@login_required
def export_csv_view(request, file_id):
    uploaded_file = get_object_or_404(UploadedFile, id=file_id, user=request.user)
    file_path = uploaded_file.file.path

    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path, engine="openpyxl")
        else:
            raise ValueError("Unsupported file format.")

        csv_buffer = download_csv(df)

    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect("analyse:upload")

    response = HttpResponse(csv_buffer, content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=export.csv"
    return response

# Example View for Exporting PDF
def export_pdf_view(request):
    data = pd.read_csv("path_to_your_csv_file.csv")
    pdf = download_pdf(data)
    response = HttpResponse(pdf.output(dest="S").encode("latin1"), content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=output.pdf"
    return response

# view of interactive visualization
@login_required
def interactive_visualization_view(request, file_id):
    uploaded_file = get_object_or_404(UploadedFile, id=file_id, user=request.user)
    file_path = uploaded_file.file.path

    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path, engine="openpyxl")
        else:
            raise ValueError("Unsupported file format.")
        
        x = request.GET.get("x")
        y = request.GET.get("y")
        chart_type = request.GET.get("chart_type", "scatter")
        html_chart = interactive_visualization(df, x, y, chart_type)

    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect("analyse:upload")

    return HttpResponse(html_chart)

# Fonction loi_probability
def loi_probability(request):
    """
    View to calculate probabilities for different distributions and display results on the same page.
    """
    result = None
    error = None

    if request.method == 'POST':
        distribution = request.POST.get('distribution')  # Type of distribution
        params = {}  # Initialize an empty dictionary for parameters

        try:
            # Extract parameters based on the distribution
            if distribution == 'uniform_discrete':
                params = {
                    'a': float(request.POST.get('a', 0)),
                    'b': float(request.POST.get('b', 1)),
                    'x': float(request.POST.get('x', 0)),
                }
                a, b, x = params['a'], params['b'], params['x']
                if a > b:
                    raise ValueError("For uniform discrete distribution, 'a' must be less than 'b'.")
                result = 1 / (b - a + 1) if a <= x <= b else 0

            elif distribution == 'binomial':
                params = {
                    'n': int(request.POST.get('n', 1)),
                    'p': float(request.POST.get('p', 0.5)),
                    'k': int(request.POST.get('k', 0)),
                }
                n, p, k = params['n'], params['p'], params['k']
                if not (0 <= p <= 1):
                    raise ValueError("For binomial distribution, 'p' must be between 0 and 1.")
                if k < 0 or k > n:
                    raise ValueError("For binomial distribution, 'k' must be between 0 and 'n'.")
                result = stats.binom.pmf(k, n, p)

            elif distribution == 'bernoulli':
                params = {
                    'p': float(request.POST.get('p', 0.5)),
                    'x': int(request.POST.get('x', 0)),
                }
                p, x = params['p'], params['x']
                if not (0 <= p <= 1):
                    raise ValueError("For Bernoulli distribution, 'p' must be between 0 and 1.")
                if x not in [0, 1]:
                    raise ValueError("For Bernoulli distribution, 'x' must be 0 or 1.")
                result = stats.bernoulli.pmf(x, p)

            elif distribution == 'poisson':
                params = {
                    'lambda': float(request.POST.get('lambda', 1)),
                    'k': int(request.POST.get('k', 0)),
                }
                lam, k = params['lambda'], params['k']
                if lam <= 0:
                    raise ValueError("For Poisson distribution, 'lambda' must be greater than 0.")
                result = stats.poisson.pmf(k, lam)

            elif distribution == 'uniform_continuous':
                params = {
                    'a': float(request.POST.get('a', 0)),
                    'b': float(request.POST.get('b', 1)),
                    'x': float(request.POST.get('x', 0)),
                }
                a, b, x = params['a'], params['b'], params['x']
                if a >= b:
                    raise ValueError("For uniform continuous distribution, 'a' must be less than 'b'.")
                result = 1 / (b - a) if a <= x <= b else 0

            elif distribution == 'normal':
                params = {
                    'mu': float(request.POST.get('mu', 0)),
                    'sigma': float(request.POST.get('sigma', 1)),
                    'x': float(request.POST.get('x', 0)),
                }
                mu, sigma, x = params['mu'], params['sigma'], params['x']
                if sigma <= 0:
                    raise ValueError("For normal distribution, 'sigma' must be greater than 0.")
                result = stats.norm.pdf(x, mu, sigma)

            elif distribution == 'exponential':
                params = {
                    'lambda': float(request.POST.get('lambda', 1)),
                    'x': float(request.POST.get('x', 0)),
                }
                lam, x = params['lambda'], params['x']
                if lam <= 0:
                    raise ValueError("For exponential distribution, 'lambda' must be greater than 0.")
                result = lam * np.exp(-lam * x) if x >= 0 else 0

            else:
                raise ValueError("Invalid distribution selected.")

        except ValueError as ve:
            error = str(ve)
        except Exception as e:
            error = f"An unexpected error occurred: {str(e)}"

    return render(request, 'analysis/loi_probability.html', {
        'result': result,
        'error': error,
    })