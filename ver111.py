import subprocess
import time
import os
import random

# List of scancodes for common characters (add more as needed)
scancode_map = {
    'A': '1e', 'B': '30', 'C': '2e', 'D': '20', 'E': '12',
    'F': '21', 'G': '22', 'H': '23', 'I': '17', 'J': '24',
    'K': '25', 'L': '26', 'M': '32', 'N': '31', 'O': '18',
    'P': '19', 'Q': '10', 'R': '13', 'S': '1f', 'T': '14',
    'U': '16', 'V': '2f', 'W': '11', 'X': '2d', 'Y': '15',
    'Z': '2c',
    # Numbers
    '0': '45', '1': '02', '2': '03', '3': '04', '4': '05',
    '5': '06', '6': '07', '7': '08', '8': '09', '9': '0a',
    # Add other symbols as needed
}

# Scancode for Backspace
backspace_scancode = '0e'
# Scancode for Tab
tab_scancode = '0f'
# Scancode for Enter
enter_scancode = '1c'

# Default path to VBoxManage
default_vboxmanage_path = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"

# Function to send a single key press to the VM
def send_key(vm_name, vboxmanage_path, scancode):
    subprocess.run([vboxmanage_path, "controlvm", vm_name, "keyboardputscancode", scancode])
    subprocess.run([vboxmanage_path, "controlvm", vm_name, "keyboardputscancode", hex(int(scancode, 16) + 0x80)[2:]]) # Key release

def get_user_input(prompt, validation_func=None):
    while True:
        value = input(prompt).strip()
        if validation_func and not validation_func(value):
            print("Invalid input, please try again.")
            continue
        return value

def validate_file(path):
    return os.path.isfile(path)

def validate_delay(delay):
    try:
        return float(delay) >= 0
    except ValueError:
        return False

def validate_vboxmanage_path(path):
    return os.path.isfile(path) and os.path.basename(path).lower() == "vboxmanage.exe"

def bruteforce(vm_name, vboxmanage_path, length=5, output_file="bruteforced_keys.txt"):
    characters = list(scancode_map.keys())
    key = ''.join(random.choice(characters) for _ in range(length))
    print(f"Attempting key: {key}")
    try:
        with open(output_file, "a") as outfile:  # Open file in append mode
            outfile.write(key + "\n")  # Write the key to the file
    except Exception as e:
        print(f"Error writing to file: {e}")
    for char in key:
        scancode = scancode_map.get(char.upper())
        if scancode:
            send_key(vm_name, vboxmanage_path, scancode)
            time.sleep(delay)
            log.write(f"Sent: {char} ({scancode})\n")
        else:
            print(f"No scancode found for character: {char}")
    # Simulate pressing Enter twice after typing the key
    send_key(vm_name, vboxmanage_path, enter_scancode)
    time.sleep(delay)
    send_key(vm_name, vboxmanage_path, enter_scancode)
    time.sleep(delay)

    # Tab to the rightmost field (assuming 5 fields)
    for _ in range(4):  # Adjust based on the number of fields
        send_key(vm_name, vboxmanage_path, tab_scancode)
        time.sleep(delay)  # Delay between tabs

    # Press Backspace 30 times with a longer delay
    for _ in range(30):
        send_key(vm_name, vboxmanage_path, backspace_scancode)
        time.sleep(delay)  # Longer delay between backspace presses

    # Tab back to the leftmost field and clear it
    for _ in range(4):  # Adjust based on the number of fields
        send_key(vm_name, vboxmanage_path, tab_scancode)
        time.sleep(delay)  # Delay between tabs
    send_key(vm_name, vboxmanage_path, backspace_scancode)
    time.sleep(delay)  # Delay after backspace

# Prompt user for VBoxManage path
# Initial print statements
print("VirtualBox Windows XP Key Cracker\n")
print("Developed by Marcin Jacek Chmiel")

# Prompt user for VBoxManage path
print(f"Start Time: {time.ctime()}\n\n")
vboxmanage_path = get_user_input(
    f"Enter the path to VBoxManage.exe (or press Enter to use default: {default_vboxmanage_path}): ",
    validate_vboxmanage_path
)

# Use the default path if the user provides an invalid path or presses Enter
if not vboxmanage_path:
    vboxmanage_path = default_vboxmanage_path

# Ask user if they want to bruteforce
bruteforce_option = get_user_input("Do you want to start with bruteforcing? (yes/no): ").lower() == 'yes'

# Get user inputs
if not bruteforce_option:
    keys_file = get_user_input(
        "Enter path to product keys file: ",
        validate_file
    )
else:
    keys_file = None

delay = float(get_user_input(
    "Enter delay between keystrokes (float, for example 0.1): ",
    validate_delay
))

log_file = get_user_input(
    "Enter path to save execution log: "
)

# Set up logging
# Set up logging
with open(log_file, 'w') as log:
    log.write("VirtualBox Windows XP Key Cracker\n")
    log.write("Developed by Marcin Jacek Chmiel\n")
    log.write(f"Start Time: {time.ctime()}\n\n")
    log.write(f"VBoxManage Path: {vboxmanage_path}\n\n")

    # List all running VMs
    print("Available VMs:")
    vms_output = subprocess.run([vboxmanage_path, "list", "runningvms"], capture_output=True, text=True).stdout.splitlines()
    vm_names = []
    for vm in vms_output:
        vm_name = vm.split('"')[1]  # Extract the VM name between quotes
        vm_names.append(vm_name)
        print(f"{len(vm_names)}: {vm_name}")

    # Prompt user to select a VM
    selected_index = int(input("Select a VM by number: ")) - 1
    selected_vm_name = vm_names[selected_index]

    if bruteforce_option:
        output_file = get_user_input("Enter path to save bruteforced keys (filename): ")
        while True:
            bruteforce(selected_vm_name, vboxmanage_path, output_file=output_file)
            continue_bruteforce = get_user_input("Continue bruteforcing? (yes/no): ").lower() == 'yes'
            if not continue_bruteforce:
                break

    # Read product keys from file
    if keys_file:
        with open(keys_file, 'r') as f:
            product_keys = [line.strip() for line in f if line.strip()]

        # Loop through each product key and send it to the VM
        for key in product_keys:
            log.write(f"Sending product key: {key}\n")
            print(f"Sending product key: {key}")
            for char in key:
                scancode = scancode_map.get(char.upper())
                if scancode:
                    send_key(selected_vm_name, vboxmanage_path, scancode)
                    time.sleep(delay)
                    log.write(f"Sent: {char} ({scancode})\n")
                else:
                    print(f"No scancode found for character: {char}")

            # Simulate pressing Enter twice after typing the key
            send_key(selected_vm_name, vboxmanage_path, enter_scancode)
            time.sleep(delay)
            send_key(selected_vm_name, vboxmanage_path, enter_scancode)
            time.sleep(delay)

            # Tab to the rightmost field (assuming 5 fields)
            for _ in range(4):  # Adjust based on the number of fields
                send_key(selected_vm_name, vboxmanage_path, tab_scancode)
                time.sleep(delay)  # Delay between tabs

            # Press Backspace 30 times with a longer delay
            for _ in range(30):
                send_key(selected_vm_name, vboxmanage_path, backspace_scancode)
                time.sleep(delay)  # Longer delay between backspace presses

            # Tab back to the leftmost field and clear it
            for _ in range(4):  # Adjust based on the number of fields
                send_key(selected_vm_name, vboxmanage_path, tab_scancode)
                time.sleep(delay)  # Delay between tabs
            send_key(selected_vm_name, vboxmanage_path, backspace_scancode)
            time.sleep(delay)  # Delay after backspace

        # Prompt user to bruteforce if the list of codes is finished
        bruteforce_after_file = get_user_input("Do you want to bruteforce after finishing the file? (yes/no): ").lower() == 'yes'
        if bruteforce_after_file:
            output_file = get_user_input("Enter path to save bruteforced keys (filename): ")
            while True:
                bruteforce(selected_vm_name, vboxmanage_path, output_file=output_file)
                continue_bruteforce = get_user_input("Continue bruteforcing? (yes/no): ").lower() == 'yes'
                if not continue_bruteforce:
                    break

    log.write("\nOperation completed successfully.\n")
    print(f"Process complete. Log saved to {log_file}")
