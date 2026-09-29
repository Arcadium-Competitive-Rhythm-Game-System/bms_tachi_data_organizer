import json
import argparse
import csv

def output_sieglinde_csv(songs):
    headers_chart = ["song_id", "chart_id", "md5", "sha256", "artist", "title", "subtitle", "sg_ec", "sg_hc"]
    headers_table = ["chart_id", "table_icon", "table_level"]
    rows_chart = []
    rows_table = []

    with open("data/charts-bms-7k.json", encoding="utf-8-sig") as f:
        data = json.load(f)

        for item in data:
            key_data = item.get("data") or {}
            song = songs[item["songID"]]

            ec = key_data.get("sglEC")
            hc = key_data.get("sglHC")
            if (ec is not None and ec != 0 or hc is not None and hc != 0):
                rows_chart.append({"song_id": item["songID"], 
                                   "chart_id": item["id"], 
                                   "md5": key_data["hashMD5"], 
                                   "sha256": key_data["hashSHA256"], 
                                   "artist": song["artist"],
                                   "title": song["title"],
                                   "subtitle": song.get("subtitle"),
                                   "sg_ec": ec,
                                   "sg_hc": hc
                                   })
            for icon, level in (key_data.get("tableFolders") or {}).items():
                rows_table.append({
                    "chart_id": item["id"],
                    "table_icon": icon,
                    "table_level": level
                })

        with open("output/chart_sieglinde_organized.csv", "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=headers_chart)
            writer.writeheader()
            writer.writerows(rows_chart)

        with open("output/chart_table_connection.csv", "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=headers_table)
            writer.writeheader()
            writer.writerows(rows_table)
def main():
    with open("data/songs-bms.json", encoding="utf-8-sig") as f:
        songs = {song["id"]: song for song in json.load(f)}

    output_sieglinde_csv(songs)

if __name__ == "__main__":
    main()