# Local Android emulator

Goal: open the existing Flutter Instagram concept as an Android app and keep access
to the local Meta + profile-ML backend. No public backend or app-store release.

Acceptance: APK builds, installs and opens in an Android emulator; the app reads
the existing server's profile status and opens the report/reviewer screens.

1. Install official Android command-line tools, platform-tools, emulator, Android 35
   Google APIs x86_64 image, Android 36 compile SDK/build tools and Flutter's NDK.
2. Create a local virtual phone and build the existing app for Android.
3. Forward emulator port 8000 to the host's existing loopback API with `adb reverse`.
4. Launch the app and verify its UI and server connectivity.

The debug manifest permits HTTP only for localhost / 127.0.0.1. No Meta API key is
included in the APK. The backend continues reading the key from its ignored `.env`.
The existing local reviewer define is used only for this development demo.

## Run again

From the project directory in PowerShell:

```powershell
.\scripts\run_android.ps1
# Rebuild after changing Flutter code:
.\scripts\run_android.ps1 -Rebuild
```

The launcher starts the local API if needed, boots `Meta_Demo_API_35` on port 5554,
forwards the API port, installs the debug APK and opens `com.example.social_demo`.
The SDK is configured at `%LOCALAPPDATA%\Android\Sdk` (with the Codex MSIX local-cache
path as a launcher fallback). Microsoft OpenJDK 21.0.13 is installed under
`C:\Users\admin\develop\jdk`; its path is recorded in `outputs/android-setup/jdk-home.txt`.
The existing PyCharm JBR lacks `jlink.exe` and cannot complete the Android JDK image
transform, so Flutter uses the full Microsoft JDK.

The installed command-line tools 23.0 use the new Android CLI. Its package names
use `/`, for example `android sdk install platforms/android-36`; the compatibility
`sdkmanager.bat` wrapper can split old semicolon package names on Windows.

## Verified on 2026-10-28

- Pixel 7 virtual device, Android 15 / API 35, x86_64, WHPX acceleration.
- Debug APK 0.4.0+5 built, installed and launched successfully.
- The native app loaded the existing confirmed profile status from the local API.
- The report form displayed live Meta `muse-spark-1.3` readiness and enabled profile ML.
- Flutter analysis and all 11 widget tests passed; Meta server key was absent from the APK.
- Screenshots, APK hash and device verification: `outputs/android-demo/verification.json`.

Official references: [Android CLI](https://developer.android.com/tools/agents/android-cli),
[emulator acceleration](https://developer.android.com/studio/run/emulator-acceleration),
[Microsoft OpenJDK](https://learn.microsoft.com/en-us/java/openjdk/download).
