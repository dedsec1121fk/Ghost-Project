# Ghost Project Audio / Ήχος

<details>
<summary><strong>English</strong></summary>

Ghost Project includes generated narration MP3 files for its own archive summaries.

Original game voice recordings are not included.

If you legally possess original recordings, place them in:

```text
audio/original/rorke/
audio/original/extinction/
```

Ghost Project checks original local audio first and then falls back to bundled narration.

Play an entry:

```text
audio rorke RF01
```

Record a personal note:

```text
record my_note
```

Termux uses Termux:API for microphone recording. Ubuntu, Kali Linux, and Linux Mint use available Linux audio tools such as `ffmpeg` or `arecord`.

</details>

<details>
<summary><strong>Ελληνικά</strong></summary>

Το Ghost Project περιλαμβάνει generated narration MP3 για τις δικές του περιλήψεις αρχείου.

Δεν περιλαμβάνονται αυθεντικές ripped φωνές από το παιχνίδι.

Αν διαθέτεις νόμιμα αυθεντικές ηχογραφήσεις, τοποθέτησέ τες στα:

```text
audio/original/rorke/
audio/original/extinction/
```

Το Ghost Project ελέγχει πρώτα για αυθεντικό local audio και μετά χρησιμοποιεί το bundled narration.

Αναπαραγωγή:

```text
ήχος rorke RF01
```

Ηχογράφηση προσωπικής σημείωσης:

```text
εγγραφή my_note
```

Στο Termux χρησιμοποιείται Termux:API. Σε Ubuntu, Kali Linux και Linux Mint χρησιμοποιούνται διαθέσιμα Linux audio tools όπως `ffmpeg` ή `arecord`.

</details>
