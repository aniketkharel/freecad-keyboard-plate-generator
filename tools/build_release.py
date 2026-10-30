# Copyright (c) 2026 eco-ergo.com
# SPDX-License-Identifier: MIT
"""Build and verify an installation ZIP from an explicit file allowlist."""
from pathlib import Path
import hashlib
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from keyboard_plate import __version__


def main():
    output = ROOT / 'dist'
    output.mkdir(exist_ok=True)
    archive = output / ('keyboard_plate_generator-%s-eco-ergo.com.zip' % __version__)
    files = [ROOT / name for name in (
        'plate_generator.FCMacro', 'README.md', 'LICENSE', 'CHANGELOG.md', 'demo.png')]
    files.extend(sorted((ROOT / 'keyboard_plate').glob('*.py')))
    files.extend(sorted((ROOT / 'examples').glob('*.json')))
    for path in files:
        if path.suffix in ('.py', '.FCMacro'):
            compile(path.read_text(encoding='utf-8-sig'), str(path), 'exec')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for path in files:
            bundle.write(path, path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
        assert set(bundle.namelist()) == {p.relative_to(ROOT).as_posix() for p in files}
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix('.zip.sha256').write_text(digest + '  ' + archive.name + '\n', encoding='utf-8')
    print('%s (%d files)' % (archive, len(files)))
    print('SHA256: ' + digest)


if __name__ == '__main__':
    main()
