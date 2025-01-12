# /Users/thejoker/Documents/GitHub/analyseur_donnees/analyse/utils.py

import os
import pandas as pd
import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import logging
from .visualization_utils import create_histogram
logger = logging.getLogger(__name__)

# Load data 
def load_data(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    try:
        if file_extension in [".xls", ".xlsx"]:
            return pd.read_excel(file_path, engine="openpyxl")
        elif file_extension == ".csv":
            return pd.read_csv(file_path)
        else:
            raise ValueError("Unsupported file format.")
    except Exception as e:
        raise ValueError(f"Error loading file: {e}")

# Calculate statistics
def calculate_statistics(df):
    mean = df.mean().to_dict()
    median = df.median().to_dict()
    mode = df.mode().iloc[0].to_dict()
    std_dev = df.std().to_dict()
    variance = df.var().to_dict()
    range_values = (df.max() - df.min()).to_dict()
    coefficient_of_variation = (df.std() / df.mean()).to_dict()
    histograms = {col: create_histogram(df, col) for col in df.columns if pd.api.types.is_numeric_dtype(df[col])}

    return {
        "mean": mean,
        "median": median,
        "mode": mode,
        "std_dev": std_dev,
        "variance": variance,
        "range": range_values,
        "coefficient_of_variation": coefficient_of_variation,
        "histograms": histograms,
    }