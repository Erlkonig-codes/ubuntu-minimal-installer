from storage import *

import subprocess as sp
import os
from bool_confirmation import *

class User:
    def __init__(self, efi_part):
        self.efi_part = efi_part
    def create(self):
        username = input("What would be your username? ")
        os.system("chroot /mnt/ubuntu-installer adduser " + username)
        os.system("chroot /mnt/ubuntu-installer usermod -aG sudo " + username)
        print("")
        print("Please enter your ROOT PASSWORD")
        os.system("chroot /mnt/ubuntu-installer passwd")
        self.user_specifics()
    def user_specifics(self):
        sp.run(['chroot /mnt/ubuntu-installer /usr/sbin/dpkg-reconfigure', 'locales'])
        sp.run(['chroot /mnt/ubuntu-installer /usr/sbin/dpkg-reconfigure', 'tzdata'])
        sp.run(['chroot /mnt/ubuntu-installer /usr/sbin/dpkg-reconfigure', 'keyboard-configuration'])
        self.network()
    def network(self):
        hostname = input("Please provide a hostname for the system... [e.g. ubuntu] ")
        hostname_file = open("/mnt/ubuntu-installer/etc/hostname", "w")
        hostname_file.write(hostname)
        hostname.close()
        hosts_file = open("/mnt/ubuntu-installer/etc/hosts", "a")
        hosts_file.write("\n127.0.1.1   " + hostname)
        hosts_file.close()

        os.system("chroot /mnt/ubuntu-installer systemctl enable NetworkManager")
        self.grub()
    def grub(self):
        grub = input("Would you like to install grub? [Y/y or N/n] ")
        if grub is True:
            os.system("chroot /mnt/ubuntu-installer apt install -y grub2")
            if self.efi_part is True:
                os.system("chroot /mnt/ubuntu-installer grub2-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=GRUB")
                os.system("chroot /mnt/ubuntu-installer grub2-mkconfig -o /boot/grub2/grub.cfg")
            else:
                disk = input("Where would you like to install grub? [e.g. sda or mmcblk]")
                os.system("chroot /mnt/ubuntu-installer grub2-install /dev/" + disk)
                os.system("chroot /mnt/ubuntu-installer grub2-mkconfig -o /boot/grub2/grub.cfg")
            print("Installation is now finished! ")
        else:
            print("Installation is now finished! ")
