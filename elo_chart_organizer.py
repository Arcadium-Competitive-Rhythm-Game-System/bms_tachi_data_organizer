import csv
import math
import statistics

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

def adjusted_sieglinde(unified, table_levels, ladder) -> float:
    value = float(unified)
    floor = chart_floor(table_levels, ladder)
    return soft_floor(value, floor) if floor is not None else value

def sieglinde_to_elo(unified):
    return max(ELO_FLOOR, round(100 + 100 * float(unified)))

def main():
    headers_ec = ["chart_id", "sg_ec", "elo"]
    headers_hc = ["chart_id", "sg_hc", "elo"]
    rows_ec = []
    rows_hc = []
    gaps = {}

    table_level_map = {}

    # Creates a dictionary linking a chart ID to the various tables and levels it is a part of
    with open("output/chart_table_connection.csv", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            table_level_map.setdefault(row["chart_id"], []).append({"table_icon": row["table_icon"], "table_level": row["table_level"]})

    # This is where all the ELO calculations happen.
    with open("output/chart_sieglinde_organized.csv", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        rows = list(reader)

        # Builds a margin dictionary. This is for determining the median ec -> hc difference gap in a given ec sieglinde
        for row in rows:
            if row["sg_ec"].strip() == "" or row["sg_hc"].strip() == "":
                continue

            chart_levels = table_level_map.get(row["chart_id"], [])
            ec = adjusted_sieglinde(row["sg_ec"], chart_levels, "ec")
            hc = adjusted_sieglinde(row["sg_hc"], chart_levels, "hc")

            if hc >= ec:
                bucket = math.floor(ec)
                gaps.setdefault(bucket, []).append(hc - ec)

        margins = {b: statistics.median(g) for b, g in gaps.items()}
        fallback = statistics.median([x for g in gaps.values() for x in g])
        fraction = 1

        # Calculates ELO. We take into account a few things here.
        # If Easy Clear sieglinde is 2 or more levels below the "unified" level of its table, we adjust a soft floor and take the ELO to the limit of that floor.
        # We take Hard Clear sieglinde to a soft floor + margin of the Easy Clear sieglinde (adjusted by the band of 0.5), enforcing that hard clears are, on average, harder than easy clears
        # This means that charts that have a much easier Hard Clear rating than their Easy Clear will have their Hard Clear rating adjusted
        for row in rows:
            chart_levels = table_level_map.get(row["chart_id"], [])
            has_ec = bool(row["sg_ec"].strip())
            has_hc = bool(row["sg_hc"].strip())

            sg_ec = adjusted_sieglinde(row["sg_ec"], chart_levels, "ec") if has_ec else None
            sg_hc = adjusted_sieglinde(row["sg_hc"], chart_levels, "hc") if has_hc else None

            if sg_ec is not None and sg_hc is not None:
                bucket = math.floor(sg_ec)
                sg_hc = soft_floor(sg_hc, sg_ec + margins.get(bucket, fallback) * fraction, 0.5)
            
            if row["sg_ec"].strip():
                rows_ec.append({
                    "chart_id": row["chart_id"],
                    "sg_ec": sg_ec,
                    "elo": chart_elo(sg_ec, chart_levels, "ec")
                })

            if row["sg_hc"].strip():
                rows_hc.append({
                    "chart_id": row["chart_id"],
                    "sg_hc": sg_hc,
                    "elo": chart_elo(sg_hc, chart_levels, "hc")
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