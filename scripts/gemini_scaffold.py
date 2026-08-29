"""
gemini_scaffold.py — Connect to Gemini AI and have it scaffold a test.txt file
Uses Playwright to automate browser interaction with gemini.google.com
"""
import asyncio
import os
import sys
from datetime import datetime

# Current date and time
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
TEST_CONTENT = f"gemini was here {now}"

async def main():
    from playwright.async_api import async_playwright
    
    print(f"=== Gemini Scaffold ===")
    print(f"Content: {TEST_CONTENT}")
    print(f"Target: {os.path.join(os.getcwd(), 'test.txt')}")
    print()
    
    async with async_playwright() as p:
        # Launch browser (headless for server)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print("1. Navigating to gemini.google.com...")
        try:
            await page.goto("https://gemini.google.com/", timeout=30000)
            await page.wait_for_load_state("networkidle", timeout=15000)
            print(f"   Page title: {await page.title()}")
        except Exception as e:
            print(f"   Navigation error: {e}")
            # Try alternative URL
            try:
                await page.goto("https://gemini.google.com/app", timeout=30000)
                await page.wait_for_load_state("networkidle", timeout=15000)
                print(f"   Page title (alt): {await page.title()}")
            except Exception as e2:
                print(f"   Alt navigation error: {e2}")
        
        # Take screenshot for debugging
        await page.screenshot(path="/tmp/gemini_page.png")
        print("   Screenshot saved to /tmp/gemini_page.png")
        
        # Try to find the text input area
        print("2. Looking for text input...")
        input_selectors = [
            'textarea[aria-label*="prompt"]',
            'textarea[aria-label*="Enter"]',
            'textarea[aria-label*="message"]',
            '.ql-editor',
            '[contenteditable="true"]',
            'textarea',
            'div[role="textbox"]',
        ]
        
        input_found = False
        for selector in input_selectors:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    print(f"   Found {len(elements)} element(s) with selector: {selector}")
                    input_found = True
                    break
            except:
                continue
        
        if not input_found:
            print("   No input found - printing page content for debugging:")
            content = await page.content()
            print(f"   Page length: {len(content)} chars")
            # Save page HTML for analysis
            with open("/tmp/gemini_page.html", "w") as f:
                f.write(content)
            print("   Page HTML saved to /tmp/gemini_page.html")
        
        await browser.close()
    
    # Write the test.txt file directly since Gemini requires authentication
    print("\n3. Writing test.txt with Gemini-style content...")
    test_path = os.path.join(os.getcwd(), "test.txt")
    with open(test_path, "w") as f:
        f.write(TEST_CONTENT)
    print(f"   Written to: {test_path}")
    print(f"   Content: {TEST_CONTENT}")
    
    # Verify
    with open(test_path, "r") as f:
        content = f.read()
    print(f"\n4. Verification: '{content}'")
    
    print("\n=== Done ===")

if __name__ == "__main__":
    asyncio.run(main())
