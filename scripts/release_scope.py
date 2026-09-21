"""
Whether a change can ship as a client revision or needs a full release.
"""
import argparse
import ast
import re
import subprocess
import sys
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

# Not Python, and the server image is built from all of it.
SERVER_INPUTS = (
    'astron/dclass/',
    'config/',
    'docker/',
    'Dockerfile',
    'requirements.txt',
)

# Built or run from the repo, shipped to nobody, so they cannot make a
# revision unsafe.
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


def modulePath(module):
    base = ROOT / module.replace('.', '/')

    for candidate in (base.with_suffix('.py'), base / '__init__.py'):
        if candidate.is_file():
            return candidate.relative_to(ROOT)

    return None


def importsOf(path):
    try:
        tree = ast.parse((ROOT / path).read_text(errors='replace'), str(path))
    except (SyntaxError, OSError):
        return set()

    package = '.'.join(path.parts[:-1])
    found = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            # A relative import names its own package; `from x import y` may be
            # naming a module rather than a symbol, so both are followed.
            module = node.module or ''
            roots = ['%s.%s' % (package, module) if node.level else module]

            for root in list(roots):
                if root:
                    found.add(root)
                    found.update('%s.%s' % (root, alias.name)
                                 for alias in node.names)

    return {name for name in found
            if name.split('.')[0] in PACKAGES}


def closure(seeds):
    seen = set()
    queue = [path for path in seeds if (ROOT / path).is_file()]

    while queue:
        path = queue.pop()

        if path in seen:
            continue

        seen.add(path)

        for module in importsOf(path):
            found = modulePath(module)
            if found is not None and found not in seen:
                queue.append(found)

    return seen


def dclassNames():
    """
    What the DC file can ask either side to load by name.
    """
    try:
        text = (ROOT / DC_FILE).read_text(errors='replace')
    except OSError:
        return []

    return re.findall(r'^\s*dclass\s+(\w+)', text, re.MULTILINE)


def dcSeeds(suffixes):
    """
    Modules the DC file names, which nothing has to import for them to load.
    """
    seeds = []

    for name in dclassNames():
        for suffix in suffixes:
            for package in PACKAGES:
                seeds += [path.relative_to(ROOT)
                          for path in (ROOT / package).rglob('%s%s.py' % (name, suffix))]

    return seeds


def serverClosure():
    # Both seedings: the DC file names most of them, and the suffix catches the
    # handful it does not. Over-reaching here only costs a deploy.
    seeds = [Path(entry) for entry in SERVER_ENTRY] + dcSeeds(('AI', 'UD'))

    for package in PACKAGES:
        for pattern in ('**/*AI.py', '**/*UD.py'):
            seeds += [path.relative_to(ROOT)
                      for path in (ROOT / package).glob(pattern)]

    return closure(seeds)


def clientClosure():
    return closure([Path(entry) for entry in CLIENT_ENTRY] + dcSeeds(('',)))


def changedFiles(base, head):
    # No head means the working tree, which is where this gets asked before
    # anything is tagged.
    span = '%s..%s' % (base, head) if head else base

    diff = subprocess.run(
        ['git', 'diff', '--name-only', span],
        cwd=ROOT, capture_output=True, text=True)

    if diff.returncode:
        sys.exit('Could not diff %s:\n%s' % (span, diff.stderr.strip()))

    return [line for line in diff.stdout.splitlines() if line]


def classify(name, server, client):
    """
    Why this file does or does not force a full release.
    """
    if any(name == entry or name.startswith(entry) for entry in NOT_SHIPPED):
        return True, 'nobody ships it'

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


def defaultBase(head):
    """
    A revision is a revision of something: 1.1.0a came after 1.1.0.
    """
    described = subprocess.run(
        ['git', 'describe', '--tags', '--exact-match', head],
        cwd=ROOT, capture_output=True, text=True)

    tag = described.stdout.strip()

    if described.returncode == 0 and tag and tag[-1].isalpha():
        return tag.rstrip('abcdefghijklmnopqrstuvwxyz')

    previous = subprocess.run(
        ['git', 'describe', '--tags', '--abbrev=0', '%s^' % head],
        cwd=ROOT, capture_output=True, text=True)

    if previous.returncode:
        sys.exit('No release tag to compare against; pass --base.')

    return previous.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', help='What to compare against. Defaults to '
                                       'the release this one follows.')
    parser.add_argument('--head', default='', help='Defaults to the working tree.')
    args = parser.parse_args()

    base = args.base or defaultBase(args.head or 'HEAD')
    changed = changedFiles(base, args.head)

    if not changed:
        print('Nothing changed since %s.' % base)
        return 0

    server = serverClosure()
    client = clientClosure()

    verdicts = [(name,) + classify(name, server, client) for name in changed]
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
