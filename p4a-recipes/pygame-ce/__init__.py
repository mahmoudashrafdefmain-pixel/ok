import os
import re
from os.path import join, exists
import sh
from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pythonforandroid.logger import shprint, info
from pythonforandroid.toolchain import current_directory


class Pygame2Recipe(CompiledComponentsPythonRecipe):
    """
    Recipe to build apps based on SDL2-based pygame-ce.
    """

    version = '2.5.8'
    url = 'https://files.pythonhosted.org/packages/source/p/pygame-ce/pygame_ce-{version}.tar.gz'

    site_packages_name = 'pygame'
    name = 'pygame-ce'

    depends = ['sdl2', 'sdl2_image', 'sdl2_mixer', 'sdl2_ttf', 'setuptools', 'jpeg', 'png']
    call_hostpython_via_targetpython = False
    install_in_hostpython = False

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)

        bdir = self.get_build_dir(arch.arch)
        with current_directory(bdir):
            # 1. Update pyproject.toml: keep version metadata for get_version.py,
            # but replace build-system backend with setuptools to prevent meson invocation
            if exists("pyproject.toml"):
                with open("pyproject.toml", "r", encoding="utf-8") as f:
                    pyproject = f.read()
                pyproject = re.sub(
                    r'\[build-system\].*?build-backend\s*=\s*[\'"].*?[\'"]',
                    '[build-system]\nrequires = ["setuptools>=61.0"]\nbuild-backend = "setuptools.build_meta"',
                    pyproject,
                    flags=re.DOTALL
                )
                with open("pyproject.toml", "w", encoding="utf-8") as f:
                    f.write(pyproject)

            # 2. Delete any meson files so meson-python cannot be invoked
            for mf in ["meson.build", "meson_options.txt"]:
                if exists(mf):
                    os.remove(mf)

            # 3. Patch setup.py:
            # - Ensure working directory stays in bdir regardless of sys.argv[0] (which is _in_process.py under pip)
            # - Force AUTO_CONFIG = False to prevent buildconfig/config.py running desktop unix configs
            # - Bypass Cython so pre-generated C sources are used
            # - Safe header removal so empty/missing scale.h doesn't raise ValueError
            # - Prevent -Werror on CI so Android Clang warnings don't fail the build
            # - Ensure Setup file path is resolved relative to setup.py location
            with open("setup.py", "r", encoding="utf-8") as f:
                setup_content = f.read()

            patch_header = (
                "import sys, os\n"
                "__SETUP_DIR__ = os.path.dirname(os.path.abspath(__file__))\n"
                "os.chdir(__SETUP_DIR__)\n"
                "if __SETUP_DIR__ not in sys.path:\n"
                "    sys.path.insert(0, __SETUP_DIR__)\n"
                "import setuptools\n"
            )

            setup_content = patch_header + setup_content.replace(
                "path = os.path.split(os.path.abspath(sys.argv[0]))[0]",
                "path = os.path.dirname(os.path.abspath(__file__))"
            ).replace(
                "AUTO_CONFIG = not os.path.isfile('Setup') and not no_compilation",
                "AUTO_CONFIG = False"
            ).replace(
                "compile_cython = not no_compilation",
                "compile_cython = False"
            ).replace(
                "headers.remove(os.path.join('src_c', 'scale.h'))",
                "if os.path.join('src_c', 'scale.h') in headers: headers.remove(os.path.join('src_c', 'scale.h'))"
            ).replace(
                "extensions = read_setup_file('Setup')",
                "extensions = read_setup_file(os.path.join(path, 'Setup'))"
            ).replace(
                's_mtime = os.stat("Setup")[stat.ST_MTIME]',
                's_mtime = os.stat(os.path.join(path, "Setup"))[stat.ST_MTIME]'
            ).replace(
                'e.extra_compile_args.append("/WX" if sys.platform == "win32" else "-Werror")',
                'pass'
            )

            with open("setup.py", "w", encoding="utf-8") as f:
                f.write(setup_content)

            # 4. Build Setup file from template
            setup_template = open(join("buildconfig", "Setup.Android.SDL2.in")).read()

            png = self.get_recipe('png', self.ctx)
            png_lib_dir = join(png.get_build_dir(arch.arch), '.libs')
            png_inc_dir = png.get_build_dir(arch.arch)

            jpeg = self.get_recipe('jpeg', self.ctx)
            jpeg_inc_dir = jpeg_lib_dir = jpeg.get_build_dir(arch.arch)

            sdl_mixer_includes = ""
            try:
                sdl2_mixer_recipe = self.get_recipe('sdl2_mixer', self.ctx)
                for include_dir in sdl2_mixer_recipe.get_include_dirs(arch):
                    sdl_mixer_includes += f"-I{include_dir} "
            except Exception:
                pass

            sdl2_image_includes = ""
            try:
                sdl2_image_recipe = self.get_recipe('sdl2_image', self.ctx)
                for include_dir in sdl2_image_recipe.get_include_dirs(arch):
                    sdl2_image_includes += f"-I{include_dir} "
            except Exception:
                pass

            setup_file = setup_template.format(
                sdl_includes=(
                    " -I" + join(self.ctx.bootstrap.build_dir, 'jni', 'SDL', 'include') +
                    " -L" + join(self.ctx.bootstrap.build_dir, "libs", str(arch)) +
                    " -L" + png_lib_dir + " -L" + jpeg_lib_dir + " -L" + arch.ndk_lib_dir_versioned),
                sdl_ttf_includes="-I" + join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_ttf'),
                sdl_image_includes=sdl2_image_includes or ("-I" + join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_image')),
                sdl_mixer_includes=sdl_mixer_includes or ("-I" + join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_mixer')),
                jpeg_includes="-I" + jpeg_inc_dir,
                png_includes="-I" + png_inc_dir,
                freetype_includes=""
            )

            # 5. Filter out any modules whose C source files are not present on disk
            out_lines = []
            for line in setup_file.splitlines():
                stripped = line.strip()
                if stripped and not stripped.startswith('#') and '=' not in stripped:
                    tokens = stripped.split()
                    c_files = [t for t in tokens[1:] if t.endswith('.c')]
                    if any(not exists(c) for c in c_files):
                        out_lines.append('# ' + line)
                        continue
                out_lines.append(line)
            setup_file = '\n'.join(out_lines) + '\n'

            with open("Setup", "w", encoding="utf-8") as f:
                f.write(setup_file)

    def install_python_package(self, arch, name=None, env=None, is_dir=True):
        if env is None:
            env = self.get_recipe_env(arch)
        info(f'Installing {self.name} into site-packages')
        bdir = self.get_build_dir(arch.arch)
        with current_directory(bdir):
            hostpython = sh.Command(self.ctx.hostpython)
            try:
                shprint(hostpython, '-m', 'pip', 'install', 'wheel', 'setuptools')
            except Exception as e:
                pass
            env = env.copy()
            env['PYTHONPATH'] = bdir + ((':' + env['PYTHONPATH']) if 'PYTHONPATH' in env else '')
            shprint(hostpython, '-m', 'pip', 'install', '.',
                    '--no-build-isolation',
                    '--no-deps',
                    '--target', self.ctx.get_python_install_dir(arch.arch),
                    _env=env)

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env['USE_SDL2'] = '1'
        env["PYGAME_CROSS_COMPILE"] = "TRUE"
        env["PYGAME_ANDROID"] = "TRUE"
        env['ANDROID_ROOT'] = join(self.ctx.ndk.sysroot, 'usr')
        bdir = self.get_build_dir(arch.arch)
        env['PYTHONPATH'] = bdir + ((':' + env['PYTHONPATH']) if 'PYTHONPATH' in env else '')
        return env


recipe = Pygame2Recipe()
