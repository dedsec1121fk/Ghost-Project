from __future__ import annotations
from pathlib import Path
import json, random

PRIMARY_CLASSES = {"Assault Rifles","Submachine Guns","Light Machine Guns","Marksman Rifles","Sniper Rifles","Shotguns","Special / Campaign / Extinction"}
SECONDARY_CLASSES = {"Handguns","Launchers"}

def _load_json(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return default

def _save_json(path, value):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding="utf-8")

def _name(w):
    return w.get("display_name") or w.get("name") or w.get("id")

def _choose(label, options, allow_none=False, lang="en"):
    if not options and allow_none:
        return None
    while True:
        print(f"\n{label}")
        if allow_none:
            print("  0. None" if lang=="en" else "  0. Κανένα")
        for i,opt in enumerate(options,1):
            text = opt if isinstance(opt,str) else opt.get("label") or opt.get("name") or str(opt)
            print(f"  {i}. {text}")
        value=input("> ").strip()
        if allow_none and value in ("","0","none","None","κανένα","κανενα"):
            return None
        if value.isdigit():
            idx=int(value)
            if 1 <= idx <= len(options):
                return options[idx-1]
        for opt in options:
            text=opt if isinstance(opt,str) else opt.get("label") or opt.get("name") or str(opt)
            if value.lower()==text.lower():
                return opt
        print("Invalid choice." if lang=="en" else "Μη έγκυρη επιλογή.")

def _weapon_choices(weapons, primary=True):
    allowed=PRIMARY_CLASSES if primary else SECONDARY_CLASSES
    return [w for w in weapons if w.get("class") in allowed and "Campaign" not in w.get("class","")]

def _attachment_pool(options, weapon):
    pool=list(options.get("attachments",{}).get(weapon.get("class"),[]))
    name=_name(weapon)
    blocked=set(options.get("weapon_attachment_blocks",{}).get(name,[]))
    return [x for x in pool if x not in blocked]

def _choose_attachments(options, weapon, max_count, lang):
    if not weapon or max_count <= 0:
        return []
    pool=_attachment_pool(options,weapon)
    selected=[]
    prompt=("Choose attachments for " if lang=="en" else "Επίλεξε attachments για ") + _name(weapon)
    while pool and len(selected)<max_count:
        remaining=[x for x in pool if x not in selected]
        choice=_choose(f"{prompt} ({len(selected)}/{max_count})",remaining,allow_none=True,lang=lang)
        if choice is None:
            break
        selected.append(choice)
    return selected

def _perk_budget(primary, secondary, lethal, tactical):
    empty=sum(x is None for x in (primary,secondary,lethal,tactical))
    return min(12,8+empty)

def _select_perks(options,budget,lang):
    perks=options["perks"]
    selected=[]
    spent=0
    while True:
        print("\nPerks" if lang=="en" else "\nPerks")
        for i,p in enumerate(perks,1):
            mark="*" if p["name"] in selected else " "
            print(f"{mark} {i:2}. {p['name']} ({p['cost']}) - {p['category']}")
        print((f"Budget: {spent}/{budget}. Enter a number; press Enter when finished."
               if lang=="en" else
               f"Budget: {spent}/{budget}. Γράψε αριθμό· Enter όταν τελειώσεις."))
        raw=input("> ").strip()
        if not raw:
            break
        if not raw.isdigit() or not (1<=int(raw)<=len(perks)):
            print("Invalid perk." if lang=="en" else "Μη έγκυρο perk.")
            continue
        p=perks[int(raw)-1]
        if p["name"] in selected:
            selected.remove(p["name"]); spent-=p["cost"]; continue
        if spent+p["cost"]>budget:
            print("Not enough perk points." if lang=="en" else "Δεν υπάρχουν αρκετοί perk points.")
            continue
        selected.append(p["name"]); spent+=p["cost"]
    return selected,spent

def _select_strike(options, lang):
    package=_choose("Strike Package",["Assault","Support","Specialist"],lang=lang)
    if package=="Specialist":
        choices=[p for p in options["perks"] if p["name"]!="Overkill"]
        chosen=[]
        while len(chosen)<3:
            remaining=[p for p in choices if p["name"] not in chosen]
            p=_choose(("Specialist bonus perk" if lang=="en" else "Specialist bonus perk"),remaining,allow_none=(len(chosen)>0),lang=lang)
            if p is None: break
            chosen.append(p["name"])
        return {"package":"Specialist","rewards":chosen}
    rewards=options["strike_packages"][package]
    formatted=[{"name":x["name"],"label":f"{x['points']} - {x['name']}","points":x["points"]} for x in rewards]
    chosen=[]
    while len(chosen)<3:
        rem=[x for x in formatted if x["name"] not in [c["name"] for c in chosen]]
        x=_choose(("Strike reward" if lang=="en" else "Strike reward"),rem,allow_none=(len(chosen)>0),lang=lang)
        if x is None: break
        chosen.append({"points":x["points"],"name":x["name"]})
    chosen.sort(key=lambda x:x["points"])
    return {"package":package,"rewards":chosen}

def _saves_path(root):
    return Path(root)/"saves"/"loadouts.json"

def load_saved(root):
    return _load_json(_saves_path(root),[])

def save_saved(root, rows):
    _save_json(_saves_path(root),rows)

def create_loadout(root, archive, lang="en"):
    options_path=Path(root)/"data"/("el" if lang=="el" else "")/"loadout_options.json"
    if lang=="en":
        options_path=Path(root)/"data"/"loadout_options.json"
    options=_load_json(options_path,{})
    weapons=archive.items("weapons")
    name=input("\nLoadout name: " if lang=="en" else "\nΌνομα loadout: ").strip()
    if not name:
        print("Cancelled." if lang=="en" else "Ακυρώθηκε.")
        return

    primary=_choose("Primary weapon" if lang=="en" else "Primary weapon",_weapon_choices(weapons,True),allow_none=True,lang=lang)
    secondary=_choose("Secondary weapon" if lang=="en" else "Secondary weapon",_weapon_choices(weapons,False),allow_none=True,lang=lang)
    lethal=_choose("Lethal",options["lethal"],allow_none=True,lang=lang)
    tactical=_choose("Tactical",options["tactical"],allow_none=True,lang=lang)

    budget=_perk_budget(primary,secondary,lethal,tactical)
    selected_perks,spent=_select_perks(options,budget,lang)

    if "Overkill" in selected_perks:
        use=input("Use Overkill for a second primary? [y/N]: " if lang=="en" else "Χρήση Overkill για δεύτερο primary; [y/N]: ").strip().lower()
        if use in ("y","yes","ν","ναι"):
            secondary=_choose("Overkill secondary primary",_weapon_choices(weapons,True),allow_none=False,lang=lang)

    primary_limit=options["rules"]["extra_attachment_slots"] if "Extra Attachment" in selected_perks else options["rules"]["default_attachment_slots"]
    primary_atts=_choose_attachments(options,primary,primary_limit,lang)
    secondary_atts=_choose_attachments(options,secondary,2,lang)
    strike=_select_strike(options,lang)

    record={
        "name":name,
        "primary": _name(primary) if primary else None,
        "primary_id": primary.get("id") if primary else None,
        "primary_attachments":primary_atts,
        "secondary": _name(secondary) if secondary else None,
        "secondary_id": secondary.get("id") if secondary else None,
        "secondary_attachments":secondary_atts,
        "lethal":lethal,
        "tactical":tactical,
        "perks":selected_perks,
        "perk_points":{"used":spent,"available":budget},
        "strike_package":strike
    }
    rows=load_saved(root)
    rows=[x for x in rows if x.get("name","").lower()!=name.lower()]
    rows.append(record)
    save_saved(root,rows)
    print("Loadout saved." if lang=="en" else "Το loadout αποθηκεύτηκε.")
    show_loadout(record,lang)

def show_loadout(item,lang="en"):
    if not item:
        return
    fields=[
        ("Primary","Primary",item.get("primary")),
        ("Primary attachments","Primary attachments",", ".join(item.get("primary_attachments",[])) or "-"),
        ("Secondary","Secondary",item.get("secondary")),
        ("Secondary attachments","Secondary attachments",", ".join(item.get("secondary_attachments",[])) or "-"),
        ("Lethal","Lethal",item.get("lethal")),
        ("Tactical","Tactical",item.get("tactical")),
        ("Perks","Perks",", ".join(item.get("perks",[])) or "-"),
        ("Perk points","Perk points",f"{item.get('perk_points',{}).get('used',0)}/{item.get('perk_points',{}).get('available',8)}"),
        ("Strike package","Strike package",item.get("strike_package",{}).get("package")),
        ("Rewards","Rewards",", ".join(str(x.get("name",x)) if isinstance(x,dict) else str(x) for x in item.get("strike_package",{}).get("rewards",[])) or "-"),
    ]
    print(f"\n== {item.get('name','Loadout')} ==")
    for en,el_label,val in fields:
        print(f"{en if lang=='en' else el_label}: {val if val is not None else '-'}")

def list_loadouts(root,lang="en"):
    rows=load_saved(root)
    if not rows:
        print("No saved loadouts." if lang=="en" else "Δεν υπάρχουν αποθηκευμένα loadouts.")
        return
    for i,x in enumerate(rows,1):
        print(f"{i:2}. {x.get('name')} - {x.get('primary') or '-'} / {x.get('secondary') or '-'}")

def get_loadout(root,name):
    q=name.lower()
    for x in load_saved(root):
        if x.get("name","").lower()==q:
            return x
    return None

def delete_loadout(root,name,lang="en"):
    rows=load_saved(root)
    kept=[x for x in rows if x.get("name","").lower()!=name.lower()]
    if len(kept)==len(rows):
        print("Loadout not found." if lang=="en" else "Το loadout δεν βρέθηκε.")
        return
    save_saved(root,kept)
    print("Loadout deleted." if lang=="en" else "Το loadout διαγράφηκε.")

def random_loadout(root,archive,lang="en"):
    options_path=Path(root)/"data"/("el" if lang=="el" else "")/"loadout_options.json"
    if lang=="en": options_path=Path(root)/"data"/"loadout_options.json"
    options=_load_json(options_path,{})
    weapons=archive.items("weapons")
    primary=random.choice(_weapon_choices(weapons,True))
    secondary=random.choice(_weapon_choices(weapons,False))
    lethal=random.choice(options["lethal"])
    tactical=random.choice(options["tactical"])
    # Random perks within standard 8-point budget.
    available=options["perks"][:]
    random.shuffle(available)
    selected=[]; spent=0
    for p in available:
        if spent+p["cost"]<=8 and random.random()<0.45:
            selected.append(p["name"]); spent+=p["cost"]
    if not selected:
        p=random.choice([p for p in options["perks"] if p["cost"]<=2])
        selected=[p["name"]]; spent=p["cost"]
    pa=_attachment_pool(options,primary)
    sa=_attachment_pool(options,secondary)
    strike_name=random.choice(["Assault","Support"])
    rewards=sorted(random.sample(options["strike_packages"][strike_name],3),key=lambda x:x["points"])
    record={
        "name":"Random Loadout",
        "primary":_name(primary),"primary_id":primary["id"],"primary_attachments":random.sample(pa,min(2,len(pa))),
        "secondary":_name(secondary),"secondary_id":secondary["id"],"secondary_attachments":random.sample(sa,min(1,len(sa))),
        "lethal":lethal,"tactical":tactical,"perks":selected,"perk_points":{"used":spent,"available":8},
        "strike_package":{"package":strike_name,"rewards":rewards}
    }
    show_loadout(record,lang)
