import asyncio
import random
import logging
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
from playwright_stealth import Stealth

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
TARGET_SELECTOR = "button#submit-action, .click-me, button:has-text('Submit')" # Flexible selector
IP_LIST_FILE = "ip-list.txt"
UA_LIST_FILE = "ua-list.txt"
NAVIGATION_TIMEOUT = 30000 # 30 seconds

def load_proxies(filepath: str) -> list:
    """
    Parses the ip-list.txt file and returns a list of Playwright-compatible proxy dictionaries.
    Handles multiple formats: ip:port, ip:port:user:pass, and user:pass@ip:port
    Now intelligently handles protocol prefixes (http://, socks5://).
    """
    proxies = []
    path = Path(filepath)
    
    if not path.exists():
        logger.error(f"Proxy file {filepath} not found.")
        return proxies

    with open(path, 'r') as file:
        lines = [line.strip() for line in file if line.strip()]
        
    for line in lines:
        try:
            # Check if a protocol scheme is explicitly provided, otherwise default to http://
            if "://" in line:
                scheme, rest = line.split("://", 1)
                scheme = scheme + "://"
            else:
                scheme = "http://"
                rest = line

            # Format: user:pass@ip:port
            if "@" in rest:
                auth, endpoint = rest.split("@")
                user, pw = auth.split(":")
                proxies.append({
                    "server": f"{scheme}{endpoint}",
                    "username": user,
                    "password": pw
                })
            else:
                parts = rest.split(":")
                # Format: ip:port
                if len(parts) == 2:
                    proxies.append({"server": f"{scheme}{rest}"})
                # Format: ip:port:user:pass
                elif len(parts) == 4:
                    proxies.append({
                        "server": f"{scheme}{parts[0]}:{parts[1]}",
                        "username": parts[2],
                        "password": parts[3]
                    })
                else:
                    logger.warning(f"Unrecognized proxy format skipped: {line}")
        except Exception as e:
            logger.warning(f"Error parsing proxy line '{line}': {e}")
            
    return proxies

def load_user_agents(filepath: str) -> list:
    """
    Parses the ua-list.txt file and returns a list of User-Agents.
    """
    uas = []
    path = Path(filepath)
    
    if not path.exists():
        logger.error(f"User-Agent file {filepath} not found.")
        return uas

    with open(path, 'r', encoding='utf-8') as file:
        uas = [line.strip() for line in file if line.strip()]
        
    return uas

def generate_headers(user_agents: list) -> dict:
    """
    Picks a random User-Agent from the provided list.
    """
    return {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "en-US,en;q=0.9",
    }

async def human_like_interaction(page):
    """
    Simulates human-like mouse movements and scrolling.
    """
    # Random mouse movements across the viewport
    for _ in range(random.randint(2, 4)):
        x = random.randint(100, 800)
        y = random.randint(100, 800)
        await page.mouse.move(x, y)
        await asyncio.sleep(random.uniform(0.1, 0.4))

    # Random scroll up/down
    scroll_amount = random.randint(200, 700)
    await page.mouse.wheel(0, scroll_amount)
    await asyncio.sleep(random.uniform(0.5, 1.5))
    
    # Slight scroll back
    await page.mouse.wheel(0, -random.randint(50, 200))

async def automation_cycle(semaphore: asyncio.Semaphore, proxy: dict, url: str, selector: str, user_agents: list):
    """
    The core logic: launches a context via proxy, visits the URL, acts human, and clicks.
    """
    async with semaphore:
        headers = generate_headers(user_agents)
        user_agent = headers.pop("User-Agent")
        proxy_server = proxy.get("server")
        
        logger.info(f"Starting session via proxy: {proxy_server}")

        async with async_playwright() as p:
            browser = None
            try:
                # Launch Chromium (Headless by default; set to False for debugging)
                browser = await p.chromium.launch(headless=True)
                
                # Create a strict, isolated context for this specific proxy to prevent leakage
                context = await browser.new_context(
                    proxy=proxy,
                    user_agent=user_agent,
                    extra_http_headers=headers,
                    viewport={"width": random.randint(1024, 1920), "height": random.randint(768, 1080)}
                )
                
                # Apply stealth logic to the entire context (v2.x API standard)
                stealth = Stealth()
                await stealth.apply_stealth_async(context)
                
                page = await context.new_page()
                
                # Navigate to the target with a networkidle wait state
                logger.info(f"[{proxy_server}] Navigating to {url} ...")
                await page.goto(url, wait_until="networkidle", timeout=NAVIGATION_TIMEOUT)
                
                # Perform human-like behavior
                logger.info(f"[{proxy_server}] Performing human-like interactions ...")
                await human_like_interaction(page)
                
                # Wait random.uniform(2, 5) seconds before clicking
                delay = random.uniform(2.0, 5.0)
                logger.info(f"[{proxy_server}] Waiting {delay:.2f} seconds before click ...")
                await asyncio.sleep(delay)
                
                # Locate the button using the flexible selector and click
                locator = page.locator(selector).first
                if await locator.is_visible():
                    await locator.click(timeout=10000)
                    logger.info(f"[{proxy_server}] Successfully clicked the target element.")
                else:
                    logger.warning(f"[{proxy_server}] Target element '{selector}' not visible.")

            except PlaywrightTimeoutError:
                logger.error(f"[{proxy_server}] Proxy Timeout.")
            except PlaywrightError as pe:
                # Cleanly catch Playwright network errors without dumping the giant call log
                error_msg = str(pe).split('\n')[0]
                logger.error(f"[{proxy_server}] Playwright Error: {error_msg}")
            except Exception as e:
                logger.error(f"[{proxy_server}] Unexpected error: {e}")
            finally:
                # Graceful Exit: Always close the browser to free resources
                if browser:
                    await browser.close()
                    logger.debug(f"[{proxy_server}] Browser context closed.")

async def main():
    # --- USER INPUT ---
    target_url = input("Enter the target URL (e.g., https://example.com): ").strip()
    if not target_url:
        logger.error("Target URL cannot be empty. Exiting.")
        return

    try:
        concurrency_input = input("Enter the number of concurrent browser sessions (default 5): ").strip()
        concurrency_limit = int(concurrency_input) if concurrency_input else 5
    except ValueError:
        logger.warning("Invalid number for browser sessions. Using default (5).")
        concurrency_limit = 5

    logger.info("Initializing Automation Suite...")
    
    # 1. Load Proxies and User-Agents
    proxies = load_proxies(IP_LIST_FILE)
    if not proxies:
        logger.error("No valid proxies loaded. Exiting.")
        return
    
    logger.info(f"Loaded {len(proxies)} proxies from {IP_LIST_FILE}.")

    user_agents = load_user_agents(UA_LIST_FILE)
    if not user_agents:
        logger.error("No valid User-Agents loaded. Exiting.")
        return
    
    logger.info(f"Loaded {len(user_agents)} User-Agents from {UA_LIST_FILE}.")

    # 2. Setup Concurrency Limit Semaphore
    semaphore = asyncio.Semaphore(concurrency_limit)
    
    # 3. Create and Gather Tasks
    tasks = []
    for proxy in proxies:
        task = asyncio.create_task(
            automation_cycle(semaphore, proxy, target_url, TARGET_SELECTOR, user_agents)
        )
        tasks.append(task)
        
    # Wait for all iterations to finish
    await asyncio.gather(*tasks)
    
    logger.info("Automation suite finished execution.")

if __name__ == "__main__":
    asyncio.run(main())
