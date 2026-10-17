# HabitOps AI — Development Runbook

## 1. Purpose

This document describes how to resume local HabitOps AI development on Windows and test the React Native app on a physical Android phone.

It covers:
- Starting Metro.
- Connecting Android through wireless ADB.
- Connecting to the phone using Termux SSH.
- Starting the Flask backend for the current development setup.
- Building, installing, and launching the app.
- Capturing logs and troubleshooting common issues.

**Important:** This is the current development workflow. The future standalone APK must work without Metro, ADB pairing, SSH, or a laptop-hosted Flask server.

## 2. Environment and paths

| Item | Configuration |
|---|---|
| Project root | `C:\Users\Richie\Documents\HabitOps-AI` |
| React Native app | `C:\Users\Richie\Documents\HabitOps-AI\HabitOpsMobile` |
| Backend | `C:\Users\Richie\Documents\HabitOps-AI\backend` |
| Android SDK tools | `C:\Users\Richie\AppData\Local\Android\Sdk\platform-tools` |
| Python virtual environment | `C:\Users\Richie\envs\habitops-lab-python3.14` |
| Android package | `com.habitopsmobile` |
| Metro port | `8081` |
| Flask development port | `5000` |
| Termux SSH port | `8022` |
| Windows laptop LAN IP (previously observed) | `192.168.1.8` |
| Android phone LAN IP (previously observed) | `192.168.1.2` |
| Raspberry Pi LAN IP | `192.168.1.50` |

IPs may change. Retrieve current addresses when necessary.

## 3. Step 1 — Open PowerShell and activate Python

Open PowerShell and run:

```powershell
cd C:\Users\Richie\Documents\HabitOps-AI

C:\Users\Richie\envs\habitops-lab-python3.14\Scripts\Activate.ps1
```

Confirm the project directories exist:

```powershell
Get-ChildItem
```

Expected directories include `agent`, `backend`, `docs`, `infrastructure`, `labs`, and `HabitOpsMobile`.

## 4. Step 2 — Connect the Android phone using wireless ADB

### 4.1 Prepare the phone

On Android:

1. Enable Developer options if they are not already enabled.
2. Open Developer options.
3. Enable **Wireless debugging**.
4. Ensure the phone and Windows laptop are on the same Wi-Fi network.

### 4.2 Find the ADB pairing information

Open Wireless debugging on the phone.

Use **Pair device with pairing code**. Android displays a pairing IP address, pairing port, and pairing code.

In PowerShell, define the ADB command:

```powershell
$adb = "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe"
```

Pair the phone, replacing the example values with those displayed on the phone:

```powershell
& $adb pair <PHONE_IP>:<PAIRING_PORT>
```

Enter the pairing code when prompted.

**Pairing port and connection port are different values.** Do not substitute the Termux SSH port `8022`.

### 4.3 Connect to the paired device

Return to the main Wireless debugging screen and find the current IP address and port.

```powershell
& $adb connect <PHONE_IP>:<CONNECT_PORT>
```

Verify:

```powershell
& $adb devices
```

Expected result: the phone appears with the status `device`.

If the phone is already paired and connected, skip the pairing step and check `adb devices` first.

### 4.4 Set up ADB port forwarding

Forward Metro's port:

```powershell
& $adb reverse tcp:8081 tcp:8081
```

For the current laptop-hosted Flask development setup, you can also forward the API port:

```powershell
& $adb reverse tcp:5000 tcp:5000
```

Debug builds call `http://localhost:5000/api` through this reverse. Standalone release
builds use the embedded Flask service at `http://localhost:8765/api` instead.
The emulator and physical-device debug workflow therefore need the port-5000 reverse
while the laptop Flask server is running.

The second command allows the phone to reach the laptop's port 5000 through ADB reverse forwarding. It is a development convenience, not a requirement for the eventual standalone APK.

Check the configured forwarding:

```powershell
& $adb reverse --list
```

## 5. Step 3 — Start Metro

Open a **dedicated PowerShell window** for Metro.

Run:

```powershell
cd C:\Users\Richie\Documents\HabitOps-AI\HabitOpsMobile

npx react-native start --reset-cache
```

Keep this terminal running while testing the current debug app.

Metro serves the React Native JavaScript bundle on port `8081`. The `--reset-cache` option clears Metro's cache when starting.

### If port 8081 is already occupied

In another PowerShell window:

```powershell
netstat -ano | findstr :8081
```

Inspect the output before terminating any process. If an unwanted process is confirmed to own the listening port, terminate its specific PID:

```powershell
taskkill /PID <PID> /F
```

Then restart Metro.

Do not change to port 8082 as a routine workaround; the established development port is `8081`.

## 6. Step 4 — Start the Flask backend

Open a **separate PowerShell window**.

Activate the virtual environment and navigate to the backend:

```powershell
C:\Users\Richie\envs\habitops-lab-python3.14\Scripts\Activate.ps1

cd C:\Users\Richie\Documents\HabitOps-AI\backend
```

Start Flask:

```powershell
python -m flask --app app run --host 0.0.0.0 --port 5000
```

Keep this terminal running.

The `0.0.0.0` bind makes the development server listen on available network interfaces. Do not use this development configuration as a production deployment.

### Verify the API

From another PowerShell window:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/health
```

The health endpoint should return a successful response.

The current API health check also exercises the database connectivity logic. A successful response should be checked for the reported database status rather than assuming MySQL is available solely because Flask returned HTTP 200.

### Important API configuration note

For the current laptop-hosted development setup, the phone needs a valid route to Flask on port `5000`.

With ADB reverse forwarding enabled, the phone can use a loopback API URL if the app's development configuration supports it. Without that forwarding, a physical phone cannot reach the laptop by using its own `localhost`.

The app's API configuration must agree with the selected development route. Do not assume the current `src/config/api.ts` is correct without checking it.

## 7. Step 5 — Launch HabitOps AI on the phone

Once Metro is running, Flask is ready, and ADB reports the phone as `device`, open another PowerShell window.

Set the ADB variable if it has not already been defined in that window:

```powershell
$adb = "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe"
```

Apply port forwarding:

```powershell
& $adb reverse tcp:8081 tcp:8081
& $adb reverse tcp:5000 tcp:5000
```

Stop any running instance of the app:

```powershell
& $adb shell am force-stop com.habitopsmobile
```

Launch it:

```powershell
& $adb shell monkey -p com.habitopsmobile 1
```

The installed debug app should load its JavaScript from Metro.

If the app has not yet been installed, follow Step 8.

## 8. Step 6 — Build and install the debug APK

This step is only necessary when native Android code or build configuration has changed, or when the APK needs to be installed again.

Open PowerShell:

```powershell
cd C:\Users\Richie\Documents\HabitOps-AI\HabitOpsMobile\android

.\gradlew.bat assembleDebug
```

The expected APK path is:

`HabitOpsMobile\android\app\build\outputs\apk\debug\app-debug.apk`

Install or update the application:

```powershell
$adb = "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe"

& $adb install -r .\app\build\outputs\apk\debug\app-debug.apk
```

If running the install command from the `android` directory, the relative path above is correct.

Then launch the app using Step 5.

**When only JavaScript changes:** Metro can serve those changes without rebuilding the APK, provided the app is connected to Metro and the native dependencies have not changed.

## 9. Step 7 — Connect to the phone using Termux SSH

Termux SSH is useful for shell access to the Android phone. It is separate from ADB.

### 9.1 Start the SSH server on Android

Open Termux on the phone.

If OpenSSH is not installed:

```bash
pkg install openssh
```

Start the SSH server:

```bash
sshd
```

Termux normally uses port `8022` for SSH.

Find the current phone Wi-Fi address:

```bash
ip addr show wlan0
```

Look for the current `inet` address. Do not assume the phone still uses its previously observed address.

### 9.2 Connect from Windows

In PowerShell:

```powershell
ssh -p 8022 u0_a843@<PHONE_IP>
```

Replace `<PHONE_IP>` with the current phone Wi-Fi IP address.

The username `u0_a843` is the previously observed Termux username. If it has changed, verify it inside Termux:

```bash
whoami
```

The first SSH connection may ask you to confirm the host key.

### 9.3 Useful SSH operations

Check the username:

```bash
whoami
```

Check the phone's IP configuration:

```bash
ip addr show wlan0
```

Exit the SSH session:

```bash
exit
```

If SSH fails, verify that `sshd` is running, the phone is reachable on the current Wi-Fi network, and port `8022` is being used. ADB wireless debugging does not automatically start or configure Termux SSH.

## 10. Step 8 — Capture app logs

To clear previous logs:

```powershell
& $adb logcat -c
```

Reproduce the issue on the phone, then inspect React Native JavaScript logs:

```powershell
& $adb logcat -d -s ReactNativeJS:V
```

To inspect broader startup and native errors:

```powershell
& $adb logcat -d -v time |
    Select-String -Pattern "FATAL EXCEPTION|AndroidRuntime|ReactNativeJS|SoLoader|UnsatisfiedLinkError|Network request failed" -Context 3,10
```

If an error occurs, capture the output immediately after reproducing it. Do not clear the logs before capturing the failure.

## 11. Step 9 — Troubleshooting checklist

### ADB does not list the phone

1. Check Wireless debugging on Android.
2. Verify the phone and laptop are on the same network.
3. Check the current connection port on Android.
4. Reconnect with `adb connect`.
5. Run `adb devices` again.

### The app cannot load JavaScript

1. Confirm Metro is still running.
2. Check port `8081`.
3. Run `adb reverse tcp:8081 tcp:8081`.
4. Force-stop and relaunch the app.
5. Inspect React Native logs.

### Saving a workout reports a network error

1. Confirm Flask is running on port `5000`.
2. Test `http://127.0.0.1:5000/api/health` from Windows.
3. Check `adb reverse --list`.
4. Confirm the app's API configuration uses the expected development route.
5. Inspect the Flask terminal for the corresponding request.
6. If Flask receives no request, inspect the app's actual API URL and save handler.

### Flask responds but database operations fail

1. Check the health endpoint's database status.
2. Verify the existing `.env` settings without exposing passwords.
3. Check MySQL availability on the Raspberry Pi.
4. Inspect Flask logs for database errors.

Do not delete or recreate the MySQL container or volume as a troubleshooting shortcut.

## 12. Quick-start checklist

Use this checklist whenever resuming development.

- [ ] Activate the Python virtual environment.
- [ ] Connect the Android phone through wireless ADB.
- [ ] Confirm `adb devices` lists the phone as `device`.
- [ ] Set up ADB reverse forwarding for ports `8081` and `5000`.
- [ ] Start Metro in its own terminal.
- [ ] Start Flask in its own terminal.
- [ ] Verify the Flask health endpoint.
- [ ] Launch HabitOps AI on the phone.
- [ ] Test the required screen or feature.
- [ ] Capture logs if something fails.

## 13. Transition to standalone APK

The above steps describe the existing development workflow only.

Once the standalone release architecture has been implemented and verified, the normal usage workflow must no longer require:

- Metro running on Windows.
- ADB pairing or reverse forwarding.
- Termux SSH.
- Flask running separately on Windows.
- The Windows laptop being available at app launch.

Follow the Change 04 and Change 05 specifications for that transition.

Do not declare the app standalone until it has been installed and launched successfully with Metro stopped and the laptop unavailable.
