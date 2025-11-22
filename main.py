import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, urlunparse
import os
from dotenv import load_dotenv
import chromedriver_autoinstaller

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
    def __init__(self, headless=True):
        self.headless = headless
        self.connected_count = 0
        self.driver = self.__login()
        self.wait = WebDriverWait(self.driver, 15)  # Wait up to 15 seconds for elements

    def __login(self):
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")

        chromedriver_autoinstaller.install()
        driver = webdriver.Chrome(options=options)

        driver.get("https://www.linkedin.com/login")
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(LINKEDIN_EMAIL)
        driver.find_element(By.ID, "password").send_keys(LINKEDIN_PASSWORD)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        profile_element_xpath = "//a[@data-view-name='identity-self-profile']"
        wait.until(EC.visibility_of_element_located((By.XPATH, profile_element_xpath)))
        print("✅ Logged in successfully")
        time.sleep(2)
        return driver

    def recommended_jobs(self, job_index):
        job_url = "https://www.linkedin.com/jobs/collections/recommended/"
        self.driver.get(job_url)

        job_list_container_xpath = "//div[contains(@class, 'jobs-search-results-list__list-item--active')]"

        # Wait for the recommended jobs list to be visible
        self.wait.until(
            EC.presence_of_element_located((By.XPATH, job_list_container_xpath))
        )

        try:
            company_element = self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//div[contains(@class, 'job-details-jobs-unified-top-card__company-name')]//a"
                ))
            )
            company_url = company_element.get_attribute("href")
            if not company_url:
                print("❌ No company URL found")
                return
            parsed = urlparse(company_url)
            parts = parsed.path.split('/')
            try:
                idx = parts.index("company")
                base_path = '/'.join(parts[:idx+2])
            except ValueError:
                base_path = parsed.path

            people_url = urlunparse((parsed.scheme, parsed.netloc, base_path + "/people/", '', '', ''))
            time.sleep(2)
            self.driver.get(people_url)
            self.wait.until(
               EC.presence_of_element_located((
                    By.CLASS_NAME, "top-card-background-hero-image"
                ))
            )
            time.sleep(2)
            self.connect(reco=True)
        except Exception as e:
            print(f"❌ Error: {e}")

    def fetch(self, keyword, page_number):
        search_url = f"https://www.linkedin.com/search/results/people/?keywords={keyword}&page={page_number}"
        self.driver.get(search_url)
        time.sleep(2)
        self.connect()

    def connect(self, reco= False):
        prev_count = 0
        while True:
            if reco:
                buttons = self.driver.find_elements(By.XPATH, "//button[.//span[normalize-space()='Connect']]")
            else:
                buttons = self.driver.find_elements(
                    By.XPATH,
                    "//div[@data-view-name='edge-creation-connect-action']"
                    "//span[span[normalize-space()='Connect']]"
                )            
            curr_count = len(buttons)
            if curr_count == 0:
                print("No connections found")
                return

            # Scroll if new buttons may exist
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

            if reco:
                buttons_after_scroll = self.driver.find_elements(By.XPATH, "//button[.//span[normalize-space()='Connect']]")
            else:
                buttons_after_scroll = self.driver.find_elements(
                    By.XPATH,
                    "//div[@data-view-name='edge-creation-connect-action']"
                    "//span[span[normalize-space()='Connect']]"
                )
            new_count = len(buttons_after_scroll)

            # Stop if no new buttons loaded
            if new_count <= curr_count:
                break

            prev_count = curr_count

        # Click all buttons
        for button in buttons_after_scroll:
            try:
                self.driver.execute_script("arguments[0].click();", button)
                time.sleep(1)
                if reco:
                    send_buttons = self.driver.find_elements(
                        By.XPATH, "//button[.//span[normalize-space()='Send without a note']]"
                    )
                    if send_buttons:
                        self.driver.execute_script("arguments[0].click();", send_buttons[0])
                else:
                    host = self.driver.find_element(By.XPATH, "/html/body/div/div[4]")
                    # query inside shadow DOM and return the FINAL element
                    send_button = self.driver.execute_script("""
                        return arguments[0].shadowRoot
                            .querySelector("button[aria-label='Send without a note']");
                    """, host)
                    if send_button:
                        self.driver.execute_script("arguments[0].click();", send_button)
                print("✅ Connection Request Sent")
                self.connected_count += 1
                time.sleep(2)
            except Exception as e:
                print(f"❌ Error: {e}")
                break

