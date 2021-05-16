from storage import *

from bool_confirmation import *
import os
import subprocess as sp

class Bootstrap():
    def __init__(self, swap, efi_bool, root):
        self.swap_part = swap
        self.efi_part_bool = efi_bool
        self.root_part = root
    def start(self):
        print("Starting bootstrap!!!")
        time.sleep(1)
        version = input("What ubuntu version would you like to install? [hirsute or focal] ")
        self.ubuntu_version = version
        sp.run(['debootstrap', version,'/mnt/ubuntu-installer'])
        self.fstab()
    def fstab(self):
        fstab = bool_confirmation("Would you like to generate the fstab? [Y/y or N/n] ")
        if fstab is True:
            root_uuid = sp.getoutput("lsblk -o PATH,UUID | grep " + self.root_part)
            root_uuid = root_uuid[5:].replace(self.root_part, '')
            root_uuid = root_uuid[2:]
            if self.efi_part_bool == True:
                efi_uuid = sp.getoutput("lsblk - o PATH,UUID | grep " + efi)
                efi_uuid = efu_uuid[5:].replace(efi, '')
                efi_uuid = efi_uuid[2:]
                os.system("echo 'UUID=" + efi_uuid + "  /boot/efi fat32 defaults 0 1' >> /mnt/ubuntu-installer/etc/fstab")
            if self.swap_part != '':
                os.system("echo '/dev/" + self.swap_part + "  swap    swap    defaults    0 0' >> /mnt/ubuntu-installer/etc/fstab")
            os.system("echo 'UUID=" + root_uuid + "  / ext4 errors=remount-ro 0 1' >> /mnt/ubuntu-installer/etc/fstab")
