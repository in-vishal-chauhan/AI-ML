import schedule
import time
from datetime import datetime

def process_emails():
    print(f"Processing emails at {datetime.now().strftime('%H:%M:%S')}")
    # Add your email processing logic here

# Schedule to run every 2 minutes
schedule.every(2).minutes.do(process_emails)

# Keep the script running
while True:
    try:
        print("Scheduler run")
        schedule.run_pending()
        time.sleep(60)
    except KeyboardInterrupt:
        print("Scheduler stopped")
        break
    if __name__ == "__main__":
        process_emails()
