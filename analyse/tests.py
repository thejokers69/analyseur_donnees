# /Users/thejoker/Documents/GitHub/analyseur_donnees/analyse/tests.py

import os
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from analyse.models import UploadedFile
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import UploadedFile, AnalysisHistory
from .utils import calculate_statistics
import pandas as pd


class AnalyseurTests(TestCase):
    def setUp(self):
        # Create a user and log in
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")

        # Create a temporary file
        self.test_file = SimpleUploadedFile(
            "test.csv", b"col1,col2\n1,2\n3,4", content_type="text/csv"
        )
        self.uploaded_file = UploadedFile.objects.create(
            user=self.user,
            file=self.test_file,
        )

    def tearDown(self):
        # Clean up the created files
        if self.uploaded_file.file:
            self.uploaded_file.file.delete()

    def test_results_view(self):
        # Test the results view
        url = reverse("analyse:results", args=[self.uploaded_file.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Moyenne")

    def test_visualization_options(self):
        # Test the visualization options view
        url = reverse("analyse:visualization_options", args=[self.uploaded_file.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sélectionner les Colonnes")


class VisualizationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")
        self.test_file = SimpleUploadedFile(
            "test.csv", b"col1,col2\n1,10\n2,20\n3,30", content_type="text/csv"
        )
        self.uploaded_file = UploadedFile.objects.create(
            user=self.user, file=self.test_file
        )

    def test_visualization_histogram(self):
        url = reverse("analyse:visualization_options", args=[self.uploaded_file.id])
        response = self.client.post(
            url, {"columns": ["col1"], "visualization": "histogram"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Résultat de la Visualisation")

    def test_visualization_heatmap(self):
        url = reverse("analyse:visualization_options", args=[self.uploaded_file.id])
        response = self.client.post(
            url, {"columns": ["col1", "col2"], "visualization": "correlation_heatmap"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Résultat de la Visualisation")


class UtilsTest(TestCase):
    def test_calculate_statistics(self):
        data = {"A": [1, 2, 3, 4, 5], "B": [5, 6, 7, 8, 9]}
        df = pd.DataFrame(data)
        stats = calculate_statistics(df)
        self.assertEqual(stats["mean"]["A"], 3)
        self.assertEqual(stats["range"]["B"], 4)


class AnalysisViewsTest(TestCase):
    def test_upload_file_view(self):
        response = self.client.get("/upload/")
        self.assertEqual(response.status_code, 200)

    def test_linear_regression_view(self):
        response = self.client.get("/analysis/linear_regression/1/")
        self.assertEqual(response.status_code, 200)


class UploadFileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")

    def test_upload_csv_file(self):
        url = reverse("analyse:upload")
        test_file = SimpleUploadedFile(
            "test.csv", b"col1,col2\n1,2\n3,4", content_type="text/csv"
        )
        response = self.client.post(url, {"file": test_file})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "uploaded successfully")

    def test_upload_invalid_file_format(self):
        url = reverse("analyse:upload")
        test_file = SimpleUploadedFile(
            "test.txt", b"Invalid content", content_type="text/plain"
        )
        response = self.client.post(url, {"file": test_file})
        self.assertContains(response, "Unsupported file format", status_code=400)


class DataAnalysisTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")
        self.test_file = SimpleUploadedFile(
            "test.csv", b"col1,col2\n10,20\n30,40", content_type="text/csv"
        )
        self.uploaded_file = UploadedFile.objects.create(
            user=self.user, file=self.test_file
        )

    def test_results_view(self):
        url = reverse("analyse:results", args=[self.uploaded_file.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Moyenne")
        self.assertContains(response, "Médiane")


class CorrelationAndRegressionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")
        self.test_file = SimpleUploadedFile(
            "test.csv", b"col1,col2\n1,2\n2,4\n3,6", content_type="text/csv"
        )
        self.uploaded_file = UploadedFile.objects.create(
            user=self.user, file=self.test_file
        )

    def test_correlation_analysis(self):
        url = reverse("analyse:correlation_analysis", args=[self.uploaded_file.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Correlation Matrix")

    def test_linear_regression(self):
        url = reverse(
            "analyse:linear_regression_analysis", args=[self.uploaded_file.id]
        )
        response = self.client.post(
            url, {"target_column": "col2", "features": ["col1"]}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Résultats de la régression linéaire")


class MissingValuesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")
        self.test_file = SimpleUploadedFile(
            "test.csv", b"col1,col2\n1,\n2,4\n,6", content_type="text/csv"
        )
        self.uploaded_file = UploadedFile.objects.create(
            user=self.user, file=self.test_file
        )

    def test_handle_missing_values_drop(self):
        url = reverse("analyse:missing_values", args=[self.uploaded_file.id])
        response = self.client.post(url, {"missing_value_strategy": "drop"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Missing values handled successfully")

    def test_handle_missing_values_fill_mean(self):
        url = reverse("analyse:missing_values", args=[self.uploaded_file.id])
        response = self.client.post(url, {"missing_value_strategy": "mean"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Missing values handled successfully")


def test_coefficient_of_variation(self):
    url = reverse("analyse:results", args=[self.uploaded_file.id])
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "Coefficient de Variation")


class FileDownloadTest(TestCase):
    def test_download_csv(self):
        url = reverse("analyse:download_csv", args=[1])  # Replace 1 with a valid analysis ID
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")

    def test_download_pdf(self):
        url = reverse("analyse:download_pdf", args=[1])  # Replace 1 with a valid analysis ID
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
