import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_rating_distribution(df):
    plt.figure(figsize=(10, 6))
    sns.histplot(df['rating'], bins=20, kde=True)
    plt.title('Distribution of Movie Ratings')
    plt.xlabel('Rating')
    plt.ylabel('Frequency')
    plt.grid()
    plt.show()

def plot_revenue_over_time(df):
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x='year', y='revenue', marker='o')
    plt.title('Revenue of Movies Over Time')
    plt.xlabel('Year')
    plt.ylabel('Revenue (in billions)')
    plt.xticks(rotation=45)
    plt.grid()
    plt.show()

def plot_top_n_movies(df, n=10):
    top_n = df.nlargest(n, 'rating')
    plt.figure(figsize=(12, 6))
    sns.barplot(data=top_n, x='title', y='rating', palette='viridis')
    plt.title(f'Top {n} Movies by Rating')
    plt.xlabel('Movie Title')
    plt.ylabel('Rating')
    plt.xticks(rotation=45)
    plt.show()