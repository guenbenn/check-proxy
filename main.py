import requests
import time
from colorama import Fore, Style, init

init(autoreset=True)

def kiem_tra_proxy(proxy):
    url = 'https://ipinfo.io/json'
    proxies = {
        'http': proxy,
        'https': proxy
    }

    try:
        start_time = time.time()
        response = requests.get(url, proxies=proxies, timeout=15)
        end_time = time.time()
        ping = (end_time - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            country = data.get('country')
            
            print(f'{Fore.GREEN}--> Proxy hoạt động | Quốc gia: {country} | Ping: {ping:.2f} ms')
        else:
            print(f'{Fore.RED}--> Proxy không hoạt động.')
    except requests.exceptions.RequestException as e:
        print(f'{Fore.RED}--> Lỗi khi kết nối đến proxy: {e}')

def kiem_tra_tat_ca_proxy(file_proxy):
    try:
        with open(file_proxy, 'r') as f:
            proxies = f.readlines()
        for proxy in proxies:
            proxy = proxy.strip()
            if not proxy.startswith('http://') and not proxy.startswith('https://'):
                proxy = 'http://' + proxy
            if proxy:
                print(f'\nKiểm tra proxy: {proxy}')
                kiem_tra_proxy(proxy)
    except FileNotFoundError:
        print(f'Không tìm thấy file {file_proxy}')

file_proxy = 'proxy.txt'
kiem_tra_tat_ca_proxy(file_proxy)
