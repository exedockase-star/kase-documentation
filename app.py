import os
import json
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# --- CONFIGURATION ---
FOLDER_ID = '19S09p8BGF-eCyRFWY75Chl1mM7w61gec' 
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'credentials.json'

drive_service = None

# Direct credentials dictionary — completely eliminates base64/decoding errors
creds_dict = {
    "type": "service_account",
    "project_id": "rugged-silo-505709-i3",
    "private_key_id": "7c9f19d9bb02fe32084e380faaa3c3c18f55c66a",
    "private_key": (
        "-----BEGIN PRIVATE KEY-----\n"
        "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCl+naQQGtbLsmY\n"
        "lfB6EWo3DjcVR51uqnG/q1ZuOcYh1/bo0mUOyltJ06aBdTDLh1zXPezxexKovE4b\n"
        "goQ07gOeGssPZU0FyX7ISW98AzNvCwLeLjo6Tg++aBYYrDe5ds8EkTk1Mt+C/3MW\n"
        "R1LLGgTf4M9Hc2U+Nmh39ADB9Wcy+uEHGergDrcMHvAFZjf3/N+fNmQwmflJpn5i\n"
        "iYvi94arHE1dbNzvIjRv2C8k1i8KpZ3jDm4fyYEigtuVm28H2DEMvPyAUJptQJWR\n"
        "uSsacwIqRn11cI7R432J+Cu66ZVGdE/npWRma1HdXMp/TCElVFDEPSDWOTPUp2du\n"
        "9KcMHVgxAgMBAAECggEABgQ4WkYFhjiB1QLBZPFe6eg9Yat3BtkNlsKvlz8Hojgt\n"
        "gnbG9ERsTvapu1lbx5Lsb/52CXJaRKzPwYJHh9IlZiynNfOIeVhanMjBrmuAyKqL\n"
        "4/ElyfGEs1SbUXFjszi97BbWDao+jSV0nub+tq9GpDVmWhsSHVFUU93PzbgXMbM0\n"
        "sltBSdICYqBK+pz5Y2lnk0ojfpvQYUMyeNv/9rGyaBmM6lrrpldstG7kL/BkEowC\n"
        "KvFnOEV4WAUO/3RNPXceAIQWwhLkOItR+I3z7M5G1bUc6WZ4PfbiJV4rJERCzI8L\n"
        "03z47vbEbByKVxhy8nv+Eu0+/UNbzDbsqEGp5qXggQKBgQDWsx/kdjB2xADvnFTG\n"
        "JzvDO38bv8O+fvDwYA0kX3ijt7HbH87hlRI3cs0RNFGIF9cE+4jC+pTVAqqPtC1L\n"
        "O+VAHUc5jintQ+ZI2SSAUfZd28qWygULcKxDQoI1bkQsRZeAdPLl2FUrJtDEXEJq\n"
        "Z3L/ulI1iolqmSwa5IbHSS8fcQKBgQDF6A8hcKN1bwpIkQ11D4HQ7B5Ta1I8q16N\n"
        "gVZX5PLCYADTQ0deSedbeEjrHxpbqDbRzrdJ2F12BBR6pcQBJk7/5ludBf1tEGbP\n"
        "029X9E95imQuRoO0JhTvK2VCE297bEpEg2iQsVRos/ASaDB9YSvyxRrJnotephLn\n"
        "31LnQfbkwQKBgHdu87naiYE37bFdTMdiQduMOFxOY+yPnyaIuCbYuTqR0G2uFx7k\n"
        "F1sjELKWYRiM8n8CEgUs8ihAsHL6bwvgCNqOrvV0gRxM3kj+ClEbxypVPzB8tyuz\n"
        "BRDxaY+hhGkAWZQK+qgjnNVBZXcmP4gDfjSGCH9iTqkvBhr7r4Ii0wTxAoGAYiql\n"
        "trSkoA+gTjaFMleq0PMOZ9qIREfM8uwA5EBQmlH8ls58jCykch7MLLSU4noiFxgu\n"
        "mpaUZYHIlr2658cU0KJ3NwBNoNfN57C9PieVdHhNERcxJR7uq2QfKhNx7QreG/YC\n"
        "3CLZ98Wpg7fitY6JujZC/1eBUkWWgyWnfcaerQECgYEAu6utR5cEZwe5WwTJ6Ixt\n"
        "1w70UAsE6knkk0Ag62OmpbvSyLHU3WuAA91X1GgoSz1/OYRxraYy6JFyul4uStxY\n"
        "h6ltKHlD0yrRj7aX/gpI82elh+UvKHcBzCFfjzJbe+wk2QuCXUPGu+KHGZz7lu/i\n"
        "P1hhspaKDBOALIYU9uq3chw=\n-----END PRIVATE KEY-----\n"
    ),
    "client_email": "kase-uploader@rugged-silo-505709-i3.iam.gserviceaccount.com",
    "client_id": "102498253290640451030",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/kase-uploader%40rugged-silo-505709-i3.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

try:
    with open(SERVICE_ACCOUNT_FILE, 'w', encoding='utf-8') as f:
        json.dump(creds_dict, f, ensure_ascii=False)

    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)
    print("Google Drive connected successfully!")
except Exception as e:
    print(f"Warning: Google Drive connection deferred: {e}")

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

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
            
            drive_id = 'simulated_drive_id'
            if drive_service:
                try:
                    from googleapiclient.http import MediaFileUpload
                    file_metadata = {'name': safe_name, 'parents': [FOLDER_ID]}
                    media = MediaFileUpload(safe_name, resumable=True)
                    drive_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                    drive_id = drive_file.get('id')
                    
                    permission = {'type': 'anyone', 'role': 'reader'}
                    drive_service.permissions().create(fileId=drive_id, body=permission).execute()
                except Exception as ex:
                    print(f"Drive upload error: {ex}")
            
            if not file_id: 
                file_id = drive_id
            gallery.append(drive_id)
            
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
