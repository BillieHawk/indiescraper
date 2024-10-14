# indiescraper

indiescraper is a Python-based tool that scrapes campaign stories and updates from Indiegogo campaigns. This tool uses Selenium and BeautifulSoup to automate the extraction process, saving the scraped data in both text and pickle formats for flexibility. It supports multiple languages and handles pagination, making it ideal for data collection and analysis.

## Features
- Scrapes Indiegogo campaign stories and updates.
- Saves extracted data in `.pkl` formats.
- Supports multiple languages (UTF-8 compatible).
- Handles pagination for complete extraction.
- Customizable save directories for each campaign.

## Prerequisites

- Python 3.x
- `Selenium` for browser automation
- `BeautifulSoup` for parsing HTML
- `webdriver-manager` to manage browser drivers
- Google Chrome and the Chrome WebDriver

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/IndiegogoCampaignScraper.git
    cd IndiegogoCampaignScraper
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Ensure you have Chrome installed, as this tool uses Chrome WebDriver.

## Usage

1. Prepare a CSV file with the project details (e.g., `XSIndigegogoProduction.csv`). The CSV should contain:
    - `id`: Project ID
    - `combined.url`: The URL path for the campaign

2. Update the script with your CSV file path.

3. Run the script:

    ```bash
    python main.py
    ```

4. Alternatively, scrape an individual project:

    ```bash
    python main.py
    ```

## Example Code Snippet

```python
scrape_indiegogo_story('https://www.indiegogo.com/projects/livall-pikaboost-2-electrify-your-rides-with-ease', 'path_to_save')
scrape_indiegogo_updates('https://www.indiegogo.com/projects/livall-pikaboost-2-electrify-your-rides-with-ease#/updates/all', 'path_to_save')
