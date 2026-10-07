# Dump's Test v17.0 — Mobile Build Guide (Android & iOS)

This guide provides step-by-step instructions for building the **Android APK** and **iOS package** for Dump's Test v17.0.

The codebase has been adapted for mobile compatibility:
- **100% Identical Game**: Same questions, same graphics, same sound effects, same mechanics, same Arabic/English localization.
- **Safe Mobile Storage**: SQLite database (`accounts.db`), scores, and history automatically save to Android internal storage and iOS Documents directory.
- **Soft Keyboard**: Virtual keyboard opens automatically when tapping text input fields.
- **Aspect Ratio**: Locked to 1280x720 landscape with smooth auto-scaling and letterboxing.
- **Android Back Button**: Navigates back gracefully instead of crashing.

---

## Method 1: Cloud Build via GitHub Actions (Recommended — Zero PC Setup)

Because compiling an Android APK requires Linux + Android NDK + Java JDK 17, and compiling iOS strictly requires macOS + Xcode, a pre-configured GitHub Actions workflow is provided at `.github/workflows/build_mobile.yml`.

### Steps:
1. **Push or Upload this folder to GitHub**:
   - Create a new repository on [GitHub](https://github.com).
   - Push your project code to the repository:
     ```bash
     git init
     git add .
     git commit -m "Dump's Test v17.0 Mobile Build"
     git branch -M main
     git remote add origin https://github.com/<your-username>/<your-repo-name>.git
     git push -u origin main
     ```
2. **Trigger the Cloud Build**:
   - Go to your repository on GitHub.
   - Click on the **Actions** tab at the top.
   - In the left sidebar, click **Build Mobile (Android APK & iOS)**.
   - Click **Run workflow** -> **Run workflow**.
3. **Download Your APK and iOS Package**:
   - Once the workflow completes (~10-15 minutes):
   - Click on the completed run.
   - Under **Artifacts**, download:
     - `Dumps_Test_v17.0_Android_APK`: Contains your installable `.apk` file for Android.
     - `Dumps_Test_v17.0_iOS_Package`: Contains the Xcode project ready for macOS / iOS.

---

## Method 2: Local Android APK Build on Windows (via WSL2)

If you prefer building the `.apk` directly on your Windows PC:

### 1. Install WSL (Ubuntu):
Open PowerShell as Administrator and run:
```powershell
wsl --install -d Ubuntu
```
Restart your computer when prompted.

### 2. Install Build Dependencies inside WSL Ubuntu:
Open Ubuntu terminal and run:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git zip unzip autoconf libtool pkg-config zlib1g-dev \
    libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev \
    build-essential ccache openjdk-17-jdk python3-pip python3-virtualenv

pip3 install --upgrade pip buildozer cython
```

### 3. Build the APK:
Navigate to your project folder inside WSL:
```bash
cd "/mnt/d/PythonApplication1/PythonApplication1/.pytest_cache/dump's test_mine"
buildozer android debug
```
The compiled APK will appear in the `bin/` directory:
`bin/dumpstest-17.0-arm64-v8a_armeabi-v7a-debug.apk`

---

## Method 3: Installing and Testing on Mobile Devices

### On Android:
1. Transfer the `.apk` file to your Android phone (via USB, Google Drive, WhatsApp, or email).
2. Tap the APK file to install. If prompted, enable *"Install unknown apps"*.
3. Launch **Dump's Test v17.0**!

### On iOS (iPhone / iPad):
Apple requires all iOS apps to be signed with an Apple ID:
1. **Via Xcode (Mac)**:
   - Extract `Dumps_Test_iOS_Xcode_Project.zip`.
   - Open the `.xcodeproj` file in Xcode.
   - Select your iPhone in the device list.
   - Under *Signing & Capabilities*, select your Apple ID team.
   - Click **Run** (Play button) to install on your iPhone.
2. **Via Sideloading (Windows/Mac with AltStore or Sideloadly)**:
   - Once packaged as `.ipa`, open [Sideloadly](https://sideloadly.io/) or [AltStore](https://altstore.io/).
   - Connect your iPhone with USB, drag the `.ipa` into the app, and enter your Apple ID to sign and install directly.
