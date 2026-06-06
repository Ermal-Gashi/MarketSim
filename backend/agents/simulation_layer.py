import logging
import random
import uuid

logger = logging.getLogger(__name__)

LIKELIHOOD_COUNTS = {"High": 55, "Medium": 40, "Low": 25}

# Lat/lng for major cities across top 30 target markets
CITY_COORDS: dict[str, tuple[float, float]] = {
    # Brazil
    "Sao Paulo": (-23.5505, -46.6333),
    "São Paulo": (-23.5505, -46.6333),
    "Rio de Janeiro": (-22.9068, -43.1729),
    "Belo Horizonte": (-19.9167, -43.9345),
    "Porto Alegre": (-30.0346, -51.2177),
    "Curitiba": (-25.4284, -49.2733),
    "Brasilia": (-15.7942, -47.8825),
    "Brasília": (-15.7942, -47.8825),
    "Fortaleza": (-3.7172, -38.5433),
    "Salvador": (-12.9714, -38.5014),
    "Recife": (-8.0578, -34.8829),
    # Mexico
    "Mexico City": (19.4326, -99.1332),
    "Guadalajara": (20.6597, -103.3496),
    "Monterrey": (25.6866, -100.3161),
    "Puebla": (19.0414, -98.2063),
    "Tijuana": (32.5027, -117.0039),
    # Colombia
    "Bogota": (4.7110, -74.0721),
    "Bogotá": (4.7110, -74.0721),
    "Medellin": (6.2442, -75.5812),
    "Medellín": (6.2442, -75.5812),
    "Cali": (3.4516, -76.5319),
    "Cartagena": (10.3910, -75.4794),
    # Argentina
    "Buenos Aires": (-34.6037, -58.3816),
    "Cordoba": (-31.4201, -64.1888),
    "Córdoba": (-31.4201, -64.1888),
    "Rosario": (-32.9442, -60.6505),
    "Mendoza": (-32.8908, -68.8272),
    # Chile
    "Santiago": (-33.4489, -70.6693),
    "Valparaiso": (-33.0472, -71.6127),
    "Valparaíso": (-33.0472, -71.6127),
    "Concepcion": (-36.8201, -73.0444),
    # Peru
    "Lima": (-12.0464, -77.0428),
    "Arequipa": (-16.4090, -71.5375),
    "Trujillo": (-8.1116, -79.0288),
    # India
    "Mumbai": (19.0760, 72.8777),
    "Delhi": (28.6139, 77.2090),
    "New Delhi": (28.6139, 77.2090),
    "Bangalore": (12.9716, 77.5946),
    "Bengaluru": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Chennai": (13.0827, 80.2707),
    "Pune": (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714),
    "Kolkata": (22.5726, 88.3639),
    # Nigeria
    "Lagos": (6.5244, 3.3792),
    "Abuja": (9.0579, 7.4951),
    "Kano": (12.0022, 8.5920),
    "Ibadan": (7.3775, 3.9470),
    # South Africa
    "Johannesburg": (-26.2041, 28.0473),
    "Cape Town": (-33.9249, 18.4241),
    "Durban": (-29.8587, 31.0218),
    "Pretoria": (-25.7479, 28.2293),
    # Kenya
    "Nairobi": (-1.2921, 36.8219),
    "Mombasa": (-4.0435, 39.6682),
    # Indonesia
    "Jakarta": (-6.2088, 106.8456),
    "Surabaya": (-7.2575, 112.7521),
    "Bandung": (-6.9175, 107.6191),
    "Medan": (3.5952, 98.6722),
    "Bali": (-8.3405, 115.0920),
    # Vietnam
    "Ho Chi Minh City": (10.8231, 106.6297),
    "Hanoi": (21.0285, 105.8542),
    "Da Nang": (16.0544, 108.2022),
    # Thailand
    "Bangkok": (13.7563, 100.5018),
    "Chiang Mai": (18.7883, 98.9853),
    "Phuket": (7.8804, 98.3923),
    # Philippines
    "Manila": (14.5995, 120.9842),
    "Cebu": (10.3157, 123.8854),
    "Davao": (7.1907, 125.4553),
    # Malaysia
    "Kuala Lumpur": (3.1390, 101.6869),
    "Penang": (5.4141, 100.3288),
    "Johor Bahru": (1.4927, 103.7414),
    # Germany
    "Berlin": (52.5200, 13.4050),
    "Munich": (48.1351, 11.5820),
    "Hamburg": (53.5753, 10.0153),
    "Frankfurt": (50.1109, 8.6821),
    "Cologne": (50.9333, 6.9500),
    "Stuttgart": (48.7758, 9.1829),
    # France
    "Paris": (48.8566, 2.3522),
    "Lyon": (45.7640, 4.8357),
    "Marseille": (43.2965, 5.3698),
    "Toulouse": (43.6047, 1.4442),
    "Bordeaux": (44.8378, -0.5792),
    # Spain
    "Madrid": (40.4168, -3.7038),
    "Barcelona": (41.3851, 2.1734),
    "Valencia": (39.4699, -0.3763),
    "Seville": (37.3891, -5.9845),
    "Sevilla": (37.3891, -5.9845),
    # Poland
    "Warsaw": (52.2297, 21.0122),
    "Krakow": (50.0647, 19.9450),
    "Kraków": (50.0647, 19.9450),
    "Wroclaw": (51.1079, 17.0385),
    "Gdansk": (54.3520, 18.6466),
    # Turkey
    "Istanbul": (41.0082, 28.9784),
    "Ankara": (39.9334, 32.8597),
    "Izmir": (38.4237, 27.1428),
    # Egypt
    "Cairo": (30.0444, 31.2357),
    "Alexandria": (31.2001, 29.9187),
    # UAE
    "Dubai": (25.2048, 55.2708),
    "Abu Dhabi": (24.4539, 54.3773),
    # Singapore
    "Singapore": (1.3521, 103.8198),
    # Japan
    "Tokyo": (35.6762, 139.6503),
    "Osaka": (34.6937, 135.5023),
    "Nagoya": (35.1815, 136.9066),
    "Fukuoka": (33.5902, 130.4017),
    # South Korea
    "Seoul": (37.5665, 126.9780),
    "Busan": (35.1796, 129.0756),
    "Incheon": (37.4563, 126.7052),
    # Taiwan
    "Taipei": (25.0330, 121.5654),
    "Kaohsiung": (22.6273, 120.3014),
    # China
    "Shanghai": (31.2304, 121.4737),
    "Beijing": (39.9042, 116.4074),
    "Shenzhen": (22.5431, 114.0579),
    "Guangzhou": (23.1291, 113.2644),
    "Chengdu": (30.5728, 104.0668),
    "Hangzhou": (30.2741, 120.1551),
    # Australia
    "Sydney": (-33.8688, 151.2093),
    "Melbourne": (-37.8136, 144.9631),
    "Brisbane": (-27.4698, 153.0251),
    "Perth": (-31.9505, 115.8605),
    # Canada
    "Toronto": (43.6532, -79.3832),
    "Vancouver": (49.2827, -123.1207),
    "Montreal": (45.5017, -73.5673),
    "Calgary": (51.0447, -114.0719),
    # UK
    "London": (51.5074, -0.1278),
    "Manchester": (53.4808, -2.2426),
    "Birmingham": (52.4862, -1.8904),
    "Edinburgh": (55.9533, -3.1883),
    # USA
    "New York": (40.7128, -74.0060),
    "San Francisco": (37.7749, -122.4194),
    "Los Angeles": (34.0522, -118.2437),
    "Chicago": (41.8781, -87.6298),
    "Austin": (30.2672, -97.7431),
    "Seattle": (47.6062, -122.3321),
    "Boston": (42.3601, -71.0589),
    "Miami": (25.7617, -80.1918),
}

JITTER = 0.3

MANDATORY_INSTANCE_FIELDS = [
    "instance_id", "archetype_name", "archetype_index", "city", "region",
    "lat", "lng", "conversion_outcome", "confidence_score", "pulse_intensity",
    "spawn_delay_ms", "rolled_variables", "tipping_high_met", "tipping_low_met",
    "display_name", "job_title", "archetype_label", "avatar_style",
    "outcome_reason", "deciding_factor",
]

VALID_OUTCOMES = {"converted", "evaluating", "abandoned"}


_MALE_NAMES = {
    "rodrigo", "marcos", "rafael", "carlos", "bruno", "joao", "joão",
    "pedro", "lucas", "miguel", "gabriel", "gustavo", "felipe",
}
_FEMALE_NAMES = {
    "fernanda", "leticia", "letícia", "camila", "ana", "maria",
    "beatriz", "juliana", "isabela", "larissa", "mariana", "patricia",
    "patrícia", "sandra",
}


def _infer_gender(first_name: str) -> str:
    """Return 'female' or 'male' based on first name lookup."""
    first = first_name.lower()
    if first in _FEMALE_NAMES:
        return "female"
    return "male"  # default to male if not found in either list


def _infer_avatar_style(job_title: str, first_name: str) -> str:
    title = job_title.upper()
    suffix = f"-{_infer_gender(first_name)}"
    if any(kw in title for kw in ("CTO", "CEO", "DIRECTOR", "VP", "CHIEF")):
        return f"executive{suffix}"
    if any(kw in title for kw in ("COACH", "COORDINATOR", "MANAGER")):
        return f"professional{suffix}"
    if "FOUNDER" in title:
        return f"founder{suffix}"
    return f"professional{suffix}"


def _get_coords(city: str) -> tuple[float, float]:
    base = CITY_COORDS.get(city, (0.0, 0.0))
    lat = base[0] + random.uniform(-JITTER, JITTER)
    lng = base[1] + random.uniform(-JITTER, JITTER)
    return round(lat, 6), round(lng, 6)


def _build_outcome_reason(rolled_variables: dict[str, bool], outcome: str) -> str:
    true_vars = [k for k, v in rolled_variables.items() if v]
    false_vars = [k for k, v in rolled_variables.items() if not v]
    if outcome == "converted" and true_vars:
        factors = " and ".join(true_vars[:2])
        return f"Converted because {factors} aligned with buyer expectations."
    if outcome == "abandoned" and false_vars:
        factors = " and ".join(false_vars[:2])
        return f"Abandoned because {factors} was not satisfied during evaluation."
    if true_vars:
        return f"Still evaluating — {true_vars[0]} is a positive signal but decision pending."
    return "Outcome undetermined — insufficient signals from evaluation period."


def _pick_deciding_factor(rolled_variables: dict[str, bool], outcome: str) -> str:
    if outcome == "converted":
        candidates = [k for k, v in rolled_variables.items() if v]
    elif outcome == "abandoned":
        candidates = [k for k, v in rolled_variables.items() if not v]
    else:
        candidates = list(rolled_variables.keys())
    if candidates:
        return candidates[0]
    return list(rolled_variables.keys())[0] if rolled_variables else "unknown"


def _build_instances(personas: list[dict], regional_weights: dict[str, int]) -> list[dict]:
    instances: list[dict] = []
    regions = list(regional_weights.keys())
    region_w = list(regional_weights.values())

    for arch_idx, persona in enumerate(personas):
        likelihood = persona.get("likelihood_to_convert", "Medium")
        count = LIKELIHOOD_COUNTS.get(likelihood, 40)
        vp = persona.get("variance_profile", {})
        key_vars: list[str] = vp.get("key_variables", [])
        archetype_name = persona.get("archetype_name", f"Archetype {arch_idx}")
        base_city = persona.get("city", "Unknown")
        persona_name = persona.get("name", "Unknown")
        persona_age = persona.get("age", 0)
        job_title = persona.get("job_title", "Unknown")

        for _ in range(count):
            rolled: dict[str, bool] = {var: (random.random() < 0.6) for var in key_vars}

            true_count = sum(1 for v in rolled.values() if v)
            false_count = len(rolled) - true_count
            tipping_high_met = true_count > false_count
            tipping_low_met = false_count > true_count

            if tipping_high_met and not tipping_low_met:
                outcome = "converted"
                confidence = random.randint(65, 95)
                pulse = random.randint(70, 100)
            elif tipping_low_met and not tipping_high_met:
                outcome = "abandoned"
                confidence = random.randint(5, 35)
                pulse = random.randint(5, 34)
            else:
                outcome = "evaluating"
                confidence = random.randint(35, 65)
                pulse = random.randint(35, 69)

            spawn_delay = (100 - confidence) * 80
            # Bug 1 fix: city is derived from the picked region so they always match.
            # Agent 6 regional_weights keys are city/area names (e.g. "São Paulo").
            region = random.choices(regions, weights=region_w, k=1)[0]
            city = region
            lat, lng = _get_coords(city)

            first_name = persona_name.split()[0] if persona_name else "Unknown"
            # Pre-compute display_name so we can pass first_name to _infer_avatar_style
            display_name = f"{first_name}, {persona_age}"

            instances.append({
                "instance_id": str(uuid.uuid4()),
                "archetype_name": archetype_name,
                "archetype_index": arch_idx,
                "city": city,
                "region": region,
                "lat": lat,
                "lng": lng,
                "conversion_outcome": outcome,
                "confidence_score": confidence,
                "pulse_intensity": pulse,
                "spawn_delay_ms": spawn_delay,
                "rolled_variables": rolled,
                "tipping_high_met": tipping_high_met,
                "tipping_low_met": tipping_low_met,
                "display_name": display_name,
                "job_title": job_title,
                "archetype_label": archetype_name,
                # Bug 2 fix: gender inferred from first_name, not random
                "avatar_style": _infer_avatar_style(job_title, first_name),
                "outcome_reason": _build_outcome_reason(rolled, outcome),
                "deciding_factor": _pick_deciding_factor(rolled, outcome),
            })

    return instances


def _build_summary(instances: list[dict]) -> dict:
    total = len(instances)
    converted = sum(1 for i in instances if i["conversion_outcome"] == "converted")
    evaluating = sum(1 for i in instances if i["conversion_outcome"] == "evaluating")
    abandoned = sum(1 for i in instances if i["conversion_outcome"] == "abandoned")
    conversion_rate = round(converted / total * 100, 1) if total > 0 else 0.0

    by_region: dict[str, dict] = {}
    for inst in instances:
        r = inst["region"]
        if r not in by_region:
            by_region[r] = {"total": 0, "converted": 0}
        by_region[r]["total"] += 1
        if inst["conversion_outcome"] == "converted":
            by_region[r]["converted"] += 1
    for stats in by_region.values():
        stats["rate"] = round(stats["converted"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0.0

    by_archetype: dict[str, dict] = {}
    for inst in instances:
        name = inst["archetype_name"]
        if name not in by_archetype:
            by_archetype[name] = {"total": 0, "converted": 0}
        by_archetype[name]["total"] += 1
        if inst["conversion_outcome"] == "converted":
            by_archetype[name]["converted"] += 1
    for stats in by_archetype.values():
        stats["rate"] = round(stats["converted"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0.0

    return {
        "total": total,
        "converted": converted,
        "evaluating": evaluating,
        "abandoned": abandoned,
        "conversion_rate": conversion_rate,
        "by_region": by_region,
        "by_archetype": by_archetype,
    }


def _validate(instances: list[dict], summary: dict) -> None:
    if len(instances) != 200:
        raise ValueError(f"Expected exactly 200 instances, got {len(instances)}")

    for i, inst in enumerate(instances):
        missing = [f for f in MANDATORY_INSTANCE_FIELDS if f not in inst]
        if missing:
            raise ValueError(f"Instance {i} missing mandatory fields: {missing}")
        if inst["conversion_outcome"] not in VALID_OUTCOMES:
            raise ValueError(f"Instance {i} has invalid conversion_outcome: {inst['conversion_outcome']}")

    total_check = summary["converted"] + summary["evaluating"] + summary["abandoned"]
    if total_check != summary["total"]:
        raise ValueError(
            f"Summary totals mismatch: {summary['converted']}+{summary['evaluating']}+"
            f"{summary['abandoned']}={total_check} != total={summary['total']}"
        )


def run(inputs: dict) -> dict:
    agent4_output = inputs["agent4_output"]
    agent6_output = inputs["agent6_output"]

    personas = agent4_output.get("personas", [])
    regional_weights: dict[str, int] = agent6_output.get("regional_weights", {})

    if not personas:
        raise ValueError("agent4_output must contain a non-empty 'personas' list")
    if not regional_weights:
        raise ValueError("agent6_output must contain a non-empty 'regional_weights' dict")

    instances = _build_instances(personas, regional_weights)
    summary = _build_summary(instances)
    _validate(instances, summary)

    logger.info(
        "Simulation Layer: %d instances — converted=%d evaluating=%d abandoned=%d rate=%.1f%%",
        summary["total"], summary["converted"], summary["evaluating"],
        summary["abandoned"], summary["conversion_rate"],
    )
    return {"instances": instances, "summary": summary}
