import requests
import socks
import socket
from colorama import Fore, init
import re
import ipaddress
import time
import os

init(autoreset=True)

# Hiển thị thông báo
def display_notice():
    print(Fore.YELLOW + "\nLưu ý: chỉ kiểm tra những proxy nào có giao thức, proxy nào không có sẽ hiển thị trạng thái không hoạt động.\n")
    print("Các định dạng proxy hỗ trợ:")
    print("- protocol://ip:port")
    print("- protocol://user:pass@ip:port")
    print("- protocol://ip:port@user:pass")
    print("- protocol://user:pass:ip:port")
    print("- protocol://ip:port:user:pass")
    print("\n--------------------")

# Chuẩn hóa định dạng proxy
def normalize_proxy(proxy):
    match1 = re.match(r'^(http|https|socks4|socks5)://([^@:]+):([0-9]+)@([^:]+):([^@]+)$', proxy)
    if match1:
        protocol = match1.group(1)
        ip = match1.group(2)
        port = match1.group(3)
        user = match1.group(4)
        password = match1.group(5)
        return f"{protocol}://{user}:{password}@{ip}:{port}"

    match2 = re.match(r'^(http|https|socks4|socks5)://([^:]+):([^@]+):([^:]+):([0-9]+)$', proxy)
    if match2:
        protocol = match2.group(1)
        user = match2.group(2)
        password = match2.group(3)
        ip = match2.group(4)
        port = match2.group(5)
        return f"{protocol}://{user}:{password}@{ip}:{port}"

    match3 = re.match(r'^(http|https|socks4|socks5)://([^:]+):([0-9]+):([^:]+):([^@]+)$', proxy)
    if match3:
        protocol = match3.group(1)
        ip = match3.group(2)
        port = match3.group(3)
        user = match3.group(4)
        password = match3.group(5)
        return f"{protocol}://{user}:{password}@{ip}:{port}"

    return proxy

# Xác định loại proxy
def get_ip_type(ip):
    try:
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.version == 4:
            return "IPv4"
        elif ip_obj.version == 6:
            return "IPv6"
    except ValueError:
        return "Unknown"

# Lấy thông tin quốc gia proxy
def get_country_info(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        if response.status_code == 200:
            data = response.json()
            return data.get("country", "Unknown")
        else:
            return "Unknown"
    except requests.RequestException:
        return "Unknown"

# Kiểm tra tính khả dụng của proxy và đo thời gian phản hồi
def check_proxy(proxy):
    try:
        proxy = normalize_proxy(proxy)
        protocol, proxy_address = proxy.split("://")
        if "@" in proxy_address:
            auth, proxy_address = proxy_address.split("@")
        else:
            auth = None
        ip, port = proxy_address.split(":")
        port = int(port)

        session = requests.Session()

        if protocol == 'socks5' or protocol == 'socks4':
            socks.set_default_proxy(
                getattr(socks, protocol.upper()), ip, port,
                username=auth.split(":")[0] if auth else None,
                password=auth.split(":")[1] if auth and len(auth.split(":")) > 1 else None
            )
            socket.socket = socks.socksocket
            proxies = {
                'http': f'{protocol}://{ip}:{port}',
                'https': f'{protocol}://{ip}:{port}'
            }
        elif protocol == 'http' or protocol == 'https':
            proxies = {protocol: f"{proxy}"}
        else:
            return False, None, None, None, None

        url = "https://httpbin.org/ip" if protocol == 'https' else "http://httpbin.org/ip"

        start_time = time.time()
        response = session.get(url, proxies=proxies, timeout=5)
        ping_time = (time.time() - start_time) * 1000

        if response.status_code == 200:
            real_ip = response.json()['origin']
            ip_type = get_ip_type(real_ip)
            country = get_country_info(real_ip)

            if ping_time < 50:
                ping_color = Fore.GREEN
            elif ping_time < 150:
                ping_color = Fore.YELLOW
            else:
                ping_color = Fore.RED

            return True, real_ip, ip_type, country, ping_time, ping_color
        else:
            return False, None, None, None, None, None
    except Exception:
        return False, None, None, None, None, None

# Đọc danh sách proxy và hiển thị kết quả
def check_proxies_from_file(filename):
    if not os.path.isfile(filename):
        print(Fore.RED + f"\nKhông tìm thấy file {filename}.")
        return

    with open(filename, 'r') as file:
        proxies = file.readlines()

    if not proxies:
        print(Fore.RED + f"\nFile {filename} trống.")
        return

    for proxy in proxies:
        proxy = proxy.strip()
        status, real_ip, ip_type, country, ping_time, ping_color = check_proxy(proxy)
        print(f"\nThông tin proxy: {proxy}")
        if status:
            print(f"- Trạng thái: {Fore.GREEN}Hoạt động")
            print(f"- IP thực tế: {Fore.CYAN}{real_ip}")
            print(f"- Loại: {Fore.YELLOW}{ip_type}")
            print(f"- Quốc gia: {Fore.YELLOW}{country}")
            print(f"- Ping: {ping_color}{ping_time:.2f} ms")
        else:
            print(f"- Trạng thái: {Fore.RED}Không hoạt động")

if __name__ == "__main__":
    display_notice()
    check_proxies_from_file("proxies.txt")
