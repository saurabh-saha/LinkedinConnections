from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, urlunparse

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

        profiles = self.driver.find_elements(
            By.XPATH, "//button[.//span[normalize-space()='Connect']]"
        )

        for button in profiles:
            try:
                self.driver.execute_script("arguments[0].click();", button)
                time.sleep(2)
                
                send_buttons = self.driver.find_elements(
                    By.XPATH, "//button[.//span[normalize-space()='Send without a note']]"
                )                
                if send_buttons:
                    self.driver.execute_script("arguments[0].click();", send_buttons[0])

                print("Connection Request Sent!")
                self.connected_count += 1
                time.sleep(2)
            except Exception as e:
                print(f"Error: {str(e)}")
                break

    def recommended_jobs(self, job_index):
        job_url = "https://www.linkedin.com/jobs/collections/recommended/"
        self.driver.get(job_url)
        time.sleep(5)
        
        try:
            company_element = self.driver.find_element(
                By.XPATH, "//div[contains(@class, 'job-details-jobs-unified-top-card__company-name')]//a"
            )
            company_url = company_element.get_attribute("href")
            if not company_url:
                print("❌ No company URL found.")
                return
            
            # Normalize the company URL to keep only /company/<name>
            parsed = urlparse(company_url)
            parts = parsed.path.split('/')
            try:
                idx = parts.index("company")
                base_path = '/'.join(parts[:idx+2])
            except ValueError:
                base_path = parsed.path  # fallback
            
            people_url = urlunparse((parsed.scheme, parsed.netloc, base_path + "/people/", '', '', ''))            
            self.driver.get(people_url)
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

