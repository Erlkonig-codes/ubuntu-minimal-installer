#!/usr/bin/env python3

import subprocess as sp
import os
import time
import bool_confirmation

supported_os = ['Fedora', 'Ubuntu', 'ubuntu', 'Arch', 'Manjaro', 'Debian']

def bool_confirmation(confirmation_question):
    answer = input(confirmation_question)
    bool_data = answer.lower() == 'y'
    return bool_data

def ask_question(confirmation_question):
        answer = input(confirmation_question)
        return answer

class Installer:
    def __init__(self):
        os_type_literal = sp.getoutput("grep '^NAME' /etc/os-release")
        os_type_literal = os_type_literal[5:]
        if os_type_literal in supported_os:
            self.os_type = os_type_literal
        else:
            print("Your Linux Distro is not supported yet!")
        self.check_debootstrap()
    def check_debootstrap(self):
        if self.os_type == "Fedora":
            dbs_check = sp.getoutput("dnf list installed | grep debootstrap")
            dbs_check = dbs_check[:11]
            if dbs_check == "debootstrap":
                print("Debootstrap is found!")
                self.debootstrap_status = True
            else:
                print("Debootstrap is not installed!")
                confirm = bool_confirmation("Would you like to install deboostrap? [Y/y or N/n] ")
                if confirm is True:
                    print("Deboostrap will be installed!")
                    sp.run(['dnf', 'install', '-y', 'debootstrap'])
                else:
                    print("Debootstrap is not found!!! Exiting!")

class Storage:
    def __init__(self):
        pass
    def storage_devices(self):
        sp.run(['lsblk', '-o', 'PATH,FSTYPE'])
        blocks_path = sp.getoutput("lsblk -o PATH")
        blocks_path = blocks_path.replace("/dev/","")
        print('')
        print('')
        media_choice = ask_question("Would you like to create a new partition, format an existing one, or proceed with preconfigured partitions? [Create/create or Format/format or Proceed/proceed] ")
        if media_choice.lower() == 'create':
            print("Creation is unavailable for now... Please create partitions for yourself for the mean time...")
            time.sleep(3)
            self.storage_devices()
            # creation_method = ask_question("Would you like to use GParted (GUI) or gdisk (TUI)? [gparted or gdisk] ")
            # if creation_method == 'gparted':
            #     sp.run(['gparted'])
            #     # os.system("gparted >> /dev/null")
            #     self.mount_stage()
            # elif creation_method == 'gdisk':
            #     disk = ask_question("What disk would you like to create partitions in? [sda, mmcblk5] ")
            #     os.system("gdisk " + disk)
            # else:
            #     print('No choice named' + creation_method)
            #     self.storage_devices()
        elif media_choice.lower() == 'format':
            format_drive = ask_question("Which partition would you like to format and use? [E.g. sda5 or sdc1] ")
            if format_drive in blocks_path:
                format_confirmation = bool_confirmation("Would you like to proceed formatting " + format_drive + " (ext4 is the only choice for now)? [Y/y or N/n] ")
                if format_confirmation is True:
                    sp.run(['mkfs.ext4', '/dev/' + format_drive])
                    self.mount_stage()
        elif media_choice.lower() == 'proceed':
            self.mount_stage()
        else:
            print("Unknown choice... Try again")
    def mount_stage(self):
        os.system("mkdir /mnt/ubuntu-installer")
        root = ask_question("Which is the root partition? [e.g. sda1] ")
        swap = ask_question("Which is the swap partition? (Leave blank if you did not create one) ")
        global efi
        efi = ask_question("Which is the efi partition to be mounted at /boot/efi? (Leave blank if you boot in legacy BIOS mode) ")
        
        os.system("mount /dev/" + root + " /mnt/ubuntu-installer")
        if efi != '':
            os.system("mkdir -p /mnt/ubuntu-installer/boot/efi")
            os.system("mount /dev" + efi + " /mnt/ubuntu-installer/boot/efi")
            self.efi_partition = True
        else:
            self.efi_partition = False
        self.swap_partition = swap
        self.root_partition = root

class Bootstrap():
    def __init__(self, swap, efi_bool, root):
        self.swap_part = swap
        self.efi_part_bool = efi_bool
        self.root_part = root
    def start(self):
        print("Starting bootstrap!!!")
        time.sleep(1)
        version = ask_question("What ubuntu version would you like to install? [hirsute or focal] ")
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

class Chroot:
    def __init__(self, swap):
        self.swap_part = swap
        os.system("mount --bind /dev /mnt/ubuntu-installer/dev")
        os.system("mount --bind /proc /mnt/ubuntu-installer/proc")
        os.system("mount --bind /sys /mnt/ubuntu-installer/sys")
        os.system("rm -f /mnt/ubuntu-installer/etc/resolv.conf")
        os.system("mv /etc/resolv.conf /mnt/ubuntu-installer/etc/")
        os.system("chroot /mnt/ubuntu-installer /bin/bash << 'EOT'")
    def work(self):
        os.system("echo 'deb http://archive.ubuntu.com/ubuntu main restricted universe multiverse' > /etc/apt/sources.list")
        os.system("echo 'deb-src http://archive.ubuntu.com/ubuntu main restricted universe multiverse' > /etc/apt/sources.list")
        os.system("apt update -y")
        os.system("apt install -y linux-kernel-generic nano linux-headers-generic network-manager")
        
        if self.swap_part != '':
            os.system("mkswap /dev/" + self.swap_part)
            os.system("swapon -a")

class User:
    def __init__(self, efi_part):
        self.efi_part = efi_part
    def create(self):
        username = ask_question("What would be your username? ")
        os.system("adduser " + username)
        os.system("usermod -aG sudo " + username)
        print("")
        print("Please enter your ROOT PASSWORD")
        os.system("passwd")
        self.user_specifics()
    def user_specifics(self):
        sp.run(['dpkg-reconfigure', 'locales'])
        sp.run(['dpkg-reconfigure', 'tzdata'])
        sp.run(['dpkg-reconfigure', 'keyboard-configuration'])
        self.hostname()
    def hostname(self):
        hostname = ask_question("Please provide a hostname for the system... [e.g. ubuntu] ")
        os.system("systemctl enable NetworkManager")
        self.grub()
    def grub(self):
        grub = ask_question("Would you like to install grub? [Y/y or N/n] ")
        if grub is True:
            os.system("apt install -y grub2")
            if self.efi_part is True:
                os.system("grub2-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=GRUB")
                os.system("grub2-mkconfig -o /boot/grub2/grub.cfg")
            else:
                disk = ask_question("Where would you like to install grub? [e.g. sda or mmcblk]")
                os.system("grub2-install /dev/" + disk)
                os.system("grub2-mkconfig -o /boot/grub2/grub.cfg")
            print("Installation is now finished! ")
        else:
            print("Installation is now finished! ")
            
                
def start_installer():
    installer = Installer()
    #swct = Shall we continue to
    swct_devices = bool_confirmation("Would you like to continue to drive options? [Y/y or N/n] ")
    storage = Storage()
    if swct_devices is True:
        storage.storage_devices()
    else:
        print("Installation is aborted. Exiting...")
        exit()
    dbs_ask = bool_confirmation("Should we start the bootstrap? [Y/y or N/n] ")
    if dbs_ask is True:
        debootstrap = Bootstrap(storage.swap_partition, storage.efi_partition, storage.root_partition)
        debootstrap.start()
    else:
        print("Exiting...")
        exit()
    chroot_ask = bool_confirmation("Would you like to continue through chroot? [Y/y or N/n] ")
    if chroot_ask is True:
        chroot = Chroot(storage.swap_partition)
        chroot.work()
    else:
        print("Exiting...")
        exit()
    user_ask = bool_confirmation("Would you like to create a user in this install? [Y/y or N/n] ")
    if user_ask is True:
        user = User(storage.efi_partition)
        user.create()
    else:
        print("Exiting...")
    os.system("EOT")
    os.system("umount -a")
    os.system("rm -r /mnt/ubuntu-installer")
    print('')
    print('')
    print('Thank You! Enjoy!')

su_state = sp.getoutput("echo $EUID")
if su_state != "0":
    print("You can only run this command as root")
    print("Exiting!")
else:
    start_installer()
