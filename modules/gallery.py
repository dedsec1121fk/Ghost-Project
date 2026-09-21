from __future__ import annotations
from pathlib import Path
import importlib.util, json, shutil, subprocess, sys

CATEGORIES={"maps":"maps.json","weapons":"weapons.json","characters":"characters.json"}

def _run(cmd):
    try: return subprocess.run(cmd,check=False).returncode==0
    except Exception: return False

def _ensure_pillow():
    if importlib.util.find_spec("PIL") is not None: return True
    print("[Ghost Project] Installing missing gallery dependency: pillow")
    try: subprocess.run([sys.executable,"-m","pip","install","pillow"],check=False)
    except Exception: return False
    return importlib.util.find_spec("PIL") is not None

def _font(size,bold=False):
    from PIL import ImageFont
    paths=[
      "/system/fonts/Roboto-Bold.ttf" if bold else "/system/fonts/Roboto-Regular.ttf",
      "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf" if bold else "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans.ttf",
      "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        if p and Path(p).exists():
            try: return ImageFont.truetype(p,size=size)
            except Exception: pass
    return ImageFont.load_default()

def _wrap(draw,text,font,width):
    words=str(text or "").split(); out=[]; line=""
    for word in words:
        test=word if not line else line+" "+word
        b=draw.textbbox((0,0),test,font=font)
        if b[2]-b[0] <= width: line=test
        else:
            if line: out.append(line)
            line=word
    if line: out.append(line)
    return out

def _safe(v):
    return ", ".join(map(str,v)) if isinstance(v,list) else str(v or "")

def _icon(draw,category):
    if category=="maps":
        draw.rounded_rectangle((680,120,1000,390),35,outline=(225,225,225),width=6)
        for x in range(725,970,70): draw.line((x,150,x-25,360),fill=(145,145,145),width=3)
        for y in range(180,350,55): draw.line((710,y,970,y-18),fill=(145,145,145),width=3)
        draw.ellipse((800,210,860,270),outline=(245,245,245),width=6)
        draw.ellipse((817,227,843,253),fill=(245,245,245))
    elif category=="weapons":
        pts=[(630,220),(855,220),(855,198),(990,208),(990,247),(855,260),(800,305),(752,305),(778,258),(680,258)]
        draw.polygon(pts,fill=(220,220,220)); draw.rectangle((688,255,727,370),fill=(185,185,185))
        draw.polygon([(745,258),(795,258),(775,350),(733,350)],fill=(165,165,165))
        draw.rectangle((990,222,1040,238),fill=(220,220,220))
    else:
        draw.ellipse((725,105,980,400),outline=(225,225,225),width=7)
        draw.polygon([(770,195),(815,174),(850,207),(812,245)],fill=(220,220,220))
        draw.polygon([(935,195),(890,174),(855,207),(893,245)],fill=(220,220,220))
        draw.polygon([(805,285),(855,258),(905,285),(886,362),(823,362)],fill=(90,90,90),outline=(220,220,220))
        for x in (830,850,870,890): draw.line((x,305,x-5,350),fill=(230,230,230),width=5)

def generate_card(root,category,item,greek=None):
    if not _ensure_pillow(): return False
    from PIL import Image,ImageDraw
    rel=item.get("image_local")
    if not rel: return False
    out=Path(root)/rel; out.parent.mkdir(parents=True,exist_ok=True)
    W,H=1080,1440
    seed=sum(ord(c) for c in str(item.get("id","")))%24
    img=Image.new("RGB",(W,H),(20+seed//2,23+seed//3,26+seed//4)); d=ImageDraw.Draw(img)
    for y in range(0,H,96):
        q=28+((y//96+seed)%4)*4
        d.rectangle((0,y,W,y+42),fill=(q,q,q+2))
    d.rectangle((0,0,W,72),fill=(8,8,8)); d.rectangle((0,H-68,W,H),fill=(8,8,8))
    d.text((48,18),"GHOST PROJECT",font=_font(30,True),fill=(245,245,245))
    title=item.get("display_name") or item.get("name") or item.get("title") or item.get("id")
    d.text((50,105),str(title),font=_font(50,True),fill=(250,250,250))
    d.text((52,174),f"{category.upper()}  •  {item.get('id','')}",font=_font(24,True),fill=(190,190,190))
    _icon(d,category)

    y=430; lf=_font(22,True); tf=_font(23); gf=_font(21)
    if category=="maps":
        fields=[("TYPE / PACK",f"{item.get('type','')} • {item.get('pack','')}"),("LOCATION",item.get("location","")),
                ("SCALE / COMBAT",f"{item.get('scale','')} • {item.get('combat','')}"),("DETAIL",item.get("description","")),
                ("DYNAMICS",item.get("dynamics","")),("CONNECTIONS",item.get("connections","")),("EASTER EGGS",item.get("easter_eggs",""))]
    elif category=="weapons":
        fields=[("CLASS",item.get("class","")),("AVAILABILITY",item.get("availability","")),("MODES",_safe(item.get("modes"))),
                ("ROLE",item.get("role","")),("DETAIL",item.get("special_notes",""))]
    else:
        fields=[("GROUP / FACTION",f"{item.get('group','')} • {item.get('faction','')}"),("ROLE",item.get("role","")),
                ("STATUS",item.get("status","")),("DETAIL",item.get("notes",""))]
    for lab,val in fields:
        if not val: continue
        d.text((50,y),lab,font=lf,fill=(185,185,185)); y+=31
        lines=_wrap(d,_safe(val),tf,965)
        for line in lines[:4]:
            d.text((50,y),line,font=tf,fill=(238,238,238)); y+=31
        y+=13
        if y>1125: break
    if greek and y<1240:
        d.line((48,y,1032,y),fill=(105,105,105),width=2); y+=18
        d.text((50,y),"ΕΛΛΗΝΙΚΑ",font=lf,fill=(205,205,205)); y+=34
        txt=greek.get("description") or greek.get("notes") or greek.get("special_notes") or ""
        for line in _wrap(d,txt,gf,965)[:4]:
            d.text((50,y),line,font=gf,fill=(225,225,225)); y+=29
    d.text((48,H-46),"Offline gallery card • Original Ghost Project reference image",font=_font(18),fill=(145,145,145))
    img.save(out,"JPEG",quality=85)
    return True

def ensure_gallery(root):
    root=Path(root); missing=[]
    for cat,fn in CATEGORIES.items():
        try:
            en=json.loads((root/"data"/fn).read_text(encoding="utf-8"))
            el=json.loads((root/"data"/"el"/fn).read_text(encoding="utf-8"))
        except Exception: continue
        gm={x.get("id"):x for x in el}
        for item in en:
            rel=item.get("image_local")
            if rel and not (root/rel).exists(): missing.append((cat,item,gm.get(item.get("id"))))
    if not missing: return True
    print(f"[Ghost Project] {len(missing)} gallery image(s) are missing. Rebuilding...")
    if not _ensure_pillow(): return False
    done=sum(1 for cat,item,g in missing if generate_card(root,cat,item,g))
    print(f"[Ghost Project] Rebuilt {done}/{len(missing)} gallery image(s).")
    return done==len(missing)

def open_image(root,item):
    p=Path(root)/item.get("image_local","")
    if not p.exists(): return False,f"Image not found: {p}"
    for opener in ("termux-open","xdg-open"):
        if shutil.which(opener):
            ok=_run([opener,str(p)]); return ok,(f"Opening {p}" if ok else "Could not open image.")
    return False,f"Image is available at: {p}"

def export_gallery(root,category="all"):
    root=Path(root)
    dest=Path.home()/"storage"/"pictures"/"Ghost Project"
    if not dest.parent.exists():
        return False,"Android Pictures storage is unavailable. Run termux-setup-storage, then try again."
    dest.mkdir(parents=True,exist_ok=True)
    cats=list(CATEGORIES) if category=="all" else [category]
    n=0
    for cat in cats:
        out=dest/cat; out.mkdir(parents=True,exist_ok=True)
        for p in (root/"images"/cat).glob("*.jpg"):
            shutil.copy2(p,out/p.name); n+=1
    return True,f"Exported {n} JPG files to {dest}"
