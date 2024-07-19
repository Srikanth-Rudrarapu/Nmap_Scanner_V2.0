import PySimpleGUI as sg
import subprocess
import threading

# Counter for keeping track of requests
requests_counter = 0

# Function to run Nmap scan and update output in window
def run_nmap(target_ip, nmap_command, port, output_elem):
    global requests_counter
    try:
        nmap_cmd = f'nmap -Pn {nmap_command} {target_ip} -p {port}'
        process = subprocess.Popen(nmap_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        while True:
            line = process.stdout.readline()
            if not line:
                break
            output_elem.print(line.strip(), text_color='green')
            requests_counter += 1  # Increment the counter for each request sent
        
        process.wait()
    except subprocess.CalledProcessError as e:
        output_elem.print(f"Error running Nmap: {e.stderr}", text_color='red')

# Function to run ping command and update output in window
def ping_host(target_ip, output_elem):
    global requests_counter
    try:
        ping_cmd = f'ping {target_ip}'
        process = subprocess.Popen(ping_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        while True:
            line = process.stdout.readline()
            if not line:
                break
            output_elem.print(line.strip(), text_color='green')
            requests_counter += 1  # Increment the counter for each request sent

        process.wait()
    except subprocess.CalledProcessError as e:
        output_elem.print(f"Error running Ping: {e.stderr}", text_color='red')

# Function to save output to a file
def save_to_file(output, file_path):
    if output:
        try:
            with open(file_path, 'w') as file:
                file.write(output)
            sg.popup_quick_message(f"Output saved to '{file_path}'", background_color='black', text_color='white')
        except Exception as e:
            sg.popup_error(f"Error saving file: {e}")

# Define layout for the GUI window
layout = [
    [sg.Text('Enter Target IP:', text_color='white', background_color='black'), sg.InputText(key='-TARGET_IP-')],
    [sg.Text('Select Nmap Command:', text_color='white', background_color='black'), sg.Combo(['-sS', '-sV', '-sS -sV', '-sU', '-sS -sV -vv', '-A -T4 -sS -sV -vv', '--script ssl-cert', '--script ssl-enum-ciphers', '--script ssl-dh-params', '--script ssl-poodle', '--script http-headers', '--script http-security-headers', '--script http-slowloris-check', '--script rtsp-url-brute'], key='-NMAP_COMMAND-', enable_events=True)],
    [sg.Text('Port/Port Range:', text_color='white', background_color='black'), sg.InputText(key='-PORT-')],
    [sg.Button('Run Scan'), sg.Button('Exit'), sg.Button('Save Output')],
    [sg.Button('Ping host'), sg.Text('(Enter Target IP and click on Ping host)', text_color='white', background_color='black')],
    [sg.Text('Note: By default this tool disables ping scan i.e., it uses (-Pn) in background.', text_color='white', background_color='black')],
    [sg.Multiline(size=(80, 30), key='-OUTPUT-', background_color='black', sbar_background_color='white', text_color='green', autoscroll=True, expand_x=True, expand_y=True)],
    [sg.Text('Requests Sent: 0', key='-REQUEST_COUNT-', text_color='white', background_color='black')]
]

# Create the GUI window
window = sg.Window('Nmap Scanner By Srikanth Rudrarapu', layout, background_color='black', resizable=True)

# Event loop to process events and get user input
while True:
    event, values = window.read(timeout=100)

    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break
    elif event == sg.TIMEOUT_KEY:
        window['-REQUEST_COUNT-'].update(f"Requests Sent: {requests_counter}")
        continue
    elif event == 'Run Scan':
        target_ip = values['-TARGET_IP-']
        nmap_command = values['-NMAP_COMMAND-'] if '-NMAP_COMMAND-' in values else values['-NMAP_COMMAND-0']
        port = values['-PORT-']
        output_elem = window['-OUTPUT-']

        # Clear previous output
        output_elem.update('')

        # Run Nmap scan in a separate thread
        output = run_nmap(target_ip, nmap_command, port, output_elem)

        # Save output to a file
        if output:
            file_path = sg.popup_get_file('Save Output As', save_as=True, default_extension='.txt', file_types=(("Text Files", "*.txt"), ("All Files", "*.*")), no_window=True)
            if file_path:
                threading.Thread(target=save_to_file, args=(output, file_path), daemon=True).start()
    elif event == 'Ping host':
        target_ip = values['-TARGET_IP-']
        output_elem = window['-OUTPUT-']

        # Clear previous output
        output_elem.update('')

        # Run Ping command in a separate thread
        threading.Thread(target=ping_host, args=(target_ip, output_elem), daemon=True).start()

window.close()
