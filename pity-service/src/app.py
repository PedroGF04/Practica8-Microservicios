from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3, os
from datetime import datetime

app = Flask(__name__)
CORS(app)
DB_PATH = "/data/pity.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs("/data", exist_ok=True)
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS pity_tracker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT NOT NULL,
            banner_id TEXT NOT NULL,
            pity_count INTEGER DEFAULT 0,
            guarantee_featured INTEGER DEFAULT 0,
            total_pulls INTEGER DEFAULT 0,
            total_ssr INTEGER DEFAULT 0,
            total_sr INTEGER DEFAULT 0,
            total_featured INTEGER DEFAULT 0,
            total_fifty_fifty_wins INTEGER DEFAULT 0,
            total_fifty_fifty_losses INTEGER DEFAULT 0,
            last_ssr_pull INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id, banner_id)
        );

        CREATE TABLE IF NOT EXISTS pull_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT NOT NULL,
            banner_id TEXT NOT NULL,
            character_id TEXT NOT NULL,
            character_name TEXT NOT NULL,
            rarity TEXT NOT NULL,
            pity_at_pull INTEGER NOT NULL,
            was_soft_pity INTEGER DEFAULT 0,
            was_hard_pity INTEGER DEFAULT 0,
            is_featured INTEGER DEFAULT 0,
            was_guaranteed INTEGER DEFAULT 0,
            won_fifty_fifty INTEGER DEFAULT 0,
            roll_value REAL,
            pulled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    # Migración segura: añadir columnas que puedan faltar en DBs antiguas
    migrations = [
        ("pity_tracker",  "guarantee_featured",        "INTEGER DEFAULT 0"),
        ("pity_tracker",  "total_featured",             "INTEGER DEFAULT 0"),
        ("pity_tracker",  "total_fifty_fifty_wins",     "INTEGER DEFAULT 0"),
        ("pity_tracker",  "total_fifty_fifty_losses",   "INTEGER DEFAULT 0"),
        ("pull_history",  "is_featured",                "INTEGER DEFAULT 0"),
        ("pull_history",  "was_guaranteed",             "INTEGER DEFAULT 0"),
        ("pull_history",  "won_fifty_fifty",            "INTEGER DEFAULT 0"),
    ]
    for table, col, definition in migrations:
        try:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {definition}")
        except Exception:
            pass
    conn.commit()
    conn.close()

def get_or_create_pity(conn, player_id, banner_id):
    row = conn.execute(
        "SELECT * FROM pity_tracker WHERE player_id=? AND banner_id=?",
        (player_id, banner_id)
    ).fetchone()
    if not row:
        conn.execute(
            "INSERT INTO pity_tracker (player_id, banner_id) VALUES (?,?)",
            (player_id, banner_id)
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM pity_tracker WHERE player_id=? AND banner_id=?",
            (player_id, banner_id)
        ).fetchone()
    return dict(row)

@app.route('/health')
def health():
    return jsonify({"status": "ok", "service": "pity"})

@app.route('/pity/<player_id>/<banner_id>', methods=['GET'])
def get_pity(player_id, banner_id):
    conn = get_db()
    pity = get_or_create_pity(conn, player_id, banner_id)
    conn.close()
    return jsonify(pity)

@app.route('/pity/<player_id>', methods=['GET'])
def get_all_pity(player_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM pity_tracker WHERE player_id=?", (player_id,)
    ).fetchall()
    conn.close()
    return jsonify({"pity_data": [dict(r) for r in rows]})

@app.route('/record_pull', methods=['POST'])
def record_pull():
    data      = request.json or {}
    player_id = data["player_id"]
    banner_id = data["banner_id"]
    results   = data["results"]

    conn = get_db()
    pity = get_or_create_pity(conn, player_id, banner_id)

    current_pity        = pity.get("pity_count") or 0
    guarantee_featured  = pity.get("guarantee_featured") or 0
    total_pulls         = pity.get("total_pulls") or 0
    total_ssr           = pity.get("total_ssr") or 0
    total_sr            = pity.get("total_sr") or 0
    total_featured      = pity.get("total_featured") or 0
    last_ssr_pull       = pity.get("last_ssr_pull") or 0
    fifty_wins          = pity.get("total_fifty_fifty_wins") or 0
    fifty_losses        = pity.get("total_fifty_fifty_losses") or 0

    for r in results:
        total_pulls += 1

        # ── Leer flags del banner service (nombres exactos que devuelve) ──
        # banner_is_limited → el banner donde se hizo el pull es de tipo limitado
        # is_char_limited   → el personaje obtenido es el limitado/destacado
        # is_featured       → el personaje es el featured del banner
        banner_is_limited = r.get("banner_is_limited", False)
        is_featured       = r.get("is_featured", False)
        was_guaranteed    = r.get("was_guaranteed", False)
        won_fifty_fifty   = r.get("won_fifty_fifty", False)

        conn.execute(
            """INSERT INTO pull_history
               (player_id, banner_id, character_id, character_name,
                rarity, pity_at_pull, was_soft_pity, was_hard_pity,
                is_featured, was_guaranteed, won_fifty_fifty, roll_value)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (player_id, banner_id,
             r["character_id"], r["character_name"], r["rarity"],
             current_pity,
             1 if r.get("was_soft_pity") else 0,
             1 if r.get("was_hard_pity") else 0,
             1 if is_featured            else 0,
             1 if was_guaranteed         else 0,
             1 if won_fifty_fifty        else 0,
             r.get("roll_value", 0))
        )

        if r["rarity"] == "SSR":
            total_ssr     += 1
            last_ssr_pull  = total_pulls
            current_pity   = 0

            # Contar destacados obtenidos
            if is_featured:
                total_featured += 1

            # Actualizar estado del 50/50 solo en banners limitados
            if banner_is_limited:
                if won_fifty_fifty or was_guaranteed:
                    # Ganó (por 50/50 o por garantía): limpiar garantía
                    guarantee_featured = 0
                    if won_fifty_fifty:
                        fifty_wins += 1
                else:
                    # Perdió el 50/50: activar garantía para el próximo SSR
                    guarantee_featured = 1
                    fifty_losses += 1
            else:
                # Banner permanente: nunca hay garantía
                guarantee_featured = 0

        elif r["rarity"] == "SR":
            total_sr     += 1
            current_pity += 1
        else:
            current_pity += 1

    conn.execute(
        """UPDATE pity_tracker SET
           pity_count=?, guarantee_featured=?, total_pulls=?,
           total_ssr=?, total_sr=?, total_featured=?,
           total_fifty_fifty_wins=?, total_fifty_fifty_losses=?,
           last_ssr_pull=?, updated_at=?
           WHERE player_id=? AND banner_id=?""",
        (current_pity, guarantee_featured, total_pulls,
         total_ssr, total_sr, total_featured,
         fifty_wins, fifty_losses,
         last_ssr_pull, datetime.utcnow().isoformat(),
         player_id, banner_id)
    )
    conn.commit()
    conn.close()

    return jsonify({
        "success":            True,
        "new_pity":           current_pity,
        "guarantee_featured": guarantee_featured,
        "total_pulls":        total_pulls,
        "total_ssr":          total_ssr,
        "total_featured":     total_featured,
        "fifty_wins":         fifty_wins,
        "fifty_losses":       fifty_losses,
    })

@app.route('/history/<player_id>', methods=['GET'])
def get_history(player_id):
    banner_id = request.args.get("banner_id")
    limit     = int(request.args.get("limit", 50))
    conn      = get_db()
    if banner_id:
        rows = conn.execute(
            """SELECT * FROM pull_history WHERE player_id=? AND banner_id=?
               ORDER BY id DESC LIMIT ?""",
            (player_id, banner_id, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM pull_history WHERE player_id=? ORDER BY id DESC LIMIT ?",
            (player_id, limit)
        ).fetchall()
    conn.close()
    return jsonify({"history": [dict(r) for r in rows], "count": len(rows)})

@app.route('/stats/<player_id>', methods=['GET'])
def get_stats(player_id):
    conn      = get_db()
    pity_rows = conn.execute(
        "SELECT * FROM pity_tracker WHERE player_id=?", (player_id,)
    ).fetchall()
    totals = conn.execute(
        """SELECT
             COUNT(*) as total,
             SUM(CASE WHEN rarity='SSR' THEN 1 ELSE 0 END) as ssr,
             SUM(CASE WHEN rarity='SR'  THEN 1 ELSE 0 END) as sr,
             SUM(CASE WHEN rarity='R'   THEN 1 ELSE 0 END) as r,
             SUM(was_soft_pity)   as soft_pity_hits,
             SUM(was_hard_pity)   as hard_pity_hits,
             SUM(is_featured)     as destacados,
             SUM(was_guaranteed)  as guaranteed_hits,
             SUM(won_fifty_fifty) as fifty_fifty_wins
           FROM pull_history WHERE player_id=?""",
        (player_id,)
    ).fetchone()
    conn.close()
    return jsonify({
        "pity_per_banner": [dict(p) for p in pity_rows],
        "totals":          dict(totals) if totals else {}
    })

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5003, debug=True)
