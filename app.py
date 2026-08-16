import os
import json
import base64
from flask import Flask, render_template, request, redirect, url_for
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from werkzeug.utils import secure_filename

app = Flask(__name__)

# --- CONFIGURATION ---
FOLDER_ID = '1IYKRqFhhhArogNeuRe3H-bUT3TQhGk7a' 
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'credentials.json'

# Smart flexible loader: automatically handles Base64, raw JSON, or escaped newlines
google_creds_input = os.environ.get('GOOGLE_CREDENTIALS_JSON', '').strip()
if google_creds_input:
    try:
        # First, try to decode as Base64
        decoded_bytes = base64.b64decode(google_creds_input.encode('utf-8'), validate=True)
        creds_text = decoded_bytes.decode('utf-8')
    except Exception:
        # If it's not valid Base64, assume it's raw text/JSON
        creds_text = google_creds_input

    try:
        creds_dict = json.loads(creds_text)
    except json.JSONDecodeError:
        # Fallback to fix escaped newlines if raw text had formatting quirks
        fixed_text = creds_text.replace('\\\\n', '\\n')
        creds_dict = json.loads(fixed_text)

    # Ensure proper newline formatting in the private key
    if 'private_key' in creds_dict:
        creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')

    with open(SERVICE_ACCOUNT_FILE, 'w', encoding='utf-8') as f:
        json.dump(creds_dict, f, ensure_ascii=False)

creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB limit

entries = []

@app.route('/')
def index():
    category_filter = request.args.get('category', 'all')
    search_query = request.args.get('search', '').lower()
    
    filtered_entries = entries
    if category_filter != 'all':
        filtered_entries = [e for e in filtered_entries if e['category'] == category_filter]
        
    if search_query:
        filtered_entries = [e for e in filtered_entries if search_query in e['title'].lower() or search_query in e['summary'].lower()]
        
    return render_template('index.html', entries=filtered_entries, current_category=category_filter)

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
            
            # Upload directly to Google Drive
            file_metadata = {'name': safe_name, 'parents': [FOLDER_ID]}
            media = MediaFileUpload(safe_name, resumable=True)
            drive_file = drive_service.files().create(body=file_metadata, media_body=media).execute()
            
            drive_id = drive_file.get('id')
            if not file_id: 
                file_id = drive_id
            gallery.append(drive_id)
            
            # Cleanup local temp storage
            if os.path.exists(safe_name):
                os.remove(safe_name)

    badge = "bg-indigo-50 text-indigo-700"
    if category == "Event Report": 
        badge = "bg-emerald-50 text-emerald-700"
    elif category == "Field Activity": 
        badge = "bg-amber-50 text-amber-700"

    entries.insert(0, {
        'title': title, 
        'category': category, 
        'date': date,
        'summary': summary, 
        'file_id': file_id, 
        'gallery': gallery, 
        'badge': badge
    })
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
