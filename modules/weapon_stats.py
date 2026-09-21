from __future__ import annotations
from math import ceil

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    HAVE_RICH = True
except Exception:
    HAVE_RICH = False

console = Console() if HAVE_RICH else None

def weapon_name(w):
    return w.get("display_name") or w.get("name") or w.get("id")

def find_weapons(items, query):
    q = query.strip().lower()
    exact = [w for w in items if q in {str(w.get("id","")).lower(), str(w.get("name","")).lower(), str(w.get("display_name","")).lower()}]
    if exact:
        return exact
    return [w for w in items if q in weapon_name(w).lower() or q in str(w.get("name","")).lower()]

def _fmt(v, suffix=""):
    if v is None:
        return "-"
    if isinstance(v, float):
        v = f"{v:.3f}".rstrip("0").rstrip(".")
    return f"{v}{suffix}"

def _body_shots(damage):
    if not damage:
        return None
    return ceil(100 / damage)

def _ttk_ms(damage, rpm):
    if not damage or not rpm:
        return None
    shots = _body_shots(damage)
    if shots is None or shots <= 1:
        return 0
    return round((shots - 1) * 60000 / rpm)

def stat_rows(w, lang="en"):
    s = w.get("multiplayer_stats")
    if not s:
        return []
    labels_en = [
        ("Class", w.get("class")),
        ("Availability", w.get("availability")),
        ("Fire mode", s.get("fire_mode")),
        ("Damage", f"{s.get('damage_max')} -> {s.get('damage_min')}"),
        ("Rate of fire", _fmt(s.get("rpm"), " RPM")),
        ("Magazine", _fmt(s.get("magazine"), " rounds")),
        ("Starting ammo", _fmt(s.get("starting_ammo"), " rounds")),
        ("Maximum ammo", _fmt(s.get("max_ammo"), " rounds")),
        ("Reload loaded", _fmt(s.get("reload_loaded_s"), " s")),
        ("Reload empty", _fmt(s.get("reload_empty_s"), " s")),
        ("Reload cancel", _fmt(s.get("reload_cancel_s"), " s")),
        ("ADS time", _fmt(s.get("ads_time_s"), " s")),
        ("Movement", _fmt(round(s.get("movement",0)*100) if s.get("movement") is not None else None, "%")),
        ("ADS movement", _fmt(round(s.get("ads_movement",0)*100) if s.get("ads_movement") is not None else None, "%")),
        ("Center speed", _fmt(s.get("centerspeed"))),
        ("Integrated attachment", w.get("integrated_attachment") or "-"),
    ]
    if w.get("class") not in {"Shotguns","Sniper Rifles","Special / Campaign / Extinction","Launchers"}:
        labels_en.insert(-1, ("Close body shots", _fmt(_body_shots(s.get("damage_max")))))
        labels_en.insert(-1, ("Theoretical close TTK", _fmt(_ttk_ms(s.get("damage_max"), s.get("rpm")), " ms")))
    if s.get("pellets_per_shot"):
        labels_en.insert(5, ("Pellets / shot", s["pellets_per_shot"]))
    if s.get("burst_rpm"):
        labels_en.insert(5, ("Within-burst RPM", s["burst_rpm"]))
    if lang == "el":
        translations = {
            "Class":"Κατηγορία","Availability":"Διαθεσιμότητα","Fire mode":"Fire mode","Damage":"Damage",
            "Rate of fire":"Ρυθμός βολής","Magazine":"Γεμιστήρας","Starting ammo":"Αρχικό ammo",
            "Maximum ammo":"Μέγιστο ammo","Reload loaded":"Reload με ammo","Reload empty":"Reload άδειο",
            "Reload cancel":"Reload cancel","ADS time":"Χρόνος ADS","Movement":"Κίνηση",
            "ADS movement":"Κίνηση ADS","Center speed":"Center speed","Close body shots":"Body shots κοντά",
            "Theoretical close TTK":"Θεωρητικό κοντινό TTK","Integrated attachment":"Ενσωματωμένο attachment",
            "Pellets / shot":"Pellets / βολή","Within-burst RPM":"RPM μέσα στο burst"
        }
        return [(translations.get(a,a),b) for a,b in labels_en]
    return labels_en

def show_stats(w, lang="en"):
    title = weapon_name(w)
    rows = stat_rows(w, lang)
    if not rows:
        note = w.get("stats_note") or ("Δεν υπάρχουν standard multiplayer stats." if lang=="el" else "No standard multiplayer stats are stored for this weapon.")
        if HAVE_RICH:
            console.print(Panel(note, title=title))
        else:
            print(f"\n== {title} ==\n{note}")
        return
    note = w.get("multiplayer_stats",{}).get("source_note","")
    if HAVE_RICH:
        table = Table(title=title, box=box.SIMPLE_HEAVY)
        table.add_column("Stat" if lang=="en" else "Στατιστικό", style="bold")
        table.add_column("Value" if lang=="en" else "Τιμή")
        for k,v in rows:
            table.add_row(str(k), str(v))
        console.print(table)
        if note:
            console.print(note)
    else:
        print(f"\n== {title} ==")
        for k,v in rows:
            print(f"{k}: {v}")
        if note:
            print(note)

def compare_weapons(a, b, lang="en"):
    sa, sb = a.get("multiplayer_stats"), b.get("multiplayer_stats")
    if not sa or not sb:
        print("Both weapons need multiplayer stats for comparison." if lang=="en" else "Και τα δύο όπλα πρέπει να έχουν multiplayer stats για σύγκριση.")
        return
    keys = [
        ("Damage max","damage_max","higher"),("Damage min","damage_min","higher"),("RPM","rpm","higher"),
        ("Magazine","magazine","higher"),("Reload loaded","reload_loaded_s","lower"),("ADS time","ads_time_s","lower"),
        ("Movement","movement","higher")
    ]
    if HAVE_RICH:
        table = Table(title=f"{weapon_name(a)} vs {weapon_name(b)}", box=box.SIMPLE_HEAVY)
        table.add_column("Stat", style="bold")
        table.add_column(weapon_name(a))
        table.add_column(weapon_name(b))
        for label,key,_ in keys:
            va,vb=sa.get(key),sb.get(key)
            table.add_row(label,_fmt(va),_fmt(vb))
        console.print(table)
    else:
        print(f"\n== {weapon_name(a)} vs {weapon_name(b)} ==")
        for label,key,_ in keys:
            print(f"{label:18} {_fmt(sa.get(key)):>10} | {_fmt(sb.get(key)):>10}")
