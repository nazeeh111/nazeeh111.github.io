#!/usr/bin/env python3
"""Validate, render and publish a fresh, complete static site generation."""
import argparse
import hashlib
import types
import io
import json
import os
import tempfile
from pathlib import Path
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


def snapshot(root):
    # This reviewed inventory is the public source of truth, including in an
    # extracted archive without Git. Unlisted local files are never read.
    inventory_path = root / 'scripts/site-inputs.json'
    if (root / 'scripts').is_symlink() or inventory_path.is_symlink():
        raise ValueError('Input inventory must not be a symlink')
    inventory_bytes = inventory_path.read_bytes()
    inventory = json.loads(inventory_bytes)
    if not isinstance(inventory, dict) or set(inventory) != {'schema', 'files'} or inventory['schema'] != 'portfolio-public-inputs-v1':
        raise ValueError('Invalid public input inventory')
    names = inventory['files']
    if not isinstance(names, list) or not names or len(names) > 10000 or any(not isinstance(n, str) for n in names):
        raise ValueError('Invalid public input list')
    if names != sorted(set(names)) or 'scripts/site-inputs.json' not in names:
        raise ValueError('Public input list must be sorted, unique and include itself')
    files = {}
    for name in names:
        parts = name.split('/')
        if not name or any(part in ('', '.', '..', '.git', '__pycache__') for part in parts) or '\\' in name:
            raise ValueError('Invalid public input path')
        path = root
        for part in parts:
            path = path / part
            if path.is_symlink():
                raise ValueError(f'Symlinks are not supported in source: {name}')
        if not path.is_file():
            raise ValueError(f'Missing regular public input: {name}')
        files[name] = inventory_bytes if name == 'scripts/site-inputs.json' else path.read_bytes()
    return files


def module(name, source, path):
    obj = types.ModuleType(name)
    obj.__file__ = str(path)
    exec(compile(source, str(path), 'exec'), obj.__dict__)
    return obj


def prepare(files):
    catalog = json.loads(files['research/catalog.json'])
    manifest = json.loads(files['research/manifest.json'])
    projects = json.loads(files['projects.json'])
    if not isinstance(catalog, list) or not catalog or not isinstance(manifest.get('files'), list):
        raise ValueError('Invalid catalog or file manifest')
    records = manifest['files']; ids = [row['slug'] for row in records]
    studies = [study['id'] for study in catalog]
    supplements = [item['id'] for study in catalog for item in study['supplements']]
    all_ids = studies + supplements
    if any(not isinstance(x, str) or not SLUG.fullmatch(x) for x in all_ids + ids):
        raise ValueError('Invalid slug')
    if len(set(all_ids)) != len(all_ids) or len(set(ids)) != len(ids):
        raise ValueError('Duplicate study, supplement or manifest slug')
    if set(ids) != set(all_ids):
        raise ValueError('Catalog and manifest references differ')
    if 'counterpatch' not in studies:
        raise ValueError('Historical counterpatch route requires its study')
    by_id = {row['slug']: row for row in records}
    names = [p['name'] for p in projects['projects']]
    urls = [p['url'] for p in projects['projects']]
    if len(set(names)) != len(names) or len(set(urls)) != len(urls):
        raise ValueError('Duplicate portfolio project name or URL')
    formats = {study['id']: ('md' if study.get('format') == 'Markdown' else 'pdf') for study in catalog}
    formats.update({slug:'pdf' for slug in supplements})
    expected_archive = {}
    for slug in all_ids:
        ext = formats[slug]; name = f'research/papers/{slug}.{ext}'
        data = files[name]; info = by_id[slug]
        if len(data) != info['bytes'] or hashlib.sha256(data).hexdigest() != info['sha256']:
            raise ValueError(f'Paper size or digest differs: {slug}')
        if ext == 'pdf':
            source = f'research/sources/{slug}.zip'
            if source not in files:
                raise ValueError(f'Missing manuscript source: {slug}')
            with zipfile.ZipFile(io.BytesIO(files[source])) as manuscript:
                if manuscript.testzip() is not None:
                    raise ValueError(f'Invalid manuscript archive: {slug}')
        expected_archive['research-papers/' + Path(name).name] = data
    expected_archive['research-papers/manifest.json'] = files['research/manifest.json']
    for study in catalog:
        figure = study['article']['figure']
        if not isinstance(figure, str) or not figure.startswith('/') or figure[1:] not in files:
            raise ValueError(f'Missing figure for {study["id"]}')
    archive = files['research/all-papers.zip']
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        entries = z.namelist()
        if len(entries) != len(set(entries)) or set(entries) != set(expected_archive):
            raise ValueError('Paper collection archive member set differs')
        for name, data in expected_archive.items():
            if z.read(name) != data:
                raise ValueError(f'Paper collection archive differs: {name}')
    return catalog, by_id, formats, projects, archive


def stamp_asset_urls(outputs):
    """Give shared browser assets cache identities derived from their actual bytes."""
    assets = ('assets/design/portfolio.css', 'assets/portfolio.js',
              'assets/work.js', 'assets/social/portfolio-preview.png')
    result = dict(outputs)
    for asset in assets:
        revision = hashlib.sha256(outputs[asset]).hexdigest()[:16].encode('ascii')
        pattern = re.compile(rb'(<(?:link|script|meta)\b[^>]*?[ \t\r\n](?:href|src|content)="(?:https://nazeeh111\.github\.io)?/'
                             + re.escape(asset.encode('ascii'))
                             + rb')(?:\?v=[a-f0-9]{16})?(")')
        for name, data in result.items():
            if name.endswith('.html') and not name.startswith('scripts/'):
                result[name] = pattern.sub(lambda match: match[1] + b'?v=' + revision + match[2], data)
    return result


def render(files):
    catalog, by_id, formats, projects, archive = prepare(files)
    research = module('research_builder', files['scripts/build-research.py'], ROOT / 'scripts/build-research.py')
    portfolio = module('portfolio_builder', files['scripts/build-portfolio.py'], ROOT / 'scripts/build-portfolio.py')
    outputs = dict(files)
    outputs.update(research.render(catalog, by_id, sum(v == 'pdf' for v in formats.values()),
                                   sum(v == 'md' for v in formats.values()), len(archive)))
    outputs['index.html'] = portfolio.render(projects, files['scripts/portfolio.html'].decode('utf-8'))
    cases = json.loads(files['cases.json'])
    work = module('work_builder', files['scripts/build-work.py'], ROOT / 'scripts/build-work.py')
    case_builder = module('case_builder', files['scripts/build-cases.py'], ROOT / 'scripts/build-cases.py')
    outputs['work/index.html'] = work.render(projects, files['scripts/work.html'].decode('utf-8'), cases)
    outputs.update(case_builder.render(cases, files))
    return stamp_asset_urls(outputs)


def publish(out, files):
    out = Path(out).resolve()
    if out == ROOT or ROOT in out.parents:
        raise ValueError('Output must be a fresh directory outside the source tree')
    if '.build-manifest.json' in files:
        raise ValueError('Source contains reserved build manifest')
    manifest = {'schema': 'portfolio-static-build-v1', 'files': {name: {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()} for name, data in sorted(files.items())}}
    out.mkdir(parents=True, exist_ok=False)
    for name, data in sorted(files.items()):
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write(data)
    fd, temporary = tempfile.mkstemp(prefix='.build-manifest.', suffix='.pending', dir=out)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(manifest, stream, indent=2, sort_keys=True)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, out / '.build-manifest.json')
    finally:
        os.unlink(temporary)
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True, help='Fresh output directory outside the source checkout')
    args = parser.parse_args(argv)
    try:
        files = snapshot(ROOT)
        generated = render(files)
        out = publish(args.out, generated)
        print(f'Built {len(generated)} files into {out}')
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        print(f'Build refused: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    raise SystemExit(main())
