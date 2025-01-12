# /Users/thejoker/Documents/GitHub/analyseur_donnees/analyse/utils.py

import os
import pandas as pd
import numpy as np
import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import logging
from .visualization_utils import create_histogram
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression
import plotly.express as px
import plotly.graph_objects as go
import csv
from io import StringIO
from fpdf import FPDF

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
    
# Houssam Aoun (Sa partie )


# Correlation Analysis
def correlation_analysis(data: pd.DataFrame, col1: str, col2: str) -> dict:
    if col1 not in data.columns or col2 not in data.columns:
        raise ValueError(f"Columns {col1} or {col2} not found in dataset.")
    if data[col1].isnull().any() or data[col2].isnull().any():
        raise ValueError("Columns contain missing values.")
    correlation, _ = pearsonr(data[col1], data[col2])
    return {"correlation_coefficient": correlation}

# Linear Regression Analysis
def linear_regression_analysis(data: pd.DataFrame, x_col: str, y_col: str) -> dict:
    if x_col not in data.columns or y_col not in data.columns:
        raise ValueError(f"Columns {x_col} or {y_col} not found in dataset.")
    if data[x_col].isnull().any() or data[y_col].isnull().any():
        raise ValueError("Columns contain missing values.")
    X = data[[x_col]].values
    y = data[y_col].values
    model = LinearRegression()
    model.fit(X, y)
    return {
        "coefficient": model.coef_[0],
        "intercept": model.intercept_,
        "r_squared": model.score(X, y),
    }

# Export Data to CSV
def download_csv(data: pd.DataFrame) -> StringIO:
    csv_buffer = StringIO()
    data.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    return csv_buffer

# Export to PDF
def download_pdf(data: pd.DataFrame) -> FPDF:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add column names
    for col in data.columns:
        pdf.cell(40, 10, col, border=1)

    pdf.ln()

    # Add rows
    for _, row in data.iterrows():
        for col in row:
            pdf.cell(40, 10, str(col), border=1)
        pdf.ln()

    return pdf

# Interactive Visualization
def interactive_visualization(data: pd.DataFrame, x: str, y: str, chart_type: str = "scatter") -> str:
    if chart_type == "scatter":
        fig = px.scatter(data, x=x, y=y, title="Interactive Scatter Plot")
    elif chart_type == "line":
        fig = px.line(data, x=x, y=y, title="Interactive Line Chart")
    elif chart_type == "bar":
        fig = px.bar(data, x=x, y=y, title="Interactive Bar Chart")
    else:
        fig = go.Figure()
    return fig.to_html(full_html=False)

# Probability Analysis
def probability_analysis(data: pd.Series, value: float) -> float:
    mean = np.mean(data)
    std_dev = np.std(data)
    return 1 - (abs(value - mean) / std_dev)