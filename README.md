# 📢 Digital Notice Board (Python & Flask)

A modern, production-ready **Digital Notice Board Web Application** built with **Python (Flask)** and **Tailwind CSS**. It is fully ready to be pushed to GitHub and deployed directly to the cloud (Render, Vercel, Railway, PythonAnywhere).

---

## 🌟 Key Features

### 🛡️ Administrator Features (Full CRUD)
- **Admin Authentication**: Password-protected Admin Portal with secure sessions.
- **Post Notices**: Add new announcements with title, category, priority level, issuing department, optional expiration date, external document attachments (PDF/links), and pin status.
- **Update Notices**: Real-time editing of any posted circular with automatic timestamp updates.
- **Delete Notices**: Remove outdated notices with modal confirmation protection.
- **Pin to Top**: Highlight critical announcements to stay permanently at the top of the board.
- **Admin Dashboard**: Visual dashboard displaying real-time statistics (Total notices, Pinned notices, Urgent circulars, and Active notices).

### 👥 Public / User Features
- **Categorized Notices**: Filter notices by Academic, Examination, Events, Placement, Administrative, Urgent Notices, Sports, or General.
- **Sort by Date & Priority**: Sort notices by Newest First, Oldest First, Priority (Urgent first), or Title (A to Z).
- **Live Search**: Instant keyword search matching titles, content, categories, and departments.
- **Breaking News Marquee**: Animated live ticker showcasing urgent alerts across the top.
- **Official Circular View**: Printable institutional layout with Ref Number, Date, Authorized Signatory, and one-click "Print / Save as PDF".
- **One-Click Share**: Copy direct link to any circular.
- **RESTful JSON API**: Access notices programmatically at `/api/notices`.

---

## 🔐 Default Admin Credentials

| Field | Default Value |
|---|---|
| **Username** | `admin` |
| **Password** | `admin123` |

*(You can customize these anytime via environment variables `ADMIN_USERNAME` and `ADMIN_PASSWORD` or in `config.py`)*

---

## 🚀 Quick Start (Apne Computer Par Run Karein)

1. Open your terminal in this project directory:
   ```bash
   cd digital-notice-board
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Open your browser and visit:
   ```
   http://127.0.0.1:5000
   ```
   *(Database `notices.db` will automatically initialize with rich sample announcements!)*

---

## 📦 GitHub Pe Kaise Daalein (Step-by-Step)

Apne project ko GitHub par upload karne ke liye ye steps follow karein:

1. [GitHub](https://github.com) par jayein aur ek **New Repository** banayein (e.g. `digital-notice-board`). *(Do not add README or .gitignore while creating repo)*.

2. Apne terminal mein ye commands run karein:
   ```bash
   # Git initialize karein
   git init

   # Files add karein
   git add .

   # Commit karein
   git commit -m "Initial commit: Production-ready Digital Notice Board"

   # Main branch set karein
   git branch -M main

   # Apni GitHub repository link karein (YOUR_USERNAME replace karein)
   git remote add origin https://github.com/YOUR_USERNAME/digital-notice-board.git

   # GitHub pe push karein
   git push -u origin main
   ```

---

## 🌐 Free Deployment (Live Kaise Karein)

### Option 1: Render.com (Recommended - 100% Free & Simplest for Python)

1. [Render.com](https://render.com) par free account banayein (GitHub se sign in karein).
2. **Dashboard** -> Click **New +** -> Select **Web Service**.
3. Apni GitHub repository (`digital-notice-board`) select karein.
4. Render automatic detect kar lega:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Click **Create Web Service**.
6. 1-2 minute mein aapki website **LIVE** ho jayegi with free SSL/HTTPS URL! 🎉

---

### Option 2: Vercel

Is project mein `vercel.json` and `api/index.py` already configured hai:
1. [Vercel.com](https://vercel.com) par login karein.
2. Click **Add New...** -> **Project**.
3. Apni GitHub repo choose karein aur **Deploy** par click karein.
4. Vercel automatically detect karke deploy kar dega!

---

### Option 3: PythonAnywhere (Free Python Hosting)

1. [PythonAnywhere.com](https://www.pythonanywhere.com) par free account banayein.
2. **Web** tab mein **Add a new web app** click karein.
3. Select **Manual Configuration** -> **Python 3.10/3.11**.
4. Files upload karein ya `git clone` karein.
5. WSGI configuration file mein `from app import app as application` add karein aur Reload click karein.

---

## 📂 Project Structure

```
digital-notice-board/
├── app.py                 # Core Flask application, SQLite setup, routing, & auth
├── config.py              # Configuration & admin credentials
├── requirements.txt       # Dependencies (Flask, gunicorn)
├── Procfile               # Cloud deployment command
├── render.yaml            # Render Blueprint for 1-click deploy
├── vercel.json            # Vercel serverless configuration
├── api/
│   └── index.py           # Vercel serverless entry point
├── templates/             # HTML Templates (Jinja2)
│   ├── base.html          # Base layout (Navbar, Live Clock, Footer)
│   ├── index.html         # Main board with category filters, sort, search, & cards
│   ├── notice_detail.html # Printable notice circular with verified stamp
│   ├── admin_login.html   # Admin login page
│   ├── admin_dashboard.html # Admin panel (table, stats, quick CRUD)
│   └── notice_form.html   # Create & Edit notice form
├── static/
│   ├── css/
│   │   └── style.css      # Custom styles, marquee animation, print stylesheet
│   └── js/
│       └── main.js        # Live clock, modal dialogs, copy link
├── .gitignore
└── README.md
```

---

## 🛠️ Tech Stack

- **Backend**: Python 3, Flask
- **Database**: SQLite3 (Zero setup, runs out of the box)
- **Frontend**: HTML5, Tailwind CSS, FontAwesome Icons, Vanilla JS
- **Server**: Gunicorn WSGI
