from installer import *
from storage import *
from bootstrap import *
from chroot import *
from user import *
from bool_confirmation import *

import os

global version

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
        version = debootstrap.ubuntu_version
    else:
        print("Exiting...")
        exit()
    chroot_ask = bool_confirmation("Would you like to continue through chroot? [Y/y or N/n] ")
    if chroot_ask is True:
        chroot = Chroot(storage.swap_partition, version)
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
    os.system("umount -a")
    os.system("rm -r /mnt/ubuntu-installer")
    print('')
    print('')
    print('Thank You! Enjoy!')
