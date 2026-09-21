from __future__ import annotations
from pathlib import Path
import json,re
from typing import Any

DATASETS={
    "stories":"stories.json",
    "missions":"missions.json",
    "maps":"maps.json",
    "rorke":"rorke_files.json",
    "extinction":"extinction_intel.json",
    "characters":"characters.json",
    "locations":"locations.json",
    "timeline":"timeline.json",
    "weapons":"weapons.json",
    "easter-eggs":"easter_eggs.json",
    "connections":"cross_game_lore.json",
}

def _flatten(value:Any)->str:
    if isinstance(value,dict): return " ".join(_flatten(v) for v in value.values())
    if isinstance(value,list): return " ".join(_flatten(v) for v in value)
    return str(value)

class Archive:
    def __init__(self,root:Path,language:str="en"):
        self.root=root
        self.language="el" if language=="el" else "en"
        self.reload()

    def _directory(self):
        base=self.root/"data"
        return base/"el" if self.language=="el" else base

    def reload(self):
        self.data_dir=self._directory()
        self.datasets={}
        for name,filename in DATASETS.items():
            self.datasets[name]=json.loads((self.data_dir/filename).read_text(encoding="utf-8"))
        self.sources=json.loads((self.data_dir/"sources.json").read_text(encoding="utf-8"))

    def set_language(self,language:str):
        self.language="el" if language=="el" else "en"
        self.reload()

    def categories(self): return list(DATASETS)
    def items(self,category:str): return self.datasets.get(category,[])

    def get(self,category:str,item_id:str):
        for item in self.items(category):
            if str(item.get("id","")).lower()==item_id.lower():
                return item
        return None

    def search(self,query:str,category:str|None=None,limit:int=50):
        terms=[t.lower() for t in re.findall(r"[\w'.-]+",query,flags=re.UNICODE) if t.strip()]
        if not terms: return []
        cats=[category] if category and category in self.datasets else self.categories()
        scored=[]
        for cat in cats:
            for item in self.datasets[cat]:
                hay=_flatten(item).lower()
                title=str(item.get("name","") or item.get("title","")).lower()
                score=sum(hay.count(term)*(3 if term in title else 1) for term in terms)
                if score: scored.append((score,cat,item))
        scored.sort(key=lambda x:(-x[0],str(x[2].get("id",""))))
        return scored[:limit]

    def resolve_sources(self,item:dict):
        return [(key,self.sources[key]) for key in item.get("source_keys",[]) if key in self.sources]
