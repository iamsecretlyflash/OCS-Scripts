## Steps to run
- Install the dependencies using the the pip command
- You will need chromdriver to run the application using selenium. Download [here](https://github.com/GoogleChromeLabs/chrome-for-testing#other-api-endpoints)
- Make sure you edit the chrome driver path in both the scripts.
- You will also need to edit the Google Profile Path. Example path mentioned in the scripts
- Because of captcha, you will first need to login to OCS. To do this run the script with any args(like literally any)
- Then run the script without any args and you should see events getting added to your apple calendar.

## Installing Dependencies
```console
pip install -r requirements.txt
```

## Running the scripts
```Python
python3 create_event.py 10
python3 ceate_event.py

python3 apply_deadlines.py 10
python3 apply_deadlines.py
```

## Example Output

After running the command, your calendar should look like this:

<img width="750" alt="Screenshot 2024-09-25 at 7 00 16 PM" src="https://github.com/user-attachments/assets/ff4d8c34-4984-4908-a69b-9ddd69188841">
