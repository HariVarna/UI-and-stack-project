# Authentication Project Foundation

A minimal, scalable Python Flask application foundation configured for Jinja2 templating, SQLite database storage, and custom CSS styling.

---

## 📁 Project Structure

```text
project/
├── app.py                  # Main Flask application and routing
├── requirements.txt        # Python package dependencies
├── database/
│   └── .gitkeep            # Directory reserved for SQLite database files
├── templates/
│   ├── base.html           # Master layout template (Jinja2)
│   └── index.html          # Placeholder home page template
├── static/
│   ├── css/
│   │   └── style.css       # Custom design system and CSS styling
│   └── js/
│       └── script.js       # Client-side JavaScript
├── .gitignore              # Files and directories ignored by Git
└── README.md               # Project documentation and setup guide
```

---

## 🚀 Getting Started

### 1. Create a Python Virtual Environment

It is recommended to isolate your dependencies using a virtual environment.

**Windows (PowerShell / Command Prompt):**
```powershell
python -m venv venv
```

**macOS / Linux:**
```bash
python3 -m venv venv
```

---

### 2. Activate the Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

*(If PowerShell script execution is restricted, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

---

### 3. Install Dependencies

With the virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

---

### 4. Run the Application

Start the Flask development server:

```bash
python app.py
```

---

### 5. Verify in the Browser

Open your browser and navigate to:

👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)** (or `http://localhost:5000`)

You should see the active status card and foundation details confirming Flask, Jinja2, CSS, and JS are loaded.
