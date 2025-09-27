"""Deterministic sample data generator for the Avaire MVP.

Running this script produces:
- catalog_seed.json  (120 outfits)
- users_seed.json
- style_dna_seed.json
- tryon_history_seed.json
- feedback_seed.json
- init.sql (schema + inserts)

The script intentionally avoids external dependencies so it can run in
vanilla Python 3.9+ environments.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).parent
OUTPUTS = {
    "catalog": BASE_DIR / "catalog_seed.json",
    "users": BASE_DIR / "users_seed.json",
    "style_dna": BASE_DIR / "style_dna_seed.json",
    "tryon": BASE_DIR / "tryon_history_seed.json",
    "feedback": BASE_DIR / "feedback_seed.json",
    "sql": BASE_DIR / "init.sql",
}

CATALOG_PROFILES = [
    {"category": "indian_wear", "subcategory": "saree", "label": "Saree"},
    {"category": "indian_wear", "subcategory": "lehenga", "label": "Lehenga"},
    {"category": "indian_wear", "subcategory": "kurta", "label": "Kurta"},
    {"category": "western_wear", "subcategory": "dress", "label": "Dress"},
    {"category": "western_wear", "subcategory": "top", "label": "Top"},
    {"category": "fusion", "subcategory": "coord_set", "label": "Fusion Co-ord"},
]

OCCASIONS = [
    "casual",
    "formal",
    "party",
    "wedding",
    "festive",
    "date_night",
    "brunch",
    "college",
]

COLORS = [
    "ivory",
    "blush",
    "coral",
    "mint",
    "navy",
    "maroon",
    "black",
    "champagne",
    "emerald",
    "turmeric",
    "pearl",
    "teal",
]

SIZES = ["XS", "S", "M", "L", "XL", "XXL"]
BRANDS = [
    "Avaire Studio",
    "Desi Threads",
    "Urban Nari",
    "StreetLuxe",
    "Festive Muse",
    "Campus Chic",
    "Noir Alley",
]

MATERIALS = ["cotton", "linen", "silk", "georgette", "chiffon", "denim", "velvet"]
FIT_TYPES = ["regular", "slim", "relaxed", "draped", "structured"]
SLEEVE_LENGTHS = ["sleeveless", "short", "three_quarter", "full"]
NECKLINES = ["round", "v_neck", "boat", "square", "halter", "collared"]
STYLE_TAGS = [
    "minimal",
    "boho",
    "power",
    "street",
    "festive",
    "classic",
    "athleisure",
    "sustainable",
]

SKIN_TONES = ["fair", "light", "medium", "olive", "brown", "dark"]
BODY_TYPES = ["pear", "apple", "hourglass", "rectangle", "inverted_triangle"]
LIFESTYLES = ["student", "working", "creator", "entrepreneur"]
AGE_GROUPS = ["18-22", "23-27", "28-35"]


@dataclass
class Outfit:
    id: int
    name: str
    description: str
    brand: str
    category: str
    subcategory: str
    occasion: str
    price: float
    currency: str
    primary_image_url: str
    additional_images: List[str]
    colors: List[str]
    sizes: List[str]
    material: str
    fit_type: str
    sleeve_length: str
    neckline: str
    tags: List[str]
    stock_quantity: int
    is_available: bool
    created_at: str


@dataclass
class UserSeed:
    id: int
    email: str
    first_name: str
    last_name: str
    phone_number: str
    created_at: str
    is_active: bool = True


def chunked(iterable, size):
    for idx in range(0, len(iterable), size):
        yield iterable[idx : idx + size]


def build_catalog(num_items: int = 120) -> List[Dict[str, object]]:
    items: List[Dict[str, object]] = []
    occasion_idx = 0

    for outfit_id in range(1, num_items + 1):
        profile = CATALOG_PROFILES[(outfit_id - 1) % len(CATALOG_PROFILES)]
        category = profile["category"]
        sub_key = profile["subcategory"]
        sub_label = profile["label"]
        occasion = OCCASIONS[occasion_idx % len(OCCASIONS)]
        occasion_idx += 1

        name = f"{sub_label} {outfit_id:03d}"
        price = 1499 + (outfit_id % 12) * 150
        brand = BRANDS[outfit_id % len(BRANDS)]

        colors = [COLORS[(outfit_id + shift) % len(COLORS)] for shift in range(2)]
        sizes = SIZES[: 4 + outfit_id % 3]
        tags = [STYLE_TAGS[outfit_id % len(STYLE_TAGS)], STYLE_TAGS[(outfit_id + 3) % len(STYLE_TAGS)]]

        outfit = Outfit(
            id=outfit_id,
            name=name,
            description=f"Curated {sub_label.lower()} designed for {occasion.replace('_', ' ')} settings.",
            brand=brand,
            category=category,
            subcategory=sub_key,
            occasion=occasion,
            price=float(price),
            currency="INR",
            primary_image_url=f"storage/catalog/outfit_{outfit_id:03d}.jpg",
            additional_images=[
                f"storage/catalog/outfit_{outfit_id:03d}_alt1.jpg",
                f"storage/catalog/outfit_{outfit_id:03d}_alt2.jpg",
            ],
            colors=colors,
            sizes=sizes,
            material=MATERIALS[outfit_id % len(MATERIALS)],
            fit_type=FIT_TYPES[outfit_id % len(FIT_TYPES)],
            sleeve_length=SLEEVE_LENGTHS[outfit_id % len(SLEEVE_LENGTHS)],
            neckline=NECKLINES[outfit_id % len(NECKLINES)],
            tags=tags,
            stock_quantity=25 + (outfit_id % 10) * 5,
            is_available=True,
            created_at=datetime(2024, 10, 15, tzinfo=timezone.utc).isoformat(),
        )
        items.append(asdict(outfit))

    return items


def build_users(num_users: int = 12) -> List[Dict[str, object]]:
    users: List[Dict[str, object]] = []
    base = datetime(2024, 11, 1)
    for idx in range(1, num_users + 1):
        user = UserSeed(
            id=idx,
            email=f"user{idx:02d}@avaire.in",
            first_name=f"User{idx:02d}",
            last_name="Test",
            phone_number=f"+91-90000{idx:04d}",
            created_at=(base + timedelta(days=idx)).isoformat(),
        )
        users.append(asdict(user))
    return users


def build_style_dna(users: List[Dict[str, object]]) -> List[Dict[str, object]]:
    profiles = []
    for user in users:
        uid = user["id"]
        profile = {
            "user_id": uid,
            "skin_tone": SKIN_TONES[uid % len(SKIN_TONES)],
            "body_type": BODY_TYPES[uid % len(BODY_TYPES)],
            "height_cm": 158 + uid % 12,
            "weight_kg": 50 + uid % 15,
            "bust_size": SIZES[min(4, uid % len(SIZES))],
            "waist_size": SIZES[min(4, (uid + 1) % len(SIZES))],
            "hip_size": SIZES[min(5, (uid + 2) % len(SIZES))],
            "preferred_colors": [COLORS[(uid + shift) % len(COLORS)] for shift in range(3)],
            "avoided_colors": [COLORS[(uid + 5) % len(COLORS)]],
            "preferred_styles": [STYLE_TAGS[(uid + shift) % len(STYLE_TAGS)] for shift in range(2)],
            "preferred_occasions": [OCCASIONS[(uid + shift) % len(OCCASIONS)] for shift in range(2)],
            "budget_range": {"min": 1500 + (uid % 3) * 500, "max": 4500 + (uid % 4) * 500},
            "lifestyle": LIFESTYLES[uid % len(LIFESTYLES)],
            "age_group": AGE_GROUPS[uid % len(AGE_GROUPS)],
        }
        profiles.append(profile)
    return profiles


def build_tryon_sessions(users: List[Dict[str, object]]) -> List[Dict[str, object]]:
    sessions = []
    base_time = datetime(2025, 1, 5, 10, 0)
    for idx, user in enumerate(users, start=1):
        for offset in range(2):
            session_id = f"TRYON-{user['id']:02d}-{offset+1:02d}"
            outfit_id = (idx * (offset + 3)) % 120 or 1
            session = {
                "session_id": session_id,
                "user_id": user["id"],
                "outfit_id": outfit_id,
                "user_image_url": f"storage/uploads/user_{user['id']:02d}_original.jpg",
                "result_image_url": f"storage/results/{session_id}.jpg",
                "processing_time_seconds": 7.5 + (offset * 1.2),
                "model_version": "v0.1.0",
                "quality_score": round(0.75 + (offset * 0.05), 2),
                "created_at": (base_time + timedelta(days=idx, minutes=offset * 15)).isoformat(),
            }
            sessions.append(session)
    return sessions


def build_feedback(tryon_sessions: List[Dict[str, object]]) -> List[Dict[str, object]]:
    feedback = []
    for record in tryon_sessions:
        feedback.append(
            {
                "session_id": record["session_id"],
                "user_id": record["user_id"],
                "outfit_id": record["outfit_id"],
                "user_rating": 4 if record["quality_score"] >= 0.8 else 3,
                "user_feedback": "Loved the drape" if record["quality_score"] >= 0.8 else "Looks good",
                "was_shared": record["quality_score"] >= 0.8,
                "was_purchased_after": record["quality_score"] >= 0.82,
            }
        )
    return feedback


def write_json(path: Path, data: List[Dict[str, object]]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_sql(
    path: Path,
    catalog: List[Dict[str, object]],
    users: List[Dict[str, object]],
    style_dna: List[Dict[str, object]],
    tryon_sessions: List[Dict[str, object]],
    feedback: List[Dict[str, object]],
) -> None:
    statements: List[str] = []

    statements.append("BEGIN;")
    statements.append(
        "CREATE TABLE IF NOT EXISTS users (\n"
        "    id SERIAL PRIMARY KEY,\n"
        "    email TEXT UNIQUE NOT NULL,\n"
        "    hashed_password TEXT,\n"
        "    first_name TEXT NOT NULL,\n"
        "    last_name TEXT,\n"
        "    phone_number TEXT,\n"
        "    is_active BOOLEAN DEFAULT TRUE,\n"
        "    is_verified BOOLEAN DEFAULT FALSE,\n"
        "    created_at TIMESTAMPTZ DEFAULT NOW(),\n"
        "    updated_at TIMESTAMPTZ DEFAULT NOW()\n"
        ");"
    )

    statements.append(
        "CREATE TABLE IF NOT EXISTS style_dna (\n"
        "    id SERIAL PRIMARY KEY,\n"
        "    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,\n"
        "    skin_tone TEXT NOT NULL,\n"
        "    body_type TEXT NOT NULL,\n"
        "    height_cm NUMERIC,\n"
        "    weight_kg NUMERIC,\n"
        "    bust_size TEXT,\n"
        "    waist_size TEXT,\n"
        "    hip_size TEXT,\n"
        "    preferred_colors JSONB,\n"
        "    avoided_colors JSONB,\n"
        "    preferred_styles JSONB,\n"
        "    preferred_occasions JSONB,\n"
        "    budget_range JSONB,\n"
        "    lifestyle TEXT,\n"
        "    age_group TEXT,\n"
        "    created_at TIMESTAMPTZ DEFAULT NOW(),\n"
        "    updated_at TIMESTAMPTZ DEFAULT NOW()\n"
        ");"
    )

    statements.append(
        "CREATE TABLE IF NOT EXISTS outfits (\n"
        "    id SERIAL PRIMARY KEY,\n"
        "    name TEXT NOT NULL,\n"
        "    description TEXT,\n"
        "    brand TEXT,\n"
        "    category TEXT NOT NULL,\n"
        "    subcategory TEXT NOT NULL,\n"
        "    occasion TEXT NOT NULL,\n"
        "    price NUMERIC NOT NULL,\n"
        "    discounted_price NUMERIC,\n"
        "    currency TEXT DEFAULT 'INR',\n"
        "    primary_image_url TEXT NOT NULL,\n"
        "    additional_images JSONB,\n"
        "    colors JSONB,\n"
        "    sizes JSONB,\n"
        "    material TEXT,\n"
        "    fit_type TEXT,\n"
        "    sleeve_length TEXT,\n"
        "    neckline TEXT,\n"
        "    tags JSONB,\n"
        "    stock_quantity INTEGER DEFAULT 0,\n"
        "    is_available BOOLEAN DEFAULT TRUE,\n"
        "    created_at TIMESTAMPTZ DEFAULT NOW(),\n"
        "    updated_at TIMESTAMPTZ DEFAULT NOW()\n"
        ");"
    )

    statements.append(
        "CREATE TABLE IF NOT EXISTS tryon_history (\n"
        "    id SERIAL PRIMARY KEY,\n"
        "    session_id TEXT UNIQUE NOT NULL,\n"
        "    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,\n"
        "    outfit_id INTEGER REFERENCES outfits(id) ON DELETE SET NULL,\n"
        "    user_image_url TEXT NOT NULL,\n"
        "    result_image_url TEXT NOT NULL,\n"
        "    processing_time_seconds NUMERIC,\n"
        "    model_version TEXT,\n"
        "    quality_score NUMERIC,\n"
        "    user_rating INTEGER,\n"
        "    user_feedback TEXT,\n"
        "    was_shared BOOLEAN DEFAULT FALSE,\n"
        "    was_purchased_after BOOLEAN DEFAULT FALSE,\n"
        "    created_at TIMESTAMPTZ DEFAULT NOW()\n"
        ");"
    )

    statements.append(
        "DELETE FROM tryon_history;"
        "DELETE FROM style_dna;"
        "DELETE FROM outfits;"
        "DELETE FROM users;"
    )

    # Insert users
    for chunk in chunked(users, 50):
        values = ",".join(
            "(" "{id}," "'{email}'," "NULL," "'{first_name}'," "'{last_name}'," "'{phone_number}'," "TRUE," "FALSE," "'{created_at}'," "'{created_at}'" ")".format(**user)
            for user in chunk
        )
        statements.append(
            "INSERT INTO users (id, email, hashed_password, first_name, last_name, phone_number, is_active, is_verified, created_at, updated_at) VALUES "
            f"{values} ON CONFLICT (id) DO UPDATE SET email = EXCLUDED.email;"
        )

    # Insert outfits via JSON
    statements.append("\nWITH catalog_data AS (SELECT jsonb_array_elements(%s::jsonb) AS item)" % json.dumps(catalog))
    statements.append(
        "INSERT INTO outfits (id, name, description, brand, category, subcategory, occasion, price, currency, primary_image_url, additional_images, colors, sizes, material, fit_type, sleeve_length, neckline, tags, stock_quantity, is_available, created_at)\n"
        "SELECT\n"
        "    (item->>'id')::INTEGER,\n"
        "    item->>'name',\n"
        "    item->>'description',\n"
        "    item->>'brand',\n"
        "    item->>'category',\n"
        "    item->>'subcategory',\n"
        "    item->>'occasion',\n"
        "    (item->>'price')::NUMERIC,\n"
        "    item->>'currency',\n"
        "    item->>'primary_image_url',\n"
        "    item->'additional_images',\n"
        "    item->'colors',\n"
        "    item->'sizes',\n"
        "    item->>'material',\n"
        "    item->>'fit_type',\n"
        "    item->>'sleeve_length',\n"
        "    item->>'neckline',\n"
        "    item->'tags',\n"
        "    (item->>'stock_quantity')::INTEGER,\n"
        "    (item->>'is_available')::BOOLEAN,\n"
        "    (item->>'created_at')::TIMESTAMPTZ\n"
        "FROM catalog_data\n"
        "ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;"
    )

    # Insert Style DNA
    for profile in style_dna:
        statements.append(
            "INSERT INTO style_dna (user_id, skin_tone, body_type, height_cm, weight_kg, bust_size, waist_size, hip_size, preferred_colors, avoided_colors, preferred_styles, preferred_occasions, budget_range, lifestyle, age_group) VALUES ("
            f"{profile['user_id']}, "
            f"'{profile['skin_tone']}', "
            f"'{profile['body_type']}', "
            f"{profile['height_cm']}, "
            f"{profile['weight_kg']}, "
            f"'{profile['bust_size']}', "
            f"'{profile['waist_size']}', "
            f"'{profile['hip_size']}', "
            f"'{json.dumps(profile['preferred_colors'])}', "
            f"'{json.dumps(profile['avoided_colors'])}', "
            f"'{json.dumps(profile['preferred_styles'])}', "
            f"'{json.dumps(profile['preferred_occasions'])}', "
            f"'{json.dumps(profile['budget_range'])}', "
            f"'{profile['lifestyle']}', "
            f"'{profile['age_group']}'"
            ") ON CONFLICT DO NOTHING;"
        )

    # Insert try-on sessions and feedback
    for record in tryon_sessions:
        statements.append(
            "INSERT INTO tryon_history (session_id, user_id, outfit_id, user_image_url, result_image_url, processing_time_seconds, model_version, quality_score, created_at) VALUES ("
            f"'{record['session_id']}', {record['user_id']}, {record['outfit_id']}, '{record['user_image_url']}', '{record['result_image_url']}', {record['processing_time_seconds']}, '{record['model_version']}', {record['quality_score']}, '{record['created_at']}'"
            ") ON CONFLICT (session_id) DO NOTHING;"
        )

    statements.append("COMMIT;")

    path.write_text("\n".join(statements) + "\n", encoding="utf-8")


def main() -> None:
    catalog = build_catalog()
    users = build_users()
    style_dna = build_style_dna(users)
    tryon_sessions = build_tryon_sessions(users)
    feedback = build_feedback(tryon_sessions)

    write_json(OUTPUTS["catalog"], catalog)
    write_json(OUTPUTS["users"], users)
    write_json(OUTPUTS["style_dna"], style_dna)
    write_json(OUTPUTS["tryon"], tryon_sessions)
    write_json(OUTPUTS["feedback"], feedback)
    write_sql(OUTPUTS["sql"], catalog, users, style_dna, tryon_sessions, feedback)

    print("Sample data generated successfully.")


if __name__ == "__main__":
    main()
