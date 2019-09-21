"""Scrape all men's international rugby match results from 1st January 2013 to present."""
from bs4 import BeautifulSoup
import urllib.request
import re
import pandas as pd


def parse_fixture(html):
    # parse the html from a single element in the html table of fixtures
    try:
        text = html.text.split("\n")
        home_team = text[1]
        home_points = int(text[3])
        away_points = int(text[4])
        away_team = text[-5][2:]
        date = pd.to_datetime(text[-3])
    except ValueError:
        home_team = ""
        home_points = 0
        away_points = 0
        away_team = ""
        date = pd.to_datetime("1800-01-01")
    return {
        "home_team": home_team,
        "away_team": away_team,
        "home_points": home_points,
        "away_points": away_points,
        "date": date,
    }


def scrape_page(url):
    # extract the results from a single page
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page, "html.parser")
    fixtures = soup.find_all(attrs={"class": "data1"})
    return pd.DataFrame([parse_fixture(fixture) for fixture in fixtures])


def get_next_url(url, page_number):
    # get the next url to scrape in the set of results pages
    soup = BeautifulSoup(urllib.request.urlopen(url))
    try:
        partial_url = soup.find_all(
            "a", href=True, attrs={"title": re.compile(f"go to page {page_number + 1}")}
        )[-1].attrs["href"]
        return "http://stats.espnscrum.com" + partial_url
    except IndexError:
        return None


def scrape_all_pages(initial_page):
    # scrape all of the data
    url = init_url
    data = []
    i = 1
    while url is not None:
        data.append(scrape_page(url))
        url = get_next_url(url, i)
        i += 1
    return pd.concat(data)


def main():
    init_url = (
        "http://stats.espnscrum.com/statsguru/rugby/"
        "stats/index.html?class=1;spanmin1=1+Jan+2013;"
        "spanval1=span;template=results;type=team;view=results"
    )
    rugby_data = scrape_all_pages(init_url)

    # remove dud rows and save
    rugby_data = rugby_data[
        (rugby_data["home_team"] != "") & (rugby_data["away_team"] != "")
    ]
    rugby_data[::2].to_csv("rugby_data.csv", index=False)


if __name__ == "__main__":
    main()
