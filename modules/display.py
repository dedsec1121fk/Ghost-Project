from __future__ import annotations
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
    HAVE_RICH=True
except Exception:
    HAVE_RICH=False
from modules.ui import TEXT,CATEGORY_NAMES,FIELD_NAMES
console=Console() if HAVE_RICH else None

def tr(lang,key,**kwargs): return TEXT.get(lang,TEXT['en']).get(key,key).format(**kwargs)
def clear(): print('\033[2J\033[H',end='')
def banner(lang='en'):
    art = r"""
   ________               __     ____             _           __
  / ____/ /_  ____  _____/ /_   / __ \_________  (_)__  _____/ /_
 / / __/ __ \/ __ \/ ___/ __/  / /_/ / ___/ __ \/ / _ \/ ___/ __/
/ /_/ / / / / /_/ (__  ) /_   / ____/ /  / /_/ / /  __/ /__/ /_
\____/_/ /_/\____/____/\__/  /_/   /_/   \____/_/\___/\___/\__/
"""
    subtitle=tr(lang,'subtitle')
    if HAVE_RICH:
        console.print(Panel.fit(art,title='GHOST PROJECT',subtitle=subtitle))
    else:
        print(art)
        print(subtitle)

def title_for(item):
    if item.get('title') or item.get('name') or item.get('id'):
        return item.get('title') or item.get('name') or item.get('id')
    if item.get('date'):
        return str(item['date'])
    if item.get('event'):
        text=str(item['event'])
        return text if len(text) <= 52 else text[:49] + '...'
    return '-'
def category_label(lang,category): return CATEGORY_NAMES.get(lang,CATEGORY_NAMES['en']).get(category,category)
def field_label(lang,key): return key.replace('_',' ').title() if lang=='en' else FIELD_NAMES['el'].get(key,key.replace('_',' ').title())
def list_items(category,items,lang='en'):
    lab=category_label(lang,category).upper()
    if HAVE_RICH:
        table=Table(title=lab,box=box.SIMPLE_HEAVY); table.add_column(tr(lang,'id'),style='bold'); table.add_column(tr(lang,'title_name')); table.add_column(tr(lang,'info'))
        for item in items:
            info=item.get('date') or item.get('class') or item.get('map') or item.get('group') or item.get('universe') or item.get('area') or ''
            table.add_row(str(item.get('id','-')),str(title_for(item)),str(info))
        console.print(table)
    else:
        print(f'\n== {lab} ==')
        for item in items:
            info=item.get('date') or item.get('class') or item.get('map') or item.get('group') or item.get('universe') or ''
            print(f"{item.get('id','-'):>8} | {title_for(item)} | {info}")
def show_item(category,item,source_rows=None,lang='en'):
    if HAVE_RICH:
        body=[]
        for k,v in item.items():
            if k=='source_keys': continue
            if isinstance(v,list): v=', '.join(map(str,v))
            body.append(f'[bold]{field_label(lang,k)}:[/bold] {v}')
        if source_rows:
            body.append(f"\n[bold]{tr(lang,'sources')}:[/bold]")
            for _,src in source_rows: body.append(f"- {src['title']}: {src['url']}")
        console.print(Panel('\n'.join(body),title=f'{category_label(lang,category)} :: {title_for(item)}'))
    else:
        print(f'\n== {category_label(lang,category)} :: {title_for(item)} ==')
        for k,v in item.items():
            if k!='source_keys': print(f'{field_label(lang,k)}: {v}')
        if source_rows:
            print(f"{tr(lang,'sources')}:")
            for _,src in source_rows: print(f"  - {src['title']}: {src['url']}")
def show_search(results,lang='en'):
    if not results: print(tr(lang,'no_matches')); return
    if HAVE_RICH:
        table=Table(title=tr(lang,'search_results'),box=box.MINIMAL_DOUBLE_HEAD); table.add_column(tr(lang,'score')); table.add_column(tr(lang,'category')); table.add_column(tr(lang,'id')); table.add_column(tr(lang,'title_name'))
        for score,cat,item in results: table.add_row(str(score),category_label(lang,cat),str(item.get('id','-')),str(title_for(item)))
        console.print(table)
    else:
        for score,cat,item in results: print(f"[{score:02}] {category_label(lang,cat):12} {item.get('id','-'):10} {title_for(item)}")
def help_text(lang='en'):
    if lang=='el':
        print('''\nΕντολές\n-------\nhelp / βοήθεια                 Εμφάνιση βοήθειας\ncategories / κατηγορίες        Εμφάνιση κατηγοριών αρχείου\nlist / λίστα <category>        Λίστα καταχωρήσεων\nshow / δείξε <category> <id>   Εμφάνιση μίας καταχώρησης\nsearch / αναζήτηση <λέξεις>    Αναζήτηση σε όλο το αρχείο\nsearch <category> <λέξεις>     Αναζήτηση σε συγκεκριμένη κατηγορία\nstory / ιστορία                Επισκόπηση Campaign + Extinction\ntimeline / χρονολόγιο          Εμφάνιση χρονολογίου\naudio / ήχος <category> <id>   Αναπαραγωγή τοπικού ήχου\nopen / άνοιξε <category> <id>  Άνοιγμα πρώτης πηγής\nimage <category> <id>           Άνοιγμα τοπικής JPG κάρτας\ngallery [category]              Export JPGs στο Android Pictures\nrecord / εγγραφή <όνομα>       Ηχογράφηση προσωπικής σημείωσης\nsources / πηγές                Εμφάνιση πηγών\nlang / γλώσσα <en|el>          Αλλαγή γλώσσας\nclear / καθαρισμός             Καθαρισμός οθόνης\nquit / exit / έξοδος           Έξοδος\n\nΚατηγορίες:\nstories, missions, maps, rorke, extinction, characters, locations,\ntimeline, weapons, easter-eggs, connections\n''')
    else:
        print('''\nCommands\n--------\nhelp                         Show this help\ncategories                   Show archive categories\nlist <category>              List entries\nshow <category> <id>         Show one entry\nsearch <words>               Search every archive\nsearch <category> <words>    Search one category\nstory                        Show campaign + Extinction story overviews\ntimeline                     List timeline events\naudio <category> <id>        Play local audio\nopen <category> <id>         Open the first source URL for an entry\nimage <category> <id>        Open a local JPG gallery card\ngallery [category]           Export JPG gallery cards to Android Pictures\nrecord <filename>            Record a personal voice note with Termux:API\nsources                      List reference sources\nlang <en|el>                 Change language\nclear                        Clear screen\nquit / exit                  Leave Ghost Project\n\nCategories:\nstories, missions, maps, rorke, extinction, characters, locations,\ntimeline, weapons, easter-eggs, connections\n''')
