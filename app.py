import os
import json
import base64
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# --- CONFIGURATION ---
FOLDER_ID = '19S09p8BGF-eCyRFWY75Chl1mM7w61gec' 
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'credentials.json'

drive_service = None

# Perfectly padded base64 credentials string
EMBEDDED_CREDS_B64 = (
    "ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3Rfa2V5X2lkIjog"
    "IzdjOWYxOWQ5YmIwMmZlMzIwODRlMzgwZmFhYTNjM2MxOGY1NWM2NmEiLAogICJwcm"
    "l2YXRlX2tleSI6ICItLS0tLkJFR0lOIFBSSVZBVEUgS0VZLS0tLS0KTUlJRXZRSUJB"
    "REFOQmdrcWhraUc5dzBCQVFFRkFBU0JLZ3dnZ1pqQWdFQUFvSUJBUUNsK25hUVFHdGJM"
    "c21ZCmxmQjZFV28zRGpjVlI1MXVxbkcvcTFadU9jWWgxL2JvMG1VT3lsdEowNmFCZFRE"
    "TGgxelhQZXp4ZXhLb3ZFNGIKZ29RMDdnT2VHc3NQWlUwRnlYN0lTVzk4QXpOdkN3TGVM"
    "am82VGcrK2FCWVlyRGU1ZHM4RWtUazFNdCtDLzNNVwpSMUxMR2dUZjRNOUhjMlUrTm1o"
    "MzlBREI5V2N5K3VFSEdlcmdEcmNNSHZBRlpqZjMvTitmTm1Rd21mbEpwbjVpCmlZdmk5"
    "NGFySEUxZGJOenZJalJ2MkM4azFpOEtwWjNqRG00ZnlZRWlndHVWbTI4SDJERU12UHlB"
    "UUpwdFFKV1IKdVNzYWN3SXFSbjExY0k3UjQzMkorQ3U2NlpWR2RFL25wV1JtYTFIZFhN"
    "cC9UQ0VsVkZERVBTRFdPVFBVcDJkdQo5S2NNSFZneEFnTUJBQUVDZ2dFQUJnUTRXa1lG"
    "aGppQjFRTEJaUEZlNmVnOVlhdDNCdGtObHNLdmx6OEhvamd0CmduYkc5RVJzVHZhcHUx"
    "bGJ4NUxzYi81MkNYSmFSS3pQd1lKSGg5SWxaaXluTmZPSWVWaGFuTWpCcm11QXlLcUwK"
    "NC9FbHlmR0VzMVNiVVhGanN6aTk3QmJXRGFvK2pTVjBudWIrdHE5R3BEVm1XaHNTSFZG"
    "VU5M1B6YmdYTWJNMApzbHRCU2RJQ1lxQksrcHo1WTJsbmswb2pmcHZRWVVNeWVOdi85"
    "ckd5YUJtTTZscnJwbGRzdEc3a0wvQmtFb3dDCkt2Rm5PRVY0V0FVTy8zUk5QWGNlQUlR"
    "V3doTGtPSXRSK0kzejdNNUcxYlVjNldaNFBmYmlKVjRySkVSQ3pJOEwKMDN6NDd2YkVi"
    "QnlLVnhoeThuditFdTArL1VOYnpEYnNxRUdwNXFYZ2dRS0JnUURXc3gva2RqBjJ4QUR2"
    "bkZURwpKenZETzM4YnY4TytmdkR3WUEwa1gzaWp0N0hiSDg3aGxSSTNjczBSTkZHSUY5"
    "Y0UrNGpDK3BUVkFxcVB0QzFMCk8rVkFIVWM1amludFErWkkyU1NBVWZaZDI4cVd5Z1VM"
    "Y0t4RFFvSTFia1FzUlplQWRQTGwyRlVySnRERVhFSnEKWjNML3VsSTFpb2xxbVN3YTVJ"
    "YkhTUzhmY1FLQmdRREY2QThoY0tOMWJ3cElrUTExRDRIUTdCNVRhMUk4cTE2TgpnVlpY"
    "TlBMQ1lBRFRRMGRlU2VkYmVFanJIeHBicURiUnpyZEoyRjEyQkW5SnBjUUJKazcvNWx1"
    "ZEJmMXRFR2JQAjlYOUU5NWltUXVSb08wSmhUdksyVkNFMjk3YkVwRWcyaVFzVlJvcy9B"
    "U2FEQjlZU3Z5eFJySm5vdGVwaExuGUxuUWZia3dRS0JnSGR1ODduYWlZRTM3YkZkVE1k"
    "aVFkdU1PRnhPWSt5UG55YUl1Q2JZdVRxUjBHMnVGeDdrCkYxc2pFTEtXWVJpTThuOENF"
    "Z1VzOGloQXNITDZid3ZnQ05xT3J2VjBnUnhNM2tqK0NsRWJ4eXBWUHpCOHR5dXoKQlJE"
    "eGFZK2hoR2tBV1pRSytxZ2puTlZCWlhjbVA0Z0RmalNHQ0g5aVRxa3ZCaHI3cjRJaTB3"
    "VHhBb0dBWWlxbAp0clNrb0ErZ1RqYUZNbGVxMFBNT1o5cUlSRWZNOHV3QTVFQlFtbEg4"
    "bHM1OGpDeWtjaDdNTExTVTRub2lGeGd1Cm1wYVVaWUhJbHIyNjU4Y1UwS0ozTndCTm9O"
    "Zj41N0M5UGllVmRIaHJSUmN4SlI3dXEyUWZLaE54N1FyZUcvWUMKM0NMWjk4V3BnN2Zp"
    "dFk2SnVqWkMvMWVCVWtXV2d5V25mY2FlclFFQ2dZRUF1NnV0UjVjRVp3ZTVXd1RKNkl4"
    "dAoxdzcwVUFzRTZrbmtrMEFnNjJPbXBidlN5TEhVM1d1QUE5MVgxR2dvU3oxL09ZUnhy"
    "YVl5NkpGeXVsNHVTdHhZCmg2bHRLSGxEMHlyUmo3YVgvZ3BJODJlbGgrVXZLSGNCekNG"
    "Zmp6SmJlK3drMlF1Q1hVUEd1K0tIR1p6N2x1L2kKUDFoaHNwYUtEQk9BTElZVTl1cTNj"
    "aHc9Ci0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS0KIiwKICAiY2xpZW50X2VtYWlsIjog"
    "Imthc2UtdXBsb2FkZXJAcnVnZ2VkLXNpbG8tNTA1NzA5LWkzLmlhbS5nc2VydmljZWFj"
    "Y291bnQuY29tIiwKICAiY2xpZW50X2lkIjogIjEwMjQ5ODI1MzI5MDY0MDQ1MTAzMCIs"
    "biAgImF1dGhfdXJpIjogImh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbS9vL29hdXRo"
    "Mi9hdXRoIiwKICAidG9rZW5fdXJpIjogImh0dHBzOi8vb2F1dGgyLmdvb2dsZWFwaXMu"
    "Y29tL3Rva2VuIiwKICAidXV0aF9wcm92aWRlcl94N095X2NlcnRfdXJsIjogImh0dHBz"
    "Oi8vd3d3Lmdvb2dsZWFwaXMuY29tL29hdXRoMi92MS9jZXJ0cyIsCiAgImNsaWVudF94"
    "NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL3JvYm90L3Yx"
    "L21ldGFkYXRhL3g1MDkva2FzZS11cGxvYWRlciU0MHJ1Z2dlZC1zaWxvLTUwNTcwOS1p"
    "My5pYW0uZ3NlcnZpY2VhY2NvdW50LmNvbSIsCiAgInVuaXZlcnNlX2RvbWFpbiI6ICJn"
    "b29nbGVhcGlzLmNvbSIKfQ=="
)

try:
    # Clean padding and decode properly
    cleaned_b64 = "".join(EMBEDDED_CREDS_B64.split())
    padding_needed = len(cleaned_b64) % 4
    if padding_needed:
        cleaned_b64 += "=" * (4 - padding_needed)
        
    decoded_bytes = base64.b64decode(cleaned_b64.encode('utf-8'))
    creds_dict = json.loads(decoded_bytes.decode('utf-8'))
    
    if 'private_key' in creds_dict:
        creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')

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
