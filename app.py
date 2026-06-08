#!/usr/bin/env python3
"""
Backend Flask — Les 7 Boules de Cristal
Calcul du thème natal via Swiss Ephemeris (Kerykeion)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from kerykeion import AstrologicalSubject
from timezonefinder import TimezoneFinder
import traceback
import os

app = Flask(__name__)
CORS(app)

tf = TimezoneFinder()

# Base de coordonnées francophones étendue
VILLES = {
    # France
    "paris": (48.8566, 2.3522, "Europe/Paris"),
    "marseille": (43.2965, 5.3698, "Europe/Paris"),
    "lyon": (45.7640, 4.8357, "Europe/Paris"),
    "toulouse": (43.6047, 1.4442, "Europe/Paris"),
    "nice": (43.7102, 7.2620, "Europe/Paris"),
    "nantes": (47.2184, -1.5536, "Europe/Paris"),
    "bordeaux": (44.8378, -0.5792, "Europe/Paris"),
    "strasbourg": (48.5734, 7.7521, "Europe/Paris"),
    "lille": (50.6292, 3.0573, "Europe/Paris"),
    "rennes": (48.1173, -1.6778, "Europe/Paris"),
    "reims": (49.2583, 4.0317, "Europe/Paris"),
    "le havre": (49.4938, 0.1077, "Europe/Paris"),
    "saint-etienne": (45.4397, 4.3872, "Europe/Paris"),
    "toulon": (43.1242, 5.9280, "Europe/Paris"),
    "grenoble": (45.1885, 5.7245, "Europe/Paris"),
    "dijon": (47.3220, 5.0415, "Europe/Paris"),
    "angers": (47.4784, -0.5632, "Europe/Paris"),
    "nimes": (43.8367, 4.3601, "Europe/Paris"),
    "villeurbanne": (45.7719, 4.8902, "Europe/Paris"),
    "le mans": (48.0061, 0.1996, "Europe/Paris"),
    "aix-en-provence": (43.5297, 5.4474, "Europe/Paris"),
    "brest": (48.3905, -4.4860, "Europe/Paris"),
    "limoges": (45.8336, 1.2611, "Europe/Paris"),
    "clermont-ferrand": (45.7772, 3.0870, "Europe/Paris"),
    "amiens": (49.8942, 2.2957, "Europe/Paris"),
    # Belgique
    "bruxelles": (50.8503, 4.3517, "Europe/Brussels"),
    "bruges": (51.2093, 3.2247, "Europe/Brussels"),
    "gand": (51.0543, 3.7174, "Europe/Brussels"),
    "liege": (50.6326, 5.5797, "Europe/Brussels"),
    "anvers": (51.2194, 4.4025, "Europe/Brussels"),
    # Suisse
    "geneve": (46.2044, 6.1432, "Europe/Zurich"),
    "zurich": (47.3769, 8.5417, "Europe/Zurich"),
    "berne": (46.9480, 7.4474, "Europe/Zurich"),
    "lausanne": (46.5197, 6.6323, "Europe/Zurich"),
    "bale": (47.5596, 7.5886, "Europe/Zurich"),
    # Canada
    "montreal": (45.5017, -73.5673, "America/Montreal"),
    "quebec": (46.8139, -71.2082, "America/Toronto"),
    "ottawa": (45.4215, -75.6972, "America/Toronto"),
    "toronto": (43.6532, -79.3832, "America/Toronto"),
    # Afrique francophone
    "brazzaville": (-4.2634, 15.2662, "Africa/Brazzaville"),
    "kinshasa": (-4.3317, 15.3278, "Africa/Kinshasa"),
    "dakar": (14.6928, -17.4467, "Africa/Dakar"),
    "abidjan": (5.3600, -4.0083, "Africa/Abidjan"),
    "douala": (4.0511, 9.7679, "Africa/Douala"),
    "yaounde": (3.8480, 11.5021, "Africa/Douala"),
    "libreville": (0.3901, 9.4544, "Africa/Libreville"),
    "lome": (6.1375, 1.2123, "Africa/Lome"),
    "cotonou": (6.3654, 2.4183, "Africa/Porto-Novo"),
    "bamako": (12.6392, -8.0029, "Africa/Bamako"),
    "ouagadougou": (12.3714, -1.5197, "Africa/Ouagadougou"),
    "niamey": (13.5137, 2.1098, "Africa/Niamey"),
    "conakry": (9.5370, -13.6773, "Africa/Conakry"),
    "banjul": (13.4549, -16.5790, "Africa/Banjul"),
    "bissau": (11.8636, -15.5977, "Africa/Bissau"),
    "antananarivo": (-18.9137, 47.5361, "Indian/Antananarivo"),
    "tananarive": (-18.9137, 47.5361, "Indian/Antananarivo"),
    "djibouti": (11.5720, 43.1456, "Africa/Djibouti"),
    "moroni": (-11.7016, 43.2551, "Indian/Comoro"),
    "porto-novo": (6.4969, 2.6289, "Africa/Porto-Novo"),
    "n'djamena": (12.1048, 15.0445, "Africa/Ndjamena"),
    "ndjamena": (12.1048, 15.0445, "Africa/Ndjamena"),
    "bangui": (4.3612, 18.5550, "Africa/Bangui"),
    "malabo": (3.7500, 8.7833, "Africa/Malabo"),
    "sao tome": (0.3365, 6.7273, "Africa/Sao_Tome"),
    "luanda": (-8.8368, 13.2343, "Africa/Luanda"),
    "bujumbura": (-3.3869, 29.3619, "Africa/Bujumbura"),
    "kigali": (-1.9441, 30.0619, "Africa/Kigali"),
    "djibouti": (11.5720, 43.1456, "Africa/Djibouti"),
    # Afrique nord
    "casablanca": (33.5731, -7.5898, "Africa/Casablanca"),
    "rabat": (34.0209, -6.8416, "Africa/Casablanca"),
    "marrakech": (31.6295, -7.9811, "Africa/Casablanca"),
    "alger": (36.7372, 3.0865, "Africa/Algiers"),
    "oran": (35.6969, -0.6331, "Africa/Algiers"),
    "tunis": (36.8188, 10.1658, "Africa/Tunis"),
    "tripoli": (32.8872, 13.1913, "Africa/Tripoli"),
    "cairo": (30.0444, 31.2357, "Africa/Cairo"),
    "le caire": (30.0444, 31.2357, "Africa/Cairo"),
    # Antilles / DOM
    "fort-de-france": (14.6037, -61.0730, "America/Martinique"),
    "pointe-a-pitre": (16.2415, -61.5330, "America/Guadeloupe"),
    "cayenne": (4.9224, -52.3135, "America/Cayenne"),
    "saint-denis": (-20.8789, 55.4481, "Indian/Reunion"),
    "mamoudzou": (-12.7806, 45.2278, "Indian/Mayotte"),
    # Autres
    "port-au-prince": (18.5944, -72.3074, "America/Port-au-Prince"),
    "luxembourg": (49.6117, 6.1319, "Europe/Luxembourg"),
    "monaco": (43.7384, 7.4246, "Europe/Monaco"),
    "andorre": (42.5063, 1.5218, "Europe/Andorra"),
    # Serbie
    "belgrade": (44.7866, 20.4489, "Europe/Belgrade"),
    "novi sad": (45.2671, 19.8335, "Europe/Belgrade"),
}

SIGNES_FR = {
    "Ari": "Bélier", "Tau": "Taureau", "Gem": "Gémeaux",
    "Can": "Cancer", "Leo": "Lion", "Vir": "Vierge",
    "Lib": "Balance", "Sco": "Scorpion", "Sag": "Sagittaire",
    "Cap": "Capricorne", "Aqu": "Verseau", "Pis": "Poissons"
}

MAISONS_NUM = {
    "First_House": 1, "Second_House": 2, "Third_House": 3,
    "Fourth_House": 4, "Fifth_House": 5, "Sixth_House": 6,
    "Seventh_House": 7, "Eighth_House": 8, "Ninth_House": 9,
    "Tenth_House": 10, "Eleventh_House": 11, "Twelfth_House": 12
}

def trouver_coords(lieu):
    """Trouve les coordonnées d'un lieu"""
    lieu_lower = lieu.lower().strip()
    # Retirer le pays si présent (ex: "Paris, France")
    if "," in lieu_lower:
        lieu_lower = lieu_lower.split(",")[0].strip()
    
    for ville, coords in VILLES.items():
        if ville == lieu_lower or ville in lieu_lower or lieu_lower in ville:
            return coords
    
    return None, None, None

@app.route('/theme', methods=['POST'])
def calculer_theme():
    try:
        data = request.json
        annee = int(data['annee'])
        mois = int(data['mois'])
        jour = int(data['jour'])
        heure = int(data['heure'])
        minute = int(data['minute'])
        lieu = data.get('lieu', 'Paris')

        lat, lng, tz = trouver_coords(lieu)
        
        if lat is None:
            lat, lng, tz = 48.8566, 2.3522, "Europe/Paris"
            lieu_utilise = f"{lieu} (coordonnées non trouvées, Paris utilisé)"
        else:
            lieu_utilise = lieu

        subject = AstrologicalSubject(
            "Natif",
            annee, mois, jour, heure, minute,
            lng=lng, lat=lat,
            tz_str=tz,
            zodiac_type="Tropical",
            houses_system_identifier="P"
        )

        def get_planete(nom):
            obj = getattr(subject, nom)
            signe_court = obj['sign'][:3]
            signe_fr = SIGNES_FR.get(signe_court, obj['sign'])
            maison_num = MAISONS_NUM.get(obj['house'], 0)
            return {
                "signe": signe_fr,
                "maison": maison_num,
                "degre": round(obj['position'], 1)
            }

        theme = {
            "lieu": lieu_utilise,
            "soleil": get_planete('sun'),
            "lune": get_planete('moon'),
            "mercure": get_planete('mercury'),
            "venus": get_planete('venus'),
            "mars": get_planete('mars'),
            "jupiter": get_planete('jupiter'),
            "saturne": get_planete('saturn'),
            "uranus": get_planete('uranus'),
            "neptune": get_planete('neptune'),
            "pluton": get_planete('pluto'),
            "ascendant": SIGNES_FR.get(subject.first_house['sign'][:3], subject.first_house['sign']),
            "mc": SIGNES_FR.get(subject.tenth_house['sign'][:3], subject.tenth_house['sign'])
        }

        return jsonify({"ok": True, "theme": theme})

    except Exception as e:
        return jsonify({"ok": False, "erreur": str(e)}), 500

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"ok": True, "message": "Les 7 Boules de Cristal — API active"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5555))
    app.run(host='0.0.0.0', port=port)
