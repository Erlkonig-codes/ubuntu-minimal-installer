import os
import time
import subprocess as sp
from bool_confirmation import *

class Storage:
    def __init__(self):
        os.system("rm -rf /mnt/ubuntu-installer")
    def storage_devices(self):
        sp.run(['lsblk', '-o', 'PATH,FSTYPE'])
        block_path = sp.getoutput("lsblk -o PATH")
        self.blocks_path = block_path.replace("/dev/","")
        print('')
        print('')
        self.manage_media()
    def manage_media(self):
        media_choice = input("Would you like to create a new partition, format an existing one, or proceed with preconfigured partitions? [Create/create or Format/format or Proceed/proceed] ")
        if media_choice.lower() == 'create':
            print("Creation is unavailable for now... Please create partitions for yourself for the mean time...")
            time.sleep(3)
            self.manage_media()
            # creation_method = input("Would you like to use GParted (GUI) or gdisk (TUI)? [gparted or gdisk] ")
            # if creation_method == 'gparted':
            #     sp.run(['gparted'])
            #     # os.system("gparted >> /dev/null")
            #     self.mount_stage()
            # elif creation_method == 'gdisk':
            #     disk = input("What disk would you like to create partitions in? [sda, mmcblk5] ")
            #     os.system("gdisk " + disk)
            # else:
            #     print('No choice named' + creation_method)
            #     self.storage_devices()
        elif media_choice.lower() == 'format':
            format_drive = input("Which partition would you like to format and use? [E.g. sda5 or sdc1] ")
            if format_drive in self.blocks_path:
                format_confirmation = bool_confirmation("Would you like to proceed formatting " + format_drive + " (ext4 is the only choice for now)? [Y/y or N/n] ")
                if format_confirmation is True:
                    sp.run(['mkfs.ext4', '/dev/' + format_drive])
                    self.mount_stage()
        elif media_choice.lower() == 'proceed':
            self.mount_stage()
        else:
            print("Unknown choice... Try again")
            self.manage_media()
    def mount_stage(self):
        os.system("mkdir /mnt/ubuntu-installer")
        root = input("Which is the root partition? [e.g. sda1] ")
        swap = input("Which is the swap partition? (Leave blank if you did not create one) ")
        global efi
        efi = input("Which is the efi partition to be mounted at /boot/efi? (Leave blank if you boot in legacy BIOS mode) ")
        
        os.system("mount /dev/" + root + " /mnt/ubuntu-installer")
        if efi != '':
            os.system("mkdir -p /mnt/ubuntu-installer/boot/efi")
            os.system("mount /dev" + efi + " /mnt/ubuntu-installer/boot/efi")
            self.efi_partition = True
        else:
            self.efi_partition = False
        self.swap_partition = swap
        self.root_partition = root
