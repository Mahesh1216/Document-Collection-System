import sqlite3
import json
import re
import os
import google.generativeai as genai
from flask import Flask, jsonify, render_template, request, flash, redirect, url_for
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_secret_key')
DATABASE = 'quickdocs.db'

# Configure the Gemini API key
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_schema_representation():
    """Gets the database schema in a string format."""
    db = get_db()
    schema = db.execute("SELECT sql FROM sqlite_master WHERE type='table';").fetchall()
    return "\n".join([row['sql'] for row in schema])

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('database/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        with app.open_resource('database/sample_data.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/customers', methods=['GET', 'POST'])
def customers():
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        process_id = request.form.get('process_id')

        existing_customer = db.execute('SELECT id FROM customers WHERE email = ?', (email,)).fetchone()
        if existing_customer:
            flash('Email already exists.', 'error')
        else:
            cursor = db.cursor()
            cursor.execute('INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)', (name, email, phone))
            customer_id = cursor.lastrowid
            if process_id:
                cursor.execute('INSERT INTO process_assignments (customer_id, process_id) VALUES (?, ?)', (customer_id, process_id))
            db.commit()
            flash('Customer registered successfully!', 'success')
        return redirect(url_for('customers'))

    customers = db.execute('''
        SELECT c.id, c.name, c.email, c.phone, c.registration_date,
               GROUP_CONCAT(p.name, ', ') as processes
        FROM customers c
        LEFT JOIN process_assignments pa ON c.id = pa.customer_id
        LEFT JOIN processes p ON pa.process_id = p.id
        GROUP BY c.id
    ''').fetchall()
    processes = db.execute('SELECT id, name FROM processes WHERE status = "active"').fetchall()
    return render_template('customers.html', customers=customers, processes=processes)

@app.route('/documents', methods=['GET', 'POST'])
def documents():
    db = get_db()
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        process_id = request.form['process_id']
        document_type_id = request.form['document_type_id']
        file_url = request.form['file_url']
        ocr_data = request.form['ocr_data']

        try:
            json.loads(ocr_data)
        except json.JSONDecodeError:
            flash('Invalid JSON in OCR data.', 'error')
            return redirect(url_for('documents'))

        db.execute('''
            INSERT INTO document_submissions (customer_id, process_id, document_type_id, file_url, ocr_extracted_data)
            VALUES (?, ?, ?, ?, ?)
        ''', (customer_id, process_id, document_type_id, file_url, ocr_data))
        db.commit()

        update_completion_percentage(customer_id, process_id)

        flash('Document submitted successfully!', 'success')
        return redirect(url_for('documents'))

    submissions = db.execute('''
        SELECT ds.id, c.name as customer_name, p.name as process_name, dt.name as doc_type_name,
               ds.upload_date, ds.validation_status, ds.ocr_extracted_data
        FROM document_submissions ds
        JOIN customers c ON ds.customer_id = c.id
        JOIN processes p ON ds.process_id = p.id
        JOIN document_types dt ON ds.document_type_id = dt.id
        ORDER BY ds.upload_date DESC
    ''').fetchall()
    customers = db.execute('SELECT id, name FROM customers').fetchall()
    processes = db.execute('SELECT id, name FROM processes').fetchall()
    document_types = db.execute('SELECT id, name FROM document_types').fetchall()

    return render_template('documents.html', submissions=submissions, customers=customers, processes=processes, document_types=document_types)

@app.route('/dashboard')
def dashboard():
    db = get_db()
    assignments = db.execute('''
        SELECT pa.id, c.name as customer_name, p.name as process_name, pa.assignment_date,
               pa.status, pa.completion_percentage
        FROM process_assignments pa
        JOIN customers c ON pa.customer_id = c.id
        JOIN processes p ON pa.process_id = p.id
        ORDER BY pa.assignment_date DESC
    ''').fetchall()

    total_customers = db.execute('SELECT COUNT(id) FROM customers').fetchone()[0]
    total_processes = db.execute('SELECT COUNT(id) FROM processes').fetchone()[0]
    completed_assignments = db.execute('SELECT COUNT(id) FROM process_assignments WHERE status = "completed"').fetchone()[0]
    pending_submissions = db.execute('SELECT COUNT(id) FROM document_submissions WHERE validation_status = "pending"').fetchone()[0]

    stats = {
        'total_customers': total_customers,
        'total_processes': total_processes,
        'completed_assignments': completed_assignments,
        'pending_submissions': pending_submissions
    }

    return render_template('dashboard.html', assignments=assignments, stats=stats)

def update_completion_percentage(customer_id, process_id):
    db = get_db()
    required_docs = db.execute('''
        SELECT document_type_id FROM process_document_requirements WHERE process_id = ? AND is_mandatory = 1
    ''', (process_id,)).fetchall()
    required_doc_ids = {row['document_type_id'] for row in required_docs}

    if not required_doc_ids:
        completion_percentage = 100
    else:
        submitted_docs = db.execute('''
            SELECT document_type_id FROM document_submissions
            WHERE customer_id = ? AND process_id = ? AND validation_status = 'approved'
        ''', (customer_id, process_id)).fetchall()
        submitted_doc_ids = {row['document_type_id'] for row in submitted_docs}

        completed_docs = len(required_doc_ids.intersection(submitted_doc_ids))
        completion_percentage = (completed_docs / len(required_doc_ids)) * 100

    status = 'completed' if completion_percentage == 100 else 'pending'
    db.execute('''
        UPDATE process_assignments
        SET completion_percentage = ?, status = ?
        WHERE customer_id = ? AND process_id = ?
    ''', (completion_percentage, status, customer_id, process_id))
    db.commit()

@app.route('/query', methods=['GET', 'POST'])
def query():
    if request.method == 'POST':
        nl_query = request.form['query']
        sql_query, results, error = process_nl_query(nl_query)
        return render_template('query.html', nl_query=nl_query, sql_query=sql_query, results=results, error=error)
    return render_template('query.html')

def process_nl_query(nl_query):
    """Processes a natural language query to generate and execute a SQL query."""
    if not os.environ.get('GEMINI_API_KEY'):
        return "", [], "GEMINI_API_KEY not set. Please configure the API key."

    db = get_db()
    schema = get_schema_representation()
    prompt = f"""Given the following database schema:

{schema}

Translate the following natural language query into a SQL query:

'{nl_query}'

SQL Query:"""

    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content(prompt)
        raw_sql = response.text
        
        # Extract SQL from markdown code blocks
        match = re.search(r"```(sql)?(.*)```", raw_sql, re.DOTALL | re.IGNORECASE)
        if match:
            sql_query = match.group(2).strip()
        else:
            sql_query = raw_sql.strip()

        sql_query = sql_query.replace('\n', ' ')

        if not sql_query.lower().startswith('select'):
            return sql_query, [], "Only SELECT queries are allowed."

        cursor = db.execute(sql_query)
        results = [dict(row) for row in cursor.fetchall()]
        return sql_query, results, None
    except Exception as e:
        return "", [], f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)