import psycopg2
import time
import re

def connect_to_database():
    conn = psycopg2.connect(
        host="localhost",
        database="gmail",
        user="postgres",
        password=""
    )
    return conn

def parse_email_content(content):
    pattern = r"\b\d{6}\b"
    match = re.search(pattern, content)
    if match:
        return match.group()
    return None

def store_verification_code(code, timestamp, status):
    conn = connect_to_database()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO verification_codes (code, timestamp, status) VALUES (%s, %s, %s)",
        (code, timestamp, status)
    )
    conn.commit()
    print(f"Stored verification code: {code}, Timestamp: {timestamp}, Status: {status}")
    cur.close()
    conn.close()

def get_latest_valid_code():
    conn = connect_to_database()
    cur = conn.cursor()
    cur.execute(
        "SELECT code FROM verification_codes WHERE status = 'valid' ORDER BY timestamp DESC LIMIT 1"
    )
    result = cur.fetchone()
    cur.close()
    conn.close()
    if result:
        print(f"Retrieved latest valid code: {result[0]}")
        return result[0]
    print("No valid verification code found.")
    return None

def update_code_status(code, status):
    conn = connect_to_database()
    cur = conn.cursor()
    cur.execute(
        "UPDATE verification_codes SET status = %s WHERE code = %s",
        (status, code)
    )
    conn.commit()
    print(f"Updated status of code {code} to {status}")
    cur.close()
    conn.close()

def invalidate_all_codes_except_latest():
    conn = connect_to_database()
    cur = conn.cursor()
    cur.execute(
        "UPDATE verification_codes SET status = 'invalid' WHERE code != (SELECT code FROM verification_codes ORDER BY timestamp DESC LIMIT 1)"
    )
    conn.commit()
    print("Invalidated all verification codes except the latest one.")
    cur.close()
    conn.close()

def invalidate_expired_codes():
    conn = connect_to_database()
    cur = conn.cursor()
    cur.execute(
        "UPDATE verification_codes SET status = 'invalid' WHERE timestamp < NOW() - INTERVAL '19 seconds' AND status = 'valid'"
    )
    conn.commit()
    print("Invalidated expired verification codes.")
    cur.close()
    conn.close()

def print_latest_emails(cur):
    cur.execute("SELECT id, subject, sender, date FROM emails ORDER BY id DESC LIMIT 10")
    emails = cur.fetchall()
    print("Latest 10 emails:")
    for email in emails:
        email_id, subject, sender, date = email
        print(f"ID: {email_id}, Subject: {subject}, Sender: {sender}, Date: {date}")

def monitor_gmail_table():
    conn = connect_to_database()
    cur = conn.cursor()

    last_email_id = None
    new_email_count = 0
    start_time = time.time()

    while True:
        print(f"Monitoring Gmail table for new emails... ({time.strftime('%Y-%m-%d %H:%M:%S')})")
        cur.execute("SELECT id, content FROM emails WHERE id > %s ORDER BY id", (last_email_id,) if last_email_id else (0,))
        new_emails = cur.fetchall()

        if new_emails:
            if time.time() - start_time >= 10:  # Check if 10 seconds have passed since the start
                new_email_count += len(new_emails)
            print(f"Found {len(new_emails)} new email(s).")

            for email in new_emails:
                email_id, content = email
                last_email_id = email_id
                code = parse_email_content(content)
                if code:
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    store_verification_code(code, timestamp, "valid")
                    print(f"New verification code found: {code}")
                    invalidate_all_codes_except_latest()
                else:
                    print("No verification code found in the email content.")
        else:
            print("No new emails found.")

        print(f"Total new emails received: {new_email_count}")
        print_latest_emails(cur)  # Print the latest 10 emails
        invalidate_expired_codes()  # Invalidate expired verification codes
        time.sleep(1)  # Wait for 1 second before checking again

    cur.close()
    conn.close()

if __name__ == "__main__":
    print("Starting Gmail parser...")
    monitor_gmail_table()
