#!/usr/bin/env python3
"""Download public Scento CC BY 4.0 dataset and FragDB public sample files."""
from pathlib import Path
from urllib.request import urlopen
BASE=Path(__file__).resolve().parents[1]
FILES={
 "scento/perfumes.csv":"https://raw.githubusercontent.com/Scento-com/perfume-dataset/main/perfumes.csv",
 "scento/houses.csv":"https://raw.githubusercontent.com/Scento-com/perfume-dataset/main/houses.csv",
 "scento/materials.csv":"https://raw.githubusercontent.com/Scento-com/perfume-dataset/main/materials.csv",
 "fragdb/fragrances.csv":"https://raw.githubusercontent.com/FragDB/fragrance-database/main/samples/fragrances.csv",
 "fragdb/brands.csv":"https://raw.githubusercontent.com/FragDB/fragrance-database/main/samples/brands.csv",
 "fragdb/notes.csv":"https://raw.githubusercontent.com/FragDB/fragrance-database/main/samples/notes.csv",
 "fragdb/accords.csv":"https://raw.githubusercontent.com/FragDB/fragrance-database/main/samples/accords.csv",
 "fragdb/translations.csv":"https://raw.githubusercontent.com/FragDB/fragrance-database/main/samples/translations.csv",
}
for rel,url in FILES.items():
 p=BASE/"sources"/rel;p.parent.mkdir(parents=True,exist_ok=True)
 try:
  with urlopen(url,timeout=45) as r: p.write_bytes(r.read())
  print("OK",rel,p.stat().st_size)
 except Exception as e: print("SKIP",rel,e)
