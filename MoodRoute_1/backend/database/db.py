"""MoodRoute Database Module.

Manages SQLite database for routes, ratings, and score cache.
All routes are within 5km of University of Wollongong campus.
"""
import sqlite3
import os
import json
from datetime import datetime, timedelta

DB_PATH = None


def get_db_path():
    global DB_PATH
    if DB_PATH is None:
        DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'moodroute.db')
    return DB_PATH


def get_connection():
    connection = sqlite3.connect(get_db_path())
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA journal_mode=WAL')
    return connection


def init_db(app=None):
    database_path = get_db_path()
    os.makedirs(os.path.dirname(database_path), exist_ok=True)

    connection = sqlite3.connect(database_path)

    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')
    with open(schema_path, 'r') as schema_file:
        connection.executescript(schema_file.read())

    cursor = connection.execute('SELECT COUNT(*) FROM routes')
    route_count = cursor.fetchone()[0]

    if route_count == 0:
        seed_routes(connection)
    else:
        try:
            cursor = connection.execute("SELECT start_point FROM routes LIMIT 1")
            row = cursor.fetchone()
            if row is None or row[0] == '':
                connection.execute('DELETE FROM routes')
                connection.execute('DELETE FROM score_cache')
                seed_routes(connection)
        except sqlite3.OperationalError:
            connection.execute('DROP TABLE IF EXISTS routes')
            connection.execute('DROP TABLE IF EXISTS score_cache')
            connection.executescript(open(schema_path).read())
            seed_routes(connection)

    connection.commit()
    connection.close()


def seed_routes(connection):
    """Pre-seed 15 walking routes from UOW with researched environmental scores."""
    UOW_LAT = -34.4054
    UOW_LNG = 150.8784

    routes = [
        {
            'name': 'Botanic Garden Loop',
            'description': 'Peaceful circuit through 27 hectares of native gardens, rainforest gully and heritage trees',
            'distance_km': 2.0, 'area_type': 'park',
            'center_lat': -34.4100, 'center_lng': 150.8778,
            'start_point': 'University of Wollongong (Main Campus)',
            'end_point': 'Wollongong Botanic Garden',
            'coordinates': [[-34.4054, 150.8784], [-34.4133, 150.8788]],
            'score_greenery': 9.5, 'score_quietness': 8.8, 'score_flatness': 8.8, 'score_uncrowded': 7.2
        },
        {
            'name': 'Fairy Creek Nature Walk',
            'description': 'Hidden shaded creekside bushland with bird calls and almost no foot traffic',
            'distance_km': 1.0, 'area_type': 'creek',
            'center_lat': -34.4060, 'center_lng': 150.8750,
            'start_point': 'University of Wollongong (Main Campus)',
            'end_point': 'Fairy Creek Bridge (Northfields Ave)',
            'coordinates': [[-34.4054, 150.8784], [-34.4076, 150.8725]],
            'score_greenery': 5.5, 'score_quietness': 9.8, 'score_flatness': 8.5, 'score_uncrowded': 9.8
        },
        {
            'name': 'UOW to Mount Keira Lookout',
            'description': 'Challenging uphill rainforest track with dense canopy and panoramic summit views',
            'distance_km': 6.0, 'area_type': 'forest',
            'center_lat': -34.3990, 'center_lng': 150.8620,
            'start_point': 'University of Wollongong (Main Campus)',
            'end_point': 'Mount Keira Lookout',
            'coordinates': [[-34.4054, 150.8784], [-34.3955, 150.8582]],
            'score_greenery': 8.5, 'score_quietness': 7.5, 'score_flatness': 1.5, 'score_uncrowded': 8.5
        },
        {
            'name': 'Puckeys Estate Bushland Trail',
            'description': 'Rare coastal rainforest reserve with dunes, wetlands and birdlife — almost never crowded',
            'distance_km': 3.0, 'area_type': 'bushland',
            'center_lat': -34.3935, 'center_lng': 150.8985,
            'start_point': 'University of Wollongong (Main Campus)',
            'end_point': 'Puckeys Estate Reserve',
            'coordinates': [[-34.4054, 150.8784], [-34.3940, 150.8968]],
            'score_greenery': 9.8, 'score_quietness': 7.5, 'score_flatness': 8.0, 'score_uncrowded': 9.0
        },
        {
            'name': 'North Wollongong Beach Walk',
            'description': 'Open sandy beachfront with ocean breeze — flat, refreshing, busy on sunny days',
            'distance_km': 2.8, 'area_type': 'coastal',
            'center_lat': -34.3980, 'center_lng': 150.9065,
            'start_point': 'University of Wollongong (Main Campus)',
            'end_point': 'North Wollongong Beach',
            'coordinates': [[-34.4054, 150.8784], [-34.3943, 150.9060]],
            'score_greenery': 3.5, 'score_quietness': 5.5, 'score_flatness': 9.8, 'score_uncrowded': 4.5
        },
        {
            'name': 'Stuart Park Serenity Walk',
            'description': 'Scenic walk through Norfolk pines with harbour views and memorial gardens',
            'distance_km': 3.2, 'area_type': 'park',
            'center_lat': -34.4220, 'center_lng': 150.9010,
            'start_point': 'University of Wollongong (Main Campus)',
            'end_point': 'Stuart Park (Cliff Rd)',
            'coordinates': [[-34.4054, 150.8784], [-34.4228, 150.9024]],
            'score_greenery': 6.5, 'score_quietness': 7.0, 'score_flatness': 9.5, 'score_uncrowded': 7.0
        },
        {
            'name': 'Blue Mile Coastal Promenade',
            'description': 'Famous shared coastal path — scenic, social, flat, and always busy with locals',
            'distance_km': 4.5, 'area_type': 'coastal',
            'center_lat': -34.4150, 'center_lng': 150.9050,
            'start_point': 'University of Wollongong (Main Campus)',
            'end_point': 'Wollongong Harbour Lighthouse',
            'coordinates': [[-34.4054, 150.8784], [-34.4220, 150.9040]],
            'score_greenery': 4.5, 'score_quietness': 5.5, 'score_flatness': 9.8, 'score_uncrowded': 4.0
        },
        {
            'name': 'Keiraville Quiet Streets',
            'description': 'Leafy residential streets with jacaranda trees — calm, safe, almost traffic-free',
            'distance_km': 1.8, 'area_type': 'residential',
            'center_lat': -34.4100, 'center_lng': 150.8690,
            'start_point': 'University of Wollongong (Main Campus)',
            'end_point': 'Keiraville Shopping Village',
            'coordinates': [[-34.4054, 150.8784], [-34.4116, 150.8655]],
            'score_greenery': 6.0, 'score_quietness': 8.5, 'score_flatness': 7.0, 'score_uncrowded': 8.0
        },
        {
            'name': 'Harbour to Flagstaff Point',
            'description': 'Short walk past fishing boats, rock pools and the historic lighthouse',
            'distance_km': 3.5, 'area_type': 'coastal',
            'center_lat': -34.4270, 'center_lng': 150.9065,
            'start_point': 'University of Wollongong (Main Campus)',
            'end_point': 'Flagstaff Point Lighthouse',
            'coordinates': [[-34.4054, 150.8784], [-34.4290, 150.9078]],
            'score_greenery': 4.5, 'score_quietness': 5.5, 'score_flatness': 8.5, 'score_uncrowded': 6.0
        },
        {
            'name': 'JJ Kelly Park Mindfulness Walk',
            'description': 'Tiny hidden suburban park — extremely quiet, perfectly flat, almost never crowded',
            'distance_km': 1.0, 'area_type': 'park',
            'center_lat': -34.4130, 'center_lng': 150.8840,
            'start_point': 'University of Wollongong (Main Campus)',
            'end_point': 'JJ Kelly Park (Para Rd)',
            'coordinates': [[-34.4054, 150.8784], [-34.4137, 150.8846]],
            'score_greenery': 5.5, 'score_quietness': 8.8, 'score_flatness': 9.9, 'score_uncrowded': 9.5
        },
        {
            'name': 'Figtree Reserve Walk',
            'description': 'Suburban green corridor with gentle undulation through Figtree neighbourhood',
            'distance_km': 4.5, 'area_type': 'suburban',
            'center_lat': -34.4250, 'center_lng': 150.8620,
            'start_point': 'University of Wollongong (Main Campus)',
            'end_point': 'Figtree Oval Reserve',
            'coordinates': [[-34.4054, 150.8784], [-34.4290, 150.8590]],
            'score_greenery': 5.5, 'score_quietness': 7.0, 'score_flatness': 6.0, 'score_uncrowded': 7.5
        },
        {
            'name': 'Campus East to Corrimal Beach',
            'description': 'Urban path from campus through North Wollongong to the beachfront',
            'distance_km': 2.2, 'area_type': 'heritage',
            'center_lat': -34.4020, 'center_lng': 150.8900,
            'start_point': 'University of Wollongong (Main Campus)',
            'end_point': 'Corrimal Street Beach Access',
            'coordinates': [[-34.4054, 150.8784], [-34.4000, 150.8935]],
            'score_greenery': 4.0, 'score_quietness': 5.0, 'score_flatness': 9.0, 'score_uncrowded': 5.5
        },
        {
            'name': 'Wollongong City Walk',
            'description': 'Vibrant urban walk through the CBD — cafes, street art, and a busy social scene',
            'distance_km': 2.5, 'area_type': 'urban',
            'center_lat': -34.4260, 'center_lng': 150.8935,
            'start_point': 'University of Wollongong (Main Campus)',
            'end_point': 'Crown Street Mall Wollongong',
            'coordinates': [[-34.4054, 150.8784], [-34.4275, 150.8940]],
            'score_greenery': 2.0, 'score_quietness': 2.0, 'score_flatness': 9.5, 'score_uncrowded': 1.5
        },
        {
            'name': 'Mt Ousley Forest Track',
            'description': 'Steep rugged bushwalk through dense eucalypt forest — challenging and very remote',
            'distance_km': 5.5, 'area_type': 'forest',
            'center_lat': -34.3920, 'center_lng': 150.8650,
            'start_point': 'University of Wollongong (Main Campus)',
            'end_point': 'Mt Ousley Lookout',
            'coordinates': [[-34.4054, 150.8784], [-34.3898, 150.8600]],
            'score_greenery': 9.0, 'score_quietness': 8.5, 'score_flatness': 2.0, 'score_uncrowded': 9.0
        },
        {
            'name': 'Lang Park to Harbour Walk',
            'description': 'Easy walk from near university through city gardens to the harbour front',
            'distance_km': 3.8, 'area_type': 'park',
            'center_lat': -34.4260, 'center_lng': 150.8975,
            'start_point': 'University of Wollongong (Main Campus)',
            'end_point': 'Wollongong Harbour Foreshore',
            'coordinates': [[-34.4054, 150.8784], [-34.4250, 150.9015]],
            'score_greenery': 5.0, 'score_quietness': 4.5, 'score_flatness': 9.5, 'score_uncrowded': 4.0
        }
    ]

    for route in routes:
        connection.execute(
            '''INSERT INTO routes (name, description, coordinates, distance_km, area_type,
                                   center_lat, center_lng, start_point, end_point,
                                   score_greenery, score_quietness, score_flatness, score_uncrowded)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (route['name'], route['description'], json.dumps(route['coordinates']),
             route['distance_km'], route['area_type'],
             route['center_lat'], route['center_lng'],
             route['start_point'], route['end_point'],
             route['score_greenery'], route['score_quietness'],
             route['score_flatness'], route['score_uncrowded'])
        )


def get_routes_near(latitude, longitude, radius_km=5.0):
    """Get routes within radius of a point using approximate distance."""
    connection = get_connection()
    all_routes = connection.execute('SELECT * FROM routes').fetchall()
    connection.close()

    nearby_routes = []
    for route in all_routes:
        delta_lat = abs(route['center_lat'] - latitude)
        delta_lng = abs(route['center_lng'] - longitude)
        approximate_distance_km = ((delta_lat ** 2 + delta_lng ** 2) ** 0.5) * 111
        if approximate_distance_km <= radius_km:
            route_dict = dict(route)
            route_dict['coordinates'] = json.loads(route_dict['coordinates'])
            nearby_routes.append(route_dict)

    return nearby_routes


def get_cached_score(route_id, factor):
    connection = get_connection()
    row = connection.execute(
        'SELECT score FROM score_cache WHERE route_id=? AND factor=? AND expires_at > ?',
        (route_id, factor, datetime.now().isoformat())
    ).fetchone()
    connection.close()
    return row['score'] if row else None


def set_cached_score(route_id, factor, score, ttl_hours=6):
    connection = get_connection()
    expiry_time = (datetime.now() + timedelta(hours=ttl_hours)).isoformat()
    connection.execute(
        '''INSERT OR REPLACE INTO score_cache (route_id, factor, score, computed_at, expires_at)
           VALUES (?, ?, ?, ?, ?)''',
        (route_id, factor, score, datetime.now().isoformat(), expiry_time)
    )
    connection.commit()
    connection.close()


def save_rating(route_id, mood, rating, weather_condition=None):
    connection = get_connection()
    connection.execute(
        'INSERT INTO ratings (route_id, mood, rating, weather_condition) VALUES (?, ?, ?, ?)',
        (route_id, mood, rating, weather_condition)
    )
    connection.commit()
    connection.close()
