# Greek Map assets

This folder belongs to the **Greek Map** option in Ghost Project.

- `GreekOS.py` is the local browser-map server.
- `runtime/vendor/` stores browser libraries such as MapLibre.
- `runtime/http-cache/` stores refreshed styles, sprites, glyphs, terrain metadata and public-data responses.
- `runtime/greekos.sqlite3` stores the offline searchable place index/cache after the weekly refresh or normal use.
- `runtime/greece.mbtiles` is supported when present for a fully local vector basemap.

The application prefers these project-local assets before trying the network. The weekly GitHub Actions workflow refreshes the small redistributable dependencies and public-data snapshots.

## Important size note

A complete street-level, address-level, POI-level, terrain and routing dataset for **all of Greece** is many gigabytes and is not suitable for committing directly to a normal GitHub repository. The project therefore bundles/preloads the application dependencies and compact nationwide place index, caches map data as it is used, and automatically uses `runtime/greece.mbtiles` if you provide a Greece MBTiles package. The map still works online without that optional giant file.

## Featured Greek places

Greek Map ships with a compact built-in index of major/well-known places so they are available even before the wider online/offline indexes finish loading. It includes Athens, Piraeus, Thessaloniki, Patras, Heraklion, Larissa, Volos, Ioannina, Chania, Rhodes, Corfu, Kavala, Alexandroupoli, Serres, Drama, Kozani, Katerini, Trikala, Lamia, Chalkida, Agrinio, Kalamata, Tripoli, Nafplio, Sparta, Rethymno, Agios Nikolaos, Mytilene, Chios, Ermoupoli, Fira, Mykonos, Naxos, Parikia, Zakynthos, Argostoli, Nea Makri, Kalambaka, Metsovo, Parga, Nafpaktos, Monemvasia, Arachova, Meteora, Olympia and Delphi.

The public Wi-Fi/visitor-data availability layer currently includes Athens, Patras, Drama, Alexandroupoli and Lamia. Athens has the directly integrated aggregate station feed; the others remain availability/dashboard markers unless a stable machine-readable feed is available.

## Optional full-Greece offline map

Press the **⇩** button inside Greek Map to open **Offline Maps**. The user can either save only the visible area or choose **Download all Greece**. The full download shows a progress bar, exact percentage, transferred size and transfer speed, and resumes a partial `.part` download when the server supports byte ranges.

The downloaded file is stored at:

`Map Assets/Greek Map/runtime/greece.mbtiles`

Once it is installed, Greek Map automatically uses the MBTiles file as its local OpenMapTiles-compatible basemap.

`.github/workflows/build-greek-map-full.yml` rebuilds this optional downloadable map once a week from the current Geofabrik Greece OpenStreetMap extract using tilemaker and publishes it as the `greek-map-data` GitHub Release. The large map itself is **not** committed to the repository.

## Tiered offline packages

Greek Map now supports five resumable package tiers:

- **Lite — 10 GB budget**
- **Standard — 15 GB budget**
- **Enhanced — 20 GB budget**
- **Detailed — 25 GB budget**
- **Full — 30 GB budget**

The sizes are package budgets/labels; the actual generated MBTiles may be smaller depending on the current source data and build configuration. Packages are published as GitHub Release assets, **not normal Git blobs**. Each package is split into **128 MiB chunks** (below the requested 150 MB ceiling), with a SHA-256 checksum for every chunk plus a checksum for the final MBTiles file.

The in-app downloader is interruption-safe: it resumes a partially downloaded chunk with HTTP Range requests, retries failed transfers, verifies the chunk, appends only verified bytes to the assembling map, records its position, and continues from the next chunk after a restart. A failed upgrade does not replace the currently working `greece.mbtiles`.

`map_packages.json` defines the five tiers. `tools/chunk_greek_map_package.py` creates the release chunks/manifests. The weekly `build-greek-map-full.yml` workflow refreshes the Lite package from the current Greece OSM extract. `publish-greek-map-package.yml` can publish any prepared 15/20/25/30 GB tier from an MBTiles source URL.

### Why the 10 GB base is not stored in normal Git history

GitHub rejects normal Git objects above 100 MiB and strongly recommends keeping repositories below 5 GB. A 10 GB normal Git repository would make cloning and maintenance unreliable, and native `git clone` is not a resumable large-file downloader. The project therefore keeps source code small and uses resumable release chunks for the large offline data.
