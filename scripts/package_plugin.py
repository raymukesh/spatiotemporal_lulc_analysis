# -*- coding: utf-8 -*-
import configparser
import fnmatch
import os
import zipfile


DEFAULT_EXCLUDES = [
    '.git',
    '.gitignore',
    '.gitattributes',
    '.gitmodules',
    '__pycache__',
]


def _read_metadata(root):
    path = os.path.join(root, 'metadata.txt')
    parser = configparser.ConfigParser()
    parser.read(path, encoding='utf-8')
    name = parser.get('general', 'name', fallback=os.path.basename(root))
    version = parser.get('general', 'version', fallback='0.0.0')
    return name, version


def _load_excludes(root):
    path = os.path.join(root, '.plugin-package-ignore')
    patterns = []
    if not os.path.isfile(path):
        return patterns
    with open(path, 'r', encoding='utf-8') as handle:
        for line in handle:
            text = line.strip()
            if not text or text.startswith('#'):
                continue
            patterns.append(text.replace('\\', '/'))
    return patterns


def _is_excluded(relpath, is_dir, patterns):
    relpath = relpath.replace('\\', '/').lstrip('./')
    parts = [p for p in relpath.split('/') if p]
    if '.git' in parts or '__pycache__' in parts:
        return True
    for pattern in patterns:
        if relpath == pattern or relpath.startswith(pattern.rstrip('/') + '/'):
            return True
        if fnmatch.fnmatch(relpath, pattern):
            return True
        if fnmatch.fnmatch(os.path.basename(relpath), pattern):
            return True
    return False


def create_zip(root):
    name, version = _read_metadata(root)
    dist_dir = os.path.join(root, 'dist')
    os.makedirs(dist_dir, exist_ok=True)
    zip_name = '{}-{}.zip'.format(name, version)
    zip_path = os.path.join(dist_dir, zip_name)

    patterns = DEFAULT_EXCLUDES + _load_excludes(root) + ['dist']

    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(root):
            rel_dir = os.path.relpath(dirpath, root)
            if rel_dir == '.':
                rel_dir = ''
            rel_dir_posix = rel_dir.replace('\\', '/')
            if rel_dir_posix:
                if _is_excluded(rel_dir_posix, True, patterns):
                    dirnames[:] = []
                    continue
            dirnames[:] = [
                d for d in dirnames
                if not _is_excluded(os.path.join(rel_dir_posix, d) if rel_dir_posix else d, True, patterns)
            ]
            for filename in filenames:
                rel_file = os.path.join(rel_dir_posix, filename) if rel_dir_posix else filename
                if _is_excluded(rel_file, False, patterns):
                    continue
                abs_path = os.path.join(dirpath, filename)
                arcname = os.path.join(name, rel_file).replace('\\', '/')
                zf.write(abs_path, arcname)

    return zip_path


def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    zip_path = create_zip(root)
    print('Created:', zip_path)


if __name__ == '__main__':
    main()
