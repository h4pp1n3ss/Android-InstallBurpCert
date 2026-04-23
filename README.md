# Android-InstallBurpCert

A Python 3 script that automates installing the Burp Suite CA certificate into an Android Emulator (AVD), enabling HTTPS traffic interception.

## Requirements

- Python 3
- `adb` (Android Debug Bridge) in your `PATH`
- `openssl` in your `PATH`
- `curl` in your `PATH`
- Burp Suite running with its proxy listener on `127.0.0.1:8080`
- An Android emulator started with a writable system image

## Usage

**1. Start the emulator with a writable system partition:**

```bash
emulator @Pixel_2_XL_API_26 -writable-system -selinux disabled -no-audio -no-boot-anim
```

**2. Start Burp Suite** and ensure the proxy is listening on `127.0.0.1:8080`.

**3. Run the script:**

```bash
python3 install-burpsuite-ca.py
```

## What the Script Does

1. Verifies an emulator is connected via `adb devices`
2. Gains root access with `adb root` and remounts the system partition as writable
3. Downloads the Burp CA certificate from `http://burp/cert` through the proxy, converts it from DER to PEM, and renames it to the Android-expected hash filename (`<hash>.0`)
4. Pushes the certificate to `/system/etc/security/cacerts/` with `644` permissions

Once complete, the emulator will trust Burp Suite's CA and HTTPS traffic can be intercepted transparently.

## Tested On

- Android Emulator (AVD) — API 26 (Pixel 2 XL)
