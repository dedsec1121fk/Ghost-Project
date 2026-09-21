from __future__ import annotations
from pathlib import Path
import importlib.util,json,os,shutil,subprocess,sys,tempfile

def _msg(lang,en,el): return el if lang=='el' else en
def _run(cmd,timeout=180):
    try:return subprocess.run(cmd,check=False,timeout=timeout).returncode==0
    except Exception:return False
def _termux():
    prefix=os.environ.get('PREFIX',''); return 'com.termux' in prefix or Path('/data/data/com.termux').exists()
def _pip_install(package,lang='en'):
    print(_msg(lang,f'[Ghost Project] Installing missing Python package: {package}',f'[Ghost Project] Εγκατάσταση Python package που λείπει: {package}'))
    return _run([sys.executable,'-m','pip','install',package])
def _pkg_install(*packages,lang='en'):
    if not shutil.which('pkg'):return False
    packages=[p for p in packages if p]
    if not packages:return True
    print(_msg(lang,'[Ghost Project] Installing missing Termux package(s): '+', '.join(packages),'[Ghost Project] Εγκατάσταση Termux package(s) που λείπουν: '+', '.join(packages)))
    return _run(['pkg','install','-y',*packages],timeout=300)
def ensure_runtime(root:Path,lang='en'):
    if importlib.util.find_spec('rich') is None:_pip_install('rich',lang)
    if not _termux():return
    if not shutil.which('termux-media-player') and not shutil.which('mpv'):_pkg_install('mpv',lang=lang)
    if not shutil.which('termux-microphone-record'):_pkg_install('termux-api',lang=lang)
def _ensure_tts_tools(lang='en'):
    if shutil.which('espeak') or shutil.which('espeak-ng'):have_tts=True
    else:
        have_tts=False
        if _termux():
            have_tts=_pkg_install('espeak',lang=lang)
            if not (shutil.which('espeak') or shutil.which('espeak-ng')):_pkg_install('espeak-ng',lang=lang)
        have_tts=bool(shutil.which('espeak') or shutil.which('espeak-ng'))
    if not shutil.which('ffmpeg') and _termux():_pkg_install('ffmpeg',lang=lang)
    return have_tts and bool(shutil.which('ffmpeg'))
def _narration_jobs(root:Path):
    jobs=[]
    specs=[('stories.json',lambda x:f"{x['title']}. {x['summary']}"),('missions.json',lambda x:f"Mission {x['order']}. {x['title']}. {x['summary']}"),('rorke_files.json',lambda x:f"Rorke File {x['collectible_number']}. Mission: {x['mission']}. Archive summary. {x['summary']}"),('extinction_intel.json',lambda x:f"{x['map']} intel. {x['title']}. {x['summary']}")]
    for filename,make_text in specs:
        path=root/'data'/filename
        if not path.exists():continue
        try:items=json.loads(path.read_text(encoding='utf-8'))
        except Exception:continue
        for item in items:
            relative=item.get('audio_narration')
            if relative:jobs.append((make_text(item),root/relative))
    return jobs
def ensure_narration(root:Path,lang='en'):
    missing=[(text,path) for text,path in _narration_jobs(root) if not path.exists()]
    if not missing:return True
    print(_msg(lang,f'[Ghost Project] {len(missing)} narration file(s) are missing. Repairing audio...',f'[Ghost Project] Λείπουν {len(missing)} αρχεία αφήγησης. Γίνεται αποκατάσταση ήχου...'))
    if not _ensure_tts_tools(lang):
        print(_msg(lang,'[Ghost Project] Could not install or find espeak and ffmpeg. The archive will still run without repaired narration.','[Ghost Project] Δεν ήταν δυνατή η εγκατάσταση ή εύρεση των espeak και ffmpeg. Το αρχείο θα συνεχίσει να λειτουργεί χωρίς την αποκατάσταση της αφήγησης.'))
        return False
    espeak=shutil.which('espeak') or shutil.which('espeak-ng'); ffmpeg=shutil.which('ffmpeg'); repaired=0
    for text,out_path in missing:
        out_path.parent.mkdir(parents=True,exist_ok=True)
        try:
            with tempfile.TemporaryDirectory() as td:
                wav=Path(td)/'speech.wav'
                if not _run([espeak,'-s','142','-p','42','-a','165','-w',str(wav),text]):continue
                ok=_run([ffmpeg,'-y','-loglevel','error','-i',str(wav),'-codec:a','libmp3lame','-b:a','48k','-ac','1','-ar','22050',str(out_path)])
                if ok and out_path.exists():repaired+=1
        except Exception:pass
    print(_msg(lang,f'[Ghost Project] Repaired {repaired}/{len(missing)} narration file(s).',f'[Ghost Project] Αποκαταστάθηκαν {repaired}/{len(missing)} αρχεία αφήγησης.'))
    return repaired==len(missing)
