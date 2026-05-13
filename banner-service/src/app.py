from flask import Flask, jsonify, request
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

# --- DICCIONARIO DE PERSONAJES (Imágenes + Nuevos) ---
CHARS = {
    # SSR PERMANENTES (4)
    "himeko":    {"id": "himeko",    "name": "Himeko",    "element": "Fuego",     "color": "#ff6b35"},
    "welt":      {"id": "welt",      "name": "Welt",      "element": "Oscuridad", "color": "#9b59b6"},
    "bronya":    {"id": "bronya",    "name": "Bronya",    "element": "Viento",    "color": "#1abc9c"},
    "gepard":    {"id": "gepard",    "name": "Gepard",    "element": "Hielo",     "color": "#95a5a6"},
    
    # SR (Personajes de imágenes + Nuevos personajes)
    "herta":     {"id": "herta",     "name": "Herta",     "element": "Hielo",     "color": "#74b9ff"},
    "robin":     {"id": "robin",     "name": "Robin",     "element": "Luz",       "color": "#fd79a8"},
    "sunday":    {"id": "sunday",    "name": "Sunday",    "element": "Estelar",   "color": "#ffeaa7"},
    "hysilens":  {"id": "hysilens",  "name": "Hysilens",  "element": "Rayo",      "color": "#f1c40f"},
    "evernight": {"id": "evernight", "name": "Evernight", "element": "Oscuridad", "color": "#2c3e50"},
    "ruan-mei":  {"id": "ruan-mei",  "name": "Ruan Mei",  "element": "Hielo",     "color": "#00cec9"},
    "asta":      {"id": "asta",      "name": "Asta",      "element": "Fuego",     "color": "#ff7675"},
    "arlan":     {"id": "arlan",     "name": "Arlan",     "element": "Rayo",      "color": "#a29bfe"},
    "kafka":     {"id": "kafka",     "name": "Kafka",     "element": "Rayo",      "color": "#6c5ce7"},
    "cyrene":    {"id": "cyrene",    "name": "Cyrene",    "element": "Hielo",     "color": "#81ecec"},
    "anaxagoras":{"id": "anaxagoras","name": "Anaxágoras", "element": "Viento",    "color": "#55efc4"},
    "evanescia": {"id": "evanescia", "name": "Evanescia", "element": "Estelar",   "color": "#fd79a8"},
    "hyacine":   {"id": "hyacine",   "name": "Hyacine",   "element": "Viento",    "color": "#00b894"},
    "mydeimos":  {"id": "mydeimos",  "name": "Mydeimos",  "element": "Luz",       "color": "#fff200"},

    # SSR LIMITADOS
    "phainon":   {"id": "phainon",   "name": "Phainon",   "element": "Estelar",   "color": "#f9ca24"},
    "cerydra":   {"id": "cerydra",   "name": "Cerydra",   "element": "Oscuridad", "color": "#6c5ce7"},
    "dan-heng":  {"id": "dan-heng",  "name": "Dan Heng",  "element": "Viento",    "color": "#00cec9"}
}

# --- OBJETOS R (Categoría R) ---
OBJECTS_R = [
    {"id": "obj_1", "name": "Espada de Madera", "element": "Físico", "color": "#bdc3c7"},
    {"id": "obj_2", "name": "Escudo Oxidado",   "element": "Físico", "color": "#bdc3c7"},
    {"id": "obj_3", "name": "Flecha de Hierro", "element": "Físico", "color": "#bdc3c7"},
    {"id": "obj_4", "name": "Libro Viejo",      "element": "Magia",  "color": "#bdc3c7"},
    {"id": "obj_5", "name": "Lanza Quebrada",   "element": "Físico", "color": "#bdc3c7"},
    {"id": "obj_6", "name": "Amuleto Simple",   "element": "Magia",  "color": "#bdc3c7"}
]

# Grupos de reparto
STANDARD_SSR = [CHARS["himeko"], CHARS["welt"], CHARS["bronya"], CHARS["gepard"]]
STANDARD_SR  = [
    CHARS["herta"], CHARS["robin"], CHARS["sunday"], CHARS["hysilens"], 
    CHARS["evernight"], CHARS["ruan-mei"], CHARS["asta"], CHARS["arlan"],
    CHARS["kafka"], CHARS["cyrene"], CHARS["anaxagoras"], CHARS["evanescia"],
    CHARS["hyacine"], CHARS["mydeimos"]
]
STANDARD_R   = OBJECTS_R

BANNERS = {
    "permanente": {
        "id": "permanente",
        "name": "Banner Permanente",
        "subtitle": "El estándar — personajes de las imágenes y nuevos",
        "type": "permanent",
        "cost_tickets": 1,
        "cost_coins": 150,
        "pity_limit": 90,
        "soft_pity_start": 74,
        "featured_character": None,
        "base_rates": {"SSR": 0.006, "SR": 0.051, "R": 0.943},
        "characters": {
            "SSR": STANDARD_SSR,
            "SR":  STANDARD_SR,
            "R":   STANDARD_R
        }
    },
    "limitado_phainon": {
        "id": "limitado_phainon",
        "name": "To Evermore Burn as the Sun",
        "subtitle": "Personaje destacado: Phainon",
        "type": "limited",
        "cost_tickets": 1,
        "cost_coins": 160,
        "pity_limit": 80,
        "soft_pity_start": 64,
        "featured_character": "phainon",
        "base_rates": {"SSR": 0.006, "SR": 0.051, "R": 0.943},
        "characters": {
            "SSR": [CHARS["phainon"]] + STANDARD_SSR,
            "SR":  STANDARD_SR,
            "R":   STANDARD_R
        }
    },
    "limitado_cerydra": {
        "id": "limitado_cerydra",
        "name": "The Iron Timer of Tides",
        "subtitle": "Personaje destacado: Cerydra",
        "type": "limited",
        "cost_tickets": 1,
        "cost_coins": 160,
        "pity_limit": 80,
        "soft_pity_start": 64,
        "featured_character": "cerydra",
        "base_rates": {"SSR": 0.006, "SR": 0.051, "R": 0.943},
        "characters": {
            "SSR": [CHARS["cerydra"]] + STANDARD_SSR,
            "SR":  STANDARD_SR,
            "R":   STANDARD_R
        }
    },
    "limitado_dan_heng": {
        "id": "limitado_dan_heng",
        "name": "Slay Until Evil Ends",
        "subtitle": "Personaje destacado: Dan Heng",
        "type": "limited",
        "cost_tickets": 1,
        "cost_coins": 160,
        "pity_limit": 80,
        "soft_pity_start": 64,
        "featured_character": "dan-heng",
        "base_rates": {"SSR": 0.006, "SR": 0.051, "R": 0.943},
        "characters": {
            "SSR": [CHARS["dan-heng"]] + STANDARD_SSR,
            "SR":  STANDARD_SR,
            "R":   STANDARD_R
        }
    }
}

# ── Probability ───────────────────────────────────────────────────────────────

def calculate_ssr_rate(banner_id: str, pity_count: int) -> float:
    banner = BANNERS[banner_id]
    base = banner["base_rates"]["SSR"]
    soft = banner["soft_pity_start"]
    hard = banner["pity_limit"]
    # Hard pity: pull número `hard` (índice hard-1 acumulados sin SSR) garantiza
    if pity_count >= hard:
        return 1.0
    if pity_count >= soft:
        extra = (pity_count - soft + 1) * 0.06
        return min(base + extra, 1.0)
    return base


def resolve_ssr_character(banner: dict, guarantee_featured: bool):
    """
    50/50 para banners limitados.
    guarantee_featured=True  → siempre el destacado (ganó garantía)
    guarantee_featured=False → 50% destacado / 50% permanente aleatorio
    Devuelve (char, won_fifty_fifty, was_guaranteed)
    """
    featured_id   = banner.get("featured_character")
    ssr_pool      = banner["characters"]["SSR"]
    featured_char = next((c for c in ssr_pool if c["id"] == featured_id), None)
    perm_pool     = [c for c in ssr_pool if not c.get("is_limited", False)]

    if guarantee_featured:
        return featured_char, True, True   # won=True, guaranteed=True

    if random.random() < 0.5:
        return featured_char, True, False  # ganó el 50/50
    else:
        char = random.choice(perm_pool) if perm_pool else featured_char
        return char, False, False          # perdió el 50/50


def do_single_pull(banner_id: str, pity_count: int, guarantee_featured: bool = False) -> dict:
    banner    = BANNERS[banner_id]
    is_limited = banner["type"] == "limited"
    ssr_rate  = calculate_ssr_rate(banner_id, pity_count)
    sr_rate   = banner["base_rates"]["SR"]
    roll      = random.random()

    # Hard pity: cuando pity_count llega al límite, SSR garantizado
    was_hard_pity = (pity_count >= banner["pity_limit"])

    # Determinar rareza
    if was_hard_pity or roll < ssr_rate:
        rarity = "SSR"
    elif roll < ssr_rate + sr_rate:
        rarity = "SR"
    else:
        rarity = "R"

    # Elegir personaje
    if rarity == "SSR" and is_limited:
        char, won_fifty_fifty, was_guaranteed = resolve_ssr_character(banner, guarantee_featured)
        is_char_limited = char.get("is_limited", False)
    elif rarity == "SSR":
        char = random.choice(banner["characters"]["SSR"])
        won_fifty_fifty = False
        was_guaranteed  = False
        is_char_limited = False
    else:
        char = random.choice(banner["characters"][rarity])
        won_fifty_fifty = False
        was_guaranteed  = False
        is_char_limited = False

    return {
        "character_id":    char["id"],
        "character_name":  char["name"],
        "element":         char["element"],
        "color":           char.get("color", "#888"),
        "rarity":          rarity,
        "roll_value":      round(roll, 6),
        "ssr_rate_used":   round(ssr_rate, 6),
        # Flags de pity
        "was_soft_pity":   (rarity == "SSR" and not was_hard_pity
                            and pity_count >= banner["soft_pity_start"]),
        "was_hard_pity":   (rarity == "SSR" and was_hard_pity),
        # Flags de 50/50
        "is_featured":     char["id"] == banner.get("featured_character"),
        "is_char_limited": is_char_limited,   # ← el personaje en sí es limitado
        "banner_is_limited": is_limited,      # ← el banner es limitado
        "won_fifty_fifty": won_fifty_fifty,
        "was_guaranteed":  was_guaranteed,
    }


@app.route('/health')
def health():
    return jsonify({"status": "ok", "service": "banner"})

@app.route('/banners', methods=['GET'])
def list_banners():
    return jsonify({"banners": [
        {"id": b["id"], "name": b["name"], "subtitle": b["subtitle"],
         "type": b["type"], "cost_tickets": b["cost_tickets"],
         "cost_coins": b["cost_coins"], "pity_limit": b["pity_limit"],
         "soft_pity_start": b["soft_pity_start"],
         "featured_character": b["featured_character"],
         "rates": b["base_rates"]}
        for b in BANNERS.values()
    ]})

@app.route('/banners/<banner_id>', methods=['GET'])
def get_banner(banner_id):
    if banner_id not in BANNERS:
        return jsonify({"error": "Banner not found"}), 404
    return jsonify(BANNERS[banner_id])

@app.route('/pull', methods=['POST'])
def pull():
    data               = request.json or {}
    banner_id          = data.get("banner_id", "permanente")
    count              = min(int(data.get("count", 1)), 10)
    pity_count         = int(data.get("pity_count", 0))
    guarantee_featured = bool(data.get("guarantee_featured", False))

    if banner_id not in BANNERS:
        return jsonify({"error": "Banner not found"}), 404

    banner     = BANNERS[banner_id]
    is_limited = banner["type"] == "limited"
    results    = []
    current_pity      = pity_count
    current_guarantee = guarantee_featured

    for _ in range(count):
        result = do_single_pull(banner_id, current_pity, current_guarantee)
        results.append(result)

        if result["rarity"] == "SSR":
            current_pity = 0
            # Actualizar garantía para el siguiente pull del mismo ×10
            if is_limited:
                if result["won_fifty_fifty"] or result["was_guaranteed"]:
                    current_guarantee = False   # ganó → sin garantía
                else:
                    current_guarantee = True    # perdió → garantía activa
        else:
            current_pity += 1

    return jsonify({
        "results":             results,
        "pulls_done":          count,
        "new_pity":            current_pity,
        "new_guarantee":       current_guarantee,
        "ssr_obtained":        any(r["rarity"] == "SSR" for r in results),
        "banner_used":         banner_id,
    })

@app.route('/simulate_rates', methods=['GET'])
def simulate_rates():
    banner_id = request.args.get("banner_id", "permanente")
    if banner_id not in BANNERS:
        return jsonify({"error": "Banner not found"}), 404
    banner = BANNERS[banner_id]
    # +1 para mostrar el pull de garantía (100%)
    return jsonify({"rates": [
        {"pity": i, "ssr_rate": round(calculate_ssr_rate(banner_id, i) * 100, 4)}
        for i in range(banner["pity_limit"] + 1)
    ], "banner_id": banner_id})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)