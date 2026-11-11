#!/usr/bin/env python3
"""Merge public Scento data, licensed FragDB files/samples, and fragscrape JSON exports."""
import csv, json, re, sys
from pathlib import Path
from collections import defaultdict

BASE=Path(__file__).resolve().parents[1]
SRC=BASE/"sources"
OUT=BASE
def read_csv(path, delimiter=","):
    if not path.exists(): return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=delimiter))
def split(v):
    if isinstance(v,list): return [str(x).strip() for x in v if str(x).strip()]
    if not v: return []
    s=str(v).strip()
    if s.startswith("["):
        try:
            x=json.loads(s)
            if isinstance(x,list): return [str(a).strip() for a in x if str(a).strip()]
        except Exception: pass
    return [x.strip() for x in re.split(r"\s*;\s*|\s*\|\s*",s) if x.strip()]
def gender(v):
    s=str(v or "").lower()
    if any(x in s for x in ("unisex","women and men","both","shared","gender_for_women_and_men")): return "unisex"
    if any(x in s for x in ("women","female","femme","donna","gender_for_women")): return "women"
    if any(x in s for x in ("men","male","homme","uomo","gender_for_men")): return "men"
    return ""
def norm_name(s): return re.sub(r"[^a-z0-9]+","",str(s or "").lower())
def main():
    brands={}
    notes={}
    perfumes={}
    # Scento: openly licensed dataset (CC BY 4.0)
    for b in read_csv(SRC/"scento/houses.csv"):
        brands["scento:"+b.get("id","")]={
            "id":"scento:"+b.get("id",""),"name":b.get("name",""),"country":b.get("country",""),
            "founded":b.get("founded",""),"type":b.get("type",""),"url":b.get("url",""),
            "sources":["Scento"],"license":"CC-BY-4.0"}
    for n in read_csv(SRC/"scento/materials.csv"):
        notes["scento:"+n.get("id","")]={
            "id":"scento:"+n.get("id",""),"name":n.get("name",""),"aliases":split(n.get("aliases","")),
            "family":n.get("material_family",""),"origin":n.get("origin",""),"smell":n.get("smell",""),
            "url":n.get("url",""),"sources":["Scento"],"license":"CC-BY-4.0"}
    scentofile=SRC/"scento/perfumes.csv"
    for p in read_csv(scentofile):
        pid="scento:"+str(p.get("id") or norm_name(p.get("name")))
        perfumes[pid]={
            "id":pid,"name":p.get("name",""),"brand":p.get("house",""),"brand_id":"scento:"+str(p.get("house_id","")),
            "country":"","gender":gender(p.get("gender")),"year":p.get("year") or None,
            "family":p.get("family",""),"top":split(p.get("top_notes")),"heart":split(p.get("heart_notes")),
            "base":split(p.get("base_notes")),"tags":split(p.get("seasons"))+split(p.get("times_of_day")),
            "perfumers":split(p.get("perfumers")),"url":p.get("url",""),"sources":["Scento"],
            "license":"CC-BY-4.0","verification":"publisher-curated"}
    # Enrich Scento perfume country from its house table.
    house_by_id={k.removeprefix("scento:"):v for k,v in brands.items()}
    for p in perfumes.values():
        hid=p.get("brand_id","").removeprefix("scento:")
        if hid in house_by_id: p["country"]=house_by_id[hid].get("country","")
    # FragDB full licensed bundle or public sample. Pipe-delimited CSV.
    fdir=SRC/"fragdb"
    bfile=fdir/"brands.csv"
    nfile=fdir/"notes.csv"
    afile=fdir/"accords.csv"
    tfile=fdir/"translations.csv"
    fbrands=read_csv(bfile,"|")
    fnote=read_csv(nfile,"|")
    faccords=read_csv(afile,"|")
    trans={x.get("id"):x.get("en","") for x in read_csv(tfile,"|")}
    for b in fbrands:
        bid="fragdb:"+str(b.get("id",""))
        brands[bid]={"id":bid,"name":b.get("name",""),"country":b.get("country",""),
            "website":b.get("url",""),"parent_company":b.get("parent_company",""),
            "sources":["FragDB"],"license":"FragDB license; verify tier"}
    for n in fnote:
        nid="fragdb:"+str(n.get("id",""))
        notes[nid]={"id":nid,"name":n.get("name",""),"aliases":split(n.get("other_names","")),
            "family":n.get("group",""),"latin_name":n.get("latin_name",""),
            "smell":n.get("odor_profile",""),"url":n.get("url",""),
            "sources":["FragDB"],"license":"FragDB license; verify tier"}
    for a in faccords:
        aid="fragdb:"+str(a.get("id",""))
        notes[aid]={"id":aid,"name":a.get("name",""),"family":"Accord",
            "color":a.get("bar_color",""),"url":"","sources":["FragDB"],"license":"FragDB license; verify tier"}
    note_names={str(x.get("id","")):x.get("name","") for x in fnote}
    accord_names={str(x.get("id","")):x.get("name","") for x in faccords}
    def fragdb_pyramid(raw):
        layers={"top":[],"middle":[],"base":[]}
        if not raw: return layers
        # Example: top(n75,0.96,3.73;n132,0.92,3.42)middle(...)base(...)
        for layer, body in re.findall(r"(top|middle|base|notes)\\(([^)]*)\\)",str(raw)):
            vals=[]
            for item in body.split(";"):
                m=re.match(r"\\s*(n?\\w+)\\s*(?:,|$)",item)
                if m:
                    nid=m.group(1).removeprefix("n")
                    label=note_names.get(m.group(1)) or note_names.get("n"+nid) or note_names.get(nid)
                    if label: vals.append(label)
            if layer=="top": layers["top"]=vals
            elif layer=="middle": layers["middle"]=vals
            elif layer=="base": layers["base"]=vals
            elif layer=="notes": layers["top"]=vals
        return layers
    def fragdb_accord_list(raw):
        vals=[]
        for item in split(raw):
            aid=item.split(":")[0]
            if aid in accord_names: vals.append(accord_names[aid])
        return vals
    for f in read_csv(fdir/"fragrances.csv","|"):
        rawbrand=f.get("brand","")
        bname=rawbrand.split(";")[0].strip()
        bid=rawbrand.split(";")[1].strip() if ";" in rawbrand else ""
        brandrow=next((x for x in fbrands if x.get("id")==bid),{})
        rawgender=trans.get(f.get("gender"),f.get("gender",""))
        pid="fragdb:"+str(f.get("pid") or f.get("id") or norm_name(f.get("name")))
        def parse_pyramid(raw):
            # FragDB compact note list commonly stores note IDs and weights as structured text.
            vals=[]
            if not raw:return vals
            try:
                obj=json.loads(raw)
                if isinstance(obj,list):
                    for x in obj:
                        if isinstance(x,dict): vals.append(str(x.get("name") or x.get("note") or x.get("note_id") or "").strip())
                        else: vals.append(str(x).strip())
                    return [x for x in vals if x]
            except Exception: pass
            return split(raw)
        pyramid=fragdb_pyramid(f.get("notes_pyramid",""))
        top=parse_pyramid(f.get("top_notes") or f.get("top") or f.get("notes_top")) or pyramid["top"]
        heart=parse_pyramid(f.get("middle_notes") or f.get("heart") or f.get("notes_middle")) or pyramid["middle"]
        base=parse_pyramid(f.get("base_notes") or f.get("base") or f.get("notes_base")) or pyramid["base"]
        perfumes[pid]={"id":pid,"name":f.get("name",""),"brand":bname,"brand_id":"fragdb:"+bid if bid else "",
            "country":brandrow.get("country",""),"gender":gender(rawgender),"year":f.get("year") or None,
            "family":"","top":top,"heart":heart,"base":base,"accords":fragdb_accord_list(f.get("accords","")),"tags":[],
            "url":f.get("url",""),"sources":["FragDB"],"license":"FragDB license; verify tier",
            "verification":"source-record"}
    # fragscrape is a scraper, not a packaged database. Import its JSON/JSONL output when supplied.
    sdir=SRC/"fragscrape"
    for path in list(sdir.glob("*.json"))+list(sdir.glob("*.jsonl")):
        lines=path.read_text(encoding="utf-8").splitlines()
        records=[]
        for line in lines:
            try:
                x=json.loads(line)
                records.extend(x if isinstance(x,list) else [x])
            except Exception: continue
        for x in records:
            name=x.get("name") or x.get("perfume") or x.get("title")
            if not name: continue
            brand=x.get("brand") or x.get("house") or ""
            key="scrape:"+norm_name(brand+" "+name)
            notesx=x.get("notes") or {}
            if isinstance(notesx,list): notesx={"notes":notesx}
            perfumes[key]={"id":key,"name":name,"brand":brand,"brand_id":"",
                "country":x.get("country",""),"gender":gender(x.get("gender") or x.get("for")),
                "year":x.get("year"),"family":x.get("family",""),
                "top":split(x.get("top_notes") or notesx.get("top") or x.get("top")),
                "heart":split(x.get("heart_notes") or notesx.get("middle") or x.get("middle")),
                "base":split(x.get("base_notes") or notesx.get("base") or x.get("base")),
                "tags":[],"url":x.get("url",""),"sources":["fragscrape export"],
                "license":"source website terms apply","verification":"scraped-unverified"}
    # Merge obvious duplicates conservatively by normalized brand + perfume name.
    merged={}
    for p in perfumes.values():
        key=norm_name(p.get("brand","")+" "+p.get("name",""))
        if not key: continue
        if key not in merged: merged[key]=p
        else:
            old=merged[key]
            for field in ("country","gender","year","family","url"):
                if not old.get(field) and p.get(field): old[field]=p[field]
            for field in ("top","heart","base","tags","perfumers"):
                old[field]=list(dict.fromkeys((old.get(field) or [])+(p.get(field) or [])))
            old["sources"]=list(dict.fromkeys(old.get("sources",[])+p.get("sources",[])))
            old["id"]="merged:"+key
            old["verification"]="merged-needs-review"
    final=list(merged.values())
    (OUT/"data.json").write_text(json.dumps(final,ensure_ascii=False,indent=2),encoding="utf-8")
    (OUT/"brands.json").write_text(json.dumps(list(brands.values()),ensure_ascii=False,indent=2),encoding="utf-8")
    (OUT/"notes.json").write_text(json.dumps(list(notes.values()),ensure_ascii=False,indent=2),encoding="utf-8")
    report={"perfumes":len(final),"brands":len(brands),"notes_and_accords":len(notes),
        "scento_perfumes":sum("Scento" in p.get("sources",[]) for p in final),
        "fragdb_records":sum("FragDB" in p.get("sources",[]) for p in final),
        "scrape_records":sum("fragscrape export" in p.get("sources",[]) for p in final),
        "warning":"FragDB full data requires its applicable license; fragscrape only contributes data when an export is supplied."}
    (OUT/"merge-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
