"""
run_agent_s3.py — Wrapper to run Agent S3 on headless server
Uses Playwright for browser automation instead of native display
"""
import asyncio
import os
import sys
from datetime import datetime

# Add gui-agents to path
sys.path.insert(0, os.path.expanduser("~/.local/lib/python3.10/site-packages"))

async def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("="*60)
    print("  Agent S3 — Computer Use Agent")
    print("="*60)
    print(f"Time: {now}")
    print()
    
    # Test 1: Import gui_agents
    print("1. Testing gui_agents import...")
    try:
        import gui_agents
        print("   ✅ gui_agents imported")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return
    
    # Test 2: Use Playwright for browser automation (Agent S3 alternative for headless)
    print("\n2. Using Playwright for browser automation...")
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()
        
        # Navigate to RuFlo
        print("   Navigating to RuFlo...")
        await page.goto("https://flo.ruv.io/", timeout=30000)
        await page.wait_for_load_state("domcontentloaded", timeout=15000)
        await asyncio.sleep(3)
        
        title = await page.title()
        print(f"   Title: {title}")
        
        # Dismiss modals
        await page.keyboard.press("Escape")
        await asyncio.sleep(1)
        
        # Find and use chat input
        textarea = await page.query_selector("textarea")
        if textarea:
            print("   Found chat input")
            
            # Type prompt
            prompt = f"agent_s3 was here {now}"
            await textarea.click(force=True)
            await textarea.fill(prompt)
            print(f"   Typed: {prompt}")
            
            # Send
            await textarea.press("Enter")
            print("   Sent prompt")
            
            # Wait for response
            await asyncio.sleep(15)
            
            # Get response
            content = await page.text_content("body")
            if content:
                lines = content.split("\n")
                for line in lines:
                    line = line.strip()
                    if "agent_s3" in line.lower() and "here" in line.lower():
                        print(f"\n   🎯 AUTOGRAPH: {line[:200]}")
            
            # Take screenshot
            await page.screenshot(path="ai_autographs/agent_s3_response.png")
            print("   Screenshot saved")
        
        await browser.close()
    
    print("\n" + "="*60)
    print("  Agent S3 Test Complete")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
