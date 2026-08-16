import os
import json
from flask import Flask, render_template, request, redirect, url_for
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from werkzeug.utils import secure_filename

app = Flask(__name__)

# --- CONFIGURATION ---
# PASTE YOUR GOOGLE DRIVE FOLDER ID HERE
FOLDER_ID = 'PASTE_YOUR_FOLDER_ID_HERE' 
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'credentials.json'

# Safely build credentials file from Render Environment Variable
google_creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
if google_creds_json:
    with open(SERVICE_ACCOUNT_FILE, 'w') as f:
        f.write(google_creds_json)

creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB limit

entries = []

@app.route('/')
def index():
    return render_template('index.html', entries=entries)

@app.route('/upload', methods=['POST'])
def upload_file():
    title = request.form.get('title')
    category = request.form.get('category')
    date = request.form.get('date')
    summary = request.form.get('summary')
    
    uploaded_files = request.files.getlist('files')
    file_id = ''
    gallery = []

    for file in uploaded_files:
        if file and file.filename:
            safe_name = secure_filename(file.filename)
            file.save(safe_name)
            
            # Upload to Google Drive
            file_metadata = {'name': safe_name, 'parents': [FOLDER_ID]}
            media = MediaFileUpload(safe_name, resumable=True)
            drive_file = drive_service.files().create(body=file_metadata, media_body=media).execute()
            
            drive_id = drive_file.get('id')
            if not file_id: file_id = drive_id
            gallery.append(drive_id)
            
            os.remove(safe_name)

    badge = "bg-indigo-50 text-indigo-700"
    if category == "Event Report": badge = "bg-emerald-50 text-emerald-700"
    elif category == "Field Activity": badge = "bg-amber-50 text-amber-700"

    entries.insert(0, {
        'title': title, 'category': category, 'date': date,
        'summary': summary, 'file_id': file_id, 'gallery': gallery, 'badge': badge
    })
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
