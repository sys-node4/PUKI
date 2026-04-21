## Playwright Async Automation Bot 🤖

A robust, asynchronous Python script built with Playwright to perform automated web visits and interactions. Designed for high reliability, this suite features dynamic proxy rotation, modern randomized User-Agents, and built-in stealth capabilities to bypass basic bot detection.

## ✨ Features

# Asynchronous Execution: 
Built on asyncio and playwright.async_api for blazing-fast concurrent browser sessions.

# Concurrency Limiting:
Employs asyncio.Semaphore to manage CPU/RAM usage safely, preventing system overloads.

# Advanced Stealth: 
Integrates playwright-stealth (v2.x API) to mask browser fingerprints and avoid detection.

# Smart Proxy Parsing: 
Automatically detects and formats HTTP, SOCKS4, and SOCKS5 proxies from an external list, with or without authentication.

# Strict Context Isolation:
Ensures zero cookie, local storage, or session leakage between different proxies/IPs.

# Human-Like Interactions:
Simulates randomized mouse movements, scrolling, and delays to mimic real user behavior before interacting with the target.

# Graceful Error Handling:
Catches proxy timeouts, dead connections, and invisible elements without crashing the main event loop.

## 🛠️ Prerequisites

Python 3.8 or higher

Windows, macOS, or Linux

## 📦 Installation

Clone the repository:
```
git clone https://github.com/sys-node4/PUKI & & cd PUKI
```

## Create and activate a virtual environment (Recommended):

# Windows
```
python -m venv venv
venv\Scripts\activate

```
# macOS/Linux
```
python3 -m venv venv
source venv/bin/activate
```


# Install the required Python packages:
```
pip install playwright fake-useragent playwright-stealth
```

# Install Playwright Browser Binaries (Crucial Step):
Playwright requires specific browser binaries to run. Download them by executing:

```
python - m playwright install
```

## ⚙️ Configuration (ip-list.txt)

Create a file named ip-list.txt in the root directory of the project. The script uses this file to rotate IPs. Add one proxy per line.

The parser intelligently handles multiple formats and protocols (HTTP, SOCKS4, SOCKS5). If no protocol is specified, it defaults to http://.

Supported Formats Examples:

# Basic IP:Port (Defaults to HTTP)
192.168.1.1:8080

# IP:Port with Authentication
192.168.1.100:8000:myuser:mypassword

# Explicit Protocol (SOCKS5/SOCKS4)
socks5://212.58.132.5:1080
socks4://98.175.31.222:4145

# Explicit Protocol with Authentication (URI format)
[http://myuser:mypassword@192.168.1.150:8888](http://myuser:mypassword@192.168.1.150:8888)


## 🚀 Usage

Run the script from your terminal:
```
python bot.py
```
Upon starting, the script will prompt you for:

Target URL: The website you want the bot to visit (e.g., https://example.com).

Concurrent Sessions: The number of browsers to run at the exact same time (Default: 5).

To change the target CSS selector for the button click, edit the TARGET_SELECTOR variable directly inside bot.py:

TARGET_SELECTOR = "button#submit-action, .click-me, text='Submit'" 


## 📄 License

All Rights Reserved.

This project and its source code are proprietary. No unauthorized use, reproduction, modification, distribution, or commercialization is permitted. You may not use this software for any purpose without explicit, prior written permission from the author/repository owner.

## ⚠️ Disclaimer

This tool is provided for educational and testing purposes only. Automated interaction with websites may violate their Terms of Service. Ensure you have explicit permission to automate interactions against the target web property. The developers assume no liability for misuse or damage caused by this software.
