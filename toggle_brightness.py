import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tempo.cfg')

def get_brightness(lines):
    for line in lines:
        if "BRIGHTNESS" in line:
            return int(line.split('=')[1].strip())

def toggle_brightness():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as file:
            file.write('BRIGHTNESS = 6\n')
        return

    with open(CONFIG_FILE, 'r') as file:
        lines = file.readlines()

    current_brightness = get_brightness(lines)

    if current_brightness == 6:
        new_brightness = 2
    elif current_brightness == 2:
        new_brightness = 0
    else:
        new_brightness = 6

    with open(CONFIG_FILE, 'w') as file:
        file.writelines([line if "BRIGHTNESS" not in line else f'BRIGHTNESS = {new_brightness}\n' for line in lines])

if __name__ == "__main__":
    toggle_brightness()
