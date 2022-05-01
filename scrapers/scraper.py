import csv
from pathlib import Path
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_DIR = Path(__file__).resolve(strict=True).parent


def get_driver(
    headless: bool, binary_location: Optional[str]
        ) -> webdriver.Chrome:
    """
    Initializes the browser.

    Parameters:
        headless: bool
        binary_location: Optional[str]

    Returns:
        webdriver.Chrome
    """
    options = webdriver.ChromeOptions()

    if headless:
        options.add_argument("--headless")

    if binary_location:
        options.binary_location = binary_location

    driver = webdriver.Chrome(options=options)
    return driver


def connect_to_base(browser: webdriver.Chrome) -> bool:
    """
    Attempts to connect to Wikipedia.

    Parameters:
        browser: webdriver.Chrome

    Returns:
        bool
    """
    base_url = "https://en.wikipedia.org/wiki/Special:Random"
    connection_attempts = 0

    while connection_attempts < 3:
        try:
            browser.get(base_url)
            # wait for table element with id = 'content' to load
            # before returning True
            WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.ID, "content"))
            )
            return True
        except Exception as e:
            print(e)
            connection_attempts += 1
            print(f"Error connecting to {base_url}.")
            print(f"Attempt #{connection_attempts}.")
    return False


def parse_html(html: str) -> List[Dict[str, str]]:
    """
    Parse HTML to get wikipedia article url, title, and last modified date.

    Parameters:
        html: str

    Returns:
        List[Dict[str, str]]
    """
    soup = BeautifulSoup(html, "html.parser")
    output_list = []

    article_info = {
        "url": soup.find("link", {"rel": "canonical"})["href"],
        "title": soup.find("h1", {"id": "firstHeading"}).text,
        "last_modified": soup.find("li", {"id": "footer-info-lastmod"}).text
    }

    output_list.append(article_info)
    return output_list


def write_to_file(
    output_list: List[List[Dict[str, str]]], filename: str
        ) -> None:
    """
    Write the list of rows to a CSV table with headers
    `url`, `title` and `last_modified`.

    Parameters:
        output_list: List[Dict[str, str]]
        filename: str

    Returns:
        None
    """

    for row in output_list:
        with open(Path(BASE_DIR).joinpath(filename), "a") as csvfile:
            fieldnames = ["url", "title", "last_modified"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(row)
