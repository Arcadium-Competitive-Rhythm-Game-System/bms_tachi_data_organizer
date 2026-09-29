import csv

ELO_FLOOR = 100

def sieglinde_to_elo(unified):
    return max(ELO_FLOOR, round(200 + 50 * float(unified)))

def main():
    headers_ec = ["chart_id", "sg_ec", "elo"]
    headers_hc = ["chart_id", "sg_hc", "elo"]
    rows_ec = []
    rows_hc = []

    with open("output/chart_sieglinde_organized.csv", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows_ec.append({
                "chart_id": row["chart_id"],
                "sg_ec": row["sg_ec"],
                "elo": sieglinde_to_elo(row["sg_ec"])
            })

            rows_hc.append({
                "chart_id": row["chart_id"],
                "sg_hc": row["sg_hc"],
                "elo": sieglinde_to_elo(row["sg_hc"])
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