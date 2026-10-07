[app]

# (str) Title of your application
title = Dump's Test v17.0

# (str) Package name
package.name = dumpstest

# (str) Package domain (needed for android/ios packaging)
package.domain = org.dumpstest.master

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,mp3,mpeg,wav,qbank,json,db,ico,csv,txt

# (list) List of directory to include
source.include_patterns = assets/*,sound_effect/*,question_bank/*,game/*,network/*,security/*,ui/*

# (list) List of exclusions using pattern matching
source.exclude_patterns = test_*,validate_*,*.pyc,*.spec,*.bat,build.bat,crash_log.txt,suggestions.txt

# (list) List of directory to exclude
source.exclude_dirs = tests,tools,build,dist,.pytest_cache,__pycache__

# (str) Application versioning
version = 17.0

# (list) Application requirements
requirements = python3,pygame-ce,arabic-reshaper,python-bidi,openpyxl,sqlite3

# (str) Presplash of the application
presplash.filename = %(source.dir)s/icon.png

# (str) Icon of the application
icon.filename = %(source.dir)s/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = sensorLandscape

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (string) Presplash background color (for android toolchain)
android.presplash_color = #140f23

# (list) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE,VIBRATE

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK / AAB will support.
android.minapi = 24

# (str) Android NDK version to use
android.ndk = 25b

# (bool) If True, then skip trying to update the Android sdk
android.skip_update = False

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) Bootstrap to use for android build
p4a.bootstrap = sdl2

# (str) python-for-android branch to use
p4a.branch = develop

# (int) Android logcat filters to use
android.logcat_filters = *:S python:D

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
