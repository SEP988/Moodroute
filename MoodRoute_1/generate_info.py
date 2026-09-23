"""
MoodRoute — Technologies & Tools Information Document Generator
Produces info.pdf: a clear, plain-English guide to every technology used,
why it was chosen, and how it maps to the project requirements.
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

# Colours
DARK   = HexColor('#1a1d2e')
INDIGO = HexColor('#2d3561')
TEAL   = HexColor('#1abc9c')
LGREY  = HexColor('#f5f6fa')
MGREY  = HexColor('#6b7280')
BGREY  = HexColor('#e5e7eb')
WHITE  = white
BLACK  = black


# ── Page numbers ─────────────────────────────────────────────────────────────
def footer(canv, doc):
    canv.saveState()
    w, h = A4
    canv.setFillColor(INDIGO)
    canv.rect(0, 0, w, 0.8 * cm, fill=True, stroke=False)
    canv.setFillColor(WHITE)
    canv.setFont('Helvetica', 7.5)
    canv.drawCentredString(w / 2, 0.27 * cm,
        f'MoodRoute — Technologies & Tools Reference   |   CSIT998 Capstone · University of Wollongong 2026   |   Page {doc.page}')
    canv.restoreState()


# ── Styles ────────────────────────────────────────────────────────────────────
def styles():
    return {
        'h1': ParagraphStyle('h1', fontName='Helvetica-Bold', fontSize=26,
                             textColor=WHITE, alignment=TA_CENTER,
                             leading=32, spaceAfter=4),
        'h1sub': ParagraphStyle('h1sub', fontName='Helvetica', fontSize=12,
                                textColor=HexColor('#a5b4fc'), alignment=TA_CENTER,
                                leading=18, spaceAfter=4),
        'h2': ParagraphStyle('h2', fontName='Helvetica-Bold', fontSize=14,
                             textColor=INDIGO, spaceBefore=18, spaceAfter=6,
                             leading=18),
        'h3': ParagraphStyle('h3', fontName='Helvetica-Bold', fontSize=11,
                             textColor=INDIGO, spaceBefore=10, spaceAfter=3,
                             leading=15),
        'body': ParagraphStyle('body', fontName='Helvetica', fontSize=10,
                               textColor=DARK, leading=15.5, spaceAfter=6,
                               alignment=TA_JUSTIFY),
        'meta': ParagraphStyle('meta', fontName='Helvetica', fontSize=9,
                               textColor=MGREY, leading=14, spaceAfter=4),
        'badge': ParagraphStyle('badge', fontName='Helvetica-Bold', fontSize=9,
                                textColor=WHITE, leading=12),
        'cover_meta': ParagraphStyle('cover_meta', fontName='Helvetica', fontSize=10,
                                     textColor=HexColor('#c7d2fe'), alignment=TA_CENTER,
                                     leading=16),
        'req_label': ParagraphStyle('req_label', fontName='Helvetica-Bold', fontSize=9,
                                    textColor=TEAL, leading=13),
        'req_text': ParagraphStyle('req_text', fontName='Helvetica', fontSize=9.5,
                                   textColor=DARK, leading=14, alignment=TA_JUSTIFY),
    }


def rule(color=TEAL, thick=1.2):
    return HRFlowable(width='100%', thickness=thick, color=color,
                      spaceAfter=8, spaceBefore=4)


def thin_rule():
    return HRFlowable(width='100%', thickness=0.4, color=BGREY,
                      spaceAfter=8, spaceBefore=8)


def section_header(title, icon, s):
    """Coloured section title with icon."""
    tbl = Table([[
        Paragraph(f'{icon}  {title}', ParagraphStyle(
            'sh', fontName='Helvetica-Bold', fontSize=13,
            textColor=WHITE, leading=17))
    ]], colWidths=[PAGE_W - 2 * MARGIN])
    tbl.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, -1), INDIGO),
        ('TOPPADDING',   (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 10),
        ('LEFTPADDING',  (0, 0), (-1, -1), 14),
        ('RIGHTPADDING', (0, 0), (-1, -1), 14),
    ]))
    return tbl


def tech_block(name, category, purpose, how_it_works, requirement_link, s):
    """One technology card."""
    elements = []

    # Name row with category badge
    name_cell = Paragraph(f'<b>{name}</b>', ParagraphStyle(
        'tn', fontName='Helvetica-Bold', fontSize=11, textColor=INDIGO, leading=15))
    cat_cell = Paragraph(category, ParagraphStyle(
        'tc', fontName='Helvetica-Bold', fontSize=8, textColor=WHITE, leading=11))

    header = Table([[name_cell, cat_cell]],
                   colWidths=[PAGE_W - 2*MARGIN - 3.5*cm, 3.3*cm])
    header.setStyle(TableStyle([
        ('BACKGROUND',    (1, 0), (1, 0), TEAL),
        ('ALIGN',         (1, 0), (1, 0), 'CENTER'),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',   (0, 0), (0, 0), 0),
        ('RIGHTPADDING',  (0, 0), (0, 0), 6),
        ('LEFTPADDING',   (1, 0), (1, 0), 6),
        ('RIGHTPADDING',  (1, 0), (1, 0), 6),
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROUNDEDCORNERS', [3]),
    ]))
    elements.append(header)

    # Purpose
    elements.append(Paragraph(
        f'<b>What it does:</b>  {purpose}',
        ParagraphStyle('tp', fontName='Helvetica', fontSize=10,
                       textColor=DARK, leading=15, spaceAfter=3)))

    # How it works
    elements.append(Paragraph(
        f'<b>How it works in MoodRoute:</b>  {how_it_works}',
        ParagraphStyle('th', fontName='Helvetica', fontSize=10,
                       textColor=DARK, leading=15, spaceAfter=3)))

    # Requirement link
    elements.append(Paragraph(
        f'📋  <i>{requirement_link}</i>',
        ParagraphStyle('tr', fontName='Helvetica-Oblique', fontSize=9,
                       textColor=TEAL, leading=13, spaceAfter=0)))

    # Wrap in a box
    content_tbl = Table([[elements]], colWidths=[PAGE_W - 2*MARGIN - 0.4*cm])
    content_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), LGREY),
        ('BOX',           (0, 0), (-1, -1), 0.8, BGREY),
        ('LEFTPADDING',   (0, 0), (-1, -1), 12),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 12),
        ('TOPPADDING',    (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    return [content_tbl, Spacer(1, 0.3 * cm)]


# ── Cover ─────────────────────────────────────────────────────────────────────
def cover_page(s):
    cover = Table([[
        Spacer(1, 2.5 * cm),
        Paragraph('MoodRoute', s['h1']),
        Spacer(1, 0.3 * cm),
        Paragraph('Technologies, Tools &amp; Supporting Requirements', s['h1sub']),
        HRFlowable(width='50%', thickness=2, color=TEAL,
                   spaceAfter=30, spaceBefore=10),
        Paragraph(
            'A plain-English reference document explaining every technology used '
            'in the MoodRoute application — what it is, why we chose it, '
            'how it works inside the app, and how it maps to the '
            'project requirements.',
            ParagraphStyle('cd', fontName='Helvetica', fontSize=11,
                           textColor=HexColor('#c7d2fe'), alignment=TA_CENTER,
                           leading=18, spaceAfter=30)),
        Spacer(1, 1.5 * cm),
        Paragraph('CSIT998 Professional Capstone Project   ·   Annual Session 2026',
                  s['cover_meta']),
        Paragraph('University of Wollongong   ·   Group MoodMappers',
                  s['cover_meta']),
        Paragraph('Supervisor: Mr. Partha Sarathy Roy',
                  s['cover_meta']),
    ]], colWidths=[PAGE_W - 2*MARGIN])
    cover.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), INDIGO),
        ('TOPPADDING',    (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING',   (0, 0), (-1, -1), 0),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
    ]))
    return [cover, PageBreak()]


# ── Build the PDF ─────────────────────────────────────────────────────────────
def build(output_path):
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=1.8*cm, bottomMargin=1.5*cm,
        title='MoodRoute — Technologies & Tools Reference',
        author='Group MoodMappers — CSIT998'
    )

    s = styles()
    els = []

    # ── Cover ──────────────────────────────────────────────────────────────
    els += cover_page(s)

    # ── Introduction ───────────────────────────────────────────────────────
    els.append(section_header('About This Document', '📄', s))
    els.append(Spacer(1, 0.3*cm))
    els.append(Paragraph(
        'This document is a complete reference for every technology and tool used '
        'to build MoodRoute. It is written so that anyone — technical or '
        'non-technical — can understand what each piece does, why the team chose '
        'it, and how it connects to the original project requirements.',
        s['body']))
    els.append(Paragraph(
        'MoodRoute is a web application for University of Wollongong students. '
        'You type how you are feeling, and the app uses an AI model to understand '
        'your mood. It then scores all nearby walking routes using real environmental '
        'data — how green the area is, how quiet, how flat, how crowded — and recommends '
        'the one that best suits your emotional state right now.',
        s['body']))
    els.append(Spacer(1, 0.3*cm))

    # Quick summary table
    summary = [
        [Paragraph('<b>Layer</b>', ParagraphStyle('sh', fontName='Helvetica-Bold', fontSize=9, textColor=WHITE, leading=12)),
         Paragraph('<b>Technology</b>', ParagraphStyle('sh', fontName='Helvetica-Bold', fontSize=9, textColor=WHITE, leading=12)),
         Paragraph('<b>Role in App</b>', ParagraphStyle('sh', fontName='Helvetica-Bold', fontSize=9, textColor=WHITE, leading=12))],
        ['Frontend', 'HTML, CSS, JavaScript', 'User interface — what you see and interact with'],
        ['Maps', 'Leaflet.js + OpenStreetMap', 'Interactive map showing routes and UOW boundary'],
        ['Backend', 'Python + Flask', 'Server that handles all logic and API calls'],
        ['AI / NLP', 'HuggingFace distilRoBERTa', 'Understands what mood you described in text'],
        ['Weather', 'OpenWeatherMap API', 'Live weather — blocks walks when dangerous'],
        ['Greenery', 'OpenStreetMap Overpass API', 'Counts parks and trees near each route'],
        ['Noise', 'OpenStreetMap Road Data', 'Estimates traffic noise by road type'],
        ['Terrain', 'Open-Elevation API', 'Checks how hilly or flat a route is'],
        ['Crowd', 'Foursquare Places API', 'Estimates how busy/crowded an area is'],
        ['Routing', 'OSRM (Open Source Routing Machine)', 'Draws real walkable paths between points'],
        ['Database', 'SQLite', 'Stores routes, ratings, and cached scores'],
        ['Security', 'Flask-Talisman + Flask-Limiter + bleach', 'HTTPS, rate limiting, input sanitisation'],
    ]

    col_w = [3.0*cm, 5.5*cm, PAGE_W - 2*MARGIN - 8.9*cm]
    tbl_data = []
    for i, row in enumerate(summary):
        if i == 0:
            tbl_data.append([
                Paragraph(str(c), ParagraphStyle('sh', fontName='Helvetica-Bold',
                          fontSize=9, textColor=WHITE, leading=12)) for c in row])
        else:
            tbl_data.append([
                Paragraph(str(c), ParagraphStyle('sc', fontName='Helvetica',
                          fontSize=9, textColor=DARK, leading=13)) for c in row])

    t = Table(tbl_data, colWidths=col_w)
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0), INDIGO),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [LGREY, WHITE]),
        ('GRID',          (0, 0), (-1, -1), 0.4, BGREY),
        ('LEFTPADDING',   (0, 0), (-1, -1), 8),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
    ]))
    els.append(t)
    els.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 1 — FRONTEND
    # ══════════════════════════════════════════════════════════════════════════
    els.append(section_header('Section 1 — Frontend (User Interface)', '🖥️', s))
    els.append(Spacer(1, 0.25*cm))
    els.append(Paragraph(
        'The frontend is everything the user sees and touches. It runs entirely '
        'in the browser — no installation needed. The three standard web technologies '
        'work together: HTML builds the structure, CSS makes it look good, and '
        'JavaScript makes it interactive.',
        s['body']))
    els.append(Spacer(1, 0.1*cm))

    for block in [
        ('HTML5 (HyperText Markup Language)', 'Frontend — Structure',
         'Defines every element on the page: the mood input box, the pill buttons, the result card, the map container, and the floating panel.',
         'All the visible elements you interact with — the mood description box, the Stressed/Anxious/Tired/Happy buttons, the Find My Route button, the star rating, the weather display — are defined in a single HTML file (index.html). The structure is mobile-first, meaning it works cleanly on a phone screen.',
         'Requirement: "Build a working web application … easy to use, so that someone who is already feeling stressed or tired does not have to struggle" (Section 1.1, Aims)'),

        ('CSS3 (Cascading Style Sheets)', 'Frontend — Styling',
         'Controls the visual appearance: colours, fonts, layout, animations, and responsive design.',
         'MoodRoute uses a deep indigo and teal colour palette chosen to feel calm and trustworthy — appropriate for users who may be in a stressed or anxious state. The draggable floating panel, the pulsing UOW campus ring on the map, the animated score bars, and the smooth loading steps are all CSS animations. The layout automatically adjusts for phone, tablet, and desktop screens.',
         'Requirement: "We want the app to feel natural and easy to use" (Section 1.1). Also supports the health requirement that the interface should not add to user stress.'),

        ('JavaScript (ES6+)', 'Frontend — Interactivity',
         'Handles all user interactions: detecting button clicks, sending data to the backend, receiving the route result, and updating the map without reloading the page.',
         'When you click Find My Route, JavaScript collects your typed mood and location, sanitises the input (removes any dangerous characters), sends it to the Flask backend via a fetch() call, waits for the response, and then updates the map and result panel — all without the page reloading. It also handles the draggable panel so you can move the input panel to any corner of the screen.',
         'Requirement: Real-time interaction and single-page behaviour expected for a modern web application.'),

        ('Leaflet.js (v1.9.4)', 'Frontend — Maps',
         'An open-source JavaScript library for building interactive maps in the browser. Free to use, with no licensing restrictions.',
         'Leaflet.js renders the OpenStreetMap tiles as the background of the entire page. It draws the UOW campus boundary (three concentric circles with a pulsing animation), plots the recommended walking route as a coloured polyline with direction arrows, places the green START marker at UOW campus and the red END marker at the destination, and handles the user location dot. The 5km service area circle and the Foursquare/weather overlays all go through Leaflet.',
         'Requirement: "Leaflet.js is the best free option for interactive maps … free and well documented" (Section 2, Technology Stack). Also satisfies the requirement to "display the best route on the Leaflet.js map" (Section 2.3).'),
    ]:
        els += tech_block(*block, s=s)

    els.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 2 — BACKEND
    # ══════════════════════════════════════════════════════════════════════════
    els.append(section_header('Section 2 — Backend (Server & Application Logic)', '⚙️', s))
    els.append(Spacer(1, 0.25*cm))
    els.append(Paragraph(
        'The backend is the brain of the application. It runs on the server, '
        'receives requests from the browser, calls the AI model and external APIs, '
        'runs the scoring algorithm, and sends back the route recommendation. '
        'The user never sees the backend directly.',
        s['body']))
    els.append(Spacer(1, 0.1*cm))

    for block in [
        ('Python 3.10', 'Backend — Language',
         'The programming language the entire backend is written in.',
         'Python was chosen because it is the native language of the HuggingFace Transformers library, which is what runs the AI mood detection model. Everything else — the Flask server, the API calls, the scoring algorithm, the database queries — is also written in Python so the whole backend is one consistent codebase.',
         'Requirement: "Python also works well with HuggingFace" (Section 2, Technology Stack).'),

        ('Flask (v3.0.3)', 'Backend — Web Framework',
         'A lightweight Python web framework that turns Python code into a web server that browsers can talk to.',
         'Flask listens on port 5000 and handles three API endpoints: POST /api/detect-mood (runs the NLP model), POST /api/find-route (full pipeline: mood → weather → score → route), and POST /api/rate (saves the post-walk star rating). Each endpoint is its own Python function. Flask receives the browser\'s request, runs the appropriate function, and returns a JSON response.',
         'Requirement: "Flask is lightweight and easy to learn" (Section 2, Technology Stack). The proposal specifically names Flask as the backend framework.'),

        ('SQLite', 'Backend — Database',
         'A simple, file-based database that requires no separate server to run. The entire database is a single .db file.',
         'SQLite stores three things: (1) the 15 pre-seeded walking routes around UOW campus — each with coordinates, distance, area type, start/end point names, and pre-researched environmental scores; (2) post-walk star ratings from users, linked to the route and mood used; (3) a score cache table that saves computed API scores for 24 hours so the same Overpass/Elevation query is not repeated unnecessarily.',
         'Requirement: "SQLite — Free, simple, and needs no separate server setup. Suitable for our scale" (Section 2, Technology Stack).'),
    ]:
        els += tech_block(*block, s=s)

    els.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 3 — AI / NLP
    # ══════════════════════════════════════════════════════════════════════════
    els.append(section_header('Section 3 — AI & NLP (Mood Detection)', '🧠', s))
    els.append(Spacer(1, 0.25*cm))
    els.append(Paragraph(
        'The mood detection module is the most unique part of MoodRoute. '
        'Instead of asking you to pick a mood from a list, you can type anything '
        'in your own words and the AI reads it and understands how you are feeling. '
        'This is made possible by a pre-trained transformer model from HuggingFace.',
        s['body']))
    els.append(Spacer(1, 0.1*cm))

    for block in [
        ('HuggingFace Transformers Library', 'AI — Framework',
         'An open-source Python library that provides ready-to-use pre-trained AI models. You load a model in three lines of code and it works immediately.',
         'MoodRoute uses HuggingFace to load the distilRoBERTa emotion model. The library handles everything about running the neural network — loading the model weights (~300MB) into memory, converting your text into numerical tokens the model can read, running the mathematical inference, and returning probability scores for each emotion. The MoodDetector class in nlp_service.py uses a singleton pattern so the model loads only once when the server starts, then stays in memory for all subsequent requests.',
         'Requirement: "We plan to use a pre-trained model called distilRoBERTa, available through the HuggingFace Transformers library" (Section 1.3, NLP for Emotion Detection).'),

        ('distilRoBERTa (j-hartmann/emotion-english-distilroberta-base)', 'AI — NLP Model',
         'A pre-trained deep learning model that reads English text and classifies it into one of seven emotions: joy, sadness, anger, fear, disgust, surprise, and neutral.',
         'When a user types "I am feeling really overwhelmed with my assignments", the model tokenises the text, runs it through 6 transformer layers with self-attention mechanisms (meaning it understands words in the context of the whole sentence, not just individually), and outputs probability scores for all seven emotions. In this example it would return something like sadness=0.72, anger=0.18, neutral=0.06 … The highest score becomes the detected emotion. That emotion is then mapped to one of the six MoodRoute moods: stressed, anxious, tired, sad, happy, or energetic. A keyword-based fallback activates automatically if the model cannot be downloaded due to network restrictions.',
         'Requirement: "distilRoBERTa … classifies input text into seven emotion categories: joy, sadness, anger, fear, disgust, surprise, and neutral. Using a pre-trained model means we do not need to build and train our own from scratch" (Section 1.3). Also directly satisfies Aim 1: "detect a user\'s mood from a short typed description".'),
    ]:
        els += tech_block(*block, s=s)

    els.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 4 — EXTERNAL APIs
    # ══════════════════════════════════════════════════════════════════════════
    els.append(section_header('Section 4 — External APIs (Real-World Data)', '🌐', s))
    els.append(Spacer(1, 0.25*cm))
    els.append(Paragraph(
        'MoodRoute pulls live data from five external services to score routes. '
        'None of this data is hardcoded — every recommendation is based on real '
        'information at the time of the request. Each service has a fallback value '
        'so the app continues working even if a service is temporarily unavailable.',
        s['body']))
    els.append(Spacer(1, 0.1*cm))

    for block in [
        ('OpenWeatherMap API', 'External API — Weather',
         'Provides live weather data for any location: temperature, wind speed, humidity, and weather condition (Clear, Rain, Thunderstorm, etc.).',
         'Before recommending any outdoor walk, MoodRoute checks the current weather at the user\'s location. If conditions are dangerous (thunderstorm, tornado, extreme heat above 42°C, heavy snow), the app blocks all outdoor recommendations and shows UOW-specific indoor alternatives instead — the UniActive gym, the library, the UniBar. If rain is detected, all route scores are multiplied by 0.6 as a penalty. If it is a clear day between 15–28°C, scores get a small 1.05 bonus. The weather data also appears in the top-right pill of the UI, updating in real time.',
         'Requirement: "OpenWeatherMap (free tier) — Reliable, well documented, and free for our usage level" (Section 2, Technology Stack). Also directly satisfies the safety requirement: "if the weather is dangerous, the app skips outdoor routes entirely" (Section 2.3).'),

        ('OpenStreetMap + Overpass API', 'External API — Map Data & Greenery',
         'OpenStreetMap is a free, community-built world map. The Overpass API is its query engine — you ask it questions like "how many parks and trees are within 300 metres of this point?" and it answers.',
         'MoodRoute sends an Overpass query for each route that counts green features within a 300m buffer: parks (leisure=park), forests (landuse=forest), grassland (landuse=grass), natural woodland (natural=wood), individual trees (natural=tree), and gardens (leisure=garden). The total count is normalised to a 0-10 greenery score. The same Overpass API is also used to fetch road types (highway=motorway, highway=footway, etc.) along a route, which are converted to a noise/quietness score using a lookup table — a motorway scores 10 for noise (0 for quiet), a footpath scores 0 for noise (10 for quiet).',
         'Requirement: "OpenStreetMap + Nominatim — Free and open-source. No licensing restrictions for academic use" (Section 2). Greenery and quietness are two of the five factors in the WLC scoring algorithm (Section 2, The Route Scoring Algorithm).'),

        ('Open-Elevation API', 'External API — Terrain',
         'A free, open-source service that returns the elevation in metres for any list of latitude/longitude coordinates on Earth.',
         'To calculate the flatness score for a route, MoodRoute samples up to 15 points along the route\'s path and sends them to the Open-Elevation API. It receives the elevation in metres at each point, then calculates the total elevation gain (the sum of all uphill climbs). A perfectly flat route scores 10. A route with 100m+ of climbing scores 0. This matters most for tired users (weight 0.98 on flatness) who should not be sent on a hilly route, and energetic users (weight 0.10 on flatness) who actually benefit from hills.',
         'Requirement: "Open-Elevation API — Free and open-source. Provides elevation data to calculate route incline" (Section 2, Technology Stack). Flatness is the third factor in the WLC scoring formula.'),

        ('Foursquare Places API', 'External API — Crowd Density',
         'A location intelligence platform that provides data about businesses, venues, and points of interest worldwide.',
         'MoodRoute queries Foursquare for the count of venues (cafes, shops, restaurants, bars, etc.) within a 300m radius of each route. More venues = more people = more crowded. The venue count is normalised to an uncrowded score from 0 (very crowded, like the CBD) to 10 (remote bushland, almost no venues). This score is especially important for anxious users (weight 0.98 on uncrowded) who benefit from quiet, secluded paths, and less important for happy users (weight 0.25) who may enjoy a social atmosphere. If the Foursquare API key is not configured, the service falls back to estimating crowd density based on distance from the Wollongong CBD centre.',
         'Requirement: "Foursquare Places API — Free tier available. Provides venue density to estimate how busy an area is" (Section 2, Technology Stack). Uncrowded is the fifth factor in the WLC scoring formula.'),

        ('Nominatim (OpenStreetMap Geocoding)', 'External API — Geocoding',
         'Converts a typed address or suburb name into GPS coordinates (latitude and longitude).',
         'When a user types "Wollongong" or "Keiraville" into the location box instead of using GPS, the JavaScript frontend sends that text to Nominatim. Nominatim returns the latitude and longitude for that location, which are then used to set the map view and load the local weather. This entire call happens in the browser (client-side) directly to the Nominatim API, so it does not add load to the MoodRoute server.',
         'Requirement: Supports the location input feature — users can enter a suburb or address rather than being forced to share GPS. Complies with the privacy requirement since the search text is sent to a public map service, not stored by MoodRoute.'),

        ('OSRM (Open Source Routing Machine)', 'External API — Walking Paths',
         'A free, open-source routing engine that computes real driving or walking paths along actual roads and footpaths.',
         'Before the early prototype, routes were drawn as straight lines between the start and end point, which was unrealistic — the line would pass through buildings. OSRM solves this. For each recommended route, MoodRoute sends the start coordinate (UOW campus) and the destination coordinate to the OSRM public API using the "foot" profile (walking mode). OSRM returns between 50 and 400 real GPS waypoints that trace the actual roads, footpaths, and walkways between those two points. This is what gets drawn on the Leaflet map as the coloured polyline. The result is a path a person can actually follow on foot.',
         'Requirement: Routes should be displayed on the map as real walkable paths, not theoretical lines. Supports the core aim of recommending a route a user can physically walk.'),
    ]:
        els += tech_block(*block, s=s)

    els.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 5 — ALGORITHM
    # ══════════════════════════════════════════════════════════════════════════
    els.append(section_header('Section 5 — The Route Scoring Algorithm (WLC)', '📊', s))
    els.append(Spacer(1, 0.25*cm))
    els.append(Paragraph(
        'The algorithm is the intellectual core of MoodRoute. It is the part that '
        'makes the app different from any other navigation tool. It is called '
        'Weighted Linear Combination (WLC), a method widely used in geographic '
        'decision-making since the 1990s (Malczewski, 1999).',
        s['body']))

    els.append(Paragraph(
        '<b>The formula in plain English:</b>',
        ParagraphStyle('fb', fontName='Helvetica-Bold', fontSize=10,
                       textColor=INDIGO, leading=14, spaceAfter=3)))
    els.append(Paragraph(
        'Score each route on five environmental factors (Greenery, Quietness, '
        'Flatness, Distance suitability, Uncrowded — each scored 0 to 10). '
        'Multiply each score by a weight that reflects how important that factor '
        'is for the detected mood. Add everything up and divide by 5.',
        s['body']))

    # Formula display
    formula_tbl = Table([[
        Paragraph(
            'Route Score  =  [ (w₁ × Greenery) + (w₂ × Quietness) + (w₃ × Flatness) '
            '+ (w₄ × Distance) + (w₅ × Uncrowded) ]  ÷  5',
            ParagraphStyle('fm', fontName='Courier-Bold', fontSize=10,
                           textColor=INDIGO, leading=16, alignment=TA_CENTER))
    ]], colWidths=[PAGE_W - 2*MARGIN - 0.4*cm])
    formula_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), HexColor('#eef2ff')),
        ('BOX',           (0, 0), (-1, -1), 1.5, TEAL),
        ('LEFTPADDING',   (0, 0), (-1, -1), 16),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 16),
        ('TOPPADDING',    (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
    ]))
    els.append(formula_tbl)
    els.append(Spacer(1, 0.3*cm))

    els.append(Paragraph(
        '<b>The key innovation: weights change with mood.</b>  '
        'The same route gets a completely different score depending on what mood '
        'was detected. An anxious person and an energetic person standing at UOW '
        'campus will be sent to completely different destinations:',
        s['body']))

    # Weight table
    weight_data = [
        ['Mood', 'Greenery\nw₁', 'Quietness\nw₂', 'Flatness\nw₃', 'Distance\nw₄', 'Uncrowded\nw₅', 'Champion Route'],
        ['😰 Stressed', '0.90', '0.75', '0.65', '0.55', '0.65', 'Botanic Garden (2km)'],
        ['😟 Anxious',  '0.70', '0.98', '0.80', '0.20', '0.98', 'Fairy Creek Walk (1km)'],
        ['😴 Tired',    '0.50', '0.60', '0.98', '0.30', '0.55', 'JJ Kelly Park (1km)'],
        ['😢 Sad',      '0.98', '0.55', '0.60', '0.65', '0.40', 'Puckeys Estate (3km)'],
        ['😊 Happy',    '0.05', '0.20', '0.55', '0.90', '0.30', 'Stuart Park (3.2km)'],
        ['⚡ Energetic','0.20', '0.10', '0.10', '0.98', '0.30', 'Mt Ousley Track (5.5km)'],
    ]

    wd = [(PAGE_W - 2*MARGIN) / 7] * 7
    w_tbl_data = []
    for i, row in enumerate(weight_data):
        if i == 0:
            w_tbl_data.append([Paragraph(str(c), ParagraphStyle(
                'wh', fontName='Helvetica-Bold', fontSize=8,
                textColor=WHITE, leading=11, alignment=TA_CENTER)) for c in row])
        else:
            w_tbl_data.append([Paragraph(str(c), ParagraphStyle(
                'wb', fontName='Helvetica', fontSize=8.5,
                textColor=DARK, leading=12, alignment=TA_CENTER)) for c in row])

    wt = Table(w_tbl_data, colWidths=wd)
    wt.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0), INDIGO),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [LGREY, WHITE]),
        ('GRID',          (0, 0), (-1, -1), 0.4, BGREY),
        ('LEFTPADDING',   (0, 0), (-1, -1), 5),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 5),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    els.append(wt)
    els.append(Spacer(1, 0.3*cm))
    els.append(Paragraph(
        'The weight values are grounded in environmental psychology research: '
        'Ulrich (1984) showed green environments reduce physiological stress, '
        'justifying high greenery weights for stressed/anxious/sad moods. '
        'Stansfeld & Matheson (2003) demonstrated noise worsens anxiety, '
        'justifying quietness weight 0.98 for anxious. '
        'Thayer (1987) showed low-energy states benefit from minimal physical demand, '
        'justifying flatness weight 0.98 for tired.',
        s['body']))

    els.append(Paragraph(
        '<b>Research references (from the project proposal):</b>  '
        'Malczewski (1999) — GIS and Multicriteria Decision Analysis (WLC methodology). '
        'Eastman et al. (1995) — Raster procedures for multi-criteria decisions. '
        'Frank et al. (2010) — Development of a walkability index. '
        'Dey (2001) — Context-aware computing.',
        ParagraphStyle('ref', fontName='Helvetica-Oblique', fontSize=9,
                       textColor=MGREY, leading=14, spaceAfter=6)))

    els.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 6 — SECURITY
    # ══════════════════════════════════════════════════════════════════════════
    els.append(section_header('Section 6 — Security Implementation', '🔒', s))
    els.append(Spacer(1, 0.25*cm))
    els.append(Paragraph(
        'Security was a requirement from the very beginning of this project, not an '
        'afterthought. The project supervisor Mr. Partha Sarathy Roy specifically '
        'highlighted that MoodRoute serves emotionally vulnerable users and recommends '
        'physical routes in the real world — meaning a security breach could cause real '
        'harm by directing someone to an unsafe location. Four security layers are implemented.',
        s['body']))
    els.append(Spacer(1, 0.1*cm))

    for block in [
        ('Flask-Talisman (HTTPS & Security Headers)', 'Security — Encryption',
         'Forces all connections to use HTTPS (encrypted) and automatically adds browser security headers that block common web attacks.',
         'Talisman is active in app.py. In development mode (your laptop) it runs on http://localhost:5000 without requiring a certificate, which is standard practice. In production mode (FLASK_DEBUG=False), it automatically redirects all HTTP traffic to HTTPS, activates Strict-Transport-Security, sets Content-Security-Policy to only allow scripts and styles from approved sources (blocking injected code), sets X-Frame-Options to prevent the app being embedded in a fake website, and sets Referrer-Policy to no-referrer so external services cannot track what users searched for.',
         'Requirement: "We plan to implement HTTPS encryption … to protect our users and make sure no one can tamper with the route recommendations" (Section 1.1, Aims). Also: "we also need to make the app secure so no one can break in and change the routes being suggested to our users" (Assignment 1 background).'),

        ('Flask-Limiter (Rate Limiting)', 'Security — DDoS Protection',
         'Limits how many requests any single user can send per minute, preventing the server from being overwhelmed.',
         'Configured in app.py with a limit of 30 requests per minute per IP address. If a user or automated bot tries to send more requests than this — for example, repeatedly calling the mood detection endpoint — they are automatically blocked with a 429 Too Many Requests response. This protects both the MoodRoute server and the external API quotas (OpenWeatherMap, Foursquare) from being exhausted.',
         'Requirement: "rate limiting … to protect our users" (Section 1.1, Aims). Also: "limit the number of requests the app can take at once" (Assignment 1, Story Case under security).'),

        ('bleach (Input Sanitisation)', 'Security — XSS Protection',
         'Strips all HTML tags and dangerous characters from user input before it is processed.',
         'Every piece of text that comes from the user — the mood description, the location text — is passed through bleach.clean() with tags=[] (strip everything) before being sent to the NLP model or the database. This means a user who types <script>malicious code here</script> will have the script tags stripped out before any processing happens. Input is also limited to 500 characters maximum (Config.MAX_INPUT_LENGTH). This prevents Cross-Site Scripting (XSS) and injection attacks.',
         'Requirement: "check all user inputs to block any harmful code from getting in" (Assignment 1, Story Case under security). "input sanitisation" is explicitly named in Section 1.1 Aims.'),

        ('Environment Variables — .env + python-dotenv', 'Security — Key Management',
         'Stores all secret API keys in a private file that is never uploaded to version control.',
         'The OpenWeatherMap key, Foursquare key, and Flask secret key are all stored in a .env file using python-dotenv. The .env file is listed in .gitignore so it is never accidentally committed to GitHub or any other public repository. Config.py reads the keys using os.getenv() so they are never written directly into the source code. This means even if someone finds the code online, they cannot use the APIs because the keys are not there.',
         'Requirement: "Jesvin has highlighted the importance of keeping our API keys secure … stored in a separate configuration file that will never be uploaded to any public repository" (Assignment 1, Competence section). Also: "secure environment variables for all API keys" (Section 2.1, Security challenge).'),
    ]:
        els += tech_block(*block, s=s)

    els.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 7 — REQUIREMENTS MAPPING
    # ══════════════════════════════════════════════════════════════════════════
    els.append(section_header('Section 7 — Requirements from the Proposal & How They Are Met', '📋', s))
    els.append(Spacer(1, 0.25*cm))
    els.append(Paragraph(
        'This section maps every major requirement stated in the project proposal '
        '(Assignment 2) to the technology or feature that satisfies it.',
        s['body']))
    els.append(Spacer(1, 0.1*cm))

    req_data = [
        ['#', 'Requirement (from Proposal)', 'How It Is Met', 'Technology'],
        ['R1', 'Free-text mood input — user types how they feel in their own words',
         'Textarea input in HTML → bleach sanitisation → distilRoBERTa NLP model → mapped to mood category',
         'HTML + bleach + HuggingFace'],
        ['R2', 'Quick-tap mood buttons as fallback when NLP is uncertain',
         '6 pill buttons (Stressed, Anxious, Tired, Sad, Happy, Energetic) in the UI; selecting one bypasses NLP entirely',
         'HTML / JavaScript'],
        ['R3', 'GPS and manual location input',
         'GPS button uses browser navigator.geolocation API; text input uses Nominatim geocoding to convert suburb name to coordinates',
         'JavaScript + Nominatim API'],
        ['R4', 'NLP mood detection from free text',
         'HuggingFace distilRoBERTa model classifies text into 7 emotions, mapped to 6 MoodRoute moods with compound emotion logic',
         'HuggingFace + Python'],
        ['R5', 'Real-time environmental data from multiple sources',
         '5 external APIs: OpenWeatherMap (weather), Overpass (greenery + noise), Open-Elevation (terrain), Foursquare (crowd)',
         '5 External APIs'],
        ['R6', 'Mood-weighted route scoring algorithm (WLC)',
         'RouteScorer class implements the formula with 7 mood configurations and mathematically verified weight values',
         'Python (route_scorer.py)'],
        ['R7', 'Interactive map display of recommended route',
         'OSRM fetches real walking path (50–400 waypoints); Leaflet.js draws polyline with start/end markers and direction arrows',
         'Leaflet.js + OSRM'],
        ['R8', 'Weather safety check with indoor alternatives',
         'OpenWeatherMap assessed against danger thresholds; dangerous conditions show 5 UOW-specific indoor alternatives',
         'OpenWeatherMap + Python'],
        ['R9', 'Post-walk star rating system',
         '5-star rating UI sends POST /api/rate; rating saved to SQLite ratings table with route, mood, and weather logged',
         'JavaScript + SQLite'],
        ['R10', 'HTTPS encryption',
         'Flask-Talisman active in app.py; force_https=True in production mode; CSP, HSTS, X-Frame-Options all set',
         'Flask-Talisman'],
        ['R11', 'Rate limiting',
         'Flask-Limiter enforces 30 requests/minute per IP at the server level',
         'Flask-Limiter'],
        ['R12', 'Input sanitisation',
         'bleach.clean() strips all HTML from every user text input before processing',
         'bleach library'],
        ['R13', 'Secure API key management',
         '.env file with python-dotenv; .gitignore prevents accidental commit; os.getenv() reads at runtime',
         'python-dotenv + .gitignore'],
        ['R14', 'Mood text never stored',
         'No database write for mood text anywhere in the codebase; only route ID, mood category, and rating are saved',
         'Design decision (SQLite schema)'],
        ['R15', 'Comply with Australian Privacy Act 1988',
         'No personal data retained after session; no location saved; mood text discarded after processing; clear disclaimer in UI',
         'Architecture + UI disclaimer'],
        ['R16', 'Routes start from UOW campus',
         'All 15 seed routes have UOW campus (-34.4054, 150.8784) as coordinates[0]; route_api.py always searches from UOW_CENTER',
         'Python (route_api.py + db.py)'],
        ['R17', 'University of Wollongong identified on map',
         'Three concentric circles + pulsing CSS animation + graduation cap marker drawn at UOW centre via Leaflet',
         'Leaflet.js + CSS animation'],
    ]

    req_col_w = [0.7*cm, 5.5*cm, 5.8*cm, 3.8*cm]
    req_tbl_data = []
    for i, row in enumerate(req_data):
        if i == 0:
            req_tbl_data.append([Paragraph(str(c), ParagraphStyle(
                'rh', fontName='Helvetica-Bold', fontSize=8,
                textColor=WHITE, leading=11)) for c in row])
        else:
            req_tbl_data.append([
                Paragraph(row[0], ParagraphStyle('rn', fontName='Helvetica-Bold',
                          fontSize=8.5, textColor=TEAL, leading=12)),
                Paragraph(row[1], ParagraphStyle('rq', fontName='Helvetica',
                          fontSize=8.5, textColor=DARK, leading=12)),
                Paragraph(row[2], ParagraphStyle('ra', fontName='Helvetica',
                          fontSize=8.5, textColor=DARK, leading=12)),
                Paragraph(row[3], ParagraphStyle('rt', fontName='Helvetica-Bold',
                          fontSize=8, textColor=INDIGO, leading=12)),
            ])

    rt = Table(req_tbl_data, colWidths=req_col_w)
    rt.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0), INDIGO),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [LGREY, WHITE]),
        ('GRID',          (0, 0), (-1, -1), 0.4, BGREY),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
    ]))
    els.append(rt)
    els.append(Spacer(1, 0.5*cm))

    # ── Closing note ───────────────────────────────────────────────────────
    els.append(rule())
    els.append(Paragraph(
        'Every technology in this document was chosen because it is free, '
        'open-source, and appropriate for a university capstone project — '
        'no licensing costs, no paywalls, and full documentation available. '
        'The combination of these tools produces something genuinely original: '
        'an application that connects NLP-based emotion detection, real-time '
        'environmental data, and a mood-aware scoring algorithm into one working '
        'system designed to support mental wellbeing through walking.',
        s['body']))

    # ── Build ──────────────────────────────────────────────────────────────
    doc.build(els, onFirstPage=lambda c,d: None, onLaterPages=footer)
    print(f'info.pdf saved to: {output_path}')


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'info.pdf')
    build(out)
