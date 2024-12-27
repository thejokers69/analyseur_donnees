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

class VisualizationTests(TestCase):
    def setUp(self):
        # Create a user and log in
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")

        # Create a temporary file
        self.test_file = SimpleUploadedFile(
            "test.csv", b"col1,col2\n10,20\n30,40", content_type="text/csv"
        )
        self.uploaded_file = UploadedFile.objects.create(
            user=self.user,
            file=self.test_file,
        )

    def tearDown(self):
        # Clean up the created files
        if self.uploaded_file.file:
            self.uploaded_file.file.delete()

    def test_generate_histogram(self):
        # Example test for generating a histogram
        data = [1, 2, 3, 4, 5]
        plt.figure()
        plt.hist(data)
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        plt.close()
        plot_base64 = base64.b64encode(buffer.getvalue()).decode()
        buffer.close()

        self.assertIsNotNone(plot_base64)  # Verify that the plot is generated

    def test_correlation_heatmap(self):
        # Example test for generating a correlation heatmap
        data = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
        correlation_matrix = data.corr()
        sns.heatmap(correlation_matrix, annot=True)
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        plt.close()
        plot_base64 = base64.b64encode(buffer.getvalue()).decode()
        buffer.close()

        self.assertIsNotNone(plot_base64)  # Verify that the heatmap is generated

    def test_visualization_result_view(self):
        # Test the visualization result view
        url = reverse("analyse:visualization_options", args=[self.uploaded_file.id])
        response = self.client.post(url, {
            "columns": ["col1"],
            "visualization": "histogram"
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Résultat de la Visualisation")