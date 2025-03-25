from datetime import datetime
import os

from main import keywords, Crawl

# Your existing code...
# After the connection request logic
if __name__ == '__main__':
    today = datetime.today()
    weekday = today.weekday()  # 0-6
    key = keywords[weekday]
    week_number = today.isocalendar()[1]  # 0-52
    crawler = Crawl()

    output_dir = "/Users/saurabhsaha/Documents/GitHub/linkedinselenium"  # Specify the folder where the cron job runs
    output_file = os.path.join(output_dir, f"linkedin_connection_{today.strftime('%Y-%m-%d_%H-%M-%S')}.log")
    with open(output_file, "a") as f:
        crawler.fetch(key, week_number)
        crawler.suggestions(key, week_number)
        crawler.recommended_jobs(weekday)
        f.write(f"🚀 Done Sending Connection Requests! Total: {crawler.connected_count}\n")

    crawler.driver.quit()
