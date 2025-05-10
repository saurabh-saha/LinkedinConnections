from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from dotenv import load_dotenv
from selenium.webdriver.support.ui import WebDriverWait

load_dotenv()
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
    raise ValueError("❌ Missing LinkedIn credentials! Check .env file.")

keywords = [
    'tech%20lead',
    'engineering%20manager',
    'cto',
    'ceo',
    'sde 3',
    'founder',
    'founder',
]


class Crawl:
    def __init__(self):
        self.driver = self.__login()
        self.connected_count = 0

    def __login(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        #options.add_argument("--headless")
        chrome = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        chrome.get("https://www.linkedin.com/login")
        time.sleep(2)

        chrome.find_element(By.ID, "username").send_keys(LINKEDIN_EMAIL)
        chrome.find_element(By.ID, "password").send_keys(LINKEDIN_PASSWORD)
        chrome.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(5)
        return chrome

    def connect(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # wait for new content to load
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        profiles = self.driver.find_elements(By.XPATH,
                                   "//button[contains(@id, 'ember') and count(*) = 1 and span[text()='Connect']]")

        for button in profiles:
            try:
                self.driver.execute_script("arguments[0].click();", button)
                time.sleep(2)

                send_button = self.driver.find_element(By.XPATH, "//button[count(*) = 1 and span[text()='Send without a note']]")
                self.driver.execute_script("arguments[0].click();", send_button)
                print("Connection Request Sent!")
                self.connected_count += 1
                time.sleep(2)
            except Exception as e:
                print(f"Error: {str(e)}")
                break

    def recommended_jobs(self, job_index):
        job_url = f"https://www.linkedin.com/jobs/collections/recommended/"
        self.driver.get(job_url)
        time.sleep(5)
        try:
            company_element = self.driver.find_element(By.XPATH,
                                                   "//div[contains(@class, 'job-details-jobs-unified-top-card__company-name')]//a")

            company_url = company_element.get_attribute("href")
            if company_url:
                self.driver.get(company_url)
                time.sleep(5)
                people_tab = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    "//ul[contains(@class, 'org-page-navigation__items')]/li[last()]/a[contains(normalize-space(), 'People')]"))
                )
                people_tab.click()
                time.sleep(5)
                self.connect()
        except Exception as e:
            print(f"❌ Error: {e}")

    def fetch(self, keyword, page_number):
        search_url = f"https://www.linkedin.com/search/results/people/?keywords={keyword}&page={page_number}"
        self.driver.get(search_url)
        time.sleep(5)
        self.connect()
        time.sleep(5)

    def suggestions(self, keyword, page_number):
        search_url = f"https://www.linkedin.com/search/results/all/?keywords={keyword}"
        self.driver.get(search_url)
        time.sleep(5)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        list_items = self.driver.find_elements(By.XPATH, "//li[@data-view-name='search-results-query-suggestion-item']")
        urls = [li.find_element(By.TAG_NAME, "a").get_attribute("href") for li in list_items]
        if urls:
            self.driver.get(urls[0].replace("/all/", "/people/")+f"&page={page_number}")
            time.sleep(5)
        self.connect()
        time.sleep(15)

