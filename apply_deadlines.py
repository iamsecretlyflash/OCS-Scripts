from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import subprocess
import sys
from datetime import datetime, timedelta
import time

def fetch_table():
    DATA_URL = 'https://ocs.iitd.ac.in/portal/student/applications'
    CHROME_DRIVER_PATH = './chromedriver-mac-arm64/chromedriver'
    USER_DATA_DIR = '/Users/vaibhavseth/Library/Application Support/Google/Chrome/Default'
    service = ChromeService(executable_path=CHROME_DRIVER_PATH)
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 20)
    all_data = []

    try:
        driver.get(DATA_URL)
        print("Navigated to applications page.")
        time.sleep(5)

        while True:
            table_selector = 'table.mat-table.cdk-table.mat-sort'
            table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, table_selector)))
            print("Table found on the page.")

            tbody = table.find_element(By.TAG_NAME, 'tbody')
            rows = tbody.find_elements(By.CSS_SELECTOR, 'tr.mat-row')
            print(f"Number of rows found: {len(rows)}")

            if not rows:
                print("No rows found in the table.")
                break 
            else:
                headers = ['Company Name', 'Apply Deadline']
                data = []
                for index, row in enumerate(rows, start=1):
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    if len(cells) >= 2:
                        company = cells[0].text.strip()
                        apply_cell = cells[1]
                        apply_cell.click()
                        print(f"Clicked apply cell for row {index}...")
                        deadlines_text = cells[1].text.strip()
                        apply_deadline = deadlines_text.split('\n')[0].strip()
                        if apply_deadline == "None Yet":
                            continue
                        data.append([company, apply_deadline])
                        print(f"Row {index}: {company}, {apply_deadline}")
                    else:
                        print(f"Row {index} does not have enough cells.")
                all_data.extend(data)
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, 'button.mat-paginator-navigation-next')
                if "disabled" in next_button.get_attribute("class"):
                    print("No more pages to process.")
                    break
                else:
                    next_button.click()
                    print("Navigating to the next page...")
                    time.sleep(5)
            except Exception as e:
                print("Next button not found or an error occurred:", e)
                break 
        df = pd.DataFrame(all_data, columns=headers)
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

    try:
        event_start = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
        event_end = datetime.strptime(f"{start_date} {end_time}", "%Y-%m-%d %H:%M")

        event_start_str = event_start.strftime("%A, %d %B %Y at %I:%M:%S %p")
        event_end_str = event_end.strftime("%A, %d %B %Y at %I:%M:%S %p")

        title_escaped = title.replace('"', '\\"')
        description_escaped = description.replace('"', '\\"')

        script = f"""
        set eventTitle to "{title_escaped}"
        set eventDescription to "{description_escaped}"
        set eventStart to date "{event_start_str}"
        set eventEnd to date "{event_end_str}"

        tell application "Calendar"
            tell calendar "Placements"
                set existingEvents to (every event whose summary is eventTitle)

                if (count of existingEvents) is 0 then
                    set new_event to make new event with properties {{summary:eventTitle, start date:eventStart, end date:eventEnd, description:eventDescription}}

                    tell new_event
                        make new display alarm with properties {{trigger interval:-5}}
                    end tell

                    tell new_event
                        make new display alarm with properties {{trigger interval:-15}}
                    end tell

                    tell new_event
                        make new display alarm with properties {{trigger interval:-30}}
                    end tell
                end if
            end tell
        end tell
        """
        print(script)
        subprocess.run(["osascript", "-e", script], check=True)
        print(f"Event '{title}' created successfully!")

    except Exception as e:
        print(f"Error creating calendar event: {e}")

def add_all_events():
    df = fetch_table()

    if df.empty:
        print("No data available to create events.")
        return

    for index, row in df.iterrows():
        title = row['Company Name']
        apply_deadline = row['Apply Deadline']

        try:
            current_year = datetime.now().year
            apply_deadline_with_year = f"{apply_deadline} {current_year}"
            start_datetime = datetime.strptime(apply_deadline_with_year, "Apply: %a, %b %d, %I:%M %p %Y")
        except ValueError as ve:
            print(f"Date parsing error for '{title}': {ve}")
            continue

        end_datetime = start_datetime
        start_datetime =  start_datetime - timedelta(hours=1)
        start_date_str = start_datetime.strftime("%Y-%m-%d")
        start_time_str = start_datetime.strftime("%H:%M")
        end_time_str = end_datetime.strftime("%H:%M")

        create_apple_calendar_event(
            title=title,
            start_date=start_date_str,
            start_time=start_time_str,
            end_time=end_time_str,
            description="OCS Apply Deadline"
        )

if __name__ == "__main__":
    add_all_events()
