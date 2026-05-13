from flask import Flask, jsonify, request
from flask_cors import CORS
import requests, os

app = Flask(__name__)
CORS(app)

INVENTORY_URL = os.getenv("INVENTORY_URL", "http://inventory-service:5001")
BANNER_URL    = os.getenv("BANNER_URL",    "http://banner-service:5002")
PITY_URL      = os.getenv("PITY_URL",      "http://pity-service:5003")

# ── Health ────────────────────────────────────────────────────────────────────
@app.route('/health')
def health():
    services = {}
    for name, url in [("inventory", INVENTORY_URL), ("banner", BANNER_URL), ("pity", PITY_URL)]:
        try:
            r = requests.get(f"{url}/health", timeout=3)
            services[name] = r.json()
        except Exception as e:
            services[name] = {"status": "error", "detail": str(e)}
    all_ok = all(s.get("status") == "ok" for s in services.values())
    return jsonify({"status": "ok" if all_ok else "degraded", "services": services})

# ── Player ────────────────────────────────────────────────────────────────────
@app.route('/api/player/<player_id>', methods=['GET'])
def get_player(player_id):
    inv  = requests.get(f"{INVENTORY_URL}/player/{player_id}").json()
    pity = requests.get(f"{PITY_URL}/pity/{player_id}").json()
    return jsonify({**inv, "pity_data": pity.get("pity_data", [])})

@app.route('/api/player/<player_id>/add_resources', methods=['POST'])
def add_resources(player_id):
    r = requests.post(f"{INVENTORY_URL}/player/{player_id}/add_resources", json=request.json)
    return jsonify(r.json()), r.status_code

# ── Banners ───────────────────────────────────────────────────────────────────
@app.route('/api/banners', methods=['GET'])
def get_banners():
    r = requests.get(f"{BANNER_URL}/banners")
    return jsonify(r.json())

@app.route('/api/banners/rates', methods=['GET'])
def get_rates():
    banner_id = request.args.get("banner_id", "permanente")
    r = requests.get(f"{BANNER_URL}/simulate_rates?banner_id={banner_id}")
    return jsonify(r.json())

# ── Pull ──────────────────────────────────────────────────────────────────────
@app.route('/api/pull', methods=['POST'])
def pull():
    data      = request.json or {}
    player_id = data.get("player_id", "player1")
    banner_id = data.get("banner_id", "permanente")
    count     = int(data.get("count", 1))
    use_coins = data.get("use_coins", False)

    # 1. Obtener información del banner
    banner_r = requests.get(f"{BANNER_URL}/banners/{banner_id}")
    if banner_r.status_code != 200:
        return jsonify({"error": "Banner not found"}), 404
    banner = banner_r.json()

    # 2. Obtener estado de pity actual (incluyendo guarantee_featured)
    pity_r = requests.get(f"{PITY_URL}/pity/{player_id}/{banner_id}")
    pity   = pity_r.json()
    pity_count         = pity.get("pity_count", 0)
    guarantee_featured = bool(pity.get("guarantee_featured", 0))

    # 3. Deducir recursos
    if use_coins:
        cost    = banner["cost_coins"] * count
        spend_r = requests.post(
            f"{INVENTORY_URL}/player/{player_id}/spend",
            json={"type": "coins", "amount": cost}
        )
    else:
        cost    = banner["cost_tickets"] * count
        spend_r = requests.post(
            f"{INVENTORY_URL}/player/{player_id}/spend",
            json={"type": "tickets", "amount": cost}
        )

    if spend_r.status_code != 200:
        return jsonify(spend_r.json()), 400

    # 4. Ejecutar la tirada (pasando pity y guarantee_featured al banner service)
    pull_r = requests.post(f"{BANNER_URL}/pull", json={
        "banner_id":          banner_id,
        "count":              count,
        "pity_count":         pity_count,
        "guarantee_featured": guarantee_featured,
    })
    pull_data = pull_r.json()

    # 5. Registrar en pity service (historial + actualizar guarantee_featured)
    # Los results ya traen banner_is_limited desde el banner service
    requests.post(f"{PITY_URL}/record_pull", json={
        "player_id": player_id,
        "banner_id": banner_id,
        "results":   pull_data["results"],
    })

    # 6. Añadir personajes al inventario
    for result in pull_data["results"]:
        requests.post(
            f"{INVENTORY_URL}/player/{player_id}/add_character",
            json={
                "character_id":   result["character_id"],
                "character_name": result["character_name"],
                "rarity":         result["rarity"],
            }
        )

    # 7. Obtener estado actualizado del jugador y pity
    inv_r     = requests.get(f"{INVENTORY_URL}/player/{player_id}").json()
    new_pity  = requests.get(f"{PITY_URL}/pity/{player_id}/{banner_id}").json()

    return jsonify({
        "results":    pull_data["results"],
        "pulls_done": count,
        "resources":  {
            "coins":   inv_r["player"]["coins"],
            "tickets": inv_r["player"]["tickets"],
        },
        "pity": new_pity,
    })

# ── History / Stats ───────────────────────────────────────────────────────────
@app.route('/api/history/<player_id>', methods=['GET'])
def get_history(player_id):
    banner_id = request.args.get("banner_id", "")
    limit     = request.args.get("limit", "50")
    url       = f"{PITY_URL}/history/{player_id}?limit={limit}"
    if banner_id:
        url += f"&banner_id={banner_id}"
    r = requests.get(url)
    return jsonify(r.json())

@app.route('/api/stats/<player_id>', methods=['GET'])
def get_stats(player_id):
    stats = requests.get(f"{PITY_URL}/stats/{player_id}").json()
    inv   = requests.get(f"{INVENTORY_URL}/player/{player_id}/inventory/stats").json()
    return jsonify({**stats, "inventory_stats": inv.get("stats", [])})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
