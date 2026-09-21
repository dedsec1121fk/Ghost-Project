from __future__ import annotations
from pathlib import Path
import shutil,subprocess,webbrowser

def _msg(lang,en,el): return el if lang=='el' else en
def _run(cmd):
    try:return subprocess.run(cmd,check=False).returncode==0
    except Exception:return False
def _try_termux_install(package):
    if shutil.which('pkg'):
        try:return subprocess.run(['pkg','install','-y',package],check=False).returncode==0
        except Exception:return False
    return False
def open_url(url:str)->bool:
    if shutil.which('termux-open-url'):return _run(['termux-open-url',url])
    if shutil.which('xdg-open'):return _run(['xdg-open',url])
    try:return bool(webbrowser.open(url))
    except Exception:return False
def play_file(path:Path,lang='en')->tuple[bool,str]:
    if not path.exists():return False,_msg(lang,f'Audio file not found: {path}',f'Το αρχείο ήχου δεν βρέθηκε: {path}')
    if shutil.which('termux-media-player'):
        ok=_run(['termux-media-player','play',str(path)])
        return ok,_msg(lang,'Started with Termux media player.' if ok else 'Termux media player failed.','Ξεκίνησε με το Termux media player.' if ok else 'Το Termux media player απέτυχε.')
    if not shutil.which('mpv'):_try_termux_install('mpv')
    for player in ('mpv','ffplay','play'):
        if shutil.which(player):
            cmd=['ffplay','-nodisp','-autoexit',str(path)] if player=='ffplay' else [player,str(path)]
            ok=_run(cmd)
            return ok,_msg(lang,f'Played with {player}.' if ok else f'{player} failed.',f'Αναπαραγωγή με {player}.' if ok else f'Το {player} απέτυχε.')
    return False,_msg(lang,'No supported audio player is available.','Δεν υπάρχει διαθέσιμο υποστηριζόμενο πρόγραμμα αναπαραγωγής ήχου.')
def play_entry_audio(root:Path,item:dict,lang='en')->tuple[bool,str]:
    candidates=[('original',item.get('audio_original')),('narration',item.get('audio_narration'))]
    missing=[]
    for label,relative in candidates:
        if not relative:continue
        path=root/relative
        if path.exists():
            ok,msg=play_file(path,lang)
            if ok:
                lab=('Αυθεντικός' if label=='original' else 'Αφήγηση') if lang=='el' else label.title()
                return True,f'{lab} audio: {msg}'
            return False,msg
        missing.append(str(path))
    if missing:
        return False,_msg(lang,'No local audio found. Checked:\n  ','Δεν βρέθηκε τοπικός ήχος. Ελέγχθηκαν:\n  ')+'\n  '.join(missing)
    return False,_msg(lang,'This entry has no configured audio.','Αυτή η καταχώρηση δεν έχει ρυθμισμένο ήχο.')
def record_voice(root:Path,filename:str,lang='en')->tuple[bool,str]:
    safe=''.join(c for c in filename if c.isalnum() or c in '._-').strip('.')
    if not safe:return False,_msg(lang,'Invalid filename.','Μη έγκυρο όνομα αρχείου.')
    if not safe.lower().endswith(('.m4a','.aac','.mp3','.wav')):safe+='.m4a'
    target=root/'audio'/'user'/safe; target.parent.mkdir(parents=True,exist_ok=True)
    if not shutil.which('termux-microphone-record'):_try_termux_install('termux-api')
    if not shutil.which('termux-microphone-record'):
        return False,_msg(lang,'The Termux:API command is still unavailable. Install the Termux:API Android companion app, then Ghost Project can use it automatically.','Η εντολή Termux:API δεν είναι ακόμη διαθέσιμη. Εγκατέστησε την εφαρμογή Termux:API στο Android και μετά το Ghost Project θα μπορεί να τη χρησιμοποιήσει αυτόματα.')
    ok=_run(['termux-microphone-record','-f',str(target)])
    if ok:return True,_msg(lang,f'Recording started: {target}\nStop it with: termux-microphone-record -q',f'Η ηχογράφηση ξεκίνησε: {target}\nΣταμάτησέ την με: termux-microphone-record -q')
    return False,_msg(lang,'Could not start recording. Check microphone permission for Termux:API.','Δεν ήταν δυνατό να ξεκινήσει η ηχογράφηση. Έλεγξε την άδεια μικροφώνου για το Termux:API.')
