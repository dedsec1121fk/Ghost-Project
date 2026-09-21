#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json,shlex,sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
SETTINGS=ROOT/"data"/"settings.json"

def load_language():
    try:
        d=json.loads(SETTINGS.read_text(encoding="utf-8"))
        return "el" if d.get("language")=="el" else "en"
    except Exception:
        return "en"

def save_language(lang):
    try: SETTINGS.write_text(json.dumps({"language":lang},indent=2),encoding="utf-8")
    except Exception: pass

lang=load_language()

from modules.bootstrap import ensure_runtime,ensure_narration
ensure_runtime(ROOT,lang)
ensure_narration(ROOT,lang)

from modules.gallery import ensure_gallery,open_image,export_gallery
ensure_gallery(ROOT)

from modules.archive import Archive
from modules.display import banner,clear,help_text,list_items,show_item,show_search,tr,category_label
from modules.audio import open_url,play_entry_audio,record_voice
from modules.weapon_stats import find_weapons,show_stats,compare_weapons
from modules.loadouts import create_loadout,list_loadouts,get_loadout,show_loadout,delete_loadout,random_loadout
from modules.ui import COMMAND_ALIASES,CATEGORY_ALIASES

def norm_cat(value):
    low=value.lower()
    return CATEGORY_ALIASES.get(low,low)

def print_categories(archive,lang):
    for c in archive.categories():
        print(f"  {c:13} {len(archive.items(c))} {tr(lang,'entries')} — {category_label(lang,c)}")

def show_story(archive,lang):
    for item in archive.items("stories"):
        show_item("stories",item,archive.resolve_sources(item),lang)

def first_source_url(archive,item):
    rows=archive.resolve_sources(item)
    return rows[0][1]["url"] if rows else None

def normalize_command(cmd):
    low=cmd.lower()
    return COMMAND_ALIASES.get(low,low)

def main():
    global lang
    archive=Archive(ROOT,lang)
    clear()
    banner(lang)
    print(tr(lang,"loaded",count=sum(len(v) for v in archive.datasets.values())))
    print(tr(lang,"deps"))
    print(tr(lang,"start_hint")+"\n")

    while True:
        try:
            raw=input("ghost> ").strip()
        except (EOFError,KeyboardInterrupt):
            print("\n"+tr(lang,"exiting"))
            break

        if not raw: continue

        try:
            args=shlex.split(raw)
        except ValueError as e:
            print(tr(lang,"parse_error",error=e))
            continue

        cmd=normalize_command(args[0])

        if cmd in ("quit","exit","q"):
            print(tr(lang,"archive_closed"))
            break
        elif cmd=="help":
            help_text(lang)
        elif cmd=="clear":
            clear(); banner(lang)
        elif cmd=="lang":
            if len(args)<2 or args[1].lower() not in ("en","el","english","greek","ελληνικά","ελληνικα"):
                print(tr(lang,"usage_lang")); continue
            choice=args[1].lower()
            lang="el" if choice in ("el","greek","ελληνικά","ελληνικα") else "en"
            archive.set_language(lang)
            save_language(lang)
            print(tr(lang,"language_changed"))
        elif cmd=="categories":
            print_categories(archive,lang)
        elif cmd=="sources":
            for key,src in archive.sources.items():
                print(f"{key:18} {src['title']}\n  {src['url']}")
        elif cmd=="story":
            show_story(archive,lang)
        elif cmd=="timeline":
            list_items("timeline",archive.items("timeline"),lang)
        elif cmd=="list":
            if len(args)<2:
                print(tr(lang,"usage_list")); continue
            cat=norm_cat(args[1])
            if cat not in archive.categories():
                print(tr(lang,"unknown_category",category=args[1])); continue
            list_items(cat,archive.items(cat),lang)
        elif cmd=="show":
            if len(args)<3:
                print(tr(lang,"usage_show")); continue
            cat,item_id=norm_cat(args[1]),args[2]
            item=archive.get(cat,item_id)
            if not item:
                print(tr(lang,"entry_not_found")); continue
            show_item(cat,item,archive.resolve_sources(item),lang)
        elif cmd=="search":
            if len(args)<2:
                print(tr(lang,"usage_search")); continue
            maybe=norm_cat(args[1])
            if maybe in archive.categories() and len(args)>=3:
                results=archive.search(" ".join(args[2:]),maybe)
            else:
                results=archive.search(" ".join(args[1:]))
            show_search(results,lang)
        elif cmd=="open":
            if len(args)<3:
                print(tr(lang,"usage_open")); continue
            cat,item_id=norm_cat(args[1]),args[2]
            item=archive.get(cat,item_id)
            if not item:
                print(tr(lang,"entry_not_found")); continue
            url=first_source_url(archive,item)
            if not url:
                print(tr(lang,"no_source")); continue
            print(tr(lang,"opening",url=url))
            if not open_url(url): print(tr(lang,"open_failed"))
        elif cmd=="audio":
            if len(args)<3:
                print(tr(lang,"usage_audio")); continue
            cat,item_id=norm_cat(args[1]),args[2]
            item=archive.get(cat,item_id)
            if not item:
                print(tr(lang,"entry_not_found")); continue
            ok,msg=play_entry_audio(ROOT,item,lang)
            print(msg)
            if not ok and item.get("audio_url"):
                print(tr(lang,"public_audio",url=item["audio_url"]))
        elif cmd=="stats":
            if len(args)<2:
                print("Usage: stats <weapon id or name>" if lang=="en" else "Χρήση: stats <weapon id ή όνομα>")
                continue
            matches=find_weapons(archive.items("weapons")," ".join(args[1:]))
            if not matches:
                print(tr(lang,"entry_not_found")); continue
            if len(matches)>1:
                print("Multiple matches:" if lang=="en" else "Πολλαπλά αποτελέσματα:")
                for w in matches[:20]:
                    print(f"  {w.get('id')} - {w.get('display_name') or w.get('name')}")
                continue
            show_stats(matches[0],lang)

        elif cmd=="compare":
            if len(args)<3:
                print('Usage: compare "weapon 1" "weapon 2"' if lang=="en" else 'Χρήση: compare "weapon 1" "weapon 2"')
                continue
            a=find_weapons(archive.items("weapons"),args[1])
            b=find_weapons(archive.items("weapons"),args[2])
            if len(a)!=1 or len(b)!=1:
                print("Use exact weapon names or IDs for compare." if lang=="en" else "Χρησιμοποίησε ακριβές όνομα ή ID όπλου για compare.")
                continue
            compare_weapons(a[0],b[0],lang)

        elif cmd=="loadout":
            action=args[1].lower() if len(args)>1 else "list"
            if action in ("create","new","δημιουργία","δημιουργια"):
                create_loadout(ROOT,archive,lang)
            elif action in ("list","ls","λίστα","λιστα"):
                list_loadouts(ROOT,lang)
            elif action in ("show","view","δείξε","δειξε"):
                if len(args)<3:
                    print("Usage: loadout show <name>"); continue
                item=get_loadout(ROOT," ".join(args[2:]))
                if item: show_loadout(item,lang)
                else: print("Loadout not found." if lang=="en" else "Το loadout δεν βρέθηκε.")
            elif action in ("delete","remove","rm","διαγραφή","διαγραφη"):
                if len(args)<3:
                    print("Usage: loadout delete <name>"); continue
                delete_loadout(ROOT," ".join(args[2:]),lang)
            elif action in ("random","τυχαίο","τυχαιο"):
                random_loadout(ROOT,archive,lang)
            else:
                print("Usage: loadout [create|list|show|delete|random]")
            continue

        elif cmd=="image":
            if len(args)<3:
                print("Usage: image <maps|weapons|characters> <id>"); continue
            cat,item_id=norm_cat(args[1]),args[2]
            if cat not in ("maps","weapons","characters"):
                print("Gallery images are available for maps, weapons and characters."); continue
            item=archive.get(cat,item_id)
            if not item:
                print(tr(lang,"entry_not_found")); continue
            _,msg=open_image(ROOT,item)
            print(msg)
        elif cmd=="gallery":
            category=norm_cat(args[1]) if len(args)>1 else "all"
            if category not in ("all","maps","weapons","characters"):
                print("Usage: gallery [all|maps|weapons|characters]"); continue
            _,msg=export_gallery(ROOT,category)
            print(msg)
        elif cmd=="record":
            if len(args)<2:
                print(tr(lang,"usage_record")); continue
            _,msg=record_voice(ROOT,args[1],lang)
            print(msg)
        else:
            print(tr(lang,"unknown_command"))

if __name__=="__main__":
    main()
