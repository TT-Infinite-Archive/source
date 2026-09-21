"""
Whether a change can ship as a client revision or needs a full release.
"""
import argparse
import ast
import io
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SERVER_ENTRY = (
    'toontown/ai/ServiceStart.py',
    'toontown/uberdog/ServiceStart.py',
    'toontown/dedicated/DedicatedStart.py',
)

CLIENT_ENTRY = (
    'toontown/toonbase/ClientStart.py',
)

CLIENT_INPUTS = (
    'config/client.prc',
)

SERVER_INPUTS = (
    'astron/dclass/',
    'config/',
    'docker/',
    'Dockerfile',
    'requirements.txt',
)

NOT_SHIPPED = (
    '.github/',
    'scripts/',
    'doc/',
    'logs/',
    'README.md',
    '.gitignore',
    '.dockerignore',
    'start-server.sh',
    'start-server-maintainer.sh',
)

PACKAGES = ('toontown', 'otp')

DC_FILE = 'astron/dclass/vanilla.dc'


def modulePath(module, root=ROOT):
    base = root / module.replace('.', '/')

    for candidate in (base.with_suffix('.py'), base / '__init__.py'):
        if candidate.is_file():
            return candidate.relative_to(root)

    return None


def absoluteModule(module, package):
    level = len(module) - len(module.lstrip('.'))

    if not level:
        return module

    parts = package.split('.')
    parts = parts[:len(parts) - (level - 1)]
    rest = module[level:]
    return '.'.join(parts + ([rest] if rest else []))


def importsOf(path, root=ROOT):
    try:
        tree = ast.parse((root / path).read_text(errors='replace'), str(path))
    except (SyntaxError, OSError):
        return set()

    package = '.'.join(path.parts[:-1])
    found = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = absoluteModule('.' * node.level + (node.module or ''), package)
            found.add(module)
            found.update('%s.%s' % (module, alias.name) for alias in node.names)

    names = set()

    for name in found:
        parts = name.split('.')
        if parts[0] in PACKAGES:
            names.update('.'.join(parts[:i]) for i in range(1, len(parts) + 1))

    return names


def closure(seeds, root=ROOT):
    seen = set()
    queue = [path for path in seeds if (root / path).is_file()]

    while queue:
        path = queue.pop()

        if path in seen:
            continue

        seen.add(path)

        for module in importsOf(path, root):
            found = modulePath(module, root)
            if found is not None and found not in seen:
                queue.append(found)

    return seen


def dcName(name, suffix):
    name, *suffixes = name.strip().split('/')

    if suffix in suffixes:
        return name + suffix

    if suffix == 'UD' and 'AI' in suffixes:
        return name + 'AI'

    return name


def dcSeeds(suffixes, root=ROOT):
    text = (root / DC_FILE).read_text(errors='replace')
    lines = re.findall(r'^\s*from\s+(\S+)\s+import\s+([^;\n]+)', text, re.MULTILINE)
    names = []

    for suffix in suffixes:
        for module, symbols in lines:
            module = dcName(module, suffix)
            names.append(module)
            names += ['%s.%s' % (module, dcName(symbol, suffix)) for symbol in symbols.split(',')]

    return [path for path in (modulePath(name, root) for name in names) if path is not None]


def serverClosure(root=ROOT):
    seeds = [Path(entry) for entry in SERVER_ENTRY] + dcSeeds(('AI', 'UD'), root)

    for package in PACKAGES:
        for pattern in ('**/*AI.py', '**/*UD.py'):
            seeds += [path.relative_to(root)
                      for path in (root / package).glob(pattern)]

    return closure(seeds, root)


def clientClosure(root=ROOT):
    return closure([Path(entry) for entry in CLIENT_ENTRY] + dcSeeds(('',), root), root)


def closuresAt(ref):
    if not ref:
        return serverClosure(), clientClosure()

    archive = subprocess.run(
        ['git', 'archive', ref] + list(PACKAGES) + [DC_FILE],
        cwd=ROOT, capture_output=True)

    if archive.returncode:
        sys.exit('Could not read %s:\n%s' % (ref, archive.stderr.decode().strip()))

    with tempfile.TemporaryDirectory() as tree:
        with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
            tar.extractall(tree, filter='data')

        return serverClosure(Path(tree)), clientClosure(Path(tree))


def changedFiles(base, head):
    span = '%s..%s' % (base, head) if head else base

    diff = subprocess.run(
        ['git', 'diff', '--name-status', '--no-renames', span],
        cwd=ROOT, capture_output=True, text=True)

    if diff.returncode:
        sys.exit('Could not diff %s:\n%s' % (span, diff.stderr.strip()))

    return [tuple(line.split('\t', 1)) for line in diff.stdout.splitlines() if line]


def classify(name, server, client):
    """
    Why this file does or does not force a full release.
    """
    if any(name == entry or name.startswith(entry) for entry in NOT_SHIPPED):
        return True, 'nobody ships it'

    if name in CLIENT_INPUTS:
        return True, 'only the client loads it'

    if any(name == entry or name.startswith(entry) for entry in SERVER_INPUTS):
        return False, 'the server is built from it'

    path = Path(name)

    if path in server:
        return False, 'the server imports it'

    if path in client:
        return True, 'only the client imports it'

    if name.endswith('.py'):
        return False, 'nothing proves the server leaves it alone'

    return False, 'not known to be client-only'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True, help='The release to compare against.')
    parser.add_argument('--head', default='', help='Defaults to the working tree.')
    args = parser.parse_args()

    base = args.base
    changed = changedFiles(base, args.head)

    if not changed:
        print('Nothing changed since %s.' % base)
        return 0

    server, client = closuresAt(args.head)
    verdicts = []

    if any(status == 'D' for status, name in changed):
        baseServer, baseClient = closuresAt(base)

    for status, name in changed:
        if status == 'D':
            clientOnly, why = classify(name, baseServer, baseClient)
            why = 'deleted; %s in %s' % (why, base)
        else:
            clientOnly, why = classify(name, server, client)

        verdicts.append((name, clientOnly, why))

    blocking = [row for row in verdicts if not row[1]]

    print('%d file(s) changed since %s:\n' % (len(changed), base))

    for name, clientOnly, why in sorted(verdicts, key=lambda row: (row[1], row[0])):
        print('  %-14s %s  (%s)'
              % ('client only' if clientOnly else 'FULL RELEASE', name, why))

    print()

    if blocking:
        print('Verdict: full release. %d file(s) reach the server.'
              % len(blocking))
        return 1

    print('Verdict: this can ship as a client revision.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
