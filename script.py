import argparse
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime
from distutils.util import strtobool
from time import sleep, time
from typing import Optional

from dateutil import tz

from scrapers.scraper import (
    connect_to_base, get_driver, parse_html, write_to_file
    )


def run_process(
    filename: str, headless: bool, binary_location: Optional[str]
        ) -> None:
    """
    Makes 20 requests to random Wikipedia pages,
    writes pages' names, urls and last modified times to the given CSV file.

    Parameters:
        filename: str
        headless: bool
        binary_location: Optional[str]

    Returns:
        None
    """
    browser = get_driver(headless, binary_location)

    if connect_to_base(browser):
        sleep(2)
        html = browser.page_source
        output_list = parse_html(html)
        write_to_file(output_list, filename)
        browser.quit()
    else:
        print("Error connecting to Wikipedia")
        browser.quit()


def main(headless: bool, binary_location: Optional[str]) -> None:
    """
    Makes 20 requests to random Wikipedia pages,
    writes pages' names, urls and last modified times to the output CSV file.

    Parameters:
        headless: bool
        binary_location: Optional[str]

    Returns:
        None
    """

    if headless:
        print("Running in headless mode...")

    start_time = time()

    output_timestamp = datetime.now(
        tz=tz.gettz("Russia/Moscow")
        ).strftime("%Y%m%d%H%M%S")

    output_filename = f"output_{output_timestamp}.csv"
    futures = []

    with ThreadPoolExecutor() as executor:
        for number in range(1, 21):
            futures.append(
                executor.submit(
                    run_process, output_filename, headless, binary_location
                    )
            )

    wait(futures)
    end_time = time()
    elapsed_time = end_time - start_time
    print(f"Elapsed run time: {elapsed_time} seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="wikipedia_scraper",
        description="Makes 20 requests to random Wikipedia pages,"
        " writes pages' names, urls and last modified times"
        " to the output CSV file."
    )

    parser.add_argument(
        "--headless", default=False, type=lambda x: bool(strtobool(x)),
        help="whether the scraper should run Chrome in a headless mode,"
        " default False"
        )

    parser.add_argument(
        "--binary_location",
        help="path to custom Google Chrome binary location"
        )

    args = parser.parse_args()
    main(args.headless, args.binary_location)
