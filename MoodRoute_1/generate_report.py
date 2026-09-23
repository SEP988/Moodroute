"""
MoodRoute Phase 3 & Phase 4 Report Generator
Simple, clean PDF with plain language and no heavy styling.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, PageBreak, Table, TableStyle
)
from reportlab.lib.colors import black, HexColor, white
import os

PAGE_W, PAGE_H = A4
MARGIN = 2.5 * cm
GREY = HexColor('#555555')
LIGHT_GREY = HexColor('#f2f2f2')
MID_GREY = HexColor('#999999')


# ── Page numbers ──────────────────────────────────────────────────────────────
def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(GREY)
    canvas.drawCentredString(PAGE_W / 2, 1.0 * cm, f"Page {doc.page}")
    canvas.restoreState()


# ── Styles ────────────────────────────────────────────────────────────────────
def get_styles():
    s = {}

    s['title'] = ParagraphStyle(
        'title', fontName='Helvetica-Bold', fontSize=22,
        textColor=black, alignment=TA_CENTER, spaceAfter=6, leading=28
    )
    s['subtitle'] = ParagraphStyle(
        'subtitle', fontName='Helvetica', fontSize=12,
        textColor=GREY, alignment=TA_CENTER, spaceAfter=4, leading=16
    )
    s['meta'] = ParagraphStyle(
        'meta', fontName='Helvetica', fontSize=10,
        textColor=GREY, alignment=TA_CENTER, spaceAfter=3, leading=14
    )
    s['section'] = ParagraphStyle(
        'section', fontName='Helvetica-Bold', fontSize=13,
        textColor=black, spaceBefore=16, spaceAfter=6, leading=18
    )
    s['member_header'] = ParagraphStyle(
        'member_header', fontName='Helvetica-Bold', fontSize=12,
        textColor=black, spaceBefore=14, spaceAfter=2, leading=16
    )
    s['member_sub'] = ParagraphStyle(
        'member_sub', fontName='Helvetica-Oblique', fontSize=10,
        textColor=GREY, spaceAfter=8, leading=14
    )
    s['body'] = ParagraphStyle(
        'body', fontName='Helvetica', fontSize=10,
        textColor=black, leading=15.5, spaceAfter=7, alignment=TA_JUSTIFY
    )
    s['bullet'] = ParagraphStyle(
        'bullet', fontName='Helvetica', fontSize=10,
        textColor=black, leading=15, spaceAfter=4,
        leftIndent=14, bulletIndent=4
    )
    s['sub_label'] = ParagraphStyle(
        'sub_label', fontName='Helvetica-Bold', fontSize=10,
        textColor=black, spaceBefore=8, spaceAfter=3, leading=14
    )

    return s


def rule():
    return HRFlowable(width='100%', thickness=0.5, color=GREY,
                      spaceAfter=8, spaceBefore=4)


def thin_rule():
    return HRFlowable(width='100%', thickness=0.3, color=MID_GREY,
                      spaceAfter=6, spaceBefore=6)


def bullet(text, s):
    return Paragraph(f"- {text}", s['bullet'])


# ── Build the PDF ─────────────────────────────────────────────────────────────
def build_report(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=2.0 * cm, bottomMargin=2.0 * cm,
        title="MoodRoute Phase 3 and Phase 4 Report",
        author="Group MoodMappers — CSIT998"
    )

    s = get_styles()
    els = []

    # ── COVER ─────────────────────────────────────────────────────────────────
    els.append(Spacer(1, 2.5 * cm))
    els.append(Paragraph("MoodRoute", s['title']))
    els.append(Paragraph("A Mood-Based Walking Route Recommendation App", s['subtitle']))
    els.append(Spacer(1, 0.5 * cm))
    els.append(rule())
    els.append(Spacer(1, 0.3 * cm))
    els.append(Paragraph("Phase 3 Development Report &amp; Phase 4 Plan", ParagraphStyle(
        'ch', fontName='Helvetica-Bold', fontSize=14,
        textColor=black, alignment=TA_CENTER, spaceAfter=6
    )))
    els.append(Spacer(1, 0.8 * cm))

    # Team table on cover
    rows = [
        ["Name", "Student No.", "Degree", "Role"],
        ["Resmi",              "9180679", "Master of IT",                  "Project Lead & Integration"],
        ["Albin Babychan",     "7219908", "Master of IT",                  "API Integration & Architecture"],
        ["Jesvin Jayan",       "9675851", "Master of IT",                  "NLP & Flask Backend"],
        ["Vishva M. Kalyani",  "8478338", "Master of Health Informatics",  "Frontend & Health UX"],
        ["Eldho Varghese",     "9088842", "Master of IT",                  "Algorithm & Database"],
    ]

    table_data = [
        [Paragraph(f"<b>{c}</b>" if i == 0 else c,
                   ParagraphStyle('tc', fontName='Helvetica-Bold' if i == 0 else 'Helvetica',
                                  fontSize=9, leading=13))
         for c in row]
        for i, row in enumerate(rows)
    ]

    t = Table(table_data, colWidths=[3.8 * cm, 2.8 * cm, 5.0 * cm, 4.1 * cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0), HexColor('#e0e0e0')),
        ('GRID',          (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('LEFTPADDING',   (0, 0), (-1, -1), 8),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_GREY]),
    ]))
    els.append(t)
    els.append(Spacer(1, 1.2 * cm))

    els.append(Paragraph("CSIT998 Professional Capstone Project", s['meta']))
    els.append(Paragraph("University of Wollongong  —  Annual Session 2026", s['meta']))
    els.append(Paragraph("Supervisor: Mr. Partha Sarathy Roy", s['meta']))
    els.append(PageBreak())

    # ── OVERVIEW ──────────────────────────────────────────────────────────────
    els.append(Paragraph("About This Report", s['section']))
    els.append(rule())
    els.append(Paragraph(
        "This report documents what each member of Group MoodMappers did during Phase 3 "
        "of the MoodRoute project, which ran from June to September 2026. Phase 3 was the "
        "main development phase where we built the actual application. It also outlines "
        "what each person will do in Phase 4, which is the user study and evaluation phase "
        "running in September 2026.",
        s['body']
    ))
    els.append(Paragraph(
        "MoodRoute is a web app for University of Wollongong students. It asks how you "
        "are feeling, uses an AI model to understand your mood from what you typed, and "
        "then recommends a nearby walking route that suits your emotional state. For example, "
        "if you are feeling anxious it will suggest a quiet, green, short path. If you are "
        "feeling energetic it will suggest a longer, more challenging route. All routes are "
        "within 5 km of the UOW campus.",
        s['body']
    ))
    els.append(Paragraph(
        "The app was built with a Python Flask backend, a SQLite database, a HuggingFace "
        "NLP model for mood detection, five external APIs for environmental data, and a "
        "mobile-friendly map interface using Leaflet.js.",
        s['body']
    ))

    els.append(Spacer(1, 0.3 * cm))
    els.append(Paragraph("What Was Built in Phase 3", s['section']))
    els.append(rule())
    overview = [
        ("NLP Mood Detection",      "An AI model reads what you type and detects your emotion. If the model can't download due to network issues, a keyword-based backup takes over."),
        ("Route Scoring Algorithm", "A mathematical formula (Weighted Linear Combination) scores every route on five factors — greenery, quietness, flatness, distance, and how crowded it is — and applies different weights depending on your mood."),
        ("Environmental APIs",      "Five APIs pull live data: OpenWeatherMap for weather, OpenStreetMap/Overpass for greenery and road noise, Open-Elevation for terrain, and Foursquare for crowd density."),
        ("Route Database",          "15 real walking routes around UOW campus, stored in SQLite, each with coordinates, distance, and named start and end points."),
        ("API Endpoints",           "Three REST API endpoints handle mood detection, route finding, and post-walk ratings."),
        ("Frontend UI",             "A mobile-first webpage with a bottom-sheet panel, interactive Leaflet map showing a 5 km UOW boundary circle, and animated route lines with start and end markers."),
        ("Security",                "Rate limiting, input sanitisation, and all API keys stored in environment variables — never in the code."),
    ]
    for label, desc in overview:
        els.append(Paragraph(f"<b>{label}:</b> {desc}", s['body']))

    els.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # MEMBER SECTIONS
    # ══════════════════════════════════════════════════════════════════════════

    els.append(Paragraph("Individual Contributions — Phase 3 and Phase 4", s['section']))
    els.append(rule())
    els.append(Spacer(1, 0.2 * cm))

    # ── RESMI ─────────────────────────────────────────────────────────────────
    els.append(Paragraph("Resmi  |  Student No. 9180679  |  Master of IT", s['member_header']))
    els.append(Paragraph("Role: Project Lead, Integration Coordinator, Testing", s['member_sub']))
    els.append(thin_rule())

    els.append(Paragraph("<b>Phase 3 — What She Did</b>", s['sub_label']))
    els.append(Paragraph(
        "Resmi was responsible for making sure everything the team built came together "
        "and worked as one system. At the start of Phase 3 she set up the project folder "
        "structure, the Flask app factory, and the configuration file so everyone had a "
        "clean base to work from. She ran weekly check-ins, kept the team on track, and "
        "made sure nobody stayed stuck on a problem for too long without help.",
        s['body']
    ))
    els.append(Paragraph(
        "In the final weeks of Phase 3, Resmi did the integration testing. This is where "
        "she found and fixed several bugs that only appeared once all the pieces were "
        "connected. The biggest one was a mismatch between what the backend was sending "
        "and what the frontend was reading — for example, the API was returning routes as "
        "a list called 'routes' but the JavaScript was looking for a single item called "
        "'route', which meant the screen showed nothing. She also found that the score "
        "bars were showing 0% for everyone because the scores from the backend were on a "
        "0 to 10 scale but the frontend was treating them as 0 to 1 decimals. She went "
        "through each function in the JavaScript, checked the actual data coming from the "
        "server, and fixed each mismatch one by one.",
        s['body']
    ))

    els.append(Paragraph("<b>Key things Resmi built or fixed:</b>", s['sub_label']))
    for item in [
        "Set up app.py, config.py, and the full project folder structure",
        "Registered all Flask API blueprints and configured CORS and rate limiting",
        "Wrote and ran a seven-test suite that checks every API endpoint works correctly",
        "Fixed the frontend bugs: wrong field names, wrong score scale, nested weather response",
        "Managed the UOW-specific changes: campus center coordinates, 5 km radius logic, boundary circle alignment",
        "Kept the team organised through weekly check-ins and a shared task tracker",
    ]:
        els.append(bullet(item, s))

    els.append(Paragraph("<b>Phase 4 — What She Will Do</b>", s['sub_label']))
    els.append(Paragraph(
        "In Phase 4 Resmi will continue her coordination role. She will manage the "
        "scheduling of the user study sessions, make sure the app is running correctly "
        "on test days, and be the point of contact for participants if they have any "
        "questions or issues. After the study she will help compile the results and "
        "co-write the evaluation section of the final report with Vishva and Eldho. "
        "She will also lead the writing of the overall final report in Phase 5.",
        s['body']
    ))

    els.append(Spacer(1, 0.4 * cm))
    els.append(thin_rule())

    # ── ALBIN ─────────────────────────────────────────────────────────────────
    els.append(Paragraph("Albin Babychan  |  Student No. 7219908  |  Master of IT", s['member_header']))
    els.append(Paragraph("Role: API Integration Lead, System Architecture Designer", s['member_sub']))
    els.append(thin_rule())

    els.append(Paragraph("<b>Phase 3 — What He Did</b>", s['sub_label']))
    els.append(Paragraph(
        "Albin built all five of the external data services that the app uses to score "
        "routes. These are the modules that reach out to real APIs on the internet and "
        "fetch live information about the environment around a route.",
        s['body']
    ))
    els.append(Paragraph(
        "The five services he built are: OpenWeatherMap (checks the weather and decides "
        "if it is safe to walk), Overpass API from OpenStreetMap (counts parks, trees, "
        "and green spaces near a route), Overpass API again for road types (busier roads "
        "get a higher noise score, quieter footpaths get a low noise score), "
        "Open-Elevation (checks how hilly the route is), and Foursquare Places "
        "(counts venues like cafes and shops near the route to estimate how crowded "
        "the area is). Each service has a fallback value built in so if the API is "
        "unavailable the app returns a default score of 5 out of 10 rather than crashing.",
        s['body']
    ))
    els.append(Paragraph(
        "Albin also designed the caching system in the database. Because some of these "
        "APIs are slow and have usage limits, he wrote a system that stores a computed "
        "score for each route and reuses it for 24 hours before fetching it again. This "
        "made the app much faster during testing.",
        s['body']
    ))

    els.append(Paragraph("<b>Key things Albin built:</b>", s['sub_label']))
    for item in [
        "weather_service.py — OpenWeatherMap integration, weather safety assessment",
        "greenery_service.py — Overpass API queries for parks, forests, trees (score 0-10)",
        "noise_service.py — OSM road classification to estimate quietness (score 0-10)",
        "elevation_service.py — Open-Elevation API, calculates total climb to score flatness",
        "crowd_service.py — Foursquare venue count to estimate how crowded a route area is",
        "Score caching layer in the database — avoids repeating slow API calls",
    ]:
        els.append(bullet(item, s))

    els.append(Paragraph("<b>Phase 4 — What He Will Do</b>", s['sub_label']))
    els.append(Paragraph(
        "In Phase 4 Albin will monitor the API services during the user study to make "
        "sure they are responding correctly on test days. If any external API is down "
        "during a session he will switch the affected service to its fallback mode so "
        "the study can continue without interruption. He will also document the API "
        "integration in detail for the final report, including the caching design and "
        "the fallback logic, so future developers can understand and extend the system.",
        s['body']
    ))

    els.append(Spacer(1, 0.4 * cm))
    els.append(thin_rule())

    # ── JESVIN ────────────────────────────────────────────────────────────────
    els.append(Paragraph("Jesvin Jayan  |  Student No. 9675851  |  Master of IT", s['member_header']))
    els.append(Paragraph("Role: NLP Integration Lead, Flask Backend Developer, Security", s['member_sub']))
    els.append(thin_rule())

    els.append(Paragraph("<b>Phase 3 — What He Did</b>", s['sub_label']))
    els.append(Paragraph(
        "Jesvin had two main jobs in Phase 3. The first was getting the AI mood "
        "detection model working inside the Flask app. The model used is called "
        "distilRoBERTa, available through HuggingFace. It reads a piece of text "
        "and classifies it into one of seven emotions: anger, disgust, fear, joy, "
        "neutral, sadness, or surprise. Jesvin then wrote the logic that maps those "
        "seven emotions to the six mood categories the app uses — stressed, anxious, "
        "tired, sad, happy, and energetic. This mapping required some thought because "
        "the model's emotion labels do not match the app's mood categories directly. "
        "For example, fear maps to anxious, and anger plus sadness together map to "
        "stressed rather than just angry.",
        s['body']
    ))
    els.append(Paragraph(
        "When the team found that the university network's security settings were "
        "blocking the model download, Jesvin built a full keyword-based backup "
        "detector so the app could still work during development. The backup system "
        "uses a weighted list of keywords for each mood and handles negation — so "
        "'I am not happy' will not be detected as happy.",
        s['body']
    ))
    els.append(Paragraph(
        "Jesvin's second job was building the three Flask API endpoints that the "
        "frontend talks to: one for detecting mood, one for finding and scoring "
        "routes, and one for saving post-walk ratings. He also implemented all the "
        "security features — input sanitisation using the bleach library to strip "
        "any HTML from user inputs, coordinate validation, and rate limiting so "
        "the server cannot be flooded with requests.",
        s['body']
    ))

    els.append(Paragraph("<b>Key things Jesvin built:</b>", s['sub_label']))
    for item in [
        "nlp_service.py — MoodDetector class loading distilRoBERTa, emotion-to-mood mapping, keyword fallback",
        "mood_api.py — POST /api/detect-mood endpoint",
        "route_api.py — POST /api/find-route endpoint (full recommendation pipeline)",
        "rating_api.py — POST /api/rate endpoint for saving post-walk star ratings",
        "Input sanitisation with bleach, coordinate validation, 30-requests-per-minute rate limiting",
        "Keyword-based mood fallback detector with negation handling",
    ]:
        els.append(bullet(item, s))

    els.append(Paragraph("<b>Phase 4 — What He Will Do</b>", s['sub_label']))
    els.append(Paragraph(
        "In Phase 4 Jesvin will run a technical evaluation of the NLP mood detector "
        "by testing it against at least 50 sample sentences and recording how often "
        "it correctly identifies the mood. He will present the accuracy results in a "
        "simple table showing how the model performs for each mood category. He will "
        "also check whether the keyword fallback gives reasonable results for the "
        "same sentences, so the team can report the difference in accuracy between "
        "the two methods in the final report.",
        s['body']
    ))

    els.append(Spacer(1, 0.4 * cm))
    els.append(thin_rule())
    els.append(PageBreak())

    # ── VISHVA ────────────────────────────────────────────────────────────────
    els.append(Paragraph("Vishva Manishbhai Kalyani  |  Student No. 8478338  |  Master of Health Informatics", s['member_header']))
    els.append(Paragraph("Role: Frontend UI Designer, Health Safety Features, User Study Preparation", s['member_sub']))
    els.append(thin_rule())

    els.append(Paragraph("<b>Phase 3 — What She Did</b>", s['sub_label']))
    els.append(Paragraph(
        "Vishva was responsible for designing and building the user interface of the "
        "app. She designed it as a mobile-first experience because most students would "
        "open it on their phone. The main feature of the design is a bottom panel that "
        "slides up from the bottom of the screen, similar to the way Google Maps works. "
        "The panel has three positions: mostly hidden, half open showing the input "
        "fields, and fully open showing the route result. The map takes up the whole "
        "screen behind the panel.",
        s['body']
    ))
    els.append(Paragraph(
        "She chose a clean colour scheme of dark indigo and teal to make the app feel "
        "calm and trustworthy, which felt appropriate given that users might be in a "
        "stressed or anxious state when they open it. She also added the loading "
        "animation that shows four steps as the app processes the request, and the "
        "small toast notification messages that appear at the bottom of the screen "
        "when something happens.",
        s['body']
    ))
    els.append(Paragraph(
        "Coming from a health background, Vishva made sure the app includes two "
        "important safety features. First, a weather safety gate that shows indoor "
        "alternatives (like the UOW library or UniActive gym) when the weather is "
        "dangerous. Second, the Lifeline crisis number (13 11 14) and a clear "
        "disclaimer that MoodRoute is not a clinical mental health tool appear on "
        "every screen. She also set up the Leaflet.js map on the frontend, including "
        "the dashed circle showing the 5 km UOW service area and the graduation cap "
        "marker on the campus.",
        s['body']
    ))
    els.append(Paragraph(
        "In parallel with her development work, Vishva also prepared the materials "
        "for the Phase 4 user study — the PANAS questionnaire forms, the participant "
        "information sheet, and the consent form.",
        s['body']
    ))

    els.append(Paragraph("<b>Key things Vishva built:</b>", s['sub_label']))
    for item in [
        "index.html — full HTML page: bottom-sheet panel, mood input, result card, indoor alternatives card, loading overlay",
        "style.css — complete stylesheet (1,100+ lines): colour scheme, bottom-sheet states, animations, responsive layout",
        "map.js — Leaflet map setup: UOW campus marker, 5 km boundary circle, start and end route markers with labels",
        "Weather safety gate UI and indoor alternatives card with UOW-specific venues",
        "Lifeline 13 11 14 disclaimer and 'not a clinical tool' notice on every screen",
        "PANAS questionnaire form, participant information sheet, and consent form for Phase 4",
    ]:
        els.append(bullet(item, s))

    els.append(Paragraph("<b>Phase 4 — What She Will Do</b>", s['sub_label']))
    els.append(Paragraph(
        "Phase 4 is where Vishva's health informatics background becomes most valuable. "
        "She will lead the user study from start to finish. This involves recruiting "
        "20 to 30 UOW students as participants, running the study sessions where each "
        "participant uses MoodRoute for one walk and a standard navigation app for "
        "another walk, and collecting their PANAS mood scores before and after each "
        "walk. She will also make sure the study is conducted ethically — participants "
        "will be properly informed, consent will be collected before the study begins, "
        "and no personal data will be kept after the analysis is complete. After data "
        "collection Vishva will help write up the user study methodology and findings "
        "section of the final report.",
        s['body']
    ))

    els.append(Spacer(1, 0.4 * cm))
    els.append(thin_rule())

    # ── ELDHO ─────────────────────────────────────────────────────────────────
    els.append(Paragraph("Eldho Varghese  |  Student No. 9088842  |  Master of IT", s['member_header']))
    els.append(Paragraph("Role: Route Scoring Algorithm, SQLite Database, Statistical Analysis", s['member_sub']))
    els.append(thin_rule())

    els.append(Paragraph("<b>Phase 3 — What He Did</b>", s['sub_label']))
    els.append(Paragraph(
        "Eldho built the most technically complex part of the project: the route "
        "scoring algorithm. His job was to take the formula that the team had designed "
        "in Phase 2 and turn it into working Python code that correctly ranks walking "
        "routes based on a person's mood.",
        s['body']
    ))
    els.append(Paragraph(
        "The algorithm is called Weighted Linear Combination. It scores each route on "
        "five factors — greenery, quietness, flatness, distance suitability, and how "
        "uncrowded the area is — and multiplies each score by a weight that reflects "
        "how important that factor is for the detected mood. For example, if you are "
        "anxious, quietness gets a weight of 0.95 (very important) and distance gets "
        "a weight of 0.20 (not very important). If you are energetic, distance gets "
        "0.95 and quietness gets only 0.25. The five weighted scores are added together "
        "and divided by five to give a final score out of 10 for each route.",
        s['body']
    ))
    els.append(Paragraph(
        "For the distance score specifically, Eldho used a Gaussian curve rather than "
        "a simple cutoff. This means a route that is slightly longer than the ideal "
        "range gets a moderate penalty, while one that is very far from ideal gets "
        "a much heavier penalty. This produces more realistic and fair rankings than "
        "a sharp boundary would.",
        s['body']
    ))
    els.append(Paragraph(
        "Eldho also built and seeded the SQLite database with 15 real walking routes "
        "around the UOW campus. He spent time checking each route's coordinates "
        "against satellite images to make sure the paths follow actual walkable "
        "footpaths and not through buildings. Each route has a real name, a "
        "description, a distance in kilometres, and named start and end points "
        "that students will recognise — for example, 'UOW Main Campus Ring Road' "
        "to 'Mount Keira Lookout'.",
        s['body']
    ))

    els.append(Paragraph("<b>Key things Eldho built:</b>", s['sub_label']))
    for item in [
        "route_scorer.py — RouteScorer class implementing the full WLC formula with Gaussian distance scoring",
        "mood_mapper.py — all seven mood configurations with their weights, ideal distances, and descriptions",
        "db.py — database initialisation, the 15-route seed data, cache read/write, and rating save functions",
        "schema.sql — SQLite table definitions for routes, ratings, and score cache",
        "Verified all 15 route coordinate sets against satellite imagery for accuracy",
        "Wrote the explanation generator that produces the short text explaining why a route was chosen",
    ]:
        els.append(bullet(item, s))

    els.append(Paragraph("<b>Phase 4 — What He Will Do</b>", s['sub_label']))
    els.append(Paragraph(
        "In Phase 4 Eldho will carry out the statistical analysis of the user study "
        "results. Once Vishva has collected the PANAS scores from all participants, "
        "Eldho will use a paired t-test to check whether the mood improvement after "
        "using MoodRoute is statistically significant compared to using a standard "
        "navigation app. He will calculate the mean change in positive and negative "
        "affect for both conditions, compute the p-value and effect size (Cohen's d), "
        "and present the results clearly so the team can discuss them in the final "
        "report. He will also do a technical evaluation of the scoring algorithm — "
        "testing that routes are ranked in the correct order for each mood using a "
        "set of known inputs.",
        s['body']
    ))

    els.append(PageBreak())

    # ── PHASE 4 SUMMARY ───────────────────────────────────────────────────────
    els.append(Paragraph("Phase 4 Plan — User Study and Evaluation", s['section']))
    els.append(rule())
    els.append(Paragraph(
        "Phase 4 runs through September 2026. The goal is to find out whether "
        "MoodRoute actually makes a difference to how people feel after a walk "
        "compared to just using standard navigation.",
        s['body']
    ))

    els.append(Paragraph("<b>Study Design</b>", s['sub_label']))
    els.append(Paragraph(
        "We will run a within-subjects study with 20 to 30 UOW students. Each "
        "participant will complete two walks on different days. On one day they "
        "will use MoodRoute to get a recommendation. On the other day they will "
        "use Google Maps with no mood-awareness. The order will be randomised "
        "across participants to avoid order effects. Before and after each walk "
        "participants will complete the PANAS scale, which asks them to rate how "
        "strongly they feel 20 emotions right now on a scale of 1 to 5.",
        s['body']
    ))

    els.append(Paragraph("<b>Who Does What in Phase 4</b>", s['sub_label']))

    phase4_rows = [
        ["Member",            "Phase 4 Responsibility"],
        ["Resmi",             "Coordination, scheduling sessions, managing participant communication, co-writing the evaluation section"],
        ["Albin Babychan",    "Monitoring API services on study days, technical support, documenting the API layer for the final report"],
        ["Jesvin Jayan",      "Technical evaluation of NLP accuracy (50 test sentences), comparing transformer model vs keyword fallback"],
        ["Vishva M. Kalyani", "Leading the user study — recruiting participants, running sessions, collecting PANAS data, managing ethics"],
        ["Eldho Varghese",    "Statistical analysis — paired t-test on PANAS scores, Cohen's d effect size, scoring algorithm validation"],
    ]

    phase4_data = [
        [Paragraph(f"<b>{c}</b>" if i == 0 else c,
                   ParagraphStyle('p4c', fontName='Helvetica-Bold' if i == 0 else 'Helvetica',
                                  fontSize=9, leading=13))
         for c in row]
        for i, row in enumerate(phase4_rows)
    ]

    p4t = Table(phase4_data, colWidths=[3.8 * cm, 12.4 * cm - 0.4 * cm])
    p4t.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0), HexColor('#e0e0e0')),
        ('GRID',          (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('LEFTPADDING',   (0, 0), (-1, -1), 8),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_GREY]),
    ]))
    els.append(p4t)

    els.append(Spacer(1, 0.6 * cm))
    els.append(Paragraph("<b>Timeline</b>", s['sub_label']))
    els.append(Paragraph(
        "Phase 4 (User Study): September 2026  —  "
        "Final Report due: 18 October 2026  —  "
        "Presentation: Week 25-26, October 2026",
        s['body']
    ))

    els.append(Spacer(1, 0.4 * cm))
    els.append(rule())
    els.append(Paragraph(
        "The findings from Phase 4 — whether MoodRoute improves mood more than "
        "standard navigation — will be the central result of the entire project. "
        "Even if the results are mixed, they will be a useful contribution because "
        "no one has evaluated a system like this before.",
        s['body']
    ))

    # ── BUILD ─────────────────────────────────────────────────────────────────
    doc.build(els, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"Report saved to: {output_path}")


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'MoodRoute_Phase3_Report.pdf')
    build_report(out)
