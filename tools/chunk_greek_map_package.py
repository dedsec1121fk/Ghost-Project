#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

MIB = 1024 * 1024
DEFAULT_CHUNK_MIB = 128
MAX_CHUNK_MIB = 150


def sha256_file(path: Path, block: int = 8 * MIB) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(block), b''):
            h.update(chunk)
    return h.hexdigest()


def split_package(src: Path, out_dir: Path, tier: str, label: str, target_gb: int, chunk_mib: int, release_tag: str) -> Path:
    if chunk_mib <= 0 or chunk_mib > MAX_CHUNK_MIB:
        raise SystemExit(f'chunk size must be 1..{MAX_CHUNK_MIB} MiB')
    if not src.is_file():
        raise SystemExit(f'input not found: {src}')

    out_dir.mkdir(parents=True, exist_ok=True)
    chunk_bytes = chunk_mib * MIB
    final_hash = hashlib.sha256()
    chunks = []
    total = 0
    index = 0

    with src.open('rb') as f:
        while True:
            data = f.read(chunk_bytes)
            if not data:
                break
            final_hash.update(data)
            total += len(data)
            name = f'greek-map-{tier}.part{index:04d}'
            path = out_dir / name
            path.write_bytes(data)
            chunks.append({
                'name': name,
                'bytes': len(data),
                'sha256': hashlib.sha256(data).hexdigest(),
            })
            print(f'{name}: {len(data) / MIB:.1f} MiB')
            index += 1

    manifest = {
        'schema': 1,
        'tier': tier,
        'label': label,
        'target_gb': target_gb,
        'release_tag': release_tag,
        'final_filename': 'greece.mbtiles',
        'final_bytes': total,
        'final_sha256': final_hash.hexdigest(),
        'chunk_mib': chunk_mib,
        'chunks': chunks,
    }
    manifest_path = out_dir / f'greek-map-{tier}-manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(f'manifest: {manifest_path}')
    print(f'total: {total / (1024**3):.2f} GiB in {len(chunks)} chunks')
    return manifest_path


def main() -> None:
    ap = argparse.ArgumentParser(description='Split a Greek Map MBTiles package into resumable GitHub Release chunks.')
    ap.add_argument('--input', required=True, type=Path)
    ap.add_argument('--output-dir', required=True, type=Path)
    ap.add_argument('--tier', required=True, choices=['lite', 'standard', 'enhanced', 'detailed', 'full'])
    ap.add_argument('--label', default='')
    ap.add_argument('--target-gb', required=True, type=int)
    ap.add_argument('--chunk-mib', default=DEFAULT_CHUNK_MIB, type=int)
    ap.add_argument('--release-tag', default='greek-map-packs')
    args = ap.parse_args()
    label = args.label or args.tier.title()
    split_package(args.input.resolve(), args.output_dir.resolve(), args.tier, label, args.target_gb, args.chunk_mib, args.release_tag)


if __name__ == '__main__':
    main()
