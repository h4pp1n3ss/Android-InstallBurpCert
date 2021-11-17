import subprocess

__author__ = "h4pp1n3ss"
__date__ = "18062021"
__version__ = "0.1"
__description__ = '''\ 

        Install burpsuite certificate on Android Emulator
        Tested on: Android Emulator (AVD)
        command: emulator @Pixel_2_XL_API_26 -writable-system -selinux disabled -no-audio -no-boot-anim

        '''

import os
import time
import sys

if not sys.version.startswith('3'):
    print("[!] Error:  This script only work with Python3\n")
    exit(1)


def is_device_up():

    output =  subprocess.getoutput("adb devices")

    if "emulator" in output:
        return True

    else:
        return False

def get_root():

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
    
def download_burp_certificate():

    output = subprocess.getoutput("curl --proxy http://127.0.0.1:8080 -o cacert.der http://burp/cert")

    try:

        os.path.exists('cacert.der')
        subprocess.getoutput("openssl x509 -inform DER -in cacert.der -out cacert.pem")
        subprocess.getoutput("cp cacert.der $(openssl x509 -inform PEM -subject_hash_old -in cacert.pem |head -1).0")

    except Exception as e:
        print(e)
    

    print("[+] Info: Certificate ready to install")


def install_burp_certificate():

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
