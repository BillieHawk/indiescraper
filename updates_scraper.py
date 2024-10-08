from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re
import os
import pickle  # Import pickle to save data in binary format


def clean_text(text):
    """
    Cleans the scraped text by replacing non-breaking spaces and other unwanted characters.
    """
    cleaned_text = text.replace('\xa0', ' ').strip()  # Replace non-breaking spaces with regular spaces
    return cleaned_text


def save_post_to_file(poster_name, post_date, post_content, project_directory):
    """
    Save post details to a pickle (.pkl) file in an 'updates' subfolder within the project directory.
    """
    # Create the 'updates' subfolder within the project directory
    updates_folder = os.path.join(project_directory, 'updates')
    if not os.path.exists(updates_folder):
        os.makedirs(updates_folder)

    # Ensure the filename is URL-safe
    safe_poster_name = re.sub(r'[^A-Za-z0-9]+', '_', poster_name.strip().lower())
    safe_date = re.sub(r'[^A-Za-z0-9]+', '_', post_date.strip().lower())
    filename = f'{safe_poster_name}_{safe_date}.pkl'  # Save as .pkl file

    # Save the post content to a pickle file in the 'updates' folder
    post_data = {
        'poster_name': poster_name,
        'post_date': post_date,
        'post_content': post_content
    }

    post_path = os.path.join(updates_folder, filename)
    with open(post_path, 'wb') as f:
        pickle.dump(post_data, f)  # Save the post data using pickle

    print(f"Post saved as pickle file to {post_path}")


def click_see_more_updates(driver):
    """
    Continuously clicks the 'See More Updates' button until all updates are loaded.
    """
    while True:
        try:
            # Check if the "See More Updates" button is present
            button = driver.find_element('xpath', '//button[contains(text(),"See More Updates")]')
            if button:
                # Scroll to the button and click it
                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                time.sleep(1)  # Ensure the scroll completes before clicking
                button.click()
                time.sleep(3)  # Allow time for new updates to load
            else:
                break
        except Exception as e:
            # If the button is no longer found, exit the loop
            print(f"No more 'See More Updates' button found or an error occurred: {e}")
            break


def scrape_indiegogo_updates(campaign_url, save_directory):
    """
    Scrapes all updates from the Indiegogo campaign and saves them to the specified directory.
    """
    # Initialize Chrome WebDriver with options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode (without opening a window)
    options.add_argument('--disable-gpu')  # Disable GPU rendering
    options.add_argument('--no-sandbox')  # Bypass OS security model
    options.add_argument('--disable-blink-features=AutomationControlled')  # Prevent automation detection
    options.add_argument('--window-size=1920,1080')  # Set the window size for headless mode
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    # Start the WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Open the campaign page in the browser
        driver.get(campaign_url)

        # Increase wait time to allow the page to load fully
        time.sleep(5)

        # Continuously click the "See More Updates" button until all updates are loaded
        click_see_more_updates(driver)

        # Get the page source and parse it with BeautifulSoup
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Find all update posts using the div tag and class
        updates = soup.find_all('div', class_='routerContentUpdate-update')

        if not updates:
            print("No updates found.")
            return

        for update in updates:
            # Extract the poster's name, date, and content
            poster_name = clean_text(update.find('div', class_='routerContentUpdate-name').text)
            post_date = clean_text(update.find('div', class_='routerContentUpdate-date').text)
            post_content_section = update.find('div', class_='routerContentUpdate-post')
            post_content = clean_text(post_content_section.get_text(separator="\n"))

            # Save the post to a pickle file in the specified save directory
            save_post_to_file(poster_name, post_date, post_content, save_directory)

    except Exception as e:
        print(f"Error while fetching the page: {e}")

    finally:
        # Close the browser after fetching the content
        driver.quit()
