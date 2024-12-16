#!/usr/bin/env python3

import os
import requests
import click
import time
import re
import json
import cloudscraper
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlencode
from datetime import datetime
from colorama import Fore, init
from tqdm import tqdm

# Define headers and variables
BASE_URL = "https://indeed.com/jobs"
DEFAULT_WAIT_TIME = 5
DEFAULT_QUERY = "security analyst"
TOTAL_JOBS = 0
ua = UserAgent()
roles = []
clearance_types = [
    "Secret",
    "Top Secret",
    "TS/SCI",
    "SCI",
    "Confidential",
    "Public Trust",
    "Sensitive Compartmented Information",
    "Yankee White",
    "Interim Secret",
    "Interim Top Secret",
    "Q Clearance",
    "L Clearance"
]

# Initialize colorama
init(autoreset=True)


def print_status(status: bool, message: str = "Default Message", overwrite: bool = False) -> None:
    """
    Prints a status message in green for success and red for failure.

    :param status: A boolean indicating the success (True) or failure (False) status.
    :param message: The message to print.
    :param overwrite: If set to True, the text will be overwritten on the same line.
    """
    if status and overwrite:
        print(Fore.GREEN + message, end="\r", flush=True)
    elif status and not overwrite:
        print(Fore.GREEN + message, end="\n")
    elif not status and overwrite:
        print(Fore.RED + message, end="\r", flush=True)
    else:
        print(Fore.RED + message, end="\n")


def build_url(base_url: str, params: dict) -> str:
    """
    Builds a URL with the given base URL and parameters.

    :param base_url: The base URL.
    :param params: A dictionary of query parameters.
    :return: The complete URL with query string.
    """
    return f"{base_url}?{urlencode(params)}"


def extract_ld_json(html: str) -> dict:
    """
    Extracts JSON-LD data from the given HTML content.

    :param html: The HTML content as a string.
    :return: A dictionary containing the extracted JSON-LD data or an empty structure if none found.
    """
    data = re.findall(r'<script type=\"application/ld\+json\">(.*?)</script>', html)
    if not data:
        return {"results": [], "meta": {}}
    ld_json_text = json.loads(data[0])
    return ld_json_text


def parse_search_page(html: str) -> dict:
    """
    Parses the search page HTML to extract job card results and metadata.

    :param html: The HTML content of the search page.
    :return: A dictionary containing job results and metadata or empty structures if none found.
    """
    data = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', html)
    if not data:
        return {"results": [], "meta": {}}
    data = json.loads(data[0])
    return {
        "results": data["metaData"]["mosaicProviderJobCardsModel"]["results"],
        "meta": data["metaData"]["mosaicProviderJobCardsModel"]["tierSummaries"],
    }


def get_html_with_requests(url: str, headers: dict) -> str:
    """
    Retrieves the HTML content of a URL using requests.

    :param url: The URL to retrieve.
    :param headers: Headers to use in the HTTP request.
    :return: The HTML content as a string or None if an error occurred.
    """
    scraper = cloudscraper.create_scraper()
    try:
        response = scraper.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        click.echo(f"Error with Requests: {e}")
        return None


def get_html_with_selenium(url: str, wait_time: int) -> str:
    """
    Retrieves the HTML content of a URL using Selenium.

    :param url: The URL to retrieve.
    :param wait_time: Time in seconds to wait after loading the page.
    :return: The HTML content as a string.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument(f"user-agent={ua.random}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    try:
        driver.get(url)
        time.sleep(wait_time)
        return driver.page_source
    finally:
        driver.quit()


def authenticate_and_get_token(url: str) -> dict:
    """
    Authenticates manually and returns the cookies as a dictionary.

    :param url: The URL to navigate to for authentication.
    :return: A dictionary containing cookie names and values.
    """
    options = Options()
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    try:
        driver.get(url)
        click.echo("Please authenticate manually. Press Enter after completing authentication...")
        input()
        cookies = driver.get_cookies()
        return {cookie['name']: cookie['value'] for cookie in cookies}
    finally:
        driver.quit()


def parse_html(html: str) -> dict:
    """
    Parses the HTML content to extract job search results or an error message.

    :param html: The HTML content as a string.
    :return: A dictionary containing parsed job results or an error message and the original HTML.
    """
    parsed_data = parse_search_page(html)
    if parsed_data["results"]:
        return {
            "parsedResults": parsed_data["results"],
            "meta": parsed_data["meta"]
        }
    else:
        soup = BeautifulSoup(html, 'html.parser')
        return {
            "error": "Unable to extract structured data",
            "html": soup.prettify()
        }


def find_value_in_dicts(nested_list: list) -> bool:
    """
    Checks if a specific value ("Security clearance") exists in any dictionary within a nested list.

    :param nested_list: A list of dictionaries.
    :return: True if the value is found, False otherwise.
    """
    value = "Security clearance"
    if nested_list:
        for item in nested_list:
            if any(value == str(v) for k, v in item.items()):
                return True
    return False


def strip_html_tags(text: str) -> str:
    """
    Removes HTML tags from a string.

    :param text: The input string containing HTML.
    :return: A clean string without HTML tags.
    """
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()


def get_requirements(requirements: list) -> str:
    """
    Extracts and joins requirement labels into a comma-separated string.

    :param requirements: A list of dictionaries containing job requirements.
    :return: A comma-separated string of requirement labels.
    """
    return ','.join(i["label"] for i in requirements)


def extract_job_features(json_html: list, pbar: tqdm) -> None:
    """
    Extracts relevant job features from a list of JSON job objects.

    :param json_html: A list of dictionaries representing jobs.
    :param pbar: A TQDM progress bar object to update during processing.
    """
    global roles, clearance_types
    for job in json_html:
        if not find_value_in_dicts(job["jobCardRequirementsModel"]["jobTagRequirements"]):
            requirements = get_requirements(job["jobCardRequirementsModel"].get("jobOnlyRequirements", []))
            remote_work_model = job.get("remoteWorkModel", {})
            estimated_salary = job.get("estimatedSalary", {})
            name = job.get("title", "")
            has_clearance = any(clearance.lower() in name.lower() for clearance in clearance_types)
            if not has_clearance:
                indeed_link = f'https://indeed.com{job.get("noJsUrl", "")}'
                pbar.set_description("Getting the job page")
                job_html = get_html_with_selenium(indeed_link, DEFAULT_WAIT_TIME)
                data = re.findall(r'<title>Just a moment\.\.\.</title>', job_html)
                if data:
                    pbar.set_description("Trying again")
                    job_html = get_html_with_selenium(indeed_link, 0)
                job_info = extract_ld_json(job_html)
                title = job.get("title", "")
                pbar.set_description(f"Getting the job {title}")
                jd = job_info.get("description", "No description")
                features = {
                    "Name": title,
                    "Company": job.get("truncatedCompany", ""),
                    "Description": jd,
                    "Salary": estimated_salary.get("formattedRange", ""),
                    "Remote": remote_work_model.get("inlineText", ""),
                    "Requirements": requirements,
                    "City": job.get("jobLocationCity", ""),
                    "State": job.get("jobLocationState", ""),
                    "Indeed Link": f'https://indeed.com{job.get("noJsUrl", "")}'
                }
                roles.append(features)
        pbar.update(1)


def increment_pages(query: str, location: str, wait_time: int, initial_offset: int, pbar: tqdm) -> None:
    """
    Iterates through pages of job search results and extracts job features.

    :param query: The job search query.
    :param location: The location for the job search.
    :param wait_time: Time in seconds to wait after loading each page.
    :param initial_offset: The starting offset for pagination.
    :param pbar: A TQDM progress bar object to update during processing.
    """
    global TOTAL_JOBS, BASE_URL
    total_pages = TOTAL_JOBS / 25
    curr_page = 1
    bad_pages = []
    urls = []
    offset = initial_offset
    while offset < TOTAL_JOBS:
        pbar.set_description(f"Turning the page {curr_page} of {total_pages}")
        curr_page += 1
        url = build_url(BASE_URL, {"q": query, "l": location, "start": offset})
        if url not in urls:
            urls.append(url)
            html = get_html_with_selenium(url, wait_time)
            if not html:
                click.echo(f"Failed to retrieve HTML for {url}")
                continue
            data = parse_html(html)
            error = data.get("error", "")
            if not error:
                if url not in bad_pages:
                    json_html = data.get("parsedResults", [])
                    extract_job_features(json_html, pbar)
                    if len(json_html) == 0:  # If no jobs are found, break out of the loop
                        click.echo(f"No more jobs found at offset {offset}. Total jobs processed: {offset}")
                        break
                    offset += len(json_html)
            else:
                print_status(False, f"Error on the HTML: {url}")
                bad_pages.append(url)
                offset += 1
        pbar.update(1)

    for i in bad_pages:
        print(f'\033[91mUnknown error for: {i}\033[0m')


@click.command()
@click.option("--query", default=DEFAULT_QUERY, help="Job query")
@click.option("--location", default="remote", help="Location for job search")
@click.option("--method", type=click.Choice(['requests', 'selenium']), default="selenium", help="Scraping method to use")
@click.option("--wait-time", default=DEFAULT_WAIT_TIME, help="Wait time for selenium-based scraping")
@click.option("--auth", is_flag=True, help="Authenticate before scraping")
def scrape(query: str, location: str, method: str, wait_time: int, auth: bool) -> None:
    """
    Main function to initiate the job scraping process.

    :param query: The job search query.
    :param location: The location for the job search.
    :param method: The scraping method to use ('requests' or 'selenium').
    :param wait_time: Time in seconds to wait after loading each page for selenium-based scraping.
    :param auth: A flag indicating whether to authenticate before scraping.
    """
    global roles, TOTAL_JOBS
    current_directory = os.getcwd()
    searches_directory = os.path.join(current_directory, 'searches')
    if not os.path.exists(searches_directory):
        os.makedirs(searches_directory)
    headers = {
        "User-Agent": ua.random,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }

    token = None
    if auth:
        click.echo("Authenticating to the website...")
        token = authenticate_and_get_token(build_url(BASE_URL, {"q": query, "l": location}))
        headers.update(token)
        click.echo(f"Authentication token retrieved: {token}")
    
    url = build_url(BASE_URL, {"q": query, "l": location, "start": 0})
    click.echo(f"\033[92mScraping {url} using {method} method...\033[0m")
    
    html = None
    if method == "requests":
        html = get_html_with_requests(url, headers)
    elif method == "selenium":
        html = get_html_with_selenium(url, wait_time)

    if not html:
        click.echo("Scraping failed. Please check the logs.")
        return

    data = parse_html(html)
    json_html = data.get("parsedResults", [])
    initial_offset = len(json_html)
    meta = data.get("meta", {})
    if not TOTAL_JOBS:
        try:
            TOTAL_JOBS = meta[0]["jobCount"]
        except KeyError:
            print(meta)
            TOTAL_JOBS = 500
    print_status(True, f"Total jobs to scrape: {TOTAL_JOBS}")
    with tqdm(total=TOTAL_JOBS, desc="Scraping Jobs", unit="job") as pbar:
        extract_job_features(json_html, pbar)
        increment_pages(query, location, wait_time, initial_offset, pbar)

    if roles:
        formatted_query = query.replace(' ', '_')
        today_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(searches_directory,f"{formatted_query}_{today_date}.json")
        click.echo(f"Writing extracted roles to {filename}")
        with open(filename, "w") as json_file:
            json.dump(roles, json_file, indent=4)
    else:
        click.echo("No roles extracted.")


if __name__ == "__main__":
    scrape()