import imaplib
import email
import os
import csv
import io
import sys
import datetime

# --- CONFIGURATION ---
EMAIL_USER = "aoml.glider@gmail.com"
EMAIL_PASS = "REPLACEWITHPASSWORD"   
DEST_FILE = "messages/status.csv"
EMAIL_SUBJECT = "REPLACEWITHKEYSUBJECT" # change this in the google doc javascript to add the same subject on the emails
DAYS_TO_KEEP = 30
# ---------------------

os.makedirs(os.path.dirname(DEST_FILE), exist_ok=True)
print("Checking Gmail inbox for the latest status update...")

try:
    # Connect to Gmail
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select("inbox")
    
    # 1. Search for ALL emails with our specific subject to extract the latest CSV
    status, messages = mail.search(None, f'(SUBJECT "{EMAIL_SUBJECT}")')
    email_ids = messages[0].split()
    
    if email_ids:
        print(f"Found {len(email_ids)} update(s). Processing newest first...")
        
        # Reverse the list so the most recent email is index 0
        email_ids.reverse()
        file_updated = False
        
        for num in email_ids:
            status, data = mail.fetch(num, "(RFC822)")
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            # Extract the CSV attachment
            csv_content = ""
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                
                filename = part.get_filename()
                if filename and filename.endswith('.csv'):
                    csv_content = part.get_payload(decode=True).decode('utf-8')
                    break 
                
            # Validate and write the first (newest) valid CSV we find
            if csv_content:
                try:
                    f_io = io.StringIO(csv_content.strip())
                    reader = csv.reader(f_io)
                    rows = list(reader)
                    row_count = len(rows)
                    
                    if row_count > 0 and row_count <= 20:
                        max_cols = max(len(row) for row in rows)
                        if max_cols <= 20:
                            with open(DEST_FILE, 'w', encoding='utf-8') as f:
                                f.write(csv_content.strip())
                            print(f"Successfully recovered/updated {DEST_FILE} from the latest valid email.")
                            file_updated = True
                            
                            # Break out of the loop since we found the latest valid one
                            break 
                        else:
                            print(f"Validation failed (Too many columns: {max_cols}). Discarding and checking next recent...")
                    else:
                        print(f"Validation failed (Invalid row count: {row_count}). Discarding and checking next recent...")
                except Exception as e:
                    print(f"Failed to parse CSV: {e}. Discarding and checking next recent...")
            
        if not file_updated:
            print("No valid CSV found in any of the matching emails.")
    else:
        print("No status emails found.")
        
    # 2. Cleanup old emails (Older than 30 days)
    cutoff_date = (datetime.date.today() - datetime.timedelta(days=DAYS_TO_KEEP)).strftime("%d-%b-%Y")
    print(f"Searching for backup emails older than {cutoff_date} to clean up...")
    
    # Search for emails matching the subject BEFORE the cutoff date
    cleanup_status, cleanup_messages = mail.search(None, f'(SUBJECT "{EMAIL_SUBJECT}" BEFORE {cutoff_date})')
    old_email_ids = cleanup_messages[0].split()
    
    if old_email_ids:
        print(f"Found {len(old_email_ids)} old email(s). Deleting...")
        for num in old_email_ids:
            mail.store(num, '+FLAGS', '\\Deleted')
        
        # Permanently remove the flagged emails
        mail.expunge()
        print("Cleanup complete.")
    else:
        print("No old emails required cleanup.")
    
    mail.logout()
    
except Exception as e:
    print(f"Connection or processing error: {e}")
    sys.exit(1)