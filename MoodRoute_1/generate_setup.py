"""
MoodRoute — Setup Guide PDF Generator (Clean version)
Produces setup.pdf: clear, readable, content-focused setup guide.
No nested tables. All step content rendered as flat flowables.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, Table, TableStyle, PageBreak
)
from reportlab.lib.colors import HexColor, black, white
import os

PAGE_W, PAGE_H = A4
MARGIN = 2.2 * cm
CONTENT_W = PAGE_W - 2 * MARGIN

# ── Minimal colour palette ────────────────────────────────────────────────────
BLACK  = black
DARK   = HexColor('#111111')
GREY   = HexColor('#444444')
LGREY  = HexColor('#f0f0f0')
BORDER = HexColor('#cccccc')
WHITE  = white


# ── Footer ────────────────────────────────────────────────────────────────────
def on_page(canv, doc):
    canv.saveState()
    w, h = A4
    canv.setStrokeColor(BORDER)
    canv.setLineWidth(0.5)
    canv.line(MARGIN, 1.1*cm, w - MARGIN, 1.1*cm)
    canv.setFont('Helvetica', 8)
    canv.setFillColor(GREY)
    canv.drawString(MARGIN, 0.7*cm,
        'MoodRoute — Setup & Installation Guide   |   CSIT998 Capstone · UOW 2026')
    canv.drawRightString(w - MARGIN, 0.7*cm, f'Page {doc.page}')
    canv.restoreState()


# ── Style definitions ─────────────────────────────────────────────────────────
def make_styles():
    return {
        # Cover
        'cover_title': ParagraphStyle(
            'ct', fontName='Helvetica-Bold', fontSize=30,
            textColor=BLACK, alignment=TA_CENTER, leading=36, spaceAfter=8),
        'cover_sub': ParagraphStyle(
            'cs', fontName='Helvetica', fontSize=14,
            textColor=GREY, alignment=TA_CENTER, leading=20, spaceAfter=6),
        'cover_body': ParagraphStyle(
            'cb', fontName='Helvetica', fontSize=10,
            textColor=GREY, alignment=TA_CENTER, leading=16, spaceAfter=4),

        # Section headings
        'section': ParagraphStyle(
            'sec', fontName='Helvetica-Bold', fontSize=13,
            textColor=BLACK, spaceBefore=20, spaceAfter=6,
            leading=17, borderPad=0),
        'step_heading': ParagraphStyle(
            'sh', fontName='Helvetica-Bold', fontSize=11,
            textColor=BLACK, spaceBefore=14, spaceAfter=4, leading=15),
        'subsection': ParagraphStyle(
            'ss', fontName='Helvetica-Bold', fontSize=10,
            textColor=DARK, spaceBefore=8, spaceAfter=3, leading=14),

        # Body text
        'body': ParagraphStyle(
            'body', fontName='Helvetica', fontSize=10,
            textColor=DARK, leading=15.5, spaceAfter=5,
            alignment=TA_JUSTIFY),
        'bullet': ParagraphStyle(
            'bul', fontName='Helvetica', fontSize=10,
            textColor=DARK, leading=15, spaceAfter=3,
            leftIndent=14),

        # Code / terminal
        'code': ParagraphStyle(
            'code', fontName='Courier', fontSize=9,
            textColor=HexColor('#222222'), leading=13,
            spaceAfter=2, leftIndent=0),

        # Note / tip / warning labels
        'note_label': ParagraphStyle(
            'nl', fontName='Helvetica-Bold', fontSize=9.5,
            textColor=DARK, leading=14),
        'note_body': ParagraphStyle(
            'nb', fontName='Helvetica', fontSize=9.5,
            textColor=DARK, leading=14),
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def divider():
    return HRFlowable(width='100%', thickness=0.6, color=BORDER,
                      spaceAfter=6, spaceBefore=6)


def section_title(text, s):
    """Bold underlined section heading."""
    return [
        Paragraph(text, s['section']),
        HRFlowable(width='100%', thickness=1.2, color=BLACK,
                   spaceAfter=8, spaceBefore=0),
    ]


def step_header(number, title, s):
    """Step number + title on one line, clearly visible."""
    return Paragraph(
        f'<b>Step {number}:  {title}</b>',
        ParagraphStyle(
            f'step{number}', fontName='Helvetica-Bold', fontSize=11,
            textColor=BLACK, spaceBefore=16, spaceAfter=6,
            leading=15,
            borderWidth=0, borderColor=BORDER,
            borderPad=0,
            leftIndent=0,
        )
    )


def code_block(lines, caption=''):
    """Dark-background terminal/code block. All lines rendered individually."""
    cells = []
    if caption:
        cells.append(Paragraph(
            caption,
            ParagraphStyle('cap', fontName='Helvetica-Oblique', fontSize=8.5,
                           textColor=HexColor('#888888'), leading=12, spaceAfter=3)))
    for line in lines:
        display = line if line.strip() else ' '
        cells.append(Paragraph(
            display,
            ParagraphStyle('cl', fontName='Courier', fontSize=9,
                           textColor=HexColor('#f0f0f0'), leading=13.5,
                           leftIndent=0)))

    tbl = Table([[cells]], colWidths=[CONTENT_W])
    tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), HexColor('#1c1c1c')),
        ('LEFTPADDING',   (0, 0), (-1, -1), 12),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 12),
        ('TOPPADDING',    (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    return tbl


def note_box(kind, text):
    """Simple bordered note box. kind = NOTE / TIP / WARNING."""
    labels = {'NOTE': '📝 NOTE', 'TIP': '✅ TIP', 'WARNING': '⚠  WARNING'}
    label = labels.get(kind, kind)
    content = [
        Paragraph(
            f'<b>{label}:</b>  {text}',
            ParagraphStyle('nb2', fontName='Helvetica', fontSize=9.5,
                           textColor=DARK, leading=14)),
    ]
    tbl = Table([[content]], colWidths=[CONTENT_W])
    tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), LGREY),
        ('BOX',           (0, 0), (-1, -1), 0.8, BORDER),
        ('LEFTPADDING',   (0, 0), (-1, -1), 12),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 12),
        ('TOPPADDING',    (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    return tbl


def b(text):
    """Shorthand bold inline."""
    return f'<b>{text}</b>'


# ── Main builder ──────────────────────────────────────────────────────────────
def build(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=1.8 * cm, bottomMargin=1.6 * cm,
        title='MoodRoute — Setup Guide',
        author='Group MoodMappers CSIT998'
    )

    s = make_styles()
    els = []

    # ═══════════════════════════════════════════════════════════
    # COVER PAGE
    # ═══════════════════════════════════════════════════════════
    els.append(Spacer(1, 3.5 * cm))
    els.append(Paragraph('MoodRoute', s['cover_title']))
    els.append(Paragraph('Setup and Installation Guide', s['cover_sub']))
    els.append(Spacer(1, 0.4 * cm))
    els.append(HRFlowable(width='40%', thickness=1.5, color=BLACK,
                           spaceAfter=20, spaceBefore=0))
    els.append(Paragraph(
        'Step-by-step instructions to install and run MoodRoute on any computer. '
        'Works on Windows, macOS, and Linux.',
        s['cover_body']))
    els.append(Spacer(1, 2.0 * cm))
    els.append(Paragraph('CSIT998 Professional Capstone Project', s['cover_body']))
    els.append(Paragraph('University of Wollongong  —  Annual Session 2026', s['cover_body']))
    els.append(Paragraph('Group MoodMappers', s['cover_body']))
    els.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # SECTION: OVERVIEW
    # ═══════════════════════════════════════════════════════════
    els += section_title('Overview', s)
    els.append(Paragraph(
        'MoodRoute is a Python Flask web application that runs on your local machine. '
        'Once running, you open it in any web browser at http://localhost:5000 — '
        'just like visiting a website.',
        s['body']))
    els.append(Paragraph(
        'This guide walks through everything needed to run MoodRoute on a new computer '
        'from scratch. Follow the steps in order.',
        s['body']))
    els.append(Spacer(1, 0.3 * cm))

    # Overview table
    ov_data = [
        [Paragraph(b('What you need to do'), ParagraphStyle('oh', fontName='Helvetica-Bold', fontSize=9.5, textColor=BLACK, leading=13)),
         Paragraph(b('Time'), ParagraphStyle('oh', fontName='Helvetica-Bold', fontSize=9.5, textColor=BLACK, leading=13)),
         Paragraph(b('Internet needed?'), ParagraphStyle('oh', fontName='Helvetica-Bold', fontSize=9.5, textColor=BLACK, leading=13))],
        ['Install Python 3.10 or newer', '5 min', 'Yes'],
        ['Copy the project folder to this PC', '1 min', 'No'],
        ['Create virtual environment', '1 min', 'No'],
        ['Install Python packages (pip install)', '5–10 min', 'Yes'],
        ['Install PyTorch (CPU version)', '10–20 min', 'Yes (~500 MB)'],
        ['Set up API keys in .env file', '10 min', 'Yes (register accounts)'],
        ['Download the AI model (first run only)', '5 min', 'Yes (~300 MB)'],
        ['Run the app', 'Under 30 sec', 'No'],
    ]

    ov_rows = []
    for i, row in enumerate(ov_data):
        if i == 0:
            ov_rows.append(row)
        else:
            ov_rows.append([
                Paragraph(row[0], ParagraphStyle('oc', fontName='Helvetica', fontSize=9.5, textColor=DARK, leading=13)),
                Paragraph(row[1], ParagraphStyle('oc', fontName='Helvetica', fontSize=9.5, textColor=DARK, leading=13)),
                Paragraph(row[2], ParagraphStyle('oc', fontName='Helvetica', fontSize=9.5, textColor=DARK, leading=13)),
            ])

    ov_tbl = Table(ov_rows, colWidths=[7.5*cm, 2.5*cm, 4.2*cm])
    ov_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0), LGREY),
        ('GRID',          (0, 0), (-1, -1), 0.5, BORDER),
        ('LEFTPADDING',   (0, 0), (-1, -1), 8),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    els.append(ov_tbl)
    els.append(Spacer(1, 0.3 * cm))
    els.append(note_box('NOTE',
        'Total time: about 30–45 minutes on the first setup. '
        'After that, starting the app takes under 10 seconds.'))
    els.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # SECTION: SYSTEM REQUIREMENTS
    # ═══════════════════════════════════════════════════════════
    els += section_title('Section 1 — System Requirements', s)
    els.append(Paragraph(
        'Make sure your computer meets these requirements before starting.',
        s['body']))
    els.append(Spacer(1, 0.2 * cm))

    req_rows = [
        [Paragraph(b('Requirement'), ParagraphStyle('rh', fontName='Helvetica-Bold', fontSize=9.5, textColor=BLACK, leading=13)),
         Paragraph(b('Minimum'), ParagraphStyle('rh', fontName='Helvetica-Bold', fontSize=9.5, textColor=BLACK, leading=13)),
         Paragraph(b('Why it matters'), ParagraphStyle('rh', fontName='Helvetica-Bold', fontSize=9.5, textColor=BLACK, leading=13))],
    ]
    reqs = [
        ('Operating System', 'Windows 10 / macOS 11 / Ubuntu 20.04', 'Python 3.10 runs on all three'),
        ('Python',           '3.10 or newer',                        'Required for Flask and PyTorch'),
        ('RAM (Memory)',     '4 GB (8 GB recommended)',               'PyTorch needs ~1.5 GB to load the AI model'),
        ('Free Disk Space',  '2 GB',                                  '500 MB PyTorch + 300 MB AI model + project files'),
        ('CPU',              'Any 64-bit processor',                  'No GPU required — runs entirely on CPU'),
        ('Internet',         'Required during setup',                  'Downloading packages and the AI model'),
        ('Web Browser',      'Chrome, Firefox, Edge, or Safari',      'Opens the app at localhost:5000'),
    ]
    for item, minimum, why in reqs:
        req_rows.append([
            Paragraph(item,    ParagraphStyle('rd', fontName='Helvetica', fontSize=9.5, textColor=DARK, leading=13)),
            Paragraph(minimum, ParagraphStyle('rd', fontName='Helvetica', fontSize=9.5, textColor=DARK, leading=13)),
            Paragraph(why,     ParagraphStyle('rd', fontName='Helvetica', fontSize=9.5, textColor=DARK, leading=13)),
        ])

    req_tbl = Table(req_rows, colWidths=[3.8*cm, 4.2*cm, 6.2*cm])
    req_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0), LGREY),
        ('GRID',          (0, 0), (-1, -1), 0.5, BORDER),
        ('LEFTPADDING',   (0, 0), (-1, -1), 8),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
    ]))
    els.append(req_tbl)
    els.append(Spacer(1, 0.3 * cm))
    els.append(note_box('TIP',
        'MoodRoute does NOT need a GPU (graphics card). It runs entirely on the CPU. '
        'You do not need CUDA or any GPU drivers.'))
    els.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # SECTION: STEP BY STEP INSTALLATION
    # ═══════════════════════════════════════════════════════════
    els += section_title('Section 2 — Step-by-Step Installation', s)
    els.append(Paragraph(
        'Follow each step in order. Do not skip a step — each one depends on the previous.',
        s['body']))

    # ─── STEP 1 ────────────────────────────────────────────────
    els.append(step_header(1, 'Install Python 3.10 or Newer', s))
    els.append(Paragraph(
        'Python is the programming language MoodRoute is written in. '
        'It must be installed before anything else.',
        s['body']))

    els.append(Paragraph(b('Windows:'), s['subsection']))
    els.append(code_block([
        '1.  Go to:  https://www.python.org/downloads/',
        '2.  Click "Download Python 3.11.x" (or any newer version)',
        '3.  Run the downloaded installer (.exe file)',
        '4.  IMPORTANT: Check the box "Add Python to PATH"',
        '5.  Click "Install Now" and wait for it to finish',
    ]))
    els.append(Spacer(1, 0.15 * cm))

    els.append(Paragraph(b('macOS:'), s['subsection']))
    els.append(code_block([
        '1.  Go to:  https://www.python.org/downloads/',
        '2.  Download and run the macOS installer (.pkg file)',
        '',
        '    OR if you have Homebrew installed:',
        '    brew install python@3.11',
    ]))
    els.append(Spacer(1, 0.15 * cm))

    els.append(Paragraph(b('Linux (Ubuntu / Debian):'), s['subsection']))
    els.append(code_block([
        'sudo apt update',
        'sudo apt install python3.11 python3.11-venv python3-pip -y',
    ]))
    els.append(Spacer(1, 0.2 * cm))

    els.append(Paragraph(
        b('Verify that Python installed correctly — open a terminal and type:'),
        s['subsection']))
    els.append(code_block([
        'python3 --version',
        '',
        '# Expected output:  Python 3.10.x  or higher',
        '# On Windows you may need to type:  python --version',
    ]))
    els.append(Spacer(1, 0.2 * cm))
    els.append(note_box('WARNING',
        'On Windows: if you see "python3 is not recognized", Python was not added to PATH. '
        'Re-run the installer and make sure you tick "Add Python to PATH".'))
    els.append(divider())

    # ─── STEP 2 ────────────────────────────────────────────────
    els.append(step_header(2, 'Copy the MoodRoute Project Folder to This PC', s))
    els.append(Paragraph(
        'Copy the entire MoodRoute folder to your computer — from a USB drive, '
        'GitHub, or any other transfer method.',
        s['body']))
    els.append(Paragraph(
        b('The folder must contain these files and folders:'),
        s['subsection']))
    els.append(code_block([
        'MoodRoute/',
        '  app.py                 <-- Flask entry point (run this to start the app)',
        '  config.py              <-- Configuration settings',
        '  requirements.txt       <-- List of Python packages to install',
        '  .env                   <-- API keys (you will fill this in Step 6)',
        '  backend/',
        '    database/            <-- SQLite database files',
        '    models/              <-- Mood weight configurations',
        '    routes/              <-- API endpoints',
        '    services/            <-- NLP, weather, scoring logic',
        '  frontend/',
        '    templates/           <-- HTML page',
        '    static/              <-- CSS and JavaScript files',
    ]))
    els.append(Spacer(1, 0.15 * cm))
    els.append(note_box('WARNING',
        'Do NOT copy the "venv" folder from another machine. '
        'Virtual environments contain compiled files specific to each computer. '
        'You will create a fresh one in the next step.'))
    els.append(divider())

    # ─── STEP 3 ────────────────────────────────────────────────
    els.append(step_header(3, 'Open a Terminal Inside the MoodRoute Folder', s))
    els.append(Paragraph(
        'All commands from Step 4 onwards must be run inside the MoodRoute folder.',
        s['body']))

    els.append(Paragraph(b('Windows:'), s['subsection']))
    els.append(code_block([
        '1.  Open File Explorer',
        '2.  Navigate into the MoodRoute folder',
        '3.  Click on the address bar at the top',
        '4.  Type:  cmd  and press Enter',
        '    (A black terminal window will open inside the folder)',
    ]))
    els.append(Spacer(1, 0.1 * cm))

    els.append(Paragraph(b('macOS:'), s['subsection']))
    els.append(code_block([
        'Right-click the MoodRoute folder in Finder',
        'Select "New Terminal at Folder"',
    ]))
    els.append(Spacer(1, 0.1 * cm))

    els.append(Paragraph(b('Linux:'), s['subsection']))
    els.append(code_block([
        'Right-click inside the folder and select "Open in Terminal"',
        '',
        '  OR navigate manually:',
        '  cd /path/to/MoodRoute    # replace with the actual path on your computer',
    ]))
    els.append(divider())

    els.append(PageBreak())

    # ─── STEP 4 ────────────────────────────────────────────────
    els.append(step_header(4, 'Create a Virtual Environment', s))
    els.append(Paragraph(
        'A virtual environment is an isolated space for Python packages. '
        'It keeps MoodRoute packages separate from other Python projects on your computer '
        'and prevents version conflicts.',
        s['body']))

    els.append(Paragraph(b('Create the virtual environment (same on all systems):'), s['subsection']))
    els.append(code_block([
        'python3 -m venv venv',
        '',
        '# On Windows use:',
        'python -m venv venv',
    ]))
    els.append(Spacer(1, 0.2 * cm))

    els.append(Paragraph(b('Activate the virtual environment:'), s['subsection']))
    els.append(code_block([
        '# macOS and Linux:',
        'source venv/bin/activate',
        '',
        '# Windows (Command Prompt):',
        'venv\\Scripts\\activate',
    ]))
    els.append(Spacer(1, 0.15 * cm))
    els.append(note_box('TIP',
        'After activation, your terminal prompt will start with "(venv)". '
        'For example:  (venv) C:\\MoodRoute>  or  (venv) user@computer:~/MoodRoute$  '
        'You must activate the venv every time you open a new terminal window.'))
    els.append(divider())

    # ─── STEP 5 ────────────────────────────────────────────────
    els.append(step_header(5, 'Install Python Packages', s))
    els.append(Paragraph(
        'The requirements.txt file lists all Python libraries MoodRoute needs. '
        'One command installs everything:',
        s['body']))
    els.append(code_block([
        'pip install -r requirements.txt',
    ], caption='Make sure the venv is activated (you should see "(venv)" in your prompt)'))
    els.append(Spacer(1, 0.2 * cm))

    els.append(Paragraph(b('This installs the following packages:'), s['subsection']))
    els.append(code_block([
        'flask            -- The web server framework',
        'flask-cors       -- Allows the browser to communicate with the server',
        'flask-limiter    -- Rate limiting (security)',
        'flask-talisman   -- HTTPS and security headers',
        'python-dotenv    -- Reads API keys from the .env file',
        'requests         -- Makes HTTP calls to external APIs',
        'bleach           -- Cleans and sanitises user text input',
        'transformers     -- HuggingFace library for the AI mood model',
    ]))
    els.append(Spacer(1, 0.15 * cm))
    els.append(note_box('WARNING',
        'If you see "ERROR: Could not install packages" — try upgrading pip first:  '
        'pip install --upgrade pip  then run pip install -r requirements.txt again.'))
    els.append(divider())

    # ─── STEP 6 ────────────────────────────────────────────────
    els.append(step_header(6, 'Install PyTorch (The AI Engine)', s))
    els.append(Paragraph(
        'PyTorch is the deep learning library that runs the AI mood detection model. '
        'It is not in requirements.txt because the correct version depends on your '
        'operating system. Always install the CPU-only version (no GPU needed):',
        s['body']))

    els.append(Paragraph(b('Windows and Linux (CPU version):'), s['subsection']))
    els.append(code_block([
        'pip install torch --index-url https://download.pytorch.org/whl/cpu',
        '',
        '# This downloads approximately 500 MB.',
        '# It may take 5 to 20 minutes depending on your internet speed.',
    ]))
    els.append(Spacer(1, 0.15 * cm))

    els.append(Paragraph(b('macOS (Apple Silicon M1/M2/M3 or Intel):'), s['subsection']))
    els.append(code_block([
        'pip install torch',
    ]))
    els.append(Spacer(1, 0.2 * cm))

    els.append(Paragraph(b('Verify PyTorch installed correctly:'), s['subsection']))
    els.append(code_block([
        'python3 -c "import torch; print(torch.__version__)"',
        '',
        '# Expected output:  2.3.0+cpu  (or similar version number)',
    ]))
    els.append(Spacer(1, 0.15 * cm))
    els.append(note_box('WARNING',
        'If the app later crashes with "OSError: libcudart not found", you accidentally '
        'installed the GPU version of PyTorch. Fix it with:  '
        'pip uninstall torch  then  pip install torch --index-url https://download.pytorch.org/whl/cpu'))
    els.append(divider())

    els.append(PageBreak())

    # ─── STEP 7 ────────────────────────────────────────────────
    els.append(step_header(7, 'Set Up API Keys in the .env File', s))
    els.append(Paragraph(
        'MoodRoute uses two external services that require free account registration. '
        'Open the .env file in the MoodRoute folder with any text editor '
        '(Notepad on Windows, TextEdit on macOS, or gedit/nano on Linux).',
        s['body']))

    els.append(Paragraph(b('Current contents of the .env file:'), s['subsection']))
    els.append(code_block([
        'OPENWEATHER_API_KEY=your_openweather_key_here',
        'FOURSQUARE_API_KEY=your_foursquare_key_here',
        'FLASK_SECRET_KEY=moodroute-secret-change-in-production',
        'FLASK_DEBUG=True',
    ]))
    els.append(Spacer(1, 0.2 * cm))

    els.append(Paragraph(b('API Key 1 — OpenWeatherMap (provides live weather data):'), s['subsection']))
    els.append(code_block([
        '1.  Go to:  https://openweathermap.org/api',
        '2.  Click "Sign In" and create a free account',
        '3.  After signing in, go to:  https://home.openweathermap.org/api_keys',
        '4.  Copy the "Default" key shown on that page',
        '5.  Replace "your_openweather_key_here" in .env with your key',
        '',
        '    OPENWEATHER_API_KEY=abc123youractualkey',
        '',
        '    Note: New keys take up to 2 hours to activate after registration.',
    ]))
    els.append(Spacer(1, 0.2 * cm))

    els.append(Paragraph(b('API Key 2 — Foursquare (estimates crowd density near routes):'), s['subsection']))
    els.append(code_block([
        '1.  Go to:  https://developer.foursquare.com/',
        '2.  Click "Sign Up" and create a free account',
        '3.  Create a new project (any name is fine)',
        '4.  Go to the API Keys section and copy your key',
        '5.  Replace "your_foursquare_key_here" in .env with your key',
        '',
        '    FOURSQUARE_API_KEY=xyz789youractualkey',
    ]))
    els.append(Spacer(1, 0.2 * cm))

    els.append(Paragraph(b('Flask Secret Key — generate a secure random value:'), s['subsection']))
    els.append(code_block([
        'python3 -c "import secrets; print(secrets.token_hex(32))"',
        '',
        '# Copy the output and paste it into .env:',
        '# FLASK_SECRET_KEY=the_32_character_string_you_just_generated',
    ]))
    els.append(Spacer(1, 0.15 * cm))
    els.append(note_box('NOTE',
        'The app still works without API keys — it uses built-in default values. '
        'Without keys: weather shows a clear-sky default, crowd scores use distance-based '
        'estimates. The route recommendations still work, they just do not use live data.'))
    els.append(note_box('WARNING',
        'Never share your .env file or upload it to GitHub. '
        'It contains private API keys. The .gitignore file already excludes it.'))
    els.append(divider())

    # ─── STEP 8 ────────────────────────────────────────────────
    els.append(step_header(8, 'Download the AI Model (First Run Only)', s))
    els.append(Paragraph(
        'The distilRoBERTa mood detection model (~300 MB) downloads from HuggingFace '
        'the first time the app runs. On most home or office internet connections '
        'this happens automatically — you can skip to Step 9.',
        s['body']))
    els.append(Paragraph(
        b('Only follow this step if you are on a university or corporate network with SSL inspection:'),
        s['subsection']))
    els.append(code_block([
        '# macOS and Linux -- run once in terminal:',
        'HF_HUB_DISABLE_SSL_VERIFY=1 python3 -c "from transformers import pipeline; p = pipeline(\'text-classification\', model=\'j-hartmann/emotion-english-distilroberta-base\', top_k=None); print(\'Model downloaded successfully!\')"',
    ]))
    els.append(Spacer(1, 0.15 * cm))
    els.append(code_block([
        '# Windows -- run in Command Prompt (not PowerShell):',
        'set HF_HUB_DISABLE_SSL_VERIFY=1',
        'python -c "from transformers import pipeline; pipeline(\'text-classification\', model=\'j-hartmann/emotion-english-distilroberta-base\', top_k=None); print(\'Done!\')"',
    ]))
    els.append(Spacer(1, 0.15 * cm))
    els.append(note_box('TIP',
        'After this runs once, the model is saved to ~/.cache/huggingface/hub/ on your computer. '
        'It will not need to be downloaded again, even without internet.'))
    els.append(divider())

    # ─── STEP 9 ────────────────────────────────────────────────
    els.append(step_header(9, 'Run the Application', s))
    els.append(Paragraph(
        'Everything is now installed and configured. Start MoodRoute:',
        s['body']))
    els.append(code_block([
        '# Make sure you are in the MoodRoute folder and venv is activated',
        '',
        'python3 app.py',
        '',
        '# On Windows:',
        'python app.py',
    ]))
    els.append(Spacer(1, 0.2 * cm))

    els.append(Paragraph(b('You should see this output in the terminal:'), s['subsection']))
    els.append(code_block([
        ' * Serving Flask app "app"',
        ' * Debug mode: on',
        ' * Running on http://127.0.0.1:5000',
        ' * Running on http://0.0.0.0:5000',
        'Press CTRL+C to quit',
    ]))
    els.append(Spacer(1, 0.2 * cm))

    els.append(Paragraph(b('Open your web browser and go to:'), s['subsection']))
    els.append(code_block(['http://localhost:5000']))
    els.append(Spacer(1, 0.15 * cm))
    els.append(note_box('TIP',
        'The first run may take 5–10 extra seconds while the AI model loads into memory. '
        'Subsequent runs start in under 2 seconds. '
        'To stop the app: press CTRL+C in the terminal.'))

    els.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # SECTION: QUICK START (every time)
    # ═══════════════════════════════════════════════════════════
    els += section_title('Section 3 — Starting the App Every Time', s)
    els.append(Paragraph(
        'After the first-time setup is done, you only need these commands each time '
        'you want to run MoodRoute:',
        s['body']))
    els.append(code_block([
        '# 1. Open a terminal in the MoodRoute folder',
        '',
        '# 2. Activate the virtual environment',
        'source venv/bin/activate          # macOS and Linux',
        'venv\\Scripts\\activate             # Windows',
        '',
        '# 3. Start the app',
        'python3 app.py',
        '',
        '# 4. Open this address in your browser',
        'http://localhost:5000',
    ], caption='Quick startup — 3 commands'))
    els.append(Spacer(1, 0.3 * cm))
    els.append(note_box('NOTE',
        'You do NOT need internet to run the app after the first setup. '
        'The AI model is saved locally. If no internet is available, '
        'the weather and crowd APIs will use their fallback values automatically.'))

    els.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # SECTION: TROUBLESHOOTING
    # ═══════════════════════════════════════════════════════════
    els += section_title('Section 4 — Troubleshooting Common Problems', s)
    els.append(Paragraph(
        'If something does not work, find your error below and follow the fix.',
        s['body']))
    els.append(Spacer(1, 0.2 * cm))

    problems = [
        ('"python3" is not recognized / command not found',
         ['Try "python" instead of "python3" — this is common on Windows.',
          'If neither works, Python is not installed correctly.',
          'Reinstall Python and make sure you tick "Add Python to PATH" on Windows.']),

        ('Port 5000 is already in use',
         ['Another program is using port 5000.',
          'Either close that program, or run MoodRoute on a different port:',
          '  flask run --port 5001',
          'Then open http://localhost:5001 in your browser instead.']),

        ('ModuleNotFoundError: No module named "flask" (or any package)',
         ['The virtual environment is not activated.',
          'Run:  source venv/bin/activate  (macOS/Linux)',
          '  or:  venv\\Scripts\\activate  (Windows)',
          'Then run python3 app.py again.']),

        ('SSL certificate error when downloading the AI model',
         ['You are on a university or corporate network with SSL inspection.',
          'Use the SSL-bypass command in Step 8 of this guide.',
          'This only needs to run once to cache the model locally.']),

        ('The map does not load — just a grey or blank background',
         ['The map tiles come from OpenStreetMap and require internet.',
          'If you are offline, the background will be blank but the app still works.',
          'Routes will still be drawn on the blank background.']),

        ('Weather shows "--°C" and never updates',
         ['Your OpenWeatherMap API key is missing or not yet activated.',
          'New keys take up to 2 hours to activate after registration.',
          'Check your .env file has: OPENWEATHER_API_KEY=your_actual_key',
          'The app works without weather — it uses Clear weather as the default.']),

        ('"No module named torch" even after installing packages',
         ['PyTorch is not in requirements.txt — it needs a separate install.',
          'Run:  pip install torch --index-url https://download.pytorch.org/whl/cpu',
          'Then restart the app.']),

        ('OSError: libcudart not found / CUDA error',
         ['You installed the GPU version of PyTorch but your machine has no GPU.',
          'Fix it:',
          '  pip uninstall torch',
          '  pip install torch --index-url https://download.pytorch.org/whl/cpu']),

        ('Database error or "no such table" on startup',
         ['The database file is missing or from an incompatible version.',
          'Delete this file:  backend/database/moodroute.db',
          'Restart the app — it will rebuild the database automatically.']),

        ('All moods recommend the same route',
         ['This can happen if the database was not reseeded after an update.',
          'Delete:  backend/database/moodroute.db',
          'Restart the app — it will reseed with the correct pre-scored routes.']),
    ]

    for problem, solutions in problems:
        els.append(Paragraph(f'Problem:  {b(problem)}',
                             ParagraphStyle('pb', fontName='Helvetica', fontSize=10,
                                            textColor=DARK, leading=14,
                                            spaceBefore=8, spaceAfter=3)))
        els.append(code_block(solutions, caption='Fix:'))
        els.append(Spacer(1, 0.15 * cm))

    els.append(PageBreak())

    # ═══════════════════════════════════════════════════════════
    # SECTION: FILE REFERENCE
    # ═══════════════════════════════════════════════════════════
    els += section_title('Section 5 — Project File Reference', s)
    els.append(Paragraph(
        'This table explains what each file does and whether you need to edit it.',
        s['body']))
    els.append(Spacer(1, 0.2 * cm))

    file_rows = [
        [Paragraph(b('File / Folder'), ParagraphStyle('fh', fontName='Helvetica-Bold', fontSize=9.5, textColor=BLACK, leading=13)),
         Paragraph(b('What it does'), ParagraphStyle('fh', fontName='Helvetica-Bold', fontSize=9.5, textColor=BLACK, leading=13)),
         Paragraph(b('Edit?'), ParagraphStyle('fh', fontName='Helvetica-Bold', fontSize=9.5, textColor=BLACK, leading=13))],
    ]
    files = [
        ('app.py',                           'Starts the Flask server. Registers all routes and security.',                    'Only if changing port or server settings'),
        ('config.py',                        'Reads API keys and settings from the .env file.',                                'No — edit .env instead'),
        ('.env',                             'Your private API keys and settings. Never share this file.',                     'Yes — add your API keys here'),
        ('requirements.txt',                 'List of Python packages. Used by pip install -r requirements.txt.',              'No'),
        ('backend/database/db.py',           'Sets up the SQLite database and seeds the 15 walking routes.',                   'No — unless adding new routes'),
        ('backend/database/schema.sql',      'Defines the database table structure.',                                          'No'),
        ('backend/models/mood_mapper.py',    'Mood weight configurations used by the scoring algorithm.',                      'Only if adjusting mood weights'),
        ('backend/services/nlp_service.py',  'Loads the AI model and detects mood from typed text.',                           'No'),
        ('backend/services/route_scorer.py', 'Implements the WLC scoring formula.',                                            'Only if adjusting the algorithm'),
        ('backend/routes/route_api.py',      'The main /api/find-route endpoint — full recommendation pipeline.',              'No'),
        ('frontend/templates/index.html',    'The HTML page the user sees in the browser.',                                    'If changing UI structure'),
        ('frontend/static/css/style.css',    'All styling — colours, layout, animations.',                                     'If changing appearance'),
        ('frontend/static/js/app.js',        'Handles user interactions and API calls in the browser.',                        'If changing UI behaviour'),
        ('frontend/static/js/map.js',        'Leaflet map setup — draws boundary circles, routes, and markers.',               'If changing map display'),
        ('backend/database/moodroute.db',    'The SQLite database (auto-created on first run). Delete to reset all data.',     'Delete to reset'),
    ]
    for fname, what, edit in files:
        file_rows.append([
            Paragraph(fname, ParagraphStyle('fn', fontName='Courier', fontSize=8.5, textColor=DARK, leading=12)),
            Paragraph(what,  ParagraphStyle('fd', fontName='Helvetica', fontSize=9, textColor=DARK, leading=13)),
            Paragraph(edit,  ParagraphStyle('fe', fontName='Helvetica', fontSize=9, textColor=DARK, leading=13)),
        ])

    ft = Table(file_rows, colWidths=[4.8*cm, 6.5*cm, 2.9*cm])
    ft.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0), LGREY),
        ('GRID',          (0, 0), (-1, -1), 0.5, BORDER),
        ('LEFTPADDING',   (0, 0), (-1, -1), 7),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 7),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
    ]))
    els.append(ft)
    els.append(Spacer(1, 0.5 * cm))

    # ── Final Checklist ────────────────────────────────────────
    els += section_title('Setup Checklist', s)
    els.append(Paragraph(
        'Tick each item before trying to run the app:', s['body']))
    els.append(Spacer(1, 0.1 * cm))

    checklist = [
        'Python 3.10 or newer is installed  (python3 --version)',
        'MoodRoute folder is copied to this PC with all files inside',
        'Virtual environment created:  python3 -m venv venv',
        'Virtual environment activated:  source venv/bin/activate  (or  venv\\Scripts\\activate  on Windows)',
        'Packages installed:  pip install -r requirements.txt',
        'PyTorch installed:  pip install torch --index-url https://download.pytorch.org/whl/cpu',
        '.env file has real API keys  (or confirmed fallback mode is acceptable)',
        'Flask secret key is set in .env  (not the default placeholder)',
        'App starts with:  python3 app.py  without errors',
        'Browser opens http://localhost:5000 and the map loads',
    ]
    for item in checklist:
        els.append(Paragraph(
            f'\u2610   {item}',
            ParagraphStyle('ci', fontName='Helvetica', fontSize=10,
                           textColor=DARK, leading=18)))

    # ── Build ──────────────────────────────────────────────────
    doc.build(els, onFirstPage=lambda c,d: None, onLaterPages=on_page)
    print(f'setup.pdf saved to: {output_path}')


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'setup.pdf')
    build(out)
