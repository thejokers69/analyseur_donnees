# /Users/thejoker/Documents/GitHub/analyseur_donnees/analyse/tests.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from analyse.models import UploadedFile, AnalysisHistory
import pandas as pd
import os

class AnalyseurTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="password")
        cls.test_file = SimpleUploadedFile(
            "test.csv", b"col1,col2\n1,10\n2,20\n3,30", content_type="text/csv"
        )

    def setUp(self):
        self.client.login(username="testuser", password="password")
        self.uploaded_file = UploadedFile.objects.create(
            user=self.user, file=self.test_file
        )

    def test_home_view(self):
        """Test home view accessibility."""
        response = self.client.get(reverse("analyse:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Uploaded Files")

    def test_upload_file(self):
        """Test the file upload process."""
        url = reverse("analyse:upload")
        response = self.client.post(url, {"file": self.test_file})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "uploaded successfully")
        self.assertTrue(UploadedFile.objects.filter(user=self.user).exists())

    def test_results_view(self):
        """Test the results view with statistics calculation."""
        url = reverse("analyse:results", args=[self.uploaded_file.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Moyenne")
        self.assertContains(response, "Médiane")

    def test_visualization_options(self):
        """Test visualization options availability."""
        url = reverse("analyse:visualization_options", args=[self.uploaded_file.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sélectionner les Colonnes")

    def test_missing_values_handling(self):
        """Test handling of missing values with different strategies."""
        # Create a file with missing values
        missing_data_file = SimpleUploadedFile(
            "missing.csv",
            b"col1,col2\n1,\n2,4\n,6",
            content_type="text/csv",
        )
        uploaded_file = UploadedFile.objects.create(
            user=self.user, file=missing_data_file
        )
        url = reverse("analyse:missing_values", args=[uploaded_file.id])

        # Test dropping missing values
        response = self.client.post(url, {"missing_value_strategy": "drop"})
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue("Missing values handled successfully!" in response.content.decode())

        # Test filling with mean
        response = self.client.post(url, {"missing_value_strategy": "mean"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue("Missing values handled successfully!" in response.content.decode())

    def test_download_csv(self):
        """Test CSV download functionality."""
        url = reverse("analyse:download_csv", args=[self.uploaded_file.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")

    def test_download_pdf(self):
        """Test PDF download functionality."""
        url = reverse("analyse:download_pdf", args=[self.uploaded_file.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")

    # def test_correlation_analysis(self):
    #     """Test correlation analysis view."""
    #     url = reverse("analyse:correlation_analysis", args=[self.uploaded_file.id])
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, "Correlation Matrix")

    def test_linear_regression_analysis(self):
        """Test linear regression functionality."""
        url = reverse("analyse:linear_regression_analysis", args=[self.uploaded_file.id])
        response = self.client.post(
            url, {"target_column": "col2", "features": ["col1"]}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Résultats de la régression linéaire")

    def test_delete_analysis(self):
        """Test deleting an analysis."""
        # Create a dummy analysis history
        analysis = AnalysisHistory.objects.create(
            user=self.user,
            file_name="test.csv",
            mean={"col1": 2, "col2": 20},
        )
        url = reverse("analyse:delete_analysis", args=[analysis.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(AnalysisHistory.objects.filter(id=analysis.id).exists())

    def test_invalid_file_upload(self):
        """Test handling of invalid file uploads."""
        invalid_file = SimpleUploadedFile(
            "test.txt", b"This is not a CSV or Excel file.", content_type="text/plain"
        )
        url = reverse("analyse:upload")
        response = self.client.post(url, {"file": invalid_file})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Unsupported file format")

    def test_unauthenticated_access(self):
        """Test views requiring login when not authenticated."""
        self.client.logout()
        protected_urls = [
            reverse("analyse:home"),
            reverse("analyse:upload"),
            reverse("analyse:results", args=[1]),
        ]
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Redirect to login page