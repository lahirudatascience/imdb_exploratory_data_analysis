import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Define IMDb Top 250 URL
BASE_URL = "https://www.imdb.com/chart/top/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Function to scrape IMDb movie data
def scrape_imdb_movies():
    response = requests.get(BASE_URL, headers=HEADERS)
    if response.status_code != 200:
        print("Failed to retrieve the webpage")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    movie_rows = soup.select(".ipc-metadata-list-summary-item")  # Updated selector for movie rows
    
    if not movie_rows:
        print("No movie data found. Check the HTML structure.")
        return None
    
    movies_data = []
    
    for movie in movie_rows:
        # Extract movie title
        title_element = movie.select_one("h3")
        title = title_element.text.strip() if title_element else "Unknown"
        
        # Extract release year
        year_element = movie.select(".cli-title-metadata-item")
        year = year_element[0].text.strip() if year_element else "Unknown"
        
        # Extract IMDb rating
        rating_element = movie.select_one(".ipc-rating-star--imdb")
        rating = rating_element.text.strip() if rating_element else "Unknown"
        
        # Extract movie link
        movie_link_element = movie.select_one("a.ipc-title-link-wrapper")
        movie_link = "https://www.imdb.com" + movie_link_element["href"] if movie_link_element else ""
        
        # Initialize extra details
        genre, directors, box_office_revenue, lead_actors = "Unknown", "Unknown", "Unknown", "Unknown"
        
        # Fetch individual movie page for more details
        if movie_link:
            movie_response = requests.get(movie_link, headers=HEADERS)
            if movie_response.status_code == 200:
                movie_soup = BeautifulSoup(movie_response.text, "html.parser")
                
                # Extract genre
                genre_elements = movie_soup.select(".ipc-chip-list__scroller a")
                genre = ", ".join([g.text.strip() for g in genre_elements]) if genre_elements else "Unknown"
                
                # Extract directors (Avoid duplication)
                director_elements = movie_soup.select(".ipc-metadata-list-item__content-container a[href*='/name/']")
                directors_set = {d.text.strip() for d in director_elements}  # Use a set to avoid duplicates
                directors = ", ".join(directors_set) if directors_set else "Unknown"
                
                # Extract box office revenue
                box_office_element = movie_soup.select_one(".ipc-metadata-list__item:contains('Gross worldwide')")
                box_office_revenue = box_office_element.text.strip().split(":")[-1] if box_office_element else "Unknown"
                
                # Extract lead actors (Avoid duplication)
                stars_heading = movie_soup.select_one(".sc-d49a611d-3.ieHsnX")  # Locate 'Stars' heading
                if stars_heading:
                    actor_elements = stars_heading.find_next_siblings("span", class_="sc-d49a611d-2 iPiQIX")
                    actors_set = {actor.text.strip() for actor in actor_elements}  # Use set to remove duplicates
                    lead_actors = ", ".join(actors_set) if actors_set else "Unknown"
        
        movies_data.append({
            "Title": title,
            "Year": year,
            "Rating": rating,
            "Genre": genre,
            "Director(s)": directors,
            "Box Office Revenue": box_office_revenue,
            "Lead Actors": lead_actors,
        })
        
        print(f"Scraped: {title} ({year})")  # Debugging output
        time.sleep(1)  # Prevent getting blocked by IMDb
    
    return pd.DataFrame(movies_data)

# Scrape and save the data
movies_df = scrape_imdb_movies()

# Save the dataset to CSV
if movies_df is not None and not movies_df.empty:
    movies_df.to_csv("imdb_top_movies.csv", index=False)
    print("Data saved to imdb_top_movies.csv")
else:
    print("No data to save. Check the scraping logic.")
