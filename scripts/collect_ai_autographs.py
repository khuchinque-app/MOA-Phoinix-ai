"""
collect_ai_autographs.py — Actually connect to each AI service and collect real responses.
This is NOT fake. We use Playwright to open real browsers and interact with real AI services.
"""
import asyncio
import os
import json
from datetime import datetime

RESULTS_DIR = "ai_autographs"
os.makedirs(RESULTS_DIR, exist_ok=True)

AI_SERVICES = [
    {
        "name": "Gemini",
        "url": "https://gemini.google.com/app/60cce3de35189efd",
        "prompt": "Write exactly this line and nothing else: 'gemini was here' followed by today's date and time. Format: gemini was here YYYY-MM-DD HH:MM:SS",
        "selectors": [
            'div.ql-editor[contenteditable="true"]',
            'textarea[aria-label*="prompt"]',
            'textarea[aria-label*="Enter"]',
            '.ql-editor',
            '[contenteditable="true"]',
            'textarea',
        ],
        "send_selectors": [
            'button[aria-label="Send message"]',
            'button[aria-label="Submit"]',
            'button[aria-label="Send"]',
            'button.send-button',
            'button[mattooltip="Send message"]',
        ]
    },
    {
        "name": "Claude",
        "url": "https://claude.ai/new",
        "prompt": "Write exactly this line and nothing else: 'claude was here' followed by today's date and time. Format: claude was here YYYY-MM-DD HH:MM:SS",
        "selectors": [
            'div.ProseMirror[contenteditable="true"]',
            'textarea[placeholder*="Message"]',
            'textarea',
            '[contenteditable="true"]',
        ],
        "send_selectors": [
            'button[aria-label="Send Message"]',
            'button[aria-label="Send"]',
            'button[type="submit"]',
        ]
    },
    {
        "name": "Kimi",
        "url": "https://kimi.moonshot.cn/",
        "prompt": "Write exactly this line and nothing else: 'kimi was here' followed by today's date and time. Format: kimi was here YYYY-MM-DD HH:MM:SS",
        "selectors": [
            'div[contenteditable="true"]',
            'textarea',
            '[data-testid="chat-input"]',
        ],
        "send_selectors": [
            'button[data-testid="send-button"]',
            'button[aria-label="Send"]',
            'button[type="submit"]',
        ]
    },
    {
        "name": "DeepSeek",
        "url": "https://chat.deepseek.com/",
        "prompt": "Write exactly this line and nothing else: 'deepseek was here' followed by today's date and time. Format: deepseek was here YYYY-MM-DD HH:MM:SS",
        "selectors": [
            'textarea[placeholder*="Message"]',
            'textarea',
            '[contenteditable="true"]',
        ],
        "send_selectors": [
            'button[aria-label="Send"]',
            'button[type="submit"]',
            'div[role="button"]',
        ]
    },
    {
        "name": "Qwen",
        "url": "https://tongyi.aliyun.com/qianwen/",
        "prompt": "Write exactly this line and nothing else: 'qwen was here' followed by today's date and time. Format: qwen was here YYYY-MM-DD HH:MM:SS",
        "selectors": [
            'textarea',
            'div[contenteditable="true"]',
            '[data-testid="chat-input"]',
        ],
        "send_selectors": [
            'button[aria-label="Send"]',
            'button[type="submit"]',
        ]
    },
]

async def connect_to_ai(service, browser):
    """Connect to a single AI service and try to get a response."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prompt = service["prompt"].replace("today's date and time", now)
    
    result = {
        "name": service["name"],
        "url": service["url"],
        "timestamp": now,
        "status": "pending",
        "screenshot": None,
        "response": None,
        "error": None,
    }
    
    context = await browser.new_context(
        viewport={"width": 1280, "height": 720},
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = await context.new_page()
    
    try:
        print(f"\n{'='*50}")
        print(f"Connecting to {service['name']}...")
        print(f"URL: {service['url']}")
        
        # Navigate to the service
        await page.goto(service["url"], timeout=30000)
        await page.wait_for_load_state("networkidle", timeout=15000)
        
        title = await page.title()
        print(f"Page title: {title}")
        
        # Take screenshot
        screenshot_path = os.path.join(RESULTS_DIR, f"{service['name'].lower()}_page.png")
        await page.screenshot(path=screenshot_path)
        result["screenshot"] = screenshot_path
        print(f"Screenshot saved: {screenshot_path}")
        
        # Try to find input field
        input_element = None
        for selector in service["selectors"]:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    input_element = elements[0]
                    print(f"Found input: {selector}")
                    break
            except:
                continue
        
        if input_element:
            # Type the prompt
            await input_element.click()
            await input_element.fill(prompt)
            print(f"Typed prompt: {prompt[:50]}...")
            
            # Try to send
            for send_selector in service["send_selectors"]:
                try:
                    send_button = await page.query_selector(send_selector)
                    if send_button:
                        await send_button.click()
                        print(f"Clicked send: {send_selector}")
                        break
                except:
                    continue
            
            # Wait for response
            await asyncio.sleep(10)
            
            # Take screenshot after
            after_screenshot = os.path.join(RESULTS_DIR, f"{service['name'].lower()}_response.png")
            await page.screenshot(path=after_screenshot)
            print(f"Response screenshot: {after_screenshot}")
            
            result["status"] = "connected"
            result["response"] = f"See screenshot: {after_screenshot}"
        else:
            print(f"No input field found for {service['name']}")
            result["status"] = "no_input"
            result["error"] = "Could not find input field"
        
    except Exception as e:
        print(f"Error connecting to {service['name']}: {e}")
        result["status"] = "error"
        result["error"] = str(e)
    
    finally:
        await context.close()
    
    return result

async def main():
    from playwright.async_api import async_playwright
    
    print("="*60)
    print("  COLLECTING REAL AI AUTOGRAPHS")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        for service in AI_SERVICES:
            result = await connect_to_ai(service, browser)
            results.append(result)
        
        await browser.close()
    
    # Save results
    results_file = os.path.join(RESULTS_DIR, "autographs.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "="*60)
    print("  RESULTS SUMMARY")
    print("="*60)
    for r in results:
        status_icon = "✅" if r["status"] == "connected" else "❌"
        print(f"{status_icon} {r['name']}: {r['status']}")
        if r.get("error"):
            print(f"   Error: {r['error'][:80]}")
    
    print(f"\nResults saved to: {results_file}")

if __name__ == "__main__":
    asyncio.run(main())
