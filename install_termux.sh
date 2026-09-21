#!/data/data/com.termux/files/usr/bin/bash
set -e
pkg update -y
pkg install -y python
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo
echo 'Ghost Project installed. / Το Ghost Project εγκαταστάθηκε.'
echo 'Run / Εκτέλεση: python "Ghost Project.py"'
echo
echo 'For Android audio/recording, install the Termux:API companion app.'
echo 'Για ήχο/ηχογράφηση στο Android, εγκατέστησε και την εφαρμογή Termux:API.'
echo 'Ghost Project will install the Termux command-line package automatically when needed.'
