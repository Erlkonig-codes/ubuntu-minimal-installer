from main_installer import *
import subprocess

def main():
    su_state = sp.getoutput("echo $EUID")
    if su_state != "0":
        print("You can only run this command as root")
        print("Exiting!")
    else:
        start_installer()

if __name__ == "__main__":
    main()
