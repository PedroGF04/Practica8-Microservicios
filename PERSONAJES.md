# 🎨 Cómo personalizar personajes e imágenes

## Agregar imágenes de personajes

### Paso 1 — Prepara las imágenes
Guarda tus imágenes en la carpeta `frontend/images/`.
El nombre del archivo debe coincidir exactamente con el `id` del personaje.

```
frontend/images/
├── valerian.png        ← personaje con id "valerian"
├── sylvara.png         ← personaje con id "sylvara"
├── seraphiel.png       ← personaje con id "seraphiel"
├── malphas.png         ← personaje con id "malphas"
├── astraea.png         ← personaje con id "astraea"
└── ...
```

**Tamaño recomendado:** 256×256 px o 512×512 px, formato PNG o JPG.
Si la imagen no existe, el sistema mostrará automáticamente un emoji de respaldo.

---

## Agregar o cambiar personajes

Abre `banner-service/src/app.py` y edita el diccionario `BANNERS`.

### Estructura de un personaje
```python
{
    "id": "nombre_sin_espacios",   # Debe ser único, sin espacios ni tildes
    "name": "Nombre Visible",       # Nombre que verá el jugador
    "element": "Fuego",             # Elemento del personaje
    "color": "#ff6b35",             # Color representativo (hex)
}
```

### Elementos disponibles
`Fuego`, `Oscuridad`, `Viento`, `Metal`, `Hielo`, `Tierra`, `Luz`, `Rayo`, `Estelar`

(Puedes inventar nuevos elementos, el frontend los mostrará sin emoji)

---

## Agregar un nuevo banner limitado

Copia y pega esta plantilla en el diccionario `BANNERS` de `banner-service/src/app.py`:

```python
"mi_banner": {
    "id": "mi_banner",
    "name": "Nombre del Banner",
    "subtitle": "Banner limitado · Personaje destacado: NombreSSR",
    "type": "limited",               # "limited" o "permanent"
    "cost_tickets": 1,
    "cost_coins": 160,
    "pity_limit": 80,                # Hard pity: pulls garantizado SSR
    "soft_pity_start": 64,           # Soft pity: comienza aumento
    "featured_character": "id_del_ssr_destacado",
    "base_rates": {"SSR": 0.006, "SR": 0.051, "R": 0.943},
    "characters": {
        "SSR": [
            {"id": "mi_ssr",   "name": "Mi SSR",   "element": "Fuego", "color": "#ff6b35"},
        ],
        "SR": [
            {"id": "mi_sr_1",  "name": "Mi SR 1",  "element": "Viento","color": "#1abc9c"},
            {"id": "mi_sr_2",  "name": "Mi SR 2",  "element": "Hielo", "color": "#74b9ff"},
        ],
        "R": [
            {"id": "recruit_a","name": "Recluta A", "element": "Fuego", "color": "#d63031"},
            {"id": "recruit_b","name": "Recluta B", "element": "Tierra","color": "#6c5ce7"},
        ]
    }
},
```

---

## Aplicar los cambios

Después de cualquier modificación, reconstruye los contenedores:

```bash
docker compose up --build
```

Los cambios estarán disponibles en http://localhost:8081

---

## IDs de personajes actuales

| ID              | Nombre              | Banner           |
|-----------------|---------------------|-----------------|
| `valerian`      | Valerian el Eterno  | Permanente, Aurora, Tormenta |
| `sylvara`       | Sylvara Oscura      | Permanente, Aurora |
| `crestfall`     | Crestfall           | Permanente, Abismo, Tormenta |
| `ironveil`      | Ironveil            | Permanente, Abismo |
| `seraphiel`     | Seraphiel           | Destello de Aurora (destacado) |
| `malphas`       | Malphas             | Canción del Abismo (destacado) |
| `astraea`       | Astraea             | Tormenta Estelar (destacado) |
| `ember`         | Ember               | Permanente, Aurora |
| `frostbite`     | Frostbite           | Permanente, Tormenta |
| `galeforce`     | Galeforce           | Permanente, Abismo |
| `thornwick`     | Thornwick           | Permanente, Abismo |
| `solenne`       | Solenne             | Permanente, Aurora |
| `krauss`        | Krauss              | Permanente, Abismo |
| `dawn_knight`   | Caballero del Alba  | Aurora, Tormenta |
| `starweave`     | Starweave           | Aurora, Tormenta |
| `voidwalker`    | Caminante del Vacío | Abismo |
| `comet`         | Comet               | Tormenta |
| `recruit_a`-`g` | Reclutas            | Varios |
