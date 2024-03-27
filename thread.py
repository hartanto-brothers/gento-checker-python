import requests
import os
import random
import json
import time
import concurrent.futures
from colorama import Fore, init

init(autoreset=True)

def random_color():
    color_codes = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]
    return random.choice(color_codes)

def colored_banner(text):
    return f"{random_color()}{text}"

def check_api_key(api_key):
    url = f'https://api.gento.systems/auth?api={api_key}'
    response = requests.post(url)
    if response.status_code == 200:
        data = response.json()
        if "error" in data:
            return None
        return data
    return None

def check_active_services(api_key):
    url = f'https://api.gento.systems/services?api={api_key}'
    response = requests.post(url)
    if response.status_code == 200:
        data = response.json()
        if "error" in data:
            return None
        return data
    return None

def setup_config():
    if os.path.isfile('config.json'):
        config = read_config()
        api_key = config.get("api_key")
        api_data = check_api_key(api_key)
        if api_data:
            print(colored_banner('''
            ______ _______ __   _ _______  _____  _______ _     _ _______ _______ _     _ _______  ______
            |  ____ |______ | \  |    |    |     | |       |_____| |______ |       |____/  |______ |_____/
            |_____| |______ |  \_|    |    |_____| |_____  |     | |______ |_____  |    \_ |______ |    \_
                                                                                                    
                            '''))
            print("Your API Key: ", api_key)
            print("Username: ", api_data["username"])
            print("Credit: ", api_data["credit"])
            checker(api_key)
        else:
            print("Invalid API Key. Deleting config.")
            time.sleep(2)
            print("Restart in 5 seconds")
            time.sleep(5)
            os.system('clear')
            os.remove('config.json')
            setup_config()
    else:
        print(colored_banner('''
        ______ _______ __   _ _______  _____  _______ _     _ _______ _______ _     _ _______  ______
        |  ____ |______ | \  |    |    |     | |       |_____| |______ |       |____/  |______ |_____/
        |_____| |______ |  \_|    |    |_____| |_____  |     | |______ |_____  |    \_ |______ |    \_
                                                                                                
                        '''))
        print("GENTO CHECKER CLI PYTHON")
        print("Please Setup Your Config\n")

        api_key = input("Api Key: ")
        api_data = check_api_key(api_key)
        if api_data:
            config = {"api_key": api_key}
            with open('config.json', 'w') as config_file:
                json.dump(config, config_file)
            print("SETUP SUCCESS RESTARTING SCRIPT.....")
            time.sleep(5)
            os.system('clear')
            setup_config()
        else:
            print("Invalid API Key.")
            time.sleep(2)
            print("Restarting Script in 5 seconds")
            time.sleep(5)
            os.system('clear')
            setup_config()

def read_config():
    if not os.path.isfile('config.json'):
        print("config.json not setup.")
        setup_config()
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        return config

def check_credit_card(cc, api_key, gate_id):
    cc = cc.strip()
    url = f'https://api.gento.systems/checker?api={api_key}&gate={gate_id}&cc={cc}'
    response = requests.post(url)
    data = response.json()
    status = data['status']
    if status == "DECLINED":
        message = f"DECLINED =>: {cc} - {data['brand']} - {data['level']} - {data['type']} - {data['bank']} - {data['country']} - Credit: {data['credit']} - REASON: {data['reason']} - {data['chekcedon']}"
        print(Fore.RED + message)
        with open("declined.txt", "a") as declined_file:
            declined_file.write(message + "\n")
    elif status == "Approved":
        message = f"APPROVED => {cc} - {data['brand']} - {data['level']} - {data['type']} - {data['bank']} - {data['country']} - Credit: {data['credit']} - {data['chekcedon']}"
        print(Fore.GREEN + message)
        with open("approved.txt", "a") as approved_file:
            approved_file.write(message + "\n")
    elif status == "RECHECK":
        message = f"RECHECK =? {cc} - REASON: {data['reason']}"
        print(Fore.YELLOW + message)
        with open("recheck.txt", "a") as recheck_file:
            recheck_file.write(message + "\n")
    elif status == "EXPIRED":
        message = f"EXPIRED CARD => {cc}"
        print(Fore.RED + message)
        with open("expired.txt", "a") as expired_file:
            expired_file.write(message + "\n")
    else:
        message = f"UNKNOWN => {cc}"
        print(Fore.YELLOW + message)
        with open("unknown.txt", "a") as unknown_file:
            unknown_file.write(message + "\n")

def process_credit_cards(ccs, api_key, gate_id, num_threads):
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for cc in ccs:
            futures.append(executor.submit(check_credit_card, cc, api_key, gate_id))
        # Menunggu hingga semua thread selesai
        for future in concurrent.futures.as_completed(futures):
            future.result()

def checker(api_key):
    print("Checking active services...")
    time.sleep(2)
    config = read_config()
    api_data = check_active_services(api_key)
    if api_data:
        services = api_data.get("CCC", []) + api_data.get("braintree", [])
        print("Active Services:")
        for idx, service in enumerate(services, start=1):
            print(f"{idx}. {service['name']}")
        
        selected_service_idx = int(input(f"Pilih service (1-{len(services)}): "))
        if selected_service_idx < 1 or selected_service_idx > len(services):
            print(f"Invalid Choice.")
            return

        selected_service = services[selected_service_idx - 1]
        print(f"You Chose {selected_service['name']}")
        gate_id = selected_service['gateid']

        cc_files = [f for f in os.listdir('.') if f.endswith('.txt')]
        if not cc_files:
            print("Nothing txt file.")
            return

        print("Select Your File :")
        for i, file in enumerate(cc_files, 1):
            print(f"{i}. {file}")

        selected_file_num = int(input(f"Pilih file.txt (1-{len(cc_files)}): "))
        if selected_file_num < 1 or selected_file_num > len(cc_files):
            print("Invalid File.")
            return

        selected_file = cc_files[selected_file_num - 1]

        with open(selected_file, 'r') as file:
            ccs = file.readlines()

        while True:
            num_threads = int(input("Threads (max 50): "))
            if num_threads <= 0:
                print("Threads must bigger than 0.")
                continue
            elif num_threads > 50:
                print("Max Threads 50.")
                continue
            else:
                break

        process_credit_cards(ccs, api_key, gate_id, num_threads)
    else:
        print("Invalid API Key. Deleting config.")
        time.sleep(2)
        print("Restart in 5 seconds")
        time.sleep(5)
        os.system('clear')
        os.remove('config.json')

setup_config()