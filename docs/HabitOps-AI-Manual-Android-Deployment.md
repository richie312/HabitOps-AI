# HabitOps AI --- Manual Android Deployment Runbook

**Audience:** Project owner running deployment manually in the future.\
**Purpose:** Build a signed, standalone Android APK, transfer it to the
phone, install it, and verify the app. This is a human runbook, not
instructions for the cloud coding agent.

## 1. Deployment design and important boundaries

-   Windows project root: `C:\Users\Richie\Documents\HabitOps-AI`
-   React Native application:
    `C:\Users\Richie\Documents\HabitOps-AI\HabitOpsMobile`
-   Android package: `com.habitopsmobile`
-   Expected release APK:
    `HabitOpsMobile\android\app\build\outputs\apk\release\app-release.apk`
-   MySQL database: `habitops`, on the Raspberry Pi at
    `192.168.1.50:3306`, in the existing Docker container named `mysql`.
-   The app is intended to bundle the React Native JavaScript and start
    the embedded Python/Flask service on the phone at `127.0.0.1:8765`.
    Flask then connects from the phone to the Pi's MySQL service.
    Offline records should be stored in SQLite and synced when
    connectivity returns.

**Do not delete, recreate, prune, or replace the MySQL container or its
persistent volume `mysql_ubuntu_rasp_device`.** Do not expose MySQL to
the public internet. The phone and Pi must be able to communicate on the
same trusted network/VPN.

A successful Gradle build proves only that an APK was produced. It does
**not** prove that the app starts, the embedded Flask service works, the
phone can reach MySQL, or offline sync works. Complete the device
verification below before treating a build as deployed.

## 2. One-time prerequisites

On Windows, open PowerShell and confirm the project exists:

``` powershell
Set-Location "$env:USERPROFILE\Documents\HabitOps-AI\HabitOpsMobile"
Test-Path .\android\gradlew.bat
node --version
java -version
```

Install/configure Android Studio and the Android SDK if they are not
already working. The project should have the Android SDK available at:

`C:\Users\Richie\AppData\Local\Android\Sdk`

Use a JDK version supported by this repository's Android Gradle Plugin.
If the build fails with a Java/Gradle compatibility error, inspect the
project's Gradle/AGP versions and installed JDKs; do not randomly
upgrade Gradle or the Android Gradle Plugin.

### Release signing key

The private release keystore is expected at:

`C:\Users\Richie\.habitops\habitops-release.jks`

Keep a secure backup of this keystore and its passwords. If you lose the
key, you may not be able to update the installed app with a normally
signed update. Never commit the keystore or passwords to Git, and never
paste passwords into chat or logs.

Create or edit this file locally:

`%USERPROFILE%\.gradle\gradle.properties`

It must contain these property names, with the real values filled in
locally:

``` properties
HABITOPS_RELEASE_STORE_FILE=C:/Users/Richie/.habitops/habitops-release.jks
HABITOPS_RELEASE_STORE_PASSWORD=YOUR_REAL_KEYSTORE_PASSWORD
HABITOPS_RELEASE_KEY_ALIAS=habitops-release
HABITOPS_RELEASE_KEY_PASSWORD=YOUR_REAL_KEY_PASSWORD
HABITOPS_MYSQL_PASSWORD=YOUR_REAL_HABITOPS_APP_MYSQL_PASSWORD
```

Do not include quotes around values unless the build configuration
explicitly requires them. Do not share the file or its contents.
`HABITOPS_MYSQL_PASSWORD` is a client credential, not a secure secret
vault: credentials embedded in an APK can be extracted. This setup is
suitable only for controlled private use; do not distribute the APK
publicly with a reusable database password.

## 3. Before each deployment

1.  Ensure the Raspberry Pi is powered on and connected to the trusted
    network.
2.  Confirm the existing `mysql` container is running; do not recreate
    it.
3.  Confirm the `habitops` database and expected tables exist:
    `activities`, `vitals`, and `activity_route_points`.
4.  Confirm the database account `habitops_app` is allowed to connect
    from the phone's network address. A grant restricted to the Windows
    laptop's IP will not permit a connection from the phone. Only change
    grants if an actual MySQL access-denied error confirms this is the
    issue; grant only the privileges needed for the `habitops` database.
5.  If the Pi's IP changes, update the app's configured MySQL host and
    rebuild. Do not use the Windows laptop as the production API host.
6.  Ensure the phone can reach `192.168.1.50` on TCP port `3306` on the
    trusted LAN/VPN. If the app is used away from home, the Pi must be
    reachable through a secure VPN; a private LAN IP alone will not work
    over mobile data.
7.  Keep a copy of the previous working APK until the new version passes
    all checks.

## 4. Build a signed release APK

Open PowerShell. Run this once as a single deployment operation; it does
not run the JavaScript test suite.

``` powershell
$ErrorActionPreference = "Stop"
Set-Location "$env:USERPROFILE\Documents\HabitOps-AI\HabitOpsMobile"

$props = Join-Path $env:USERPROFILE ".gradle\gradle.properties"
$keystore = "$env:USERPROFILE\.habitops\habitops-release.jks"

if (-not (Test-Path $props)) { throw "Missing $props. Complete the one-time signing setup in Section 2." }
if (-not (Test-Path $keystore)) { throw "Missing release keystore: $keystore" }

$required = @(
  "HABITOPS_RELEASE_STORE_FILE",
  "HABITOPS_RELEASE_STORE_PASSWORD",
  "HABITOPS_RELEASE_KEY_ALIAS",
  "HABITOPS_RELEASE_KEY_PASSWORD",
  "HABITOPS_MYSQL_PASSWORD"
)
$raw = Get-Content $props -Raw
foreach ($name in $required) {
  if ($raw -notmatch "(?m)^\s*$([regex]::Escape($name))\s*=\s*\S+") {
    throw "Missing or empty $name in $props. Fix it locally; do not print or share the value."
  }
}
if ($raw -match "(?im)^\s*(HABITOPS_RELEASE_STORE_PASSWORD|HABITOPS_RELEASE_KEY_PASSWORD|HABITOPS_MYSQL_PASSWORD)\s*=\s*(YOUR_REAL|CHANGE_ME|REPLACE_ME)") {
  throw "A signing/database property still contains a placeholder. Replace it locally."
}

Push-Location .\android
try {
  .\gradlew.bat validateReleaseConfiguration
  if ($LASTEXITCODE -ne 0) { throw "Release configuration validation failed." }

  .\gradlew.bat clean assembleRelease
  if ($LASTEXITCODE -ne 0) { throw "Release APK build failed." }
}
finally {
  Pop-Location
}

$apk = Join-Path $PWD "android\app\build\outputs\apk\release\app-release.apk"
if (-not (Test-Path $apk)) { throw "Build command finished but APK was not found at $apk" }
Get-Item $apk | Select-Object FullName, Length, LastWriteTime
Get-FileHash $apk -Algorithm SHA256
```

Save the APK path, file size, and SHA-256 hash printed by the final
commands. If the command fails, use the **first actual Gradle error** to
diagnose the failure. Do not repeatedly run `npm ci`, `npm test`, or
`npm audit fix --force` as a response to a Gradle build error.

## 5. Transfer the APK to an Android phone using Termux SSH

This workflow avoids requiring an ADB connection to install the APK.

### On the phone (Termux)

Install and start OpenSSH if not already configured:

``` sh
pkg install openssh
passwd
sshd
whoami
ip -4 addr show wlan0
```

Record the Termux username and the phone's current Wi-Fi IP address.
Termux's SSH server normally listens on port `8022`. Keep the phone and
Windows computer on the same trusted Wi-Fi network.

### On Windows PowerShell

Replace `PHONE_USER` and `PHONE_IP` with the values reported by Termux:

``` powershell
Set-Location "$env:USERPROFILE\Documents\HabitOps-AI\HabitOpsMobile"
$apk = (Resolve-Path ".\android\app\build\outputs\apk\release\app-release.apk").Path
scp -P 8022 $apk "PHONE_USER@PHONE_IP:storage/shared/Download/app-release.apk"
Get-FileHash $apk -Algorithm SHA256
```

Enter the Termux password when prompted. If `scp` fails, verify the
current phone IP, username, SSH service, port, and same-Wi-Fi
connection. Do not expose SSH to the internet.

### Verify on the phone (Termux)

``` sh
sha256sum ~/storage/shared/Download/app-release.apk
```

Compare this hash with the Windows SHA-256 output. They must match. If
they do not match, do not install the file; transfer it again.

## 6. Install and verify on the phone

1.  Open the phone's Downloads folder and tap `app-release.apk`.
2.  If Android asks, allow installation from the file manager used to
    open the APK. Only allow this for the trusted installer and disable
    the permission again afterward if desired.
3.  Install the APK. If Android refuses an update because the signing
    certificate differs, do not uninstall immediately if the app
    contains local data. Confirm that you are using the original
    keystore before proceeding.
4.  Launch HabitOps AI. It should start without Metro, a laptop
    development server, or USB/ADB pairing.
5.  Check the main screen and exercise the core flows.
6.  Create a test activity and a test vital record while the Pi is
    reachable. Confirm the records appear in the MySQL database.
7.  Turn off Wi-Fi/mobile data and create another test record. Confirm
    the app clearly reports or retains the offline record as designed.
8.  Restore connectivity. Confirm the queued record synchronizes and
    appears once in MySQL (no duplicate record after reopening the app).
9.  Force-stop and reopen the app; confirm records remain.
10. If any step fails, record the exact on-screen error and relevant
    app/Gradle logs before changing configuration.

**Important:** The embedded service and offline-sync behavior have not
been considered verified merely because the APK builds. Complete the
checks above on the actual phone.

## 7. Release checklist

-   [ ] Signed release build completed.
-   [ ] APK path, size, and SHA-256 recorded.
-   [ ] Transfer SHA-256 matches.
-   [ ] APK installs and launches without Metro or ADB.
-   [ ] Embedded Flask service becomes ready.
-   [ ] Phone can connect to MySQL on the Pi over the trusted
    network/VPN.
-   [ ] Activity and vital writes persist in MySQL.
-   [ ] Offline writes persist locally.
-   [ ] Reconnection sync works without duplicates.
-   [ ] Existing MySQL container and persistent volume remain intact.
-   [ ] Keystore and passwords remain private and backed up.
-   [ ] Previous working APK retained until the new version is accepted.

## 8. When the next deployment is needed

Repeat Sections 3--7. Keep the same release keystore for updates. If you
change native Android code, Python dependencies, embedded Flask startup,
database host configuration, or release signing configuration, build a
new APK and rerun the complete phone verification. Do not assume a
successful build proves runtime functionality.

## 9. Troubleshooting notes

-   **`validateReleaseConfiguration` reports a missing property:** fix
    the named property in `%USERPROFILE%\.gradle\gradle.properties`; do
    not print passwords.
-   **Keystore not found:** confirm `HABITOPS_RELEASE_STORE_FILE` points
    to the existing `.jks` file.
-   **Gradle/Java compatibility error:** use a JDK compatible with this
    repository's Gradle/Android Gradle Plugin versions. Avoid blind
    dependency upgrades.
-   **APK builds but app cannot reach MySQL:** verify phone-to-Pi
    network reachability, Pi firewall, MySQL bind/listen address, port,
    configured host/password, and the MySQL account's host grant. Do not
    open MySQL to the public internet.
-   **`Access denied for user 'habitops_app'`:** verify the password and
    the account host grant for the phone's source IP. Make only the
    narrow database-specific grant change needed.
-   **App starts but records do not save offline:** offline
    persistence/sync is a runtime behavior to diagnose; a successful APK
    build does not prove it works.
-   **APK cannot update the installed app:** check package ID and
    signing key before uninstalling. Uninstalling can delete app-local
    data.
-   **Never remove the MySQL volume as a troubleshooting step.**
