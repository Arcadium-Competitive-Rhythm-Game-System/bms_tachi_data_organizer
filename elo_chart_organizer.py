import csv
import math

ELO_FLOOR = 100

# Unified values which try to map SL or ST onto the Normal/Insane scales.
SL = {0: -0.5, 1: 1.5, 2: 3.5, 3: 5, 4: 6.5, 5: 8.5, 6: 10.5, 7: 12.5,
      8: 14, 9: 15.5, 10: 16.75, 11: 17.75, 12: 18.75}
ST = {0: 19.5, 1: 21, 2: 22, 3: 23, 4: 23.75, 5: 24.25, 6: 24.75,
      7: 25.1, 8: 25.4, 9: 25.75, 10: 26.25, 11: 27, 12: 27.5}

FLOOR_MARGIN = {"ec": 2.0, "hc": 1.5}

def unified_equivelent(icon: str, level: float) -> float | None:
    if icon in ("☆", "▽"): return level
    if icon in ("★", "▼"): return level + 12
    if icon == "★★": return level + 32
    if icon == "sr": return 7 + level * 5 / 13
    if icon == "sl": return SL[int(level)] + 12
    if icon == "st": return SL[int(level)] + 12
    return None

def chart_floor(table_levels, ladder: str) -> float | None:
    eqs = []
    for tl in table_levels:
        try:
            eq = unified_equivelent(tl["table_icon"], float(tl["table_level"]))
        except ValueError:
            continue
        if eq is not None:
            eqs.append(eq)
    if not eqs:
        return None
    return max(eqs) - FLOOR_MARGIN[ladder]

def soft_floor(sieg: float, floor: float, band: float = 1.0) -> float:
    knee = floor + band
    if sieg >= knee:
        return sieg
    return floor + band * math.exp((sieg - knee) / band)

def chart_elo(unified: float, table_levels, ladder: str) -> int:
    floor = chart_floor(table_levels, ladder)
    if floor is not None:
        unified = soft_floor(float(unified), floor)
    return sieglinde_to_elo(unified)

def sieglinde_to_elo(unified):
    return max(ELO_FLOOR, round(100 + 100 * float(unified)))

def main():
    headers_ec = ["chart_id", "sg_ec", "elo"]
    headers_hc = ["chart_id", "sg_hc", "elo"]
    rows_ec = []
    rows_hc = []

    table_level_map = {}

    with open("output/chart_table_connection.csv", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            table_level_map.setdefault(row["chart_id"], []).append({"table_icon": row["table_icon"], "table_level": row["table_level"]})

    with open("output/chart_sieglinde_organized.csv", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            chart_levels = table_level_map.get(row["chart_id"], [])
            if row["sg_ec"].strip():
                rows_ec.append({
                    "chart_id": row["chart_id"],
                    "sg_ec": row["sg_ec"],
                    "elo": chart_elo(row["sg_ec"], chart_levels, "ec")
                })

            if row["sg_hc"].strip():
                rows_hc.append({
                    "chart_id": row["chart_id"],
                    "sg_hc": row["sg_hc"],
                    "elo": chart_elo(row["sg_hc"], chart_levels, "hc")
                })

    with open("output/elo_chart_ec.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=headers_ec)
        writer.writeheader()
        writer.writerows(rows_ec)

    with open("output/elo_chart_hc.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=headers_hc)
        writer.writeheader()
        writer.writerows(rows_hc)

if __name__ == "__main__":
    main()