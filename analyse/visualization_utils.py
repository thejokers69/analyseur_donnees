# /Users/thejoker/Documents/GitHub/analyseur_donnees/analyse/utils/visualization_utils.py

import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

def create_histogram(df, column):
    plt.figure()
    sns.histplot(df[column], kde=True)
    plt.title(f"Histogram of {column}")
    plt.xlabel(column)
    plt.ylabel("Frequency")

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def create_scatterplot(df, x_column, y_column):
    plt.figure()
    sns.scatterplot(x=x_column, y=y_column, data=df)
    plt.title(f"Scatter Plot: {x_column} vs {y_column}")
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    plt.close()
    return base64.b64encode(buffer.getvalue()).decode()

def create_boxplot(df, column):
    plt.figure()
    sns.boxplot(data=df[column])
    plt.title(f"Box Plot of {column}")
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    plt.close()
    return base64.b64encode(buffer.getvalue()).decode()


def create_correlation_heatmap(df):
    """
    Generate a correlation heatmap from the given DataFrame.
    """
    plt.figure(figsize=(10, 8))
    correlation_matrix = df.corr()
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", vmin=-1, vmax=1)
    plt.title("Correlation Heatmap")
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def create_regression_plot(df, x_column, y_column):
    """
    Generate a scatter plot with a regression line between two columns.
    """
    plt.figure(figsize=(8, 6))
    sns.regplot(x=x_column, y=y_column, data=df, line_kws={"color": "red"})
    plt.title(f"Regression Plot: {x_column} vs {y_column}")
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')
