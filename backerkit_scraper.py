from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os
import re
import pandas as pd


def clean_text(text):
    """
    Cleans the scraped text by replacing non-breaking spaces and other unwanted characters.
    """
    cleaned_text = text.replace('\xa0', ' ').strip()
    return cleaned_text


def scrape_backerkit(campaign_url, save_directory):
    """
    Scrapes the funds raised, backers per day, and funding progress from the BackerKit campaign page and saves them in CSV files.
    """
    # Initialize Chrome WebDriver with options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--window-size=1920,1080')
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    # Start the WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Open the campaign page in the browser
        driver.get(campaign_url)

        # Wait for the page to load fully
        time.sleep(3)

        # Get the page source and parse it with BeautifulSoup
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Scrape data for "Daily Funding on Indiegogo"
        script_tag_funding = soup.find('script', text=re.compile(r'new Chartkick\["ColumnChart"\]\("chart-1"'))
        if script_tag_funding:
            funding_data = re.search(r'new Chartkick\["ColumnChart"\]\("chart-1", (\[\[.*?\]\])',
                                     script_tag_funding.string)
            if funding_data:
                funding_data_list = eval(funding_data.group(1))  # Convert string to list
                df_funding = pd.DataFrame(funding_data_list, columns=['Date', 'Funds Raised'])

                # Convert date column to datetime and ensure proper formatting
                df_funding['Date'] = pd.to_datetime(df_funding['Date'], errors='coerce')

                # Ensure the save directory exists
                if not os.path.exists(save_directory):
                    os.makedirs(save_directory)

                # Save "Daily Funding on Indiegogo" data to a CSV
                csv_funding_path = os.path.join(save_directory, 'daily_funding_indiegogo.csv')
                df_funding.to_csv(csv_funding_path, index=False)
                print(f"Daily funding data saved as a CSV file at {csv_funding_path}")

        # Scrape data for "Daily Backers on Indiegogo"
        script_tag_backers = soup.find('script', text=re.compile(r'new Chartkick\["ColumnChart"\]\("chart-2"'))
        if script_tag_backers:
            backers_data = re.search(r'new Chartkick\["ColumnChart"\]\("chart-2", (\[\[.*?\]\])',
                                     script_tag_backers.string)
            if backers_data:
                backers_data_list = eval(backers_data.group(1))  # Convert string to list
                df_backers = pd.DataFrame(backers_data_list, columns=['Date', 'Backers'])

                # Convert date column to datetime and ensure proper formatting
                df_backers['Date'] = pd.to_datetime(df_backers['Date'], errors='coerce')

                # Save "Daily Backers on Indiegogo" data to a CSV
                csv_backers_path = os.path.join(save_directory, 'daily_backers_indiegogo.csv')
                df_backers.to_csv(csv_backers_path, index=False)
                print(f"Daily backers data saved as a CSV file at {csv_backers_path}")

        # Scrape data for "Funding Progress on Indiegogo"
        funding_progress_data_tag = soup.find('div', {'id': 'fundingData'})
        if funding_progress_data_tag:
            funding_progress_data = funding_progress_data_tag['data-chart']

            # Replace "null" with "None" in the string and eval safely
            funding_progress_data = funding_progress_data.replace('null', 'None')
            funding_progress_data_list = eval(funding_progress_data)

            # Create a DataFrame with the relevant columns
            df_funding_progress = pd.DataFrame(funding_progress_data_list, columns=[
                'Date', 'Funds Raised', 'Goal', 'Trend', 'Projection Low', 'Projection High', 'Tooltip'
            ])

            # Convert date column to datetime and ensure proper formatting
            df_funding_progress['Date'] = pd.to_datetime(df_funding_progress['Date'], errors='coerce')

            # Convert numeric fields to the correct type and avoid scientific notation
            df_funding_progress['Funds Raised'] = pd.to_numeric(df_funding_progress['Funds Raised'], errors='coerce')
            df_funding_progress['Goal'] = pd.to_numeric(df_funding_progress['Goal'], errors='coerce')
            df_funding_progress['Trend'] = pd.to_numeric(df_funding_progress['Trend'], errors='coerce')
            df_funding_progress['Projection Low'] = pd.to_numeric(df_funding_progress['Projection Low'], errors='coerce')
            df_funding_progress['Projection High'] = pd.to_numeric(df_funding_progress['Projection High'], errors='coerce')

            # Filter out rows where "Tooltip" contains the string "Trending:" or "Trend:"
            df_funding_progress = df_funding_progress[~df_funding_progress['Tooltip'].str.contains("Trending:", na=False)]
            df_funding_progress = df_funding_progress[~df_funding_progress['Tooltip'].str.contains("Trend:", na=False)]

            # Exclude the last 2 rows
            df_funding_progress = df_funding_progress.iloc[:-2]

            # Replace NaN values with empty strings to avoid issues in CSV
            df_funding_progress.fillna('', inplace=True)

            # Save "Funding Progress on Indiegogo" data to a CSV
            csv_funding_progress_path = os.path.join(save_directory, 'funding_progress_indiegogo.csv')
            df_funding_progress.to_csv(csv_funding_progress_path, index=False)
            print(f"Funding progress data saved as a CSV file at {csv_funding_progress_path}")

    except Exception as e:
        print(f"Error while fetching the page: {e}")

    finally:
        # Close the browser after fetching the content
        driver.quit()
