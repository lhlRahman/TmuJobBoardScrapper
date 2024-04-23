import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def extract_details(driver):
    """Extracts details from the job details page."""
    print("---- Extracting Details ----")
    details_data = []
    for row in driver.find_elements(By.CSS_SELECTOR, "div.panel-body table tr"):
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) == 2:
            details_data.append(f"{cells[0].text.strip().replace(':', '')}: {cells[1].text.strip()}")
    return details_data


def extract_table_data(driver):
    """Extracts data from the table and navigates to detail pages."""
    all_data = []
    i = 0
    while True:
        for row in driver.find_elements(By.CSS_SELECTOR, "tr.searchResult"):
            row_data = [cell.text for cell in row.find_elements(By.TAG_NAME, "td") if cell.text]
            if row_data:
                print('Row data:', row_data)
                row.find_element(By.CSS_SELECTOR, "a[onclick*='buildForm']").click()
                print("---- Switching to New Tab ----")
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(1.5)
                row_data.append(' | '.join(extract_details(driver)))
                print("---- Closing Detail Tab ----")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                all_data.append(row_data)
                print(i)
                i += 1
        try:
            # Try to click the next page button
            driver.find_element(By.XPATH, '//*[@id="postingsTablePlaceholder"]/div[1]/div/ul/li[6]/a').click()
            time.sleep(5)
        except:
            break  # Exit loop if next page button not found
    return all_data

# Setup Chrome WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
base_url = 'https://recruitstudents.torontomu.ca/myAccount/careerboostjobs/postings.htm'

try:
    # Navigate to the login page and login
    website = "https://cas.torontomu.ca/login?service=https%3A%2F%2Frecruitstudents.torontomu.ca%2FcasLogin.htm%3Faction%3Dlogin"
    
    username = input("username: ")
    password = input("password: ")
    
    driver.get(website)
    time.sleep(2)
    driver.find_element(By.ID, "username").send_keys(username)  # Replace with your username
    driver.find_element(By.ID, "password").send_keys(password)  # Replace with your password
    driver.find_element(By.NAME, "submit").click()
    time.sleep(10)

    # Navigate to the job postings page
    driver.get(base_url)
    time.sleep(5)

    # Click on the link to view all postings (if necessary)
    driver.find_element(By.LINK_TEXT, "View all available postings").click()
    time.sleep(5)
    
    
    data = extract_table_data(driver)


    # Save data to CSV file
    with open('table_data.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['buttons', 'term', 'title', 'division', 'Details'])  # Adjust column headers as necessary
        writer.writerows(data)

finally:
    driver.quit()

print("Data extraction complete and saved to CSV.")