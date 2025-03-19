from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pandas as pd
import time
import requests

# Define IMDb Top 250 URL
BASE_URL = "https://www.imdb.com/chart/top/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def setup_driver():
    """Set up Selenium WebDriver."""
    service = Service("/usr/local/bin/chromedriver")  # Full path to the chromedriver binary
    driver = webdriver.Chrome(service=service)
    return driver

def get_soup(url):
    """Fetch and parse an IMDb page using BeautifulSoup."""
    response = requests.get(url, headers=HEADERS)
    return BeautifulSoup(response.text, "html.parser") if response.status_code == 200 else None

def extract_movie_details(movie_soup):
    """Extract detailed information for a single movie."""
    genre_elements = movie_soup.select(".ipc-chip-list__scroller a")
    genre = ", ".join([g.text.strip() for g in genre_elements]) if genre_elements else "Unknown"
    
    director_elements = movie_soup.select(".ipc-metadata-list-item__content-container a[href*='/name/']")
    directors_set = {d.text.strip() for d in director_elements}
    directors = ", ".join(directors_set) if directors_set else "Unknown"
    
    box_office_element = movie_soup.select_one(".ipc-metadata-list__item:-soup-contains('Gross worldwide')")
    box_office_revenue = box_office_element.text.strip().split(":")[-1] if box_office_element else "Unknown"
    
    lead_actors = "Unknown"
    metadata_sections = movie_soup.find_all("li", class_="ipc-metadata-list__item")
    for section in metadata_sections:
        if section.find(string="Stars"):
            actor_elements = section.find_all("a", href=lambda x: x and "/name/" in x)
            lead_actors_set = {actor.text.strip() for actor in actor_elements}
            lead_actors = ", ".join(lead_actors_set) if lead_actors_set else "Unknown"
            break
    
    return genre, directors, box_office_revenue, lead_actors

def scrape_imdb_movies_with_selenium():
    """Scrape IMDb Top 250 movies."""
    driver = setup_driver()
    driver.get(BASE_URL)
    time.sleep(3)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    
    movies_data = []
    movie_rows = soup.select(".ipc-metadata-list-summary-item")
    if not movie_rows:
        print("No movie data found. Check the HTML structure.")
        return None
    
    for movie in movie_rows:
        title_element = movie.select_one("h3")
        title = title_element.text.strip() if title_element else "Unknown"
        
        year_element = movie.select(".sc-f30335b4-7")
        year = year_element[0].text.strip() if year_element else "Unknown"
        
        rating_element = movie.select_one(".ipc-rating-star--imdb")
        rating = rating_element.text.strip() if rating_element else "Unknown"
        
        movie_link_element = movie.select_one("a.ipc-title-link-wrapper")
        movie_link = "https://www.imdb.com" + movie_link_element["href"] if movie_link_element else ""
        
        genre, directors, box_office_revenue, lead_actors = "Unknown", "Unknown", "Unknown", "Unknown"
        
        if movie_link:
            movie_soup = get_soup(movie_link)
            if movie_soup:
                genre, directors, box_office_revenue, lead_actors = extract_movie_details(movie_soup)
        
        movies_data.append({
            "Title": title,
            "Year": year,
            "Rating": rating,
            "Genre": genre,
            "Director(s)": directors,
            "Box Office Revenue": box_office_revenue,
            "Lead Actors": lead_actors,
        })
    
    df = pd.DataFrame(movies_data)
    df.to_csv("data/imdb_top_movies.csv", index=False)
    print("Scraping complete. Data saved.")

if __name__ == "__main__":
    scrape_imdb_movies_with_selenium()
