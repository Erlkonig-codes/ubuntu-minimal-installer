from storage import *

import os

class Chroot:
    def __init__(self, swap, version):
        self.ubuntu_version = version
        self.swap_part = swap
        os.system("mount --bind /dev /mnt/ubuntu-installer/dev")
        os.system("mount --bind /proc /mnt/ubuntu-installer/proc")
        os.system("mount --bind /sys /mnt/ubuntu-installer/sys")
        os.system("rm -f /mnt/ubuntu-installer/etc/resolv.conf")
        os.system("mv /etc/resolv.conf /mnt/ubuntu-installer/etc/")
    def work(self):
        #os.system("sudo chroot /mnt/ubuntu-installer /usr/bin/sed -i 's/main/main restricted universe multiverse/g' /etc/apt/sources.list")
        #os.system("echo 'deb-src http://archive.ubuntu.com/ubuntu main restricted universe multiverse' > /etc/apt/sources.list")
        source_list = open("/mnt/ubuntu-installer/etc/apt/sources.list", "w")
        source_list.write("deb http://archive.ubuntu.com/ubuntu " + self.ubuntu_version + " main restricted universe multiverse\n")
        source_list.write("deb-src http://archive.ubuntu.com/ubuntu " + self.ubuntu_version + " main restricted universe multiverse")
        source_list.close()
        os.system("chroot /mnt/ubuntu-installer apt update -y")
        os.system("chroot /mnt/ubuntu-installer apt install -y linux-image-generic nano linux-headers-generic network-manager")
        
        if self.swap_part != '':
            os.system("chroot /mnt/ubuntu-installer mkswap /dev/" + self.swap_part)
            os.system("chroot /mnt/ubuntu-installer swapon -a")
