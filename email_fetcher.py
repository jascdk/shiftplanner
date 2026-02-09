import imaplib
import email
import os
from email.header import decode_header

def fetch_pdf_from_email(imap_server, email_user, email_pass, subject_filter="Shift"):
    """
    Connects to IMAP, searches for the latest email matching criteria, 
    and saves the first PDF attachment found.
    """
    save_folder = "temp_downloads"
    os.makedirs(save_folder, exist_ok=True)
    
    try:
        # Connect to the server
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_user, email_pass)
        mail.select("inbox")

        # Search for emails (Subject filter)
        status, messages = mail.search(None, 'ALL')
        
        if status != "OK":
            return None, "No emails found."

        email_ids = messages[0].split()
        
        # Iterate backwards (newest first)
        for e_id in reversed(email_ids):
            res, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Decode Subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    
                    # Filter
                    if subject_filter.lower() not in subject.lower():
                        continue 

                    # Check for attachments
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_disposition = str(part.get("Content-Disposition"))
                            
                            if "attachment" in content_disposition:
                                filename = part.get_filename()
                                if filename and filename.lower().endswith(".pdf"):
                                    filepath = os.path.join(save_folder, filename)
                                    
                                    with open(filepath, "wb") as f:
                                        f.write(part.get_payload(decode=True))
                                    
                                    mail.close()
                                    mail.logout()
                                    return filepath, f"Downloaded: {filename} from '{subject}'"
        
        mail.close()
        mail.logout()
        return None, "No PDF attachment found in recent emails."

    except Exception as e:
        return None, f"IMAP Error: {e}"