from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import subprocess
import sys
from datetime import datetime

def fetch_table():
    DATA_URL = 'https://ocs.iitd.ac.in/portal/student/notify'
    CHROME_DRIVER_PATH = './chromedriver-mac-arm64/chromedriver'
    USER_DATA_DIR = '/Users/vaibhavseth/Library/Application Support/Google/Chrome/Default'
    service = ChromeService(executable_path=CHROME_DRIVER_PATH)
    options = webdriver.ChromeOptions()
    if len(sys.argv) == 1 :
        options.add_argument('headless')
    options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 20)
    try:
        driver.get(DATA_URL)
        print("Navigated to data page.")
        time.sleep(5)
        table_selector = 'table.mat-table.cdk-table.mat-sort' 
        table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, table_selector)))
        print("Table found on the page.")
        try:
            tbody = table.find_element(By.TAG_NAME, 'tbody')
        except:
            tbody = table 
        rows = tbody.find_elements(By.CSS_SELECTOR, 'tr.mat-row') 
        print(f"Number of rows found: {len(rows)}")
        if not rows:
            print("No rows found in the table.")
            return pd.DataFrame() 
        else:
            headers = ['Company Name', 'Date & Time', 'Venue']
            data = []
            for index, row in enumerate(rows, start=1):
                cells = row.find_elements(By.TAG_NAME, 'td')
                if len(cells) >= 4:
                    company = cells[0].text.strip()
                    datetime_ = cells[1].text.strip()
                    venue = cells[2].text.strip()
                    data.append([company, datetime_, venue])
                    print(f"Row {index}: {company}, {datetime_}, {venue}")
                else:
                    print(f"Row {index} does not have enough cells.")
            df = pd.DataFrame(data, columns=headers)
            if df.empty:
                print("No data extracted from the table.")
            else:
                print("Extracted Data:")
                print(df)
            return df  

    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()  
    finally:
        driver.quit()
        print("Browser closed.")

def create_apple_calendar_event(title, start_date, start_time, end_time, description=""):
    import subprocess
    from datetime import datetime

    try:
        event_start = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
        event_end = datetime.strptime(f"{start_date} {end_time}", "%Y-%m-%d %H:%M")
        event_start_str = event_start.strftime("%A, %d %B %Y at %I:%M:%S %p")
        event_end_str = event_end.strftime("%A, %d %B %Y at %I:%M:%S %p")
        title_escaped = title.replace('"', '\\"')
        description_escaped = description.replace('"', '\\"')
        script = 
        f"""
        set eventTitle to "{title_escaped}"
        set eventDescription to "{description_escaped}"
        set eventStart to date "{event_start_str}"
        set eventEnd to date "{event_end_str}"

        tell application "Calendar"
            tell calendar "Placements"
                -- Check if an event with the same summary exists
                set existingEvents to (every event whose summary is eventTitle)

                if (count of existingEvents) is 0 then
                    -- Create the new event
                    set new_event to make new event with properties {{summary:eventTitle, start date:eventStart, end date:eventEnd, description:eventDescription}}

                    -- Add 5-minute reminder
                    tell new_event
                        make new display alarm with properties {{trigger interval:-5}}
                    end tell

                    -- Add 15-minute reminder
                    tell new_event
                        make new display alarm with properties {{trigger interval:-15}}
                    end tell

                    -- Add 30-minute reminder
                    tell new_event
                        make new display alarm with properties {{trigger interval:-30}}
                    end tell
                end if
            end tell
        end tell 
        """
        
        subprocess.run(["osascript", "-e", script], check=True)
        print(f"Event '{title}' processed successfully!")

    except subprocess.CalledProcessError as e:
        print(f"Error executing AppleScript: {e}")
    except ValueError as ve:
        print(f"Date/time parsing error: {ve}")
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")

def add_all_events():
    df = fetch_table()
    if df.empty:
        print("No data available to create events.")
        return
    for index, row in df.iterrows():
        title = row['Company Name']
        date_time_str = row['Date & Time']
        venue = row['Venue']
        try:
            current_year = datetime.now().year
            date_time_str_with_year = f"{date_time_str} {current_year}"
            start_datetime = datetime.strptime(date_time_str_with_year, "%d %b, %I:%M %p %Y")
        except ValueError as ve:
            print(f"Date parsing error for '{title}': {ve}")
            continue 
        end_datetime = start_datetime + pd.Timedelta(hours=1)
        start_date_str = start_datetime.strftime("%Y-%m-%d")
        start_time_str = start_datetime.strftime("%H:%M")
        end_time_str = end_datetime.strftime("%H:%M")
        create_apple_calendar_event(
            title=title,
            start_date=start_date_str,
            start_time=start_time_str,
            end_time=end_time_str,
            description=f"Venue: {venue}"
        )

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'create_event':
        if len(sys.argv) < 6:
            print("Usage: python create_event.py create_event 'Event Title' YYYY-MM-DD HH:MM HH:MM ['Description']")
            sys.exit(1)

        title = sys.argv[2]
        start_date = sys.argv[3]
        start_time = sys.argv[4]
        end_time = sys.argv[5]
        description = sys.argv[6] if len(sys.argv) > 6 else ""

        create_apple_calendar_event(title, start_date, start_time, end_time, description)
    else:
        add_all_events()
