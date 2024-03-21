# GmailVerificationCodeParser

GmailVerificationCodeParser is an open-source Python project that complements the [GmailFetcher](https://github.com/inabakumori/GmailFetcher) project. It monitors a PostgreSQL database for new emails fetched by GmailFetcher, extracts verification codes from the email content, and stores the codes along with their timestamps and validity status in a separate database table. This tool is useful for automating the process of retrieving verification codes from emails and managing their validity.

Note: This project has been successfully tested on macOS.

## Features

- Monitors a PostgreSQL database for new emails fetched by GmailFetcher.
- Extracts verification codes from the email content using regular expressions.
- Stores verification codes, timestamps, and validity status in a separate database table.
- Invalidates expired verification codes based on a configurable time threshold.
- Retrieves the latest valid verification code.

## Prerequisites

- Python 3.x
- PostgreSQL
- GmailFetcher project set up and running

## Getting Started

### Step 1: Clone the Repository

```bash
git clone https://github.com/inabakumori/GmailVerificationCodeParser.git
cd GmailVerificationCodeParser
```

### Step 2: Set Up a Virtual Environment

Create and activate a virtual environment to manage dependencies:

```bash
python3 -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`
```

### Step 3: Install Dependencies

Install the required Python packages:

```bash
pip install psycopg2-binary
```

### Step 4: Prepare the PostgreSQL Database

#### Create the verification_codes Table

Connect to the `gmail` database created for the GmailFetcher project using `psql`:

```bash
psql -d gmail -U your_username
```

Replace `your_username` with the username you created or `postgres` if you're using the default.

Create the `verification_codes` table by executing the SQL command:

```sql
CREATE TABLE verification_codes (
    id SERIAL PRIMARY KEY,
    code TEXT,
    timestamp TIMESTAMP,
    status TEXT
);
```

Verify the table creation (optional):

```
\dt
```

Exit `psql`:

```
\q
```

### Step 5: Update GmailVerificationCodeParser Script

Update the `gmail_verification_code_parser.py` script with the PostgreSQL connection details. Replace `your_username` and `your_password` with your actual database username and password:

```python
conn = psycopg2.connect(
    host="localhost",
    database="gmail",
    user="your_username",
    password="your_password"
)
```

### Step 6: Running the Script

Run the script:

```bash
python3 gmail_verification_code_parser.py
```

The script will start monitoring the `emails` table in the PostgreSQL database for new emails. It will extract verification codes from the email content, store them in the `verification_codes` table, and manage their validity status.

## Usage Notes

- The script runs in a continuous loop, monitoring the `emails` table for new emails every second. Adjust the `time.sleep(1)` call as needed.
- Verification codes are considered expired and invalidated after 19 seconds by default. Modify the `INTERVAL '19 seconds'` in the `invalidate_expired_codes()` function to change the expiration threshold.
- To stop the script, use `CTRL+C` in the terminal.

## Troubleshooting

Refer to the troubleshooting section in the [GmailFetcher README](https://github.com/inabakumori/GmailFetcher#troubleshooting) for common issues related to PostgreSQL setup and configuration.

## Contributing

Contributions to GmailVerificationCodeParser are welcome! Please follow the standard fork, branch, and pull request workflow.

## License

GmailVerificationCodeParser is open-source software licensed under the GNU General Public License v3.0.
