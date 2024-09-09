# Google Credentials Automation

**Disclaimer:**  
This code is provided as a sample program to demonstrate how automation works. It is intended for educational purposes only. The author is not responsible for any issues or damages that may arise from the use of this code.

## Overview

This Python script demonstrates how to automate Google API credentials management and interact with Google Sheets using OAuth2 authentication. It includes functionality for installing required packages, handling Google OAuth2 flow, and updating a Google Sheet.

## Installation

The script automatically installs required packages if they are not already installed. The required packages are:

- `google-auth-oauthlib`
- `google-auth`
- `selenium_driverless`
- `requests`
- `urllib3`
- `warnings`

The `install` function ensures these packages are installed silently. If a package is missing, it is installed using `pip`.

## Example Usage

1. **Setup Google Credentials:**

    Replace placeholders with your credentials and configuration:
    
    ```python
    from auto_google_creds import GoogleCredentials
    import os
    import gspread

    creds = GoogleCredentials(
        email="<EMAIL>",  # Replace with your email address
        password="<PASSWORD>",  # Replace with your password
        credentials_path=os.path.join(os.getcwd(), 'credentials.json'),
        scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'],
        proxy="<PROXY>",  # Replace with your proxy if needed
        send_code_no_valid="<ENDPOINT>"  # Replace with your endpoint if needed
        headless=False # Headless is not stable in the off state, if you have a proxy to use, without a proxy it works fine (the problem is exactly in the authorization, the thing is that if there is a proxy, it can request several codes through the phone, and I provided only 1 time)
    ).get()

    client = gspread.authorize(creds)
    SPREADSHEET_ID = '<SPREADSHEET_ID>'  # Replace with your Google Sheets ID
    spreadsheet_url = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit'
    sheet = client.open_by_url(spreadsheet_url)
    worksheet = sheet.get_worksheet(0)
    data = worksheet.get_all_values()
    print(data)

    arr = "Hello friend, I have saved you some time with this program"
    arr = arr.split(" ")
    for idx, item in enumerate(arr):
        cell = f'A{idx+1}'
        worksheet.update(cell, [[item]])
    ```

    Ensure that the placeholders `<EMAIL>`, `<PASSWORD>`, `<PROXY>`, `<ENDPOINT>`, and `<SPREADSHEET_ID>` are replaced with actual values.

2. **Run the Script:**

    Execute the script to manage Google API credentials and update the Google Sheet. The script handles authentication via a web browser and updates the specified Google Sheet with the provided data.

## License

This code is provided for educational purposes only. Use it at your own risk. The author disclaims any responsibility for any issues or damages that may arise from the use of this code.