from datetime import datetime
import os
from main import keywords, Crawl

if __name__ == '__main__':
    today = datetime.today()
    weekday = today.weekday()  # 0-6
    key = keywords[weekday]
    week_number = today.isocalendar()[1]  # 0-52

    print(f"📅 Starting LinkedIn Auto Connector for {today.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 Keyword for today: {key}")
    print(f"📄 Week number: {week_number}")

    crawler = Crawl()
    print("✅ Logged into LinkedIn successfully!")

    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(output_dir, f"linkedin_connection_{today.strftime('%Y-%m-%d_%H-%M-%S')}.log")

    try:
        print("🔍 Fetching connections based on keyword...")
        crawler.fetch(key, week_number)
        print("💼 Processing recommended jobs...")
        crawler.recommended_jobs(weekday)

        print(f"🚀 Done sending connection requests! Total: {crawler.connected_count}")
        with open(output_file, "a") as f:
            f.write(f"{today.strftime('%Y-%m-%d %H:%M:%S')} - Done Sending Connection Requests! Total: {crawler.connected_count}\n")
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
    finally:
        crawler.driver.quit()
        print("🛑 Chrome driver closed, script finished.")
