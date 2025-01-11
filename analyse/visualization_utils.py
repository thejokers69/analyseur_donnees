
import matplotlib.pyplot as plt
import seaborn as sns

def create_histogram(data, column):
    plt.figure()
    sns.histplot(data[column], kde=True)
    plt.title(f"Histogram for {column}")
    return plt