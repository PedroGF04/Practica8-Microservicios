from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB_PATH = "/data/inventory.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs("/data", exist_ok=True)
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS players (
            id TEXT PRIMARY KEY,
            coins INTEGER DEFAULT 1000,
            tickets INTEGER DEFAULT 10,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT NOT NULL,
            character_id TEXT NOT NULL,
            character_name TEXT NOT NULL,
            rarity TEXT NOT NULL,
            obtained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (player_id) REFERENCES players(id)
        );

        INSERT OR IGNORE INTO players (id, coins, tickets) VALUES ('player1', 5000, 20);
    """)
    conn.commit()
    conn.close()

@app.route('/health')
def health():
    return jsonify({"status": "ok", "service": "inventory"})

@app.route('/player/<player_id>', methods=['GET'])
def get_player(player_id):
    conn = get_db()
    player = conn.execute("SELECT * FROM players WHERE id = ?", (player_id,)).fetchone()
    if not player:
        conn.execute("INSERT INTO players (id) VALUES (?)", (player_id,))
        conn.commit()
        player = conn.execute("SELECT * FROM players WHERE id = ?", (player_id,)).fetchone()
    
    inventory = conn.execute(
        "SELECT * FROM inventory WHERE player_id = ? ORDER BY obtained_at DESC",
        (player_id,)
    ).fetchall()
    
    conn.close()
    return jsonify({
        "player": dict(player),
        "inventory": [dict(i) for i in inventory],
        "inventory_count": len(inventory)
    })

@app.route('/player/<player_id>/resources', methods=['GET'])
def get_resources(player_id):
    conn = get_db()
    player = conn.execute("SELECT * FROM players WHERE id = ?", (player_id,)).fetchone()
    conn.close()
    if not player:
        return jsonify({"error": "Player not found"}), 404
    return jsonify({"coins": player["coins"], "tickets": player["tickets"]})

@app.route('/player/<player_id>/spend', methods=['POST'])
def spend_resources(player_id):
    data = request.json
    cost_type = data.get("type", "tickets")
    amount = data.get("amount", 1)

    conn = get_db()
    player = conn.execute("SELECT * FROM players WHERE id = ?", (player_id,)).fetchone()
    if not player:
        conn.close()
        return jsonify({"error": "Player not found"}), 404

    if cost_type == "tickets" and player["tickets"] < amount:
        conn.close()
        return jsonify({"error": "Not enough tickets", "have": player["tickets"]}), 400
    if cost_type == "coins" and player["coins"] < amount:
        conn.close()
        return jsonify({"error": "Not enough coins", "have": player["coins"]}), 400

    if cost_type == "tickets":
        conn.execute("UPDATE players SET tickets = tickets - ? WHERE id = ?", (amount, player_id))
    else:
        conn.execute("UPDATE players SET coins = coins - ? WHERE id = ?", (amount, player_id))

    conn.commit()
    updated = conn.execute("SELECT * FROM players WHERE id = ?", (player_id,)).fetchone()
    conn.close()
    return jsonify({"success": True, "coins": updated["coins"], "tickets": updated["tickets"]})

@app.route('/player/<player_id>/add_character', methods=['POST'])
def add_character(player_id):
    data = request.json
    conn = get_db()
    conn.execute(
        "INSERT INTO inventory (player_id, character_id, character_name, rarity) VALUES (?, ?, ?, ?)",
        (player_id, data["character_id"], data["character_name"], data["rarity"])
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/player/<player_id>/add_resources', methods=['POST'])
def add_resources(player_id):
    data = request.json
    conn = get_db()
    player = conn.execute("SELECT * FROM players WHERE id = ?", (player_id,)).fetchone()
    if not player:
        conn.execute("INSERT INTO players (id) VALUES (?)", (player_id,))
    if "coins" in data:
        conn.execute("UPDATE players SET coins = coins + ? WHERE id = ?", (data["coins"], player_id))
    if "tickets" in data:
        conn.execute("UPDATE players SET tickets = tickets + ? WHERE id = ?", (data["tickets"], player_id))
    conn.commit()
    updated = conn.execute("SELECT * FROM players WHERE id = ?", (player_id,)).fetchone()
    conn.close()
    return jsonify({"success": True, "coins": updated["coins"], "tickets": updated["tickets"]})

@app.route('/player/<player_id>/inventory/stats', methods=['GET'])
def inventory_stats(player_id):
    conn = get_db()
    stats = conn.execute("""
        SELECT rarity, COUNT(*) as count 
        FROM inventory WHERE player_id = ? 
        GROUP BY rarity
    """, (player_id,)).fetchall()
    conn.close()
    return jsonify({"stats": [dict(s) for s in stats]})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001, debug=True)
