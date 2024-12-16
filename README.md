# Indeed Job Scraper

## Overview

The `scrape.py` script is designed to scrape job listings from Indeed.com based on specified search criteria such as job title and location. It utilizes both Selenium and Requests-based methods to retrieve the HTML content, circumvent anti-bot protections, and extract job data including the title, company, description, salary, remote work availability, and more. The extracted data is saved in JSON format, which can later be viewed using a companion Flask application `display_json.py`.

## Requirements

Before running the script, you need to install the required Python packages. You can install these with pip:
```bash
pip install requests click time re json cloudscraper fake_useragent bs4 selenium webdriver-manager urllib datetime colorama tqdm flask
```

Make sure you have Chrome browser installed on your device since Selenium uses it to scrape dynamic content from the web.

## Usage

### Scrape.py

The `scrape.py` script offers several options to customize the scraping process:

- `--query`: Specifies the job search query (default is "security analyst").
- `--location`: Specifies the location for the job search (default is "remote").
- `--method`: Choose between 'requests' and 'selenium' for scraping. Default is 'selenium'.
- `--wait-time`: Sets a wait time in seconds for Selenium-based scraping to wait after loading a page (default is 5 seconds).
- `--auth`: Includes authentication token fetching if necessary.

To run the script, use the following command in your terminal:

```bash
python scrape.py --query "software engineer" --location "new york" --method "selenium" --wait-time 5
```

### Output

The script saves the scraped job listings in a JSON file within the 'searches' directory under the current working directory. The filename includes the query and the timestamp to avoid overwriting previous data:
