import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tempo.cfg')

def get_display_mode(lines):
    for line in lines:
        if "DISPLAY" in line:
            return line.split('=')[1].strip()

def toggle_display_mode():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as file:
            file.write('DISPLAY = elapsed\n')
        return

    with open(CONFIG_FILE, 'r') as file:
        lines = file.readlines()

    current_mode = get_display_mode(lines)
    new_mode = "elapsed" if current_mode == "remaining" else "remaining"

    with open(CONFIG_FILE, 'w') as file:
        file.writelines([line if "DISPLAY" not in line else f'DISPLAY = {new_mode}\n' for line in lines])

if __name__ == "__main__":
    toggle_display_mode()
