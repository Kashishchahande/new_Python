import os
import sqlite3
from datetime import datetime, date
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, 
    flash, session, jsonify, abort
)
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Ensure writable DB location for serverless environments (e.g., Vercel)
def get_db_path():
    db_path = app.config['DATABASE']
    try:
        # Test if the directory is writable
        db_dir = os.path.dirname(db_path)
        test_file = os.path.join(db_dir, '.write_test')
        with open(test_file, 'w') as f:
            f.write('1')
        os.remove(test_file)
        return db_path
    except (OSError, PermissionError):
        # Fallback to /tmp for Vercel / AWS Lambda
        tmp_db = os.path.join('/tmp', 'notices.db')
        return tmp_db

DB_PATH = get_db_path()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT DEFAULT 'Normal',
            department TEXT DEFAULT 'Administration',
            content TEXT NOT NULL,
            attachment_url TEXT,
            is_pinned INTEGER DEFAULT 0,
            expiry_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    
    # Check if table is empty, if so, seed sample data
    cursor.execute('SELECT COUNT(*) as count FROM notices')
    count = cursor.fetchone()['count']
    if count == 0:
        seed_sample_notices(cursor)
        conn.commit()
        
    conn.close()

def seed_sample_notices(cursor):
    sample_notices = [
        (
            "URGENT: Campus Closure Notice Due to Severe Weather Advisory",
            "Urgent Notice",
            "Urgent",
            "Office of the Principal",
            "Due to the severe weather alert issued by the Meteorological Department, all physical lectures and laboratory sessions are suspended for tomorrow. Students and faculty are advised to stay indoors. Online classes will be conducted as per the regular timetable.",
            "",
            1,
            None
        ),
        (
            "End Semester Examination Schedule & Admit Card Distribution",
            "Examination",
            "High",
            "Examination Cell",
            "The official timetable for the upcoming End Semester Examinations (Winter 2026) has been finalized and released. Students can download their admit cards through the student portal starting from Monday. Please ensure all outstanding dues are cleared before generating the hall ticket.",
            "https://example.com/exam-schedule-2026.pdf",
            1,
            "2026-12-15"
        ),
        (
            "Annual Campus Placement Drive 2026-27: Registration Open",
            "Placement",
            "High",
            "Training & Placement Cell",
            "Registrations are officially open for the Annual Campus Placement Drive. Over 40+ leading tech and core companies will be visiting the campus next month. All final year eligible students (CGPA 6.5 and above with no active backlogs) must complete their profiles by Friday 5:00 PM.",
            "https://example.com/placement-guidelines.pdf",
            0,
            "2026-11-20"
        ),
        (
            "Submission of Capstone Project Reports and Internal Assessments",
            "Academic",
            "Normal",
            "Department of Academic Affairs",
            "All final year undergraduate and postgraduate students must submit their draft project reports to their respective project guides by the 10th of next month. Internal viva voce and evaluations will commence following the submissions.",
            "",
            0,
            "2026-11-10"
        ),
        (
            "Annual Inter-College Tech Fest 'INNOVATE 2026' - Call for Volunteers",
            "Events",
            "Normal",
            "Student Affairs Committee",
            "We are thrilled to announce that 'INNOVATE 2026' will be held from November 25th to 27th! Competitions include Hackathon, Robotics Arena, Code Golf, and Startup Pitching. Interested students are invited to register as organizers and volunteers.",
            "https://example.com/innovate-2026-brochure.pdf",
            0,
            "2026-11-25"
        ),
        (
            "Central Library Extended Working Hours During Exams",
            "Administrative",
            "Normal",
            "Central Library",
            "In view of the approaching examinations, the Central Library will remain open 24/7 with full digital catalog and air-conditioned reading hall access. Quiet hours will be strictly enforced between 10:00 PM and 6:00 AM.",
            "",
            0,
            "2026-12-30"
        )
    ]
    cursor.executemany('''
        INSERT INTO notices (title, category, priority, department, content, attachment_url, is_pinned, expiry_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_notices)

# Decorator to protect admin routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Please log in with administrator credentials to access this page.', 'warning')
            return redirect(url_for('admin_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Context processor for templates
@app.context_processor
def inject_common():
    return {
        'categories': app.config['CATEGORIES'],
        'priorities': app.config['PRIORITIES'],
        'is_admin': session.get('is_admin', False),
        'admin_username': session.get('admin_username', ''),
        'current_year': datetime.now().year,
        'today_date': date.today().isoformat()
    }

# Template filter for dates
@app.template_filter('format_date')
def format_date_filter(value):
    if not value:
        return ""
    try:
        # SQLite CURRENT_TIMESTAMP returns YYYY-MM-DD HH:MM:SS
        if " " in str(value):
            dt = datetime.strptime(str(value).split('.')[0], "%Y-%m-%d %H:%M:%S")
        else:
            dt = datetime.strptime(str(value), "%Y-%m-%d")
        return dt.strftime("%b %d, %Y")
    except Exception:
        return str(value)

@app.template_filter('is_expired')
def is_expired_filter(expiry_date_str):
    if not expiry_date_str:
        return False
    try:
        exp = datetime.strptime(str(expiry_date_str), "%Y-%m-%d").date()
        return exp < date.today()
    except Exception:
        return False

# ==================== PUBLIC ROUTES ====================

@app.route('/')
def index():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query parameters
    category = request.args.get('category', 'all')
    sort_by = request.args.get('sort', 'newest')  # newest, oldest, priority, title
    search = request.args.get('search', '').strip()
    status = request.args.get('status', 'active')  # active, all
    
    # Build query
    query = "SELECT * FROM notices WHERE 1=1"
    params = []
    
    # Category filter
    if category and category.lower() != 'all':
        query += " AND category = ?"
        params.append(category)
        
    # Search filter
    if search:
        query += " AND (title LIKE ? OR content LIKE ? OR department LIKE ? OR category LIKE ?)"
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard, wildcard, wildcard])
        
    # Active/Expired filter
    today_str = date.today().isoformat()
    if status == 'active':
        query += " AND (expiry_date IS NULL OR expiry_date = '' OR expiry_date >= ?)"
        params.append(today_str)
        
    # Sorting (Pinned notices always appear on top, then order by user preference)
    if sort_by == 'oldest':
        order_clause = " ORDER BY is_pinned DESC, created_at ASC"
    elif sort_by == 'priority':
        # Order Urgent > High > Normal > Low
        order_clause = """ ORDER BY is_pinned DESC, 
            CASE priority 
                WHEN 'Urgent' THEN 1 
                WHEN 'High' THEN 2 
                WHEN 'Normal' THEN 3 
                ELSE 4 
            END, created_at DESC"""
    elif sort_by == 'title':
        order_clause = " ORDER BY is_pinned DESC, title COLLATE NOCASE ASC"
    else:  # newest (default)
        order_clause = " ORDER BY is_pinned DESC, created_at DESC"
        
    query += order_clause
    
    cursor.execute(query, params)
    notices = cursor.fetchall()
    
    # Fetch Urgent notices for ticker marquee
    cursor.execute(
        "SELECT id, title, category FROM notices WHERE priority = 'Urgent' AND (expiry_date IS NULL OR expiry_date >= ?) ORDER BY created_at DESC LIMIT 5",
        (today_str,)
    )
    ticker_notices = cursor.fetchall()
    
    # Fetch counts per category for filter badges
    cursor.execute("SELECT category, COUNT(*) as count FROM notices GROUP BY category")
    category_counts_raw = cursor.fetchall()
    category_counts = {row['category']: row['count'] for row in category_counts_raw}
    
    cursor.execute("SELECT COUNT(*) as count FROM notices")
    total_count = cursor.fetchone()['count']
    
    conn.close()
    
    return render_template(
        'index.html',
        notices=notices,
        ticker_notices=ticker_notices,
        selected_category=category,
        selected_sort=sort_by,
        search_query=search,
        selected_status=status,
        category_counts=category_counts,
        total_count=total_count
    )

@app.route('/notice/<int:id>')
def notice_detail(id):
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notices WHERE id = ?", (id,))
    notice = cursor.fetchone()
    
    if not notice:
        conn.close()
        flash('Notice not found.', 'danger')
        return redirect(url_for('index'))
        
    # Get related notices from the same category
    cursor.execute(
        "SELECT * FROM notices WHERE category = ? AND id != ? ORDER BY created_at DESC LIMIT 3",
        (notice['category'], id)
    )
    related_notices = cursor.fetchall()
    conn.close()
    
    return render_template('notice_detail.html', notice=notice, related_notices=related_notices)

# ==================== ADMIN AUTH ROUTES ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if (username == app.config['ADMIN_USERNAME'] and 
            password == app.config['ADMIN_PASSWORD']):
            session['is_admin'] = True
            session['admin_username'] = username
            flash('Logged in successfully as Administrator.', 'success')
            next_url = request.args.get('next')
            return redirect(next_url or url_for('admin_dashboard'))
        else:
            flash('Invalid username or password. (Default is admin / admin123)', 'danger')
            
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('You have been logged out of the admin panel.', 'info')
    return redirect(url_for('index'))

# ==================== ADMIN CRUD ROUTES ====================

@app.route('/admin')
@admin_required
def admin_dashboard():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query parameters
    category = request.args.get('category', 'all')
    sort_by = request.args.get('sort', 'newest')
    search = request.args.get('search', '').strip()
    
    query = "SELECT * FROM notices WHERE 1=1"
    params = []
    
    if category and category.lower() != 'all':
        query += " AND category = ?"
        params.append(category)
        
    if search:
        query += " AND (title LIKE ? OR content LIKE ? OR department LIKE ?)"
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard, wildcard])
        
    if sort_by == 'oldest':
        query += " ORDER BY is_pinned DESC, created_at ASC"
    elif sort_by == 'priority':
        query += """ ORDER BY is_pinned DESC, 
            CASE priority 
                WHEN 'Urgent' THEN 1 
                WHEN 'High' THEN 2 
                WHEN 'Normal' THEN 3 
                ELSE 4 
            END, created_at DESC"""
    elif sort_by == 'title':
        query += " ORDER BY is_pinned DESC, title COLLATE NOCASE ASC"
    else:
        query += " ORDER BY is_pinned DESC, created_at DESC"
        
    cursor.execute(query, params)
    notices = cursor.fetchall()
    
    # Stats
    cursor.execute("SELECT COUNT(*) as total FROM notices")
    total_notices = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as pinned FROM notices WHERE is_pinned = 1")
    pinned_notices = cursor.fetchone()['pinned']
    
    cursor.execute("SELECT COUNT(*) as urgent FROM notices WHERE priority = 'Urgent'")
    urgent_notices = cursor.fetchone()['urgent']
    
    today_str = date.today().isoformat()
    cursor.execute("SELECT COUNT(*) as active FROM notices WHERE expiry_date IS NULL OR expiry_date = '' OR expiry_date >= ?", (today_str,))
    active_notices = cursor.fetchone()['active']
    
    conn.close()
    
    stats = {
        'total': total_notices,
        'pinned': pinned_notices,
        'urgent': urgent_notices,
        'active': active_notices
    }
    
    return render_template(
        'admin_dashboard.html', 
        notices=notices, 
        stats=stats,
        selected_category=category,
        selected_sort=sort_by,
        search_query=search
    )

@app.route('/admin/notices/new', methods=['GET', 'POST'])
@admin_required
def create_notice():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        priority = request.form.get('priority', 'Normal')
        department = request.form.get('department', 'Administration').strip()
        content = request.form.get('content', '').strip()
        attachment_url = request.form.get('attachment_url', '').strip()
        is_pinned = 1 if request.form.get('is_pinned') else 0
        expiry_date = request.form.get('expiry_date', '').strip() or None
        
        if not title or not content or not category:
            flash('Title, category, and notice content are required fields.', 'danger')
            return render_template('notice_form.html', notice=None, action="create")
            
        init_db()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO notices (title, category, priority, department, content, attachment_url, is_pinned, expiry_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, category, priority, department, content, attachment_url, is_pinned, expiry_date))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        
        flash(f'Notice "#{new_id}: {title}" was published successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
        
    return render_template('notice_form.html', notice=None, action="create")

@app.route('/admin/notices/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_notice(id):
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notices WHERE id = ?", (id,))
    notice = cursor.fetchone()
    
    if not notice:
        conn.close()
        flash('Notice not found.', 'danger')
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        priority = request.form.get('priority', 'Normal')
        department = request.form.get('department', 'Administration').strip()
        content = request.form.get('content', '').strip()
        attachment_url = request.form.get('attachment_url', '').strip()
        is_pinned = 1 if request.form.get('is_pinned') else 0
        expiry_date = request.form.get('expiry_date', '').strip() or None
        
        if not title or not content or not category:
            flash('Title, category, and notice content cannot be empty.', 'danger')
            conn.close()
            return render_template('notice_form.html', notice=notice, action="edit")
            
        cursor.execute('''
            UPDATE notices
            SET title = ?, category = ?, priority = ?, department = ?, 
                content = ?, attachment_url = ?, is_pinned = ?, expiry_date = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (title, category, priority, department, content, attachment_url, is_pinned, expiry_date, id))
        conn.commit()
        conn.close()
        
        flash(f'Notice #{id} updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
        
    conn.close()
    return render_template('notice_form.html', notice=notice, action="edit")

@app.route('/admin/notices/delete/<int:id>', methods=['POST'])
@admin_required
def delete_notice(id):
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notices WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    
    flash(f'Notice #{id} has been permanently deleted.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/notices/toggle-pin/<int:id>', methods=['POST'])
@admin_required
def toggle_pin(id):
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE notices SET is_pinned = 1 - is_pinned WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    
    flash(f'Pin status toggled for Notice #{id}.', 'info')
    return redirect(request.referrer or url_for('admin_dashboard'))

# ==================== JSON API ENDPOINT ====================

@app.route('/api/notices')
def api_notices():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notices ORDER BY is_pinned DESC, created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    notices_list = [dict(row) for row in rows]
    return jsonify({
        'status': 'success',
        'count': len(notices_list),
        'notices': notices_list
    })

# Initialize DB on start
with app.app_context():
    init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
