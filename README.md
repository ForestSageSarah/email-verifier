# Email Verifier

This is a simple Python application that verifies a list of emails using the VerifyMail.io API. The application allows you to check if an email is disposable and writes the results to a file.

## Features

- **API Key Management:** Save and load your VerifyMail.io API key easily.
- **Email List:** Input emails through a text widget or load them from a file.
- **Verification Progress:** Track the progress of email verification with a progress bar.
- **Pause and Stop:** Pause and stop the verification process at any time.
- **Output:** Results are written to a file ('Checked_Emails.txt') and displayed in the status label.
- **Error Handling:** Handle HTTP status code 403 (API key error) and display appropriate messages.

## Prerequisites

- Python 3.x
- Required Python packages: `tkinter`, `requests`, `tqdm`

## Getting Started

1. Clone the repository:

   ```bash
   git clone https://github.com/ForestSageSarah/email-verifier.git
   cd email-verifier
   ```

2. Install the required packages:
	
	```bash
    pip install -r requirements.txt
    ```

3. Run the application:

	```bash
	python email_verifier.py
	```

## Usage

- Enter your VerifyMail.io API key in the provided entry field and click "Save API Key."
- Input emails into the text widget or load them from a file using the "Browse" button.
- Click the "Run" button to start the verification process.
- Track the progress with the progress bar and view results in the "Checked_Emails.txt" file.
- Pause or stop the verification process as needed.

## License
This project is licensed under the GNU General Public License v3.0.

For more details, see the LICENSE.md file.

## Acknowledgments
- VerifyMail.io for providing the email verification service.
    - https://verifymail.io/api-documentation  
