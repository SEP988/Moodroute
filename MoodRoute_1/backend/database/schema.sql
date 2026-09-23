-- MoodRoute Database Schema
-- Focused on University of Wollongong walking routes (5km radius)

CREATE TABLE IF NOT EXISTS routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    coordinates TEXT NOT NULL,
    distance_km REAL NOT NULL,
    area_type TEXT,
    center_lat REAL NOT NULL,
    center_lng REAL NOT NULL,
    start_point TEXT NOT NULL DEFAULT '',
    end_point TEXT NOT NULL DEFAULT '',
    -- Pre-researched environmental scores (0-10 scale)
    -- These ensure differentiated routing even when external APIs are unavailable
    score_greenery REAL NOT NULL DEFAULT 5.0,
    score_quietness REAL NOT NULL DEFAULT 5.0,
    score_flatness REAL NOT NULL DEFAULT 5.0,
    score_uncrowded REAL NOT NULL DEFAULT 5.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    route_id INTEGER NOT NULL,
    mood TEXT NOT NULL,
    rating INTEGER CHECK(rating BETWEEN 1 AND 5),
    weather_condition TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (route_id) REFERENCES routes(id)
);

CREATE TABLE IF NOT EXISTS score_cache (
    route_id INTEGER NOT NULL,
    factor TEXT NOT NULL,
    score REAL NOT NULL,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    PRIMARY KEY (route_id, factor)
);
