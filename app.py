import streamlit as st
import pandas as pd
import os
import io

# Import custom logic
from pdf_parser import extract_text_from_pdf
from ai_processor import extract_shifts_with_ai
from calendar_sync import sync_shifts_to_calendar, delete_events_from_calendar
from email_fetcher import fetch_pdf_from_email

st.set_page_config(page_title="ShiftPlanner", page_icon="📅", layout="wide")

st.title("📅 ShiftPlanner")

# --- Sidebar ---
with st.sidebar:
    st.header("Configuration")
    
    # AI Config
    # Pre-fill from environment variable if it exists, but allow user to override.
    env_api_key = os.environ.get("OPENAI_API_KEY", "")
    api_key = st.text_input("OpenAI API Key", type="password", value=env_api_key)

    # Ensure the environment variable is set for the backend functions for this session.
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        
    st.divider()
    
    # Email Config
    st.subheader("Email Settings")
    email_user = st.text_input("Email Address")
    email_pass = st.text_input("App Password", type="password", help="Use an App Password, not your login password.")
    imap_server = st.text_input("IMAP Server", value="imap.gmail.com")
    subject_filter = st.text_input("Email Subject Filter", value="Roster")
    
    if st.button("Check Email for Roster"):
        if not (email_user and email_pass):
            st.error("Please provide email credentials.")
        else:
            with st.spinner("Connecting to email..."):
                pdf_path, msg = fetch_pdf_from_email(imap_server, email_user, email_pass, subject_filter=subject_filter)
                
                if pdf_path:
                    st.success(msg)
                    st.session_state['uploaded_file_path'] = pdf_path
                else:
                    st.warning(msg)

# --- Main Area ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Input Source")
    
    # Option A: Manual Upload
    uploaded_file = st.file_uploader("Upload PDF manually", type="pdf")
    
    # Option B: File from Email
    if 'uploaded_file_path' in st.session_state:
        email_file_path = st.session_state['uploaded_file_path']
        if os.path.exists(email_file_path):
            st.info(f"Using file from email: {os.path.basename(email_file_path)}")
            # If manual upload is empty, use the email file
            if not uploaded_file:
                # Read the file into an in-memory buffer to avoid resource leaks
                # across Streamlit reruns.
                with open(email_file_path, "rb") as f:
                    uploaded_file = io.BytesIO(f.read())

    if uploaded_file and api_key:
        if st.button("Analyze Roster", type="primary"):
            with st.spinner("Extracting and Analyzing..."):
                # Reset stream position if it's a file object
                if hasattr(uploaded_file, 'seek'):
                    uploaded_file.seek(0)
                    
                raw_text = extract_text_from_pdf(uploaded_file)
                shifts_data, error_message = extract_shifts_with_ai(raw_text)
                
                if error_message:
                    st.error(f"Analysis Failed: {error_message}")
                elif shifts_data is not None:
                    st.session_state['shifts'] = shifts_data
                    if shifts_data:
                        st.success(f"Extracted {len(shifts_data)} shifts.")
                    else:
                        st.warning("Analysis complete, but no shifts were found in the PDF.")
    elif not api_key:
        st.warning("Please enter your OpenAI API Key in the sidebar.")

with col2:
    st.subheader("2. Review & Sync")
    
    if 'shifts' in st.session_state and st.session_state['shifts']:
        df = pd.DataFrame(st.session_state['shifts'])
        
        # Editable Dataframe
        edited_df = st.data_editor(df, num_rows="dynamic")
        
        st.divider()
        
        if st.button("🚀 Sync to Google Calendar"):
            # Check for credentials before attempting sync
            if not os.path.exists("token.json") and not os.path.exists("credentials.json"):
                st.error("Missing Google Credentials! Please upload 'credentials.json' to the server folder.")
            else:
                with st.spinner("Syncing..."):
                    try:
                        count, event_ids, errors = sync_shifts_to_calendar(edited_df)
                        
                        if count > 0:
                            st.balloons()
                            st.success(f"Successfully added {count} events!")
                            # Store IDs in session state so we can undo later
                            st.session_state['last_synced_event_ids'] = event_ids
                        
                        if errors:
                            st.error(f"Encountered {len(errors)} errors.")
                            with st.expander("View Errors"):
                                st.write(errors)
                    except Exception as e:
                        st.error(f"Sync failed: {e}")

        # Undo Button
        if 'last_synced_event_ids' in st.session_state and st.session_state['last_synced_event_ids']:
            st.warning("Need to undo?")
            if st.button("🗑️ Delete Last Synced Events"):
                with st.spinner("Deleting events..."):
                    del_count, del_errors = delete_events_from_calendar(st.session_state['last_synced_event_ids'])
                    st.success(f"Deleted {del_count} events.")
                    if del_errors:
                        st.error(f"Failed to delete some events: {del_errors}")
                    # Clear the state so button disappears
                    del st.session_state['last_synced_event_ids']