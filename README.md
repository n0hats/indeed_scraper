# Indeed Job Scraper

This project consists of two main components: `scrape.py` and `app.py`. The `scrape.py` script is responsible for scraping job listings from Indeed based on a specified query and location, while `app.py` provides a web interface to upload the scraped JSON data and display it in a tabular format with filtering and sorting capabilities.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [scrape.py](#scrapepy)
  - [Functionality](#functionality)
  - [Usage](#usage)
- [app.py](#appy)
  - [Functionality](#functionality-1)
  - [Usage](#usage-1)
- [table.html](#tablehtml)
  - [Example Display](#example-display)

## Prerequisites
- Python 3.x
- Flask
- Selenium (for scraping with selenium method)
- BeautifulSoup, requests, and other dependencies

You can install the required Python packages using pip:
```pip install flask selenium beautifulsoup4 requests click```

For Selenium, you will also need a WebDriver for your browser (e.g., ChromeDriver for Google Chrome).

## Setup
1. Clone this repository.
2. Navigate to the project directory.
3. Ensure all dependencies are installed as mentioned above.
4. Set up a virtual environment if necessary.

## scrape.py

### Functionality
`scrape.py` is designed to scrape job listings from Indeed based on user-provided query and location parameters. It supports two scraping methods: `requests` and `selenium`. The script can authenticate if required, handles pagination through multiple pages of search results, extracts detailed features for each job listing, and saves the extracted data into a JSON file.

### Usage
To run the scraper, use the following command:
```python scrape.py --query="your_query" --location="your_location" --method=[requests|selenium] --wait-time=seconds --auth```

- `--query`: The job search query (default is "software engineer").
- `--location`: The location for the job search (default is "remote").
- `--method`: The scraping method to use ('requests' or 'selenium') (default is "selenium").
- `--wait-time`: Time in seconds to wait after loading each page for selenium-based scraping (default is 5).
- `--auth`: A flag indicating whether to authenticate before scraping.

Example:
```python scrape.py --query="data scientist" --location="new york" --method=selenium --wait-time=10 --auth```

## app.py

### Functionality
`app.py` is a Flask web application that allows users to upload the JSON files generated by `scrape.py`. It displays the job listings in a table format with filtering and sorting capabilities.

### Usage
To run the Flask application, use the following command:
```flask run```

The application will start on `http://127.0.0.1:5000/` by default.

## table.html

### Example Display
The `table.html` file contains the HTML template for displaying job listings in a tabular format. It includes filters and sorting functionalities for each column except the last two (Indeed Link and Application Link).

Example of how the table might look:

| #  | Name            | Company        | Description                          | Salary     | Remote | Requirements                           | City      | State | Indeed Link                | Application Link         |
|----|-----------------|----------------|--------------------------------------|------------|--------|----------------------------------------|-----------|-------|----------------------------|--------------------------|
| 1  | Data Scientist  | Tech Corp      | Experienced data scientist needed.   | $120,000+  | Yes    | - Python<br>- SQL<br>- Machine Learning | New York  | NY    | [Indeed Link](#)         | [Application Link](#)  |
| 2  | Software Eng.   | Innovate Inc   | Full-stack developer position open.  | $100,000+  | No     | - JavaScript<br>- React              | San Jose  | CA    | [Indeed Link](#)         | [Application Link](#)  |
| 3  | Machine Lrnng   | Smart Labs     | ML Engineer with cloud experience.   | $140,000+  | Yes    | - Python<br>- AWS                    | Chicago   | IL    | [Indeed Link](#)         | [Application Link](#)  |

Filters and sorting can be applied to each column by typing in the filter boxes or clicking on the column headers.
