import requests
import logging
from colorama import init, Fore, Style
import time
import sys
from tabulate import tabulate

# Initialize colorama
init()

# Custom logging setup
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        colors = {
            'INFO': Fore.GREEN,
            'WARNING': Fore.YELLOW,
            'ERROR': Fore.RED,
            'CRITICAL': Fore.RED + Style.BRIGHT
        }
        level_color = colors.get(record.levelname, Fore.WHITE)
        message = super().format(record)
        return f"{level_color}{message}{Style.RESET_ALL}"

formatter = ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Banner
BANNER = f"""{Fore.CYAN}
╔══════════════════════════════════════════════╗
║       🌟 UNICH BOT - Automated Mining        ║
║   Automate your Unich mining and info tasks! ║
║  Developed by: https://t.me/sentineldiscus   ║
╚══════════════════════════════════════════════╝
{Style.RESET_ALL}"""

# Headers
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "id-ID,id;q=0.9,ja-ID;q=0.8,ja;q=0.7,en-ID;q=0.6,en;q=0.5,en-US;q=0.4",
    "origin": "https://unich.com",
    "referer": "https://unich.com/",
    "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}

# Function to create the system information table
def display_system_info(email=None, point=None):
    # Table structure with filled parameters and values
    table_data = [
        ["proxy configuration", [
            {"Parameter": "Proxy Status", "value": "Not Configured"},
            {"Parameter": "Proxy Address", "value": "N/A"}
        ]],
        ["account information", [
            {"Parameter": "Email", "value": email or "N/A"},
            {"Parameter": "Points", "value": str(point) if point is not None else "N/A"}
        ]],
        ["system settings", [
            {"Parameter": "Countdown Duration", "value": "24 hours"},
            {"Parameter": "Rate Limit Delay", "value": "1 second"}
        ]],
        ["redirect information", [
            {"Parameter": "Referer", "value": HEADERS["referer"]},
            {"Parameter": "Origin", "value": HEADERS["origin"]}
        ]],
        ["nodes information", [
            {"Parameter": "Node Count", "value": "Unknown"},
            {"Parameter": "Node Status", "value": "N/A"}
        ]],
        ["attempt limit", [
            {"Parameter": "Max Attempts", "value": "Unlimited"},
            {"Parameter": "Retry Delay", "value": "1 second"}
        ]]
    ]

    # Custom table formatting with color
    headers = [
        f"{Fore.BLUE}section{Style.RESET_ALL}",
        f"{Fore.BLUE}Parameter{Style.RESET_ALL}",
        f"{Fore.BLUE}value{Style.RESET_ALL}"
    ]

    # Prepare table rows
    formatted_rows = []
    for section, params in table_data:
        for i, param in enumerate(params):
            formatted_rows.append([
                f"{Fore.WHITE}{section}{Style.RESET_ALL}" if i == 0 else "",
                f"{Fore.BLUE}{param['Parameter']}{Style.RESET_ALL}",
                f"{Fore.BLUE}{param['value']}{Style.RESET_ALL}"
            ])

    # Green border
    border = f"{Fore.GREEN}{'═' * 70}{Style.RESET_ALL}"
    title = f"{Fore.WHITE}system information{Style.RESET_ALL}"
    print(f"\n{border}")
    print(f"{Fore.GREEN}║{Style.RESET_ALL} {title.center(66)} {Fore.GREEN}║{Style.RESET_ALL}")
    print(f"{border}")

    # Print table with full line separators using fancy_grid
    print(tabulate(formatted_rows, headers=headers, tablefmt="fancy_grid", colalign=("left", "left", "left")))
    print(f"{border}\n")

# Function to read tokens from data.txt
def read_tokens(file_path="data.txt"):
    try:
        with open(file_path, 'r') as file:
            tokens = [line.strip() for line in file if line.strip()]
        return tokens
    except Exception as e:
        logger.error(f"Gagal membaca file {file_path}: {str(e)}")
        return []

# Function to perform mining request
def start_mining(token):
    url = "https://api.unich.com/airdrop/user/v1/mining/start"
    headers = HEADERS.copy()
    headers["authorization"] = f"Bearer {token}"
    
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 201:
            logger.info(f"Berhasil memulai mining untuk akun")
        else:
            logger.warning(f"Gagal memulai mining untuk akun: {response.status_code}")
    except Exception as e:
        logger.error(f"Error saat memulai mining untuk akun: {str(e)}")

# Function to get user info
def get_user_info(token):
    url = "https://api.unich.com/airdrop/user/v1/info/my-info"
    headers = HEADERS.copy()
    headers["authorization"] = f"Bearer {token}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json().get("data", {})
            email = data.get("email", "Email tidak ditemukan")
            point = data.get("mUn", 0)
            return email, point
        else:
            logger.warning(f"Gagal mendapatkan info untuk akun: {response.status_code}")
            return None, None
    except Exception as e:
        logger.error(f"Error saat mendapatkan info untuk akun: {str(e)}")
        return None, None

# Function to display countdown
def countdown(seconds):
    while seconds > 0:
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds_left = divmod(remainder, 60)
        print(f"\r{Fore.GREEN}Menunggu untuk memulai ulang: {hours:02d}:{minutes:02d}:{seconds_left:02d}{Style.RESET_ALL}", end="")
        sys.stdout.flush()
        time.sleep(1)
        seconds -= 1
    print(f"\r{' ' * 50}\r", end="")  # Clear the countdown line

# Main function
def main():
    while True:
        print(BANNER)  # Display the banner
        tokens = read_tokens()
        
        if not tokens:
            logger.error("Tidak ada token yang ditemukan. Pastikan data.txt berisi token.")
            return
        
        for token in tokens:
            email, point = get_user_info(token)
            display_system_info(email, point)  # Display table with account info
            if email:
                logger.info(f"Memproses akun dengan {email}")
                start_mining(token)
                logger.info(f"Point untuk akun: {point}")
            else:
                logger.warning("Lewati mining karena gagal mendapatkan email")
            time.sleep(1)  # Delay to prevent rate limiting
        
        logger.info("Semua akun telah diproses. Memulai hitung mundur 24 jam...")
        countdown(24 * 3600)  # 24 hours in seconds
        logger.info("Hitung mundur selesai. Memulai ulang proses...")

if __name__ == "__main__":
    main()
