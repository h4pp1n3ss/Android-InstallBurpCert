import subprocess
import os
import time
import sys

__author__ = "h4pp1n3ss"
__date__ = "18062021"
__version__ = "0.1"
__description__ = '''\ 

        Install burpsuite certificate on Android Emulator
        Tested on: Android Emulator (AVD)
        command: emulator @Pixel_2_XL_API_26 -writable-system -selinux disabled -no-audio -no-boot-anim

        '''


if not sys.version.startswith('3'):
    print("[!] Error:  This script only work with Python3\n")
    exit(1)


def is_device_up():
    """Check whether an Android emulator is visible to adb.

    Returns:
        bool: True if at least one emulator appears in `adb devices` output, False otherwise.
    """
    output =  subprocess.getoutput("adb devices")

    if "emulator" in output:
        return True

    else:
        return False

def get_root():
    """Restart adb as root and remount the system partition as writable.

    Runs `adb root` to elevate the adb daemon, then retries `adb remount`
    in a loop until the system partition is successfully remounted.
    """
    messages = ['restarting adbd as root', 'adbd is already running as root']
   
 
    output = subprocess.getoutput("adb root")

    for n in messages:
        if n in output:
            print("[+] Info: Already root")

    n = 0
    while True:
        print("[!] Info: Retry {}".format(n))
        output = subprocess.getoutput("adb remount")
        if "remount succeeded" in output:
            print("[+] Info: remount succeded")
            break 
        else:
            print("[-] Error: remount failed, check command manually")
            n += 1
    

def is_burp_reachable(host="127.0.0.1", port=8080):
    """Check whether the Burp Suite proxy listener is accepting connections.

    Args:
        host (str): Proxy host address. Defaults to "127.0.0.1".
        port (int): Proxy port. Defaults to 8080.

    Returns:
        bool: True if a TCP connection to host:port succeeds within 3 seconds, False otherwise.
    """
    import socket
    try:
        with socket.create_connection((host, port), timeout=3):
            return True 
    except (ConnectionRefusedError, socket.timeout, OSError):
        return False

def download_burp_certificate():
    """Download and convert the Burp Suite CA certificate.

    Fetches the DER-encoded certificate from Burp's built-in web server via
    the proxy, converts it to PEM with openssl, and copies it to the
    Android-expected filename derived from the certificate's subject hash
    (e.g. ``9a5ba575.0``). Exits with code 1 if the proxy is unreachable.
    """
    if not is_burp_reachable():
        print("[-] Error: Burp Suite proxy is not reachable at 127.0.0.1")
        exit(1)
    print("[+] Info: Burp Suite proxy is reachable")
    output = subprocess.getoutput("curl --proxy http://127.0.0.1:8080 -o cacert.der http://burp/cert")

    try:

        os.path.exists('cacert.der')
        subprocess.getoutput("openssl x509 -inform DER -in cacert.der -out cacert.pem")
        subprocess.getoutput("cp cacert.der $(openssl x509 -inform PEM -subject_hash_old -in cacert.pem |head -1).0")

    except Exception as e:
        print(e)
    

    print("[+] Info: Certificate ready to install")


def install_burp_certificate():
    """Push the Burp CA certificate to the Android emulator's trusted CA store.

    Determines the hash-named certificate file produced by
    ``download_burp_certificate()``, skips installation if it is already
    present in ``/system/etc/security/cacerts/``, otherwise pushes it via
    ``/sdcard/`` and sets permissions to 644.
    """
    # Check if the certificate exists

    ca = subprocess.getoutput("ls $(openssl x509 -inform PEM -subject_hash_old -in cacert.pem |head -1).0")
    output = subprocess.getoutput("adb shell \"ls /system/etc/security/cacerts\"")

    if ca in output:

        print("[+] Info: Certificate {} already installed".format(ca))
    else:
        subprocess.getoutput("adb push {} /sdcard/".format(ca))
        time.sleep(2)
        
        subprocess.getoutput("adb shell  \"mv /sdcard/{} /system/etc/security/cacerts/\"".format(ca))

        subprocess.getoutput("adb shell  \"chmod 644 /system/etc/security/cacerts/{}\"".format(ca))

        print("[+] Info: Certificate {} installed sucessfully".format(ca))
    
def main():
    """Entry point — orchestrate device check, root, cert download, and installation."""
    if is_device_up():
        print("[*] Info: Device attached")
    else:
        print("[-] Error:  Device not attached")
        exit(-1)

    time.sleep(2)
    get_root()
    time.sleep(2)
    download_burp_certificate()
    time.sleep(2)
    install_burp_certificate()


if __name__ == "__main__":

    main()
