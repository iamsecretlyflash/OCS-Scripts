## Steps to run
- Install the dependencies using the the pip command
- You will need chromdriver to run the application using selenium. Download [here](https://github.com/GoogleChromeLabs/chrome-for-testing#other-api-endpoints)
- Make sure you edit the chrome driver path in both the scripts.
- You will also need to edit the Google Profile Path. Example path mentioned in the scripts
- Because of captcha, you will first need to login to OCS. To do this run the script with any args(like literally any)
- Then run the script without any args and you should see events getting added to your apple calendar.

## Installing Dependencies
'''console
pip install -r requirements.txt
'''

## Running the scripts
'''Python
python3 create_event.py 10
python3 ceate_event.py

python3 apply_deadlines.py 10
python3 apply_deadlines.py
'''
