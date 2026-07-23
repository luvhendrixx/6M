from pathlib import Path
import subprocess
from dotenv import load_dotenv
import sys
import getpass

from dotenv.main import dotenv_values

# to get the currently logged in user
username = getpass.getuser()

SECRET_KEY="super_secret_test_123"

def scan_dir():
    current_dir = Path.cwd() # get the cwd where the secrets naturally live
    print(f"Current dir is {current_dir}\n")
    # error checking if the .env file is not found
    try:
        secrets_dir = Path(__file__).resolve().parent / '.env' # try's to check the cwd for the .env file

        # error checking if the file actually exists BEFORE loading it into RAM
        if secrets_dir.exists():
            print("Found the secrets file...loading the secrets file into RAM....\n")

        else:
            print(f"Strange...the cwd: {current_dir} DOES NOT have a secrets file🤔🫪\n")

            while True:
                user_confirmation = input("Is that true? [y/n]\n").strip().lower()
                if user_confirmation in ["y","n"]:
                    break
                else:
                    print("That's not an option, [y/n]?")

            if user_confirmation == "n":
                input(("Ok...try creating it then hit ENTER to retry the check: "))

                if not secrets_dir.exists():
                    print("Still can't find the file...aborting🫪")
                    sys.exit(1)
                else:
                    print("Found it, proceeding with the check now...")

            else:
                print("Got it..stopping the check now")
                sys.exit(0)

    except PermissionError:
        print("Um..you don't have access rights to this file...aborting check🫪")
        sys.exit(1)

    env_secrets = dotenv_values(secrets_dir) # open and start scanning the .env file for leaked secrets

    # use subprocess to ask git diff --cached --name-only for the file's added
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True
    )

    # converting git's output (the file given or index via git add) into a clean python list (NOT JSON, otherwise it'd choke)
    staged_files = result.stdout.splitlines() # now every file is auto populated using the data of gotten from git (specifically the staged/indexed files)

    # call the rg_scan function to do the...scanning
    leak_check = rg_scan(env_secrets, staged_files) # we want to specifically check the file in the os level called .env and not..anything else(global)

    if leak_check:
        print("And blocking the commit so you don't lose your house🫪")
        sys.exit(1) # telling git to abort the commit

    else:
        print(f"Good boy {username} 😛, resuming commit...")
        sys.exit(0) # tells git all is good to go


# create the rg_scan machine
def rg_scan(env_secrets, staged_files):
    print("Starting the check...\n")

    '''
    Since load_dotenv() injects variables straight into os.environ[env_data],
    passing env_data into the rg_scan function means env_data inside the rg_scan fn,
    behaves like a dict with "key": "value" pairs.e.g ("API_KEY": "sk-12345")

    We also pass in file_content so as to actually, read the values as a whole,
    so we can..look through and compare them char for char

    We'll perform two checks here, checking if the .env files ITSELF is staged,
    we'll also check if the .env files are leaked as well
    '''

    # loop thru each file path in the staged_files
    for file_name in staged_files:
        file_path = Path(file_name)

        # check if the .env files itself is committed
        if file_path.name == ".env":
            print("Whoa brotatoe, your '.env' file is staged💀\n")
            sys.exit(1)

        # now read the list and check if the file exists or was rmed (the script check file that is)
        if file_path.exists() and file_path.is_file():
            file_text = file_path.read_text(encoding="utf-8", errors="ignore") # read the stuff inside this folder path and encodes it utf-8 architecutre and tells python to ignore weird bin files while reading this file

            # now loop thru the .env file and check if any secrets leaked onto the cwd
            for key, secret_value in env_secrets.items():
                # skip short/empty values
                if not secret_value or len(secret_value) < 4:
                    continue

                # now do the actual leaked check in the cwd
                if secret_value in file_text:
                    print(f"Damn bruh, found your key '{key}' inside {file_name}💀\n")
                    print("Aborting..NOW!!🫪\n")
                    return True # is the secret found? TRUE!!!

    return False # is there an leak found? FALSE!!!!

if __name__ == "__main__":
    scan_dir()
