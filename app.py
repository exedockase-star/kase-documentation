import os
import fitz  # PyMuPDF for automatic PDF cover extraction
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB total batch limit

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Clean slate: Starts empty so you can manually populate every report and event
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
    filename = ''
    cover_filename = ''
    gallery_images = []

    if uploaded_files:
        for index, file in enumerate(uploaded_files):
            if file and file.filename:
                safe_name = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
                file.save(file_path)
                
                ext = safe_name.rsplit('.', 1)[1].lower() if '.' in safe_name else ''
                
                # If first file is a PDF, auto-extract page 1 as cover
                if index == 0 and ext == 'pdf':
                    filename = safe_name
                    try:
                        doc = fitz.open(file_path)
                        if len(doc) > 0:
                            page = doc.load_page(0)
                            pix = page.get_pixmap(dpi=150)
                            cover_filename = "cover_" + safe_name.rsplit('.', 1)[0] + ".png"
                            cover_path = os.path.join(app.config['UPLOAD_FOLDER'], cover_filename)
                            pix.save(cover_path)
                        doc.close()
                    except Exception as e:
                        print(f"PDF cover extraction error: {e}")
                
                # If it's an image, collect it for the gallery and use the first as cover
                elif ext in ['jpg', 'jpeg', 'png', 'webp']:
                    gallery_images.append(safe_name)
                    if not filename:
                        filename = safe_name
                    if not cover_filename:
                        cover_filename = safe_name

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
        'filename': filename,
        'cover_filename': cover_filename,
        'gallery': gallery_images,
        'badge': badge
    })
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
