# Ghost Project

> **Ghost Project** is a cross-platform Python archive and reference toolkit for **Call of Duty: Ghosts**, covering campaign lore, Rorke Files, Extinction, maps, weapons, characters, Easter eggs, cross-game connections, weapon statistics, loadouts, narration, and offline gallery cards.
>
> Το **Ghost Project** είναι ένα cross-platform Python archive και reference toolkit για το **Call of Duty: Ghosts**, με campaign lore, Rorke Files, Extinction, χάρτες, όπλα, χαρακτήρες, Easter eggs, συνδέσεις με άλλα παιχνίδια, weapon statistics, loadouts, narration και offline gallery cards.

---

<details>
<summary><strong>🇬🇧 English</strong></summary>

## About

Ghost Project is an unofficial fan-made research and reference project. It is designed to work as both a searchable lore archive and a practical multiplayer companion.

It stores original summaries and structured reference data rather than complete copyrighted game transcripts or ripped game assets.

<details>
<summary><strong>Supported platforms</strong></summary>

Ghost Project supports:

- Termux on Android
- Ubuntu
- Kali Linux
- Linux Mint

Use the same workflow on every supported platform:

```bash
bash Setup.sh
./Run.sh
```

Platform behavior:

- Termux uses the native Termux Python installation and native packages.
- Ubuntu, Kali Linux, and Linux Mint use a project-local `.venv`.
- `Setup.sh` detects the platform and installs the required system/Python dependencies.
- `Run.sh` automatically selects the correct Python environment.
- The Python launcher can repair missing optional dependencies, narration files, and gallery cards when possible.

</details>

<details>
<summary><strong>Archive content</strong></summary>

The project includes:

- all 18 campaign missions
- campaign story overview
- 18 Rorke File archive entries
- Extinction story and intel for Nightfall, Mayday, Awakening, and Exodus
- 36 detailed Multiplayer and Extinction map entries
- 50 weapon entries
- detailed multiplayer statistics for 41 standard/supported weapons
- 43 campaign and Extinction character entries
- locations and timeline information
- Easter eggs
- cross-game references and lore connections
- English and Greek archive data
- generated narration for story/intel summaries
- 129 offline JPG reference cards
- a saved multiplayer loadout builder

</details>

<details>
<summary><strong>Search and archive commands</strong></summary>

Search the complete archive:

```text
search rorke
search honey badger
search infinite warfare
search warhawk
```

Search a single category:

```text
search missions rorke
search maps warhawk
search weapons honey badger
search characters logan
search connections infinite warfare
```

List and open records:

```text
categories
list missions
list maps
list weapons
show missions M07
show maps MAP011
show weapons W007
story
timeline
sources
```

</details>

<details>
<summary><strong>Weapon statistics</strong></summary>

Show detailed multiplayer statistics by weapon name or archive ID:

```text
stats "Honey Badger"
stats W003
```

Where reliable standard multiplayer data is available, the stat view includes:

- maximum and minimum damage
- fire mode
- rate of fire
- magazine capacity
- starting and maximum ammunition
- loaded/empty/cancel reload timings
- ADS time
- movement and ADS movement values
- center speed
- integrated attachment information
- close-range body-shot count where appropriate
- theoretical close-range TTK where appropriate

Special campaign/Extinction weapons without a standard multiplayer gun profile are clearly marked instead of receiving invented numbers.

Compare two weapons:

```text
compare "Honey Badger" "AK-12"
compare W005 W007
```

The weapon JPG gallery cards also include core multiplayer numbers where available.

</details>

<details>
<summary><strong>Loadout builder</strong></summary>

Create a multiplayer Create-A-Soldier style loadout:

```text
loadout create
```

The interactive builder supports:

- primary weapons
- secondary weapons
- primary and secondary attachments
- lethal equipment
- tactical equipment
- all 35 standard Ghosts perks with point costs
- the Ghosts perk-point budget
- Overkill
- Extra Attachment
- Assault Strike Package
- Support Strike Package
- Specialist Strike Package
- local saved loadouts

The normal perk budget is 8 points. Leaving the primary, secondary, lethal, or tactical slot empty adds one available perk point per empty slot, up to 12.

Manage loadouts:

```text
loadout list
loadout show "Stealth AR"
loadout delete "Stealth AR"
loadout random
```

Personal saved loadouts are stored locally in:

```text
saves/loadouts.json
```

That local save file is ignored by Git.

</details>

<details>
<summary><strong>🇬🇧 English / 🇬🇷 Greek language switching</strong></summary>

Switch the archive interface to Greek:

```text
lang el
```

Switch back to English:

```text
lang en
```

The selected language is remembered between runs.

The Greek archive mirrors story summaries, mission information, Rorke Files, Extinction intel, characters, locations, maps, timelines, weapon information, Easter eggs, cross-game lore, help text, and interface labels.

Official names such as mission names, weapon names, character names, and map names remain unchanged where no official Greek title exists.

</details>

<details>
<summary><strong>Audio and voice notes</strong></summary>

Ghost Project includes generated narration MP3 files for its own archive summaries.

Bundled narration covers:

- Campaign and Extinction story summaries
- campaign mission summaries
- Rorke File archive summaries
- indexed Extinction intel summaries

The generated narration is not ripped game audio.

If you legally possess original recordings, place them under:

```text
audio/original/rorke/
audio/original/extinction/
```

Ghost Project checks original local audio first and then falls back to bundled narration.

Example:

```text
audio rorke RF01
```

Record a personal note:

```text
record my_note
```

On Termux, recording uses Termux:API and requires the Android Termux:API companion application for microphone access.

On supported desktop Linux systems, Ghost Project uses available Linux audio tools such as `ffmpeg` or `arecord`.

</details>

<details>
<summary><strong>Image gallery</strong></summary>

Ghost Project contains phone/gallery-friendly JPG reference cards:

- 36 map JPG files
- 50 weapon JPG files
- 43 character JPG files

These are original Ghost Project reference cards, not copied game screenshots or official artwork.

Open one image:

```text
image maps MAP011
image weapons W007
image characters C01
```

Export the gallery:

```text
gallery all
gallery maps
gallery weapons
gallery characters
```

On Termux, exports go to Android Pictures when storage access is available.

On Ubuntu, Kali Linux, and Linux Mint, exports go to the user's Pictures directory.

Missing cards are rebuilt automatically when possible.

</details>

<details>
<summary><strong>Commands</strong></summary>

```text
help
categories
list <category>
show <category> <id>
search <query>
search <category> <query>
story
timeline
stats <weapon>
compare <weapon1> <weapon2>
loadout create
loadout list
loadout show <name>
loadout delete <name>
loadout random
audio <category> <id>
image <category> <id>
gallery [category]
open <category> <id>
record <filename>
sources
lang <en|el>
clear
quit
```

Archive categories:

```text
stories
missions
maps
rorke
extinction
characters
locations
timeline
weapons
easter-eggs
connections
```

</details>

<details>
<summary><strong>Project structure</strong></summary>

```text
Ghost-Project/
├── Ghost Project.py
├── Setup.sh
├── Run.sh
├── modules/
│   ├── archive.py
│   ├── audio.py
│   ├── bootstrap.py
│   ├── display.py
│   ├── gallery.py
│   ├── loadouts.py
│   ├── platforms.py
│   ├── ui.py
│   └── weapon_stats.py
├── data/
│   ├── stories.json
│   ├── missions.json
│   ├── maps.json
│   ├── rorke_files.json
│   ├── extinction_intel.json
│   ├── characters.json
│   ├── locations.json
│   ├── timeline.json
│   ├── weapons.json
│   ├── loadout_options.json
│   ├── easter_eggs.json
│   ├── cross_game_lore.json
│   ├── sources.json
│   └── el/
├── documents/
│   ├── en/
│   └── el/
├── audio/
│   ├── narration/
│   ├── original/
│   └── user/
├── images/
│   ├── maps/
│   ├── weapons/
│   └── characters/
├── saves/
│   └── .gitkeep
├── tools/
├── requirements.txt
├── CONTENT_NOTICE.md
└── README.md
```

</details>

<details>
<summary><strong>Data notes</strong></summary>

Weapon statistics are reference multiplayer values. Attachments and game balance changes can modify weapon behavior.

The project keeps campaign lore, Extinction continuity, cross-game references, remade maps, and meta-connections distinguishable rather than treating every reference as one shared canon.

Public references are recorded in `data/sources.json` and are available with:

```text
sources
```

</details>

</details>

---

<details>
<summary><strong>🇬🇷 Ελληνικά</strong></summary>

## Σχετικά με το Project

Το Ghost Project είναι ένα ανεπίσημο fan-made research και reference project. Λειτουργεί τόσο ως αναζητήσιμο lore archive όσο και ως πρακτικό multiplayer companion.

Αποθηκεύει πρωτότυπες περιλήψεις και structured reference data αντί για πλήρεις copyrighted μεταγραφές ή ripped game assets.

<details>
<summary><strong>Υποστηριζόμενες πλατφόρμες</strong></summary>

Το Ghost Project υποστηρίζει:

- Termux σε Android
- Ubuntu
- Kali Linux
- Linux Mint

Η ίδια διαδικασία χρησιμοποιείται παντού:

```bash
bash Setup.sh
./Run.sh
```

Συμπεριφορά ανά πλατφόρμα:

- Το Termux χρησιμοποιεί το native Termux Python και native packages.
- Ubuntu, Kali Linux και Linux Mint χρησιμοποιούν local `.venv` μέσα στο project.
- Το `Setup.sh` ανιχνεύει την πλατφόρμα και εγκαθιστά system/Python dependencies.
- Το `Run.sh` επιλέγει αυτόματα το σωστό Python environment.
- Ο Python launcher μπορεί να επιδιορθώνει missing optional dependencies, narration files και gallery cards όταν είναι δυνατό.

</details>

<details>
<summary><strong>Περιεχόμενο archive</strong></summary>

Το project περιλαμβάνει:

- και τις 18 campaign αποστολές
- campaign story overview
- 18 Rorke File archive entries
- Extinction story και intel για Nightfall, Mayday, Awakening και Exodus
- 36 αναλυτικές Multiplayer και Extinction map entries
- 50 weapon entries
- detailed multiplayer stats για 41 standard/supported weapons
- 43 campaign και Extinction character entries
- locations και timeline information
- Easter eggs
- cross-game references και lore connections
- English και Greek archive data
- generated narration για story/intel summaries
- 129 offline JPG reference cards
- saved multiplayer loadout builder

</details>

<details>
<summary><strong>Αναζήτηση και archive commands</strong></summary>

Αναζήτηση σε ολόκληρο το archive:

```text
αναζήτηση rorke
αναζήτηση honey badger
αναζήτηση infinite warfare
αναζήτηση warhawk
```

Αναζήτηση σε συγκεκριμένη κατηγορία:

```text
search missions rorke
search maps warhawk
search weapons honey badger
search characters logan
search connections infinite warfare
```

Λίστες και records:

```text
κατηγορίες
λίστα missions
λίστα maps
λίστα weapons
δείξε missions M07
δείξε maps MAP011
δείξε weapons W007
ιστορία
χρονολόγιο
πηγές
```

</details>

<details>
<summary><strong>Weapon statistics</strong></summary>

Εμφάνιση αναλυτικών multiplayer stats με weapon name ή archive ID:

```text
stats "Honey Badger"
stats W003
```

Όπου υπάρχουν αξιόπιστα standard multiplayer data, εμφανίζονται:

- maximum και minimum damage
- fire mode
- RPM
- magazine capacity
- starting και maximum ammunition
- loaded/empty/cancel reload timings
- ADS time
- movement και ADS movement values
- center speed
- integrated attachment information
- close-range body-shot count όπου είναι κατάλληλο
- theoretical close-range TTK όπου είναι κατάλληλο

Campaign/Extinction special weapons χωρίς standard multiplayer gun profile επισημαίνονται καθαρά χωρίς invented numbers.

Σύγκριση δύο όπλων:

```text
compare "Honey Badger" "AK-12"
compare W005 W007
```

Τα weapon JPG cards εμφανίζουν επίσης βασικά multiplayer numbers όπου υπάρχουν.

</details>

<details>
<summary><strong>Loadout builder</strong></summary>

Δημιουργία multiplayer Create-A-Soldier style loadout:

```text
loadout create
```

Ο interactive builder υποστηρίζει:

- primary weapons
- secondary weapons
- attachments
- lethal equipment
- tactical equipment
- όλα τα 35 standard Ghosts perks με point costs
- το Ghosts perk-point budget
- Overkill
- Extra Attachment
- Assault Strike Package
- Support Strike Package
- Specialist Strike Package
- local saved loadouts

Το normal perk budget είναι 8 points. Κάθε κενό primary, secondary, lethal ή tactical slot προσθέτει έναν διαθέσιμο perk point, μέχρι το όριο των 12.

Διαχείριση loadouts:

```text
loadout list
loadout show "Stealth AR"
loadout delete "Stealth AR"
loadout random
```

Τα προσωπικά loadouts αποθηκεύονται τοπικά στο:

```text
saves/loadouts.json
```

Το local save file αγνοείται από το Git.

</details>

<details>
<summary><strong>🇬🇧 English / 🇬🇷 Ελληνικά</strong></summary>

Αλλαγή σε Ελληνικά:

```text
γλώσσα el
```

Αλλαγή σε Αγγλικά:

```text
γλώσσα en
```

Η επιλεγμένη γλώσσα αποθηκεύεται ανάμεσα στις εκτελέσεις.

Το ελληνικό archive περιλαμβάνει μεταφρασμένα story summaries, mission information, Rorke Files, Extinction intel, characters, locations, maps, timelines, weapon information, Easter eggs, cross-game lore, help text και interface labels.

Official ονόματα όπως missions, weapons, characters και maps παραμένουν unchanged όπου δεν υπάρχει official Greek title.

</details>

<details>
<summary><strong>Audio και voice notes</strong></summary>

Το Ghost Project περιλαμβάνει generated narration MP3 files για τις δικές του archive summaries.

Το bundled narration καλύπτει:

- Campaign και Extinction story summaries
- campaign mission summaries
- Rorke File archive summaries
- indexed Extinction intel summaries

Το generated narration δεν είναι ripped game audio.

Αν διαθέτεις νόμιμα original recordings, τοποθέτησέ τα στα:

```text
audio/original/rorke/
audio/original/extinction/
```

Το Ghost Project ελέγχει πρώτα local original audio και μετά χρησιμοποιεί bundled narration.

Παράδειγμα:

```text
ήχος rorke RF01
```

Ηχογράφηση προσωπικής σημείωσης:

```text
εγγραφή my_note
```

Στο Termux χρησιμοποιείται Termux:API και απαιτείται η Android Termux:API companion εφαρμογή για microphone access.

Σε supported desktop Linux χρησιμοποιούνται διαθέσιμα Linux audio tools όπως `ffmpeg` ή `arecord`.

</details>

<details>
<summary><strong>Image gallery</strong></summary>

Το Ghost Project περιλαμβάνει JPG reference cards που μπορούν να προβληθούν εύκολα από κινητό/gallery app:

- 36 map JPG files
- 50 weapon JPG files
- 43 character JPG files

Οι εικόνες είναι original Ghost Project reference cards και όχι copied game screenshots ή official artwork.

Άνοιγμα μίας εικόνας:

```text
image maps MAP011
image weapons W007
image characters C01
```

Export gallery:

```text
gallery all
gallery maps
gallery weapons
gallery characters
```

Στο Termux γίνεται export στο Android Pictures όταν υπάρχει storage access.

Σε Ubuntu, Kali Linux και Linux Mint γίνεται export στο Pictures directory του χρήστη.

Missing cards δημιουργούνται ξανά αυτόματα όταν είναι δυνατό.

</details>

<details>
<summary><strong>Εντολές</strong></summary>

```text
help
κατηγορίες
λίστα <category>
δείξε <category> <id>
αναζήτηση <query>
search <category> <query>
ιστορία
χρονολόγιο
στατιστικά <weapon>
σύγκριση <weapon1> <weapon2>
κλάση create
loadout list
loadout show <name>
loadout delete <name>
loadout random
ήχος <category> <id>
image <category> <id>
gallery [category]
άνοιξε <category> <id>
εγγραφή <filename>
πηγές
γλώσσα <en|el>
καθαρισμός
έξοδος
```

Archive categories:

```text
stories
missions
maps
rorke
extinction
characters
locations
timeline
weapons
easter-eggs
connections
```

</details>

<details>
<summary><strong>Δομή project</strong></summary>

```text
Ghost-Project/
├── Ghost Project.py
├── Setup.sh
├── Run.sh
├── modules/
│   ├── archive.py
│   ├── audio.py
│   ├── bootstrap.py
│   ├── display.py
│   ├── gallery.py
│   ├── loadouts.py
│   ├── platforms.py
│   ├── ui.py
│   └── weapon_stats.py
├── data/
│   ├── English archive data
│   ├── loadout_options.json
│   └── el/
│       └── Ελληνικά archive data
├── documents/
│   ├── en/
│   └── el/
├── audio/
├── images/
├── saves/
│   └── .gitkeep
├── tools/
├── requirements.txt
├── CONTENT_NOTICE.md
└── README.md
```

</details>

<details>
<summary><strong>Σημειώσεις δεδομένων</strong></summary>

Τα weapon statistics είναι reference multiplayer values. Attachments και game balance changes μπορούν να αλλάξουν την πραγματική συμπεριφορά ενός όπλου.

Το project κρατά ξεχωριστά campaign lore, Extinction continuity, cross-game references, remade maps και meta-connections αντί να θεωρεί κάθε reference μέρος ενός ενιαίου canon.

Οι public references αποθηκεύονται στο `data/sources.json` και εμφανίζονται με:

```text
πηγές
```

</details>

</details>

---

## Disclaimer / Αποποίηση ευθύνης

Ghost Project is unofficial and is not affiliated with or endorsed by Activision, Infinity Ward, or the Call of Duty rights holders.

Το Ghost Project είναι ανεπίσημο και δεν συνδέεται ούτε υποστηρίζεται από την Activision, την Infinity Ward ή τους δικαιούχους του Call of Duty.
