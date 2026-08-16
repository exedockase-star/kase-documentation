import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Enforces 50MB max file limit

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initial archive items (Past Newsletters & Reports)
entries = [
    {
        'title': 'KASE Chronicle - March 2026',
        'category': 'Newsletter',
        'date': 'March 2026',
        'summary': 'Official coverage of the Kottarakkara Drone Research and Innovation Park launch and global education workshops.',
        'filename': '',
        'badge': 'bg-indigo-50 text-indigo-700'
    },
    {
        'title': 'Synergies in Motion Summit',
        'category': 'Event Report',
        'date': 'October 2025',
        'summary': 'Detailed activity report and documentation for the high-level Kerala-Germany partnership summit.',
        'filename': '',
        'badge': 'bg-emerald-50 text-emerald-700'
    }
]

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
    
    file = request.files.get('file')
    filename = ''
    if file and file.filename:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
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
        'badge': badge
    })
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)