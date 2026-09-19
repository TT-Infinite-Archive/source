"""
Build the Panda3D wheel the client is compiled against.
"""
import argparse
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

# Pins
PANDA3D_REPO = 'https://github.com/panda3d/panda3d.git'
PANDA3D_REV = 'ec9ea0a93a7de249efea3f41b4fdf878f5e1650b'
THIRDPARTY_REPO = 'https://github.com/rdb/panda3d-thirdparty.git'
THIRDPARTY_REV = 'b6c433a7c6b3c91369401194314bf026995a48e4'
# The oldest macOS the client supports, as in build_astrond.py
MACOS_DEPLOYMENT_TARGET = '11.0'
# Windows takes its dependencies prebuilt. Upstream's CI builds master against
# the 1.10.16 tools zip-- that's what this is:
WINDOWS_TOOLS = ('https://www.panda3d.org/download/panda3d-1.10.16/'
                 'panda3d-1.10.16-tools-win64.zip')
WINDOWS_SDK = '10'
MSVC_VERSION = '14.3'
DEBIAN_PACKAGES = (
    'build-essential', 'cmake', 'git', 'ca-certificates', 'pkg-config',
    'python3-dev', 'libgl1-mesa-dev', 'libx11-dev', 'libxrandr-dev',
    'libxcursor-dev', 'libfreetype-dev', 'libharfbuzz-dev', 'libvorbis-dev',
    'libopus-dev', 'libopenal-dev', 'libode-dev', 'libssl-dev', 'libjpeg-dev',
    'libpng-dev', 'libtiff-dev', 'libeigen3-dev', 'libavcodec-dev',
    'libavformat-dev', 'libavutil-dev', 'libswscale-dev', 'libswresample-dev',
)
ARCHITECTURES = {'amd64': 'x86_64', 'x64': 'x86_64', 'aarch64': 'arm64'}
THIRDPARTY = (
    'ZLIB', 'PNG', 'JPEG', 'TIFF', 'FREETYPE', 'HARFBUZZ', 'VORBIS', 'OPUS',
    'OPENAL', 'ODE', 'OPENSSL', 'FFMPEG', 'EIGEN',
)
# Renderers, toolkits and formats the client never reaches:
EXCLUDE = (
    'contrib', 'skel', 'speedtree', 'gles', 'gles2', 'egl', 'nvidiacg',
    'openexr', 'artoolkit', 'opencv', 'assimp', 'vrpn', 'fcollada',
    'bullet', 'fmodex', 'squish',
)
if sys.platform != 'linux':
    EXCLUDE += ('x11',)
# Imported by the game:
REQUIRED_MODULES = ('core', 'direct', 'physics', 'ode')
REQUIRED_LIBRARIES = ('openal_audio', 'ffmpeg', 'pandaode', 'pandaphysics')

def run(command, **kwargs):
    print('+ %s' % ' '.join(str(c) for c in command), flush=True)
    return subprocess.run([str(c) for c in command], check=True, **kwargs)

def capture(command):
    return subprocess.run([str(c) for c in command], capture_output=True,
                          text=True).stdout

def hostArch():
    machine = platform.machine().lower()
    return ARCHITECTURES.get(machine, machine)

def defaultJobs():
    cores = os.cpu_count() or 4

    try:
        memory = os.sysconf('SC_PHYS_PAGES') * os.sysconf('SC_PAGE_SIZE')
    except (ValueError, AttributeError, OSError):
        return cores

    return max(1, min(cores, memory // (1536 * 1024 * 1024)))

def pythonPaths():
    import sysconfig

    include = Path(sysconfig.get_paths()['include'])

    if not (include / 'Python.h').exists():
        sys.exit('No Python.h under %s; install the development headers.'
                 % include)

    library = sysconfig.get_config_var('LIBDIR')

    if not library:
        library = Path(sys.base_prefix) / ('libs' if os.name == 'nt' else 'lib')

    return ['--python-incdir', str(include), '--python-libdir', str(library)]

class Build:
    def __init__(self, work, jobs, arch):
        self.work = work
        self.jobs = jobs
        self.arch = arch
        self.source = work / 'panda3d'
        self.thirdparty = work / 'thirdparty'

    def clone(self, repo, destination, rev):
        run(['git', 'init', '-q', str(destination)], cwd=self.work)
        run(['git', '-C', str(destination), 'remote', 'add', 'origin', repo])
        run(['git', '-C', str(destination), 'fetch', '-q', '--depth', '1',
             'origin', rev])
        run(['git', '-C', str(destination), 'checkout', '-q', 'FETCH_HEAD'])

    def dependencies(self):
        if sys.platform == 'win32':
            self.windowsDependencies()
            return

        if sys.platform != 'darwin':
            return

        self.clone(THIRDPARTY_REPO, self.thirdparty, THIRDPARTY_REV)
        build = self.thirdparty / 'build'
        build.mkdir(parents=True, exist_ok=True)

        enabled = ['-DBUILD_%s=ON' % package for package in THIRDPARTY]
        run(['cmake', '..',
             '-DDISABLE_ALL=ON',
             '-DCMAKE_OSX_ARCHITECTURES=%s' % self.arch,
             '-DCMAKE_OSX_DEPLOYMENT_TARGET=%s' % MACOS_DEPLOYMENT_TARGET,
             '-DCMAKE_OSX_SYSROOT=%s' % capture(
                 ['xcrun', '--show-sdk-path']).strip(),
             *enabled], cwd=build)
        run(['make', '-j', str(self.jobs)], cwd=build)

        libraries = self.thirdparty / 'darwin-libs-a'
        missing = [p for p in THIRDPARTY
                   if not (libraries / p.lower()).is_dir()]

        if missing:
            sys.exit('Thirdparty build produced no %s.'
                     % ', '.join(sorted(missing)))

        staged = self.source / 'thirdparty'
        staged.mkdir(parents=True, exist_ok=True)
        shutil.move(str(libraries), str(staged / 'darwin-libs-a'))

    def windowsDependencies(self):
        archive = self.work / 'tools-win64.zip'
        print('+ download %s' % WINDOWS_TOOLS, flush=True)
        urllib.request.urlretrieve(WINDOWS_TOOLS, archive)

        extracted = self.work / 'tools'

        with zipfile.ZipFile(archive) as tools:
            tools.extractall(extracted)

        found = [entry / 'thirdparty' for entry in extracted.iterdir()
                 if (entry / 'thirdparty').is_dir()]

        if len(found) != 1:
            sys.exit('Expected one thirdparty directory in the tools zip, '
                     'got %d.' % len(found))

        shutil.move(str(found[0]), str(self.source / 'thirdparty'))

    def wheel(self, output):
        toolchain = []

        if sys.platform == 'win32':
            toolchain = ['--windows-sdk=%s' % WINDOWS_SDK,
                         '--msvc-version=%s' % MSVC_VERSION]

        run([sys.executable, 'makepanda/makepanda.py',
             '--everything', '--wheel',
             '--threads', str(self.jobs),
             '--outputdir', str(self.work / 'built'),
             *pythonPaths(), *toolchain,
             *('--no-%s' % package for package in EXCLUDE)],
            cwd=self.source)

        wheels = sorted(self.source.glob('*.whl'))

        if len(wheels) != 1:
            sys.exit('Expected one wheel, got %d.' % len(wheels))

        output.mkdir(parents=True, exist_ok=True)
        destination = output / wheels[0].name
        shutil.copy2(wheels[0], destination)

        return destination

def verifyInstalled(arch):
    import glob
    from panda3d.core import (AudioManager, ConfigVariableBool, PandaSystem,
                              PNMFileTypeRegistry, loadPrcFileData)
    import panda3d

    root = os.path.dirname(panda3d.__file__)
    problems = []

    for name in REQUIRED_MODULES:
        try:
            __import__('panda3d.' + name)
        except Exception as error:
            problems.append('panda3d.%s does not import: %s' % (name, error))

    present = os.listdir(root)
    for name in REQUIRED_LIBRARIES:
        if not any(name in entry for entry in present):
            problems.append('no %s library in the wheel' % name)

    registry = PNMFileTypeRegistry.getGlobalPtr()
    types = {registry.getType(i).getName().lower()
             for i in range(registry.getNumTypes())}
    for name in ('jpeg', 'png'):
        if not any(name in known for known in types):
            problems.append('no %s support, which the phase files need' % name)

    loadPrcFileData('', 'audio-library-name p3openal_audio')
    if not AudioManager.createAudioManager().isValid():
        problems.append('the audio manager is not valid')

    loadPrcFileData('', 'dpi-aware #t')
    if not ConfigVariableBool('dpi-aware', False).getValue():
        problems.append('dpi-aware is not honoured, so Retina would not work')

    core = glob.glob(os.path.join(root, 'core*.so')) or \
           glob.glob(os.path.join(root, 'core*.pyd'))
    if core and sys.platform == 'darwin':
        slices = capture(['lipo', '-archs', core[0]]).split()
        if slices != [arch]:
            problems.append('core is %s, not %s'
                            % (' and '.join(slices) or 'unreadable', arch))

    if problems:
        sys.exit('This wheel is not shippable:\n  ' + '\n  '.join(problems))

    print(PandaSystem.getVersionString())

def verify(wheel, arch, work):
    venv = work / 'verify'
    run([sys.executable, '-m', 'venv', str(venv)])
    binary = venv / ('Scripts' if os.name == 'nt' else 'bin')
    run([binary / 'python', '-m', 'pip', 'install', '--quiet',
         '--disable-pip-version-check', str(wheel)])
    run([binary / 'python', __file__, '--verify-installed', arch])

    print('\nPanda3D wheel verified at %s' % wheel)

def installDependencies():
    if sys.platform == 'linux':
        sudo = [] if os.geteuid() == 0 else ['sudo']
        os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
        run(sudo + ['apt-get', 'update', '-qq'])
        run(sudo + ['apt-get', 'install', '-y', '-qq',
                    '--no-install-recommends', *DEBIAN_PACKAGES])

    elif sys.platform == 'darwin':
        run(['brew', 'install', '--quiet', 'cmake', 'pkg-config'])

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path,
                    help='where to write the wheel; omit to only '
                         'install dependencies')
parser.add_argument('--jobs', type=int, default=defaultJobs())
parser.add_argument('--arch', choices=('x86_64', 'arm64'),
                    type=lambda value: ARCHITECTURES.get(value.lower(), value.lower()),
                    help='which architecture to produce. Defaults to the host: '
                         'macOS builds natively on each runner rather than '
                         'producing a universal wheel')
parser.add_argument('--install-deps', action='store_true',
                    help='install the build dependencies first')
parser.add_argument('--keep-work', action='store_true',
                    help='leave the build tree behind for inspection')
parser.add_argument('--verify-installed', metavar='ARCH',
                    help=argparse.SUPPRESS)
parser.add_argument('--print-pin', action='store_true',
                    help='print the pinned Panda3D revision and exit, so CI '
                         'can key the built wheel by it')
args = parser.parse_args()

if args.print_pin:
    print(PANDA3D_REV)
    raise SystemExit(0)

if args.verify_installed:
    verifyInstalled(args.verify_installed)
    raise SystemExit(0)

arch = args.arch or hostArch()

if arch != hostArch():
    sys.exit('Panda3D is built for the host architecture only; run this on a '
             '%s runner.' % arch)

if args.install_deps:
    installDependencies()

    if args.output is None:
        raise SystemExit(0)

if args.output is None:
    parser.error('--output is required unless only installing dependencies')

work = Path(tempfile.mkdtemp(prefix='panda3d-'))
print('Building Panda3D %s for %s in %s\n' % (PANDA3D_REV[:8], arch, work))

try:
    build = Build(work, args.jobs, arch)
    build.clone(PANDA3D_REPO, build.source, PANDA3D_REV)
    build.dependencies()
    wheel = build.wheel(args.output)
    verify(wheel, arch, work)
finally:
    if args.keep_work:
        print('\nBuild tree left at %s' % work)
    else:
        shutil.rmtree(work, ignore_errors=True)