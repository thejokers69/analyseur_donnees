# /Users/thejoker/Documents/GitHub/analyseur_donnees/analyse/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import UploadedFile


class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ["file"]
    def clean_file(self):
        uploaded_file = self.cleaned_data["file"]
        if uploaded_file.size > 10 * 1024 * 1024:
            raise forms.ValidationError("File size exceeds 10 MB.")
        if not uploaded_file.name.lower().endswith((".csv", ".xls", ".xlsx")):
            raise forms.ValidationError("Unsupported file format.")
        if uploaded_file.size ==0:
            raise forms.ValidationError("The file es empty.")
        return uploaded_file


class CustomizationForm(forms.Form):
    parameter = forms.CharField(
        label="Parameter",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Enter parameter"}),
    )


class EmailUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email"]
        labels = {
            "email": "Email Address",
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email


class AnalysisCustomizationForm(forms.Form):
    # Checkboxes for selecting specific statistics
    mean = forms.BooleanField(label="Mean", required=False)
    median = forms.BooleanField(label="Median", required=False)
    mode = forms.BooleanField(label="Mode", required=False)
    variance = forms.BooleanField(label="Variance", required=False)
    std_dev = forms.BooleanField(label="Standard Deviation", required=False)

    # Dynamic field for columns (to be populated after file upload)
    columns = forms.MultipleChoiceField(
        label="Select Columns",
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        columns = kwargs.pop("columns", [])
        super().__init__(*args, **kwargs)
        self.fields["columns"].choices = [(col, col) for col in columns]


class VisualizationForm(forms.Form):
    VISUALIZATION_CHOICES = [
        ("scatter", "Scatter Plot"),
        ("histogram", "Histogram"),
        ("boxplot", "Box Plot"),
        ("barchart", "Bar Chart"),
        ("correlation_heatmap", "Correlation Heatmap"),
    ]

    visualization_type = forms.ChoiceField(
        choices=VISUALIZATION_CHOICES, label="Select Visualization"
    )
    columns = forms.MultipleChoiceField(
        label="Select Columns",
        required=True,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        columns = kwargs.pop("columns", [])
        super().__init__(*args, **kwargs)
        self.fields["columns"].choices = [(col, col) for col in columns]
