# /Users/thejoker/Documents/GitHub/analyseur_donnees/analyse/views.py

import matplotlib

matplotlib.use("Agg")
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.contrib.auth.models import User
from .forms import EmailUpdateForm, UploadFileForm, AnalysisCustomizationForm
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import UploadedFile, AnalysisHistory
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
import os
import csv
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.conf import settings
from .utils import send_mailgun_email


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
    return render(request, "login.html", {"form": form})


# Homepage
def home(request):
    uploaded_files = None
    if request.user.is_authenticated:
        uploaded_files = UploadedFile.objects.filter(user=request.user)
    return render(request, "home.html", {"uploaded_files": uploaded_files})


# Register
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
    return render(request, "register.html", {"form": form})


# Profile Registration
@login_required
def profile(request):
    form = EmailUpdateForm(instance=request.user)
    if request.method == "POST":
        form = EmailUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre adresse e-mail a été mise à jour.")
            return redirect("profile")
    return render(request, "profile.html", {"form": form})


# def profile(request):
#     if request.method == "POST":
#         form = EmailUpdateForm(request.POST, instance=request.user)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Your email address has been updated.")
#             return redirect("analyse:profile")
#     else:
#         form = EmailUpdateForm(instance=request.user)
#     return render(request, "profile.html", {"form": form})


# Generate Histograms for each column
def generate_histogram(df, column_name):
    plt.figure()
    df[column_name].hist()
    plt.title(f"Histogram of {column_name}")
    plt.xlabel(column_name)
    plt.ylabel("Frequency")
    file_path = f"static/{column_name}_histogram.png"
    plt.savefig(file_path)
    plt.close()
    return file_path


# Upload file
@login_required
def upload_file(request):
    customization_form = None
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save()
            file_extension = os.path.splitext(uploaded_file.file.name)[1].lower()

            if file_extension in [".xls", ".xlsx"]:
                df = pd.read_excel(uploaded_file.file.path, engine="openpyxl")
            elif file_extension == ".csv":
                df = pd.read_csv(uploaded_file.file.path)
            else:
                messages.error(
                    request,
                    "Unsupported file format. Please upload an Excel or CSV file.",
                )
                return redirect("analyse:upload")
            customization_form = AnalysisCustomizationForm(columns=df.columns)
            if customization_form.is_valid():
                selected_columns = customization_form.cleaned_data["columns"]
                selected_stats = {
                    "mean": customization_form.cleaned_data["mean"],
                    "median": customization_form.cleaned_data["median"],
                    "mode": customization_form.cleaned_data["mode"],
                    "variance": customization_form.cleaned_data["variance"],
                    "std_dev": customization_form.cleaned_data["std_dev"],
                }

                df = df[selected_columns]

                stats_results = {}
                if selected_stats["mean"]:
                    stats_results["mean"] = (
                        df.select_dtypes(include="number").mean().to_dict()
                    )
                if selected_stats["median"]:
                    stats_results["median"] = df.median().to_dict()
                if selected_stats["mode"]:
                    stats_results["mode"] = df.mode().iloc[0].to_dict()
                if selected_stats["variance"]:
                    stats_results["variance"] = df.var().to_dict()
                if selected_stats["std_dev"]:
                    stats_results["std_dev"] = df.std().to_dict()

                analysis = AnalysisHistory(
                    user=request.user,
                    file_name=uploaded_file.file.name,
                    uploaded_file=uploaded_file,
                    mean=stats_results.get("mean"),
                    median=stats_results.get("median"),
                    mode=stats_results.get("mode"),
                    variance=stats_results.get("variance"),
                    std_dev=stats_results.get("std_dev"),
                )
                analysis.save()

                send_analysis_completed_email(
                    request.user.email, uploaded_file.file.name
                )

                messages.success(
                    request, f"Analysis of {uploaded_file.file.name} completed."
                )
                return redirect("analyse:analysis_history")
    else:
        form = UploadFileForm()
    return render(
        request, "upload.html", {"form": form, "customization_form": customization_form}
    )


# Results
def results(request, file_id):
    uploaded_file = get_object_or_404(UploadedFile, id=file_id)
    file_path = uploaded_file.file.path

    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith((".xls", ".xlsx")):
        df = pd.read_excel(file_path, engine="openpyxl")
    else:
        messages.error(request, "Unsupported file format.")
        return redirect("analyse:upload")

    mean = df.mean()
    median = df.median()
    mode = df.mode().iloc[0] if not df.mode().empty else None
    variance = df.var()
    std_dev = df.std()
    range_values = df.max() - df.min()

    context = {
        "mean": mean.to_dict(),
        "median": median.to_dict(),
        "mode": mode.to_dict() if mode is not None else None,
        "variance": variance.to_dict(),
        "std_dev": std_dev.to_dict(),
        "range_values": range_values.to_dict(),
    }
    return render(request, "results.html", context)


# Analysis History
@login_required
def analysis_history(request):
    user_analyses = AnalysisHistory.objects.filter(user=request.user).order_by(
        "-upload_date"
    )
    return render(request, "analysis_history.html", {"user_analyses": user_analyses})


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


# Notifications by email address and password
def send_analysis_completed_email(recipient_email, file_name):
    subject = "Analysis Completed"
    message = f"Your analysis for {file_name} is complete. You can download the results from your dashboard."
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [recipient_email]

    send_mail(subject, message, email_from, recipient_list)
    send_mailgun_email(subject, message, recipient_email)


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

    return render(request, "data_table.html", {"data": data, "columns": columns})


# Correlation and regression analysis
@login_required
def correlation_analysis(request, file_id):
    uploaded_file = get_object_or_404(UploadedFile, id=file_id)
    file_path = uploaded_file.file.path

    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith((".xls", ".xlsx")):
        df = pd.read_excel(file_path, engine="openpyxl")
    else:
        messages.error(request, "Unsupported file format.")
        return redirect("analyse:upload")

    correlation_matrix = df.corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", vmin=-1, vmax=1)
    heatmap_buffer = BytesIO()
    plt.savefig(heatmap_buffer, format="png")
    plt.close()
    heatmap_base64 = base64.b64encode(heatmap_buffer.getvalue()).decode()
    heatmap_buffer.close()

    reg_plots = []
    for i in range(len(correlation_matrix.columns)):
        for j in range(i + 1, len(correlation_matrix.columns)):
            col1, col2 = correlation_matrix.columns[i], correlation_matrix.columns[j]
            if abs(correlation_matrix.loc[col1, col2]) > 0.7:
                plt.figure(figsize=(6, 4))
                sns.regplot(x=col1, y=col2, data=df)
                plt.title(f"Regression between {col1} and {col2}")

                buffer = BytesIO()
                plt.savefig(buffer, format="png")
                plt.close()
                plot_base64 = base64.b64encode(buffer.getvalue()).decode()
                buffer.close()

                reg_plots.append(
                    (f"Correlation between {col1} and {col2}", plot_base64)
                )
    context = {
        "correlation_matrix": correlation_matrix.to_html(classes="table table-striped"),
        "heatmap_base64": heatmap_base64,
        "reg_plots": reg_plots,
        "file_id": file_id,
    }

    return render(
        request,
        "correlation_analysis.html",
        context,  # Use the updated context
    )


@login_required
def visualization_options(request, file_id):
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

    if not numeric_columns:
        messages.error(
            request,
            "No numeric columns available for visualization in the uploaded file.",
        )
        return redirect("analyse:upload")

    if request.method == "POST":
        selected_columns = request.POST.getlist("columns")
        visualization_type = request.POST.get("visualization")

        if visualization_type == "scatter" and len(selected_columns) != 2:
            messages.error(request, "Scatter plots require exactly two columns.")
            return redirect("analyse:visualization_options", file_id=file_id)

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

        return render(
            request,
            "visualization_result.html",
            {"plot_base64": plot_base64, "file_id": file_id},  # Pass file_id here
        )

    # Render the visualization options form
    return render(
        request,
        "visualization_options.html",
        {"uploaded_file": uploaded_file, "numeric_columns": numeric_columns},
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

            send_analysis_completed_email(request.user.email, uploaded_file.file.name)

            return render(
                request,
                "analysis_results.html",
                {"results": results, "file_name": uploaded_file.file.name},
            )
    else:
        form = AnalysisCustomizationForm(columns=df.columns)

    return render(
        request, "customize_analysis.html", {"form": form, "file_id": file_id}
    )
