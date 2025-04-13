import subprocess
import time
import os

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

# Full path to VBoxManage (adjust as necessary)
vboxmanage_path = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"

# Function to send a single key press to the VM
def send_key(vm_name, scancode):
    subprocess.run([vboxmanage_path, "controlvm", vm_name, "keyboardputscancode", scancode])
    subprocess.run([vboxmanage_path, "controlvm", vm_name, "keyboardputscancode", hex(int(scancode, 16) + 0x80)[2:]])  # Key release

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

# Get user inputs
keys_file = get_user_input(
    "Enter path to product keys file: ",
    validate_file
)

delay = float(get_user_input(
    "Enter delay between keystrokes (seconds): ",
    validate_delay
))

log_file = get_user_input(
    "Enter path to save execution log: "
)

# Read product keys from file
with open(keys_file, 'r') as f:
    product_keys = [line.strip() for line in f if line.strip()]

# Set up logging
with open(log_file, 'w') as log:
    log.write("VirtualBox Key Injector Log\n")
    log.write(f"Start Time: {time.ctime()}\n\n")

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

    # Loop through each product key and send it to the VM
    for key in product_keys:
        log.write(f"Sending product key: {key}\n")
        print(f"Sending product key: {key}")
        
        for char in key:
            scancode = scancode_map.get(char.upper())
            if scancode:
                send_key(selected_vm_name, scancode)
                time.sleep(delay)
                log.write(f"Sent: {char} ({scancode})\n")
        
        # Simulate pressing Enter twice after typing the key
        send_key(selected_vm_name, enter_scancode)
        time.sleep(delay)
        send_key(selected_vm_name, enter_scancode)
        time.sleep(delay)
        
        # Tab to the rightmost field (assuming 5 fields)
        for _ in range(4):  # Adjust based on the number of fields
            send_key(selected_vm_name, tab_scancode)
            time.sleep(delay)  # Delay between tabs
        
        # Press Backspace 30 times with a longer delay
        for _ in range(30):
            send_key(selected_vm_name, backspace_scancode)
            time.sleep(delay)  # Longer delay between backspace presses

        # Tab back to the leftmost field and clear it
        for _ in range(4):  # Adjust based on the number of fields
            send_key(selected_vm_name, tab_scancode)
            time.sleep(delay)  # Delay between tabs
            send_key(selected_vm_name, backspace_scancode)
            time.sleep(delay)  # Delay after backspace

    log.write("\nOperation completed successfully.\n")

print(f"Process complete. Log saved to {log_file}")
