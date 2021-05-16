import subprocess as sp
from bool_confirmation import *
from supported_os_list import *

class Installer:
    def __init__(self):
        os_type_literal = sp.getoutput("grep '^NAME' /etc/os-release")
        os_type_literal = os_type_literal[5:]
        supported = supported_os()
        if os_type_literal in supported:
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
                    exit()
