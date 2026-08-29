"""
browser.py — Browser automation for MoA Swarm

Provides browser control capabilities using Playwright and Chrome DevTools Protocol.
Supports stealth modes, session management, and anti-bot protection.

Author: MoA Swarm Team
Version: 1.0.0
Last Updated: August 29, 2026
"""

import asyncio
import uuid
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from pathlib import Path

from core.config import get_config, MoASwarmConfig
from core.models import Task, TaskStatus


# ─── Browser Session ──────────────────────────────────────────────────────────

class BrowserSession:
    """
    Represents a browser session with state management.
    
    A session encapsulates:
    - Browser instance
    - Page context
    - Session metadata
    - History of actions
    """
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize a browser session.
        
        Args:
            session_id: Optional session identifier
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.last_active = datetime.utcnow()
        self.history: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
        
        # Playwright objects (initialized later)
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
    
    @property
    def is_active(self) -> bool:
        """Check if session is active."""
        return self._page is not None and not self._page.is_closed()
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_active = datetime.utcnow()
    
    def add_history(self, action: str, details: Dict[str, Any]) -> None:
        """Add an action to session history."""
        self.history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "details": details,
        })
    
    async def close(self) -> None:
        """Close the browser session."""
        if self._page and not self._page.is_closed():
            await self._page.close()
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        
        self._page = None
        self._context = None
        self._browser = None
        self._playwright = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "is_active": self.is_active,
            "history_length": len(self.history),
            "metadata": self.metadata,
        }


# ─── Browser Agent ────────────────────────────────────────────────────────────

class BrowserAgent:
    """
    Browser automation agent for web interaction.
    
    Provides high-level browser control capabilities:
    - Navigation
    - Element interaction
    - Screenshot capture
    - Form filling
    - JavaScript execution
    """
    
    def __init__(self, config: Optional[MoASwarmConfig] = None):
        """
        Initialize the Browser Agent.
        
        Args:
            config: MoASwarmConfig instance (uses default if not provided)
        """
        self.config = config or get_config()
        self.sessions: Dict[str, BrowserSession] = {}
    
    # ─── Session Management ───────────────────────────────────────────────────
    
    async def create_session(
        self,
        headless: Optional[bool] = None,
        viewport_width: Optional[int] = None,
        viewport_height: Optional[int] = None,
    ) -> BrowserSession:
        """
        Create a new browser session.
        
        Args:
            headless: Run in headless mode (uses config default if not provided)
            viewport_width: Viewport width (uses config default if not provided)
            viewport_height: Viewport height (uses config default if not provided)
        
        Returns:
            BrowserSession instance
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise ImportError(
                "Playwright is required for browser automation. "
                "Install it with: pip install playwright && playwright install"
            )
        
        session = BrowserSession()
        
        # Use config defaults if not provided
        if headless is None:
            headless = self.config.browser.headless
        if viewport_width is None:
            viewport_width = self.config.browser.viewport_width
        if viewport_height is None:
            viewport_height = self.config.browser.viewport_height
        
        # Initialize Playwright
        session._playwright = await async_playwright().start()
        
        # Launch browser based on config
        browser_type = self.config.browser.browser_type
        if browser_type == "firefox":
            session._browser = await session._playwright.firefox.launch(headless=headless)
        elif browser_type == "webkit":
            session._browser = await session._playwright.webkit.launch(headless=headless)
        else:
            session._browser = await session._playwright.chromium.launch(headless=headless)
        
        # Create context with viewport
        session._context = await session._browser.new_context(
            viewport={"width": viewport_width, "height": viewport_height},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        
        # Create page
        session._page = await session._context.new_page()
        
        self.sessions[session.session_id] = session
        
        session.add_history("session_created", {
            "browser_type": browser_type,
            "headless": headless,
            "viewport": {"width": viewport_width, "height": viewport_height},
        })
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[BrowserSession]:
        """Get a session by ID."""
        return self.sessions.get(session_id)
    
    async def close_session(self, session_id: str) -> bool:
        """Close a session."""
        session = self.sessions.get(session_id)
        if session:
            await session.close()
            del self.sessions[session_id]
            return True
        return False
    
    async def close_all_sessions(self) -> None:
        """Close all sessions."""
        for session_id in list(self.sessions.keys()):
            await self.close_session(session_id)
    
    # ─── Navigation ───────────────────────────────────────────────────────────
    
    async def navigate(
        self,
        session_id: str,
        url: str,
        wait_until: str = "load"
    ) -> Dict[str, Any]:
        """
        Navigate to a URL.
        
        Args:
            session_id: Session identifier
            url: URL to navigate to
            wait_until: Wait condition (load, domcontentloaded, networkidle)
        
        Returns:
            Navigation result dictionary
        """
        session = self.sessions.get(session_id)
        if not session or not session.is_active:
            return {"error": "Session not found or inactive"}
        
        try:
            start_time = datetime.utcnow()
            
            await session._page.goto(url, wait_until=wait_until)
            
            session.update_activity()
            session.add_history("navigate", {"url": url, "wait_until": wait_until})
            
            # Get page info
            title = await session._page.title()
            current_url = session._page.url
            
            return {
                "success": True,
                "url": current_url,
                "title": title,
                "load_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
            }
            
        except Exception as e:
            session.add_history("navigate_error", {"url": url, "error": str(e)})
            return {"error": str(e)}
    
    async def go_back(self, session_id: str) -> Dict[str, Any]:
        """Navigate back."""
        session = self.sessions.get(session_id)
        if not session or not session.is_active:
            return {"error": "Session not found or inactive"}
        
        try:
            await session._page.go_back()
            session.update_activity()
            session.add_history("go_back", {})
            return {"success": True, "url": session._page.url}
        except Exception as e:
            return {"error": str(e)}
    
    async def go_forward(self, session_id: str) -> Dict[str, Any]:
        """Navigate forward."""
        session = self.sessions.get(session_id)
        if not session or not session.is_active:
            return {"error": "Session not found or inactive"}
        
        try:
            await session._page.go_forward()
            session.update_activity()
            session.add_history("go_forward", {})
            return {"success": True, "url": session._page.url}
        except Exception as e:
            return {"error": str(e)}
    
    # ─── Element Interaction ──────────────────────────────────────────────────
    
    async def click(
        self,
        session_id: str,
        selector: str,
        timeout: int = 5000
    ) -> Dict[str, Any]:
        """
        Click an element.
        
        Args:
            session_id: Session identifier
            selector: CSS selector
            timeout: Timeout in milliseconds
        
        Returns:
            Click result dictionary
        """
        session = self.sessions.get(session_id)
        if not session or not session.is_active:
            return {"error": "Session not found or inactive"}
        
        try:
            await session._page.click(selector, timeout=timeout)
            session.update_activity()
            session.add_history("click", {"selector": selector})
            return {"success": True, "selector": selector}
        except Exception as e:
            return {"error": str(e)}
    
    async def fill(
        self,
        session_id: str,
        selector: str,
        value: str,
        timeout: int = 5000
    ) -> Dict[str, Any]:
        """
        Fill a form field.
        
        Args:
            session_id: Session identifier
            selector: CSS selector
            value: Value to fill
            timeout: Timeout in milliseconds
        
        Returns:
            Fill result dictionary
        """
        session = self.sessions.get(session_id)
        if not session or not session.is_active:
            return {"error": "Session not found or inactive"}
        
        try:
            await session._page.fill(selector, value, timeout=timeout)
            session.update_activity()
            session.add_history("fill", {"selector": selector, "value_length": len(value)})
            return {"success": True, "selector": selector}
        except Exception as e:
            return {"error": str(e)}
    
    async def type_text(
        self,
        session_id: str,
        selector: str,
        text: str,
        delay: int = 0
    ) -> Dict[str, Any]:
        """
        Type text into an element.
        
        Args:
            session_id: Session identifier
            selector: CSS selector
            text: Text to type
            delay: Delay between keystrokes in milliseconds
        
        Returns:
            Type result dictionary
        """
        session = self.sessions.get(session_id)
        if not session or not session.is_active:
            return {"error": "Session not found or inactive"}
        
        try:
            await session._page.type(selector, text, delay=delay)
            session.update_activity()
            session.add_history("type", {"selector": selector, "text_length": len(text)})
            return {"success": True, "selector": selector}
        except Exception as e:
            return {"error": str(e)}
    
    async def select_option(
        self,
        session_id: str,
        selector: str,
        value: str
    ) -> Dict[str, Any]:
        """
        Select an option from a dropdown.
        
        Args:
            session_id: Session identifier
            selector: CSS selector
            value: Option value
        
        Returns:
            Select result dictionary
        """
        session = self.sessions.get(session_id)
        if not session or not session.is_active:
            return {"error": "Session not found or inactive"}
        
        try:
            await session._page.select_option(selector, value)
            session.update_activity()
            session.add_history("select_option", {"selector": selector, "value": value})
            return {"success": True, "selector": selector, "value": value}
        except Exception as e:
            return {"error": str(e)}
    
    # ─── Content Extraction ───────────────────────────────────────────────────
    
    async def get_content(
        self,
        session_id: str,
        selector: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get page content or element text.
        
        Args:
            session_id: Session identifier
            selector: Optional CSS selector (gets full page text if not provided)
        
        Returns:
            Content result dictionary
        """
        session = self.sessions.get(session_id)
        if not session or not session.is_active:
            return {"error": "Session not found or inactive"}
        
        try:
            if selector:
                content = await session._page.text_content(selector)
            else:
                content = await session._page.text_content("body")
            
            session.update_activity()
            session.add_history("get_content", {"selector": selector, "content_length": len(content or "")})
            
            return {
                "success": True,
                "content": content or "",
                "selector": selector,
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_attribute(
        self,
        session_id: str,
        selector: str,
        attribute: str
    ) -> Dict[str, Any]:
        """
        Get an element's attribute value.
        
        Args:
            session_id: Session identifier
            selector: CSS selector
            attribute: Attribute name
        
        Returns:
            Attribute result dictionary
        """
        session = self.sessions.get(session_id)
        if not session or not session.is_active:
            return {"error": "Session not found or inactive"}
        
        try:
            value = await session._page.get_attribute(selector, attribute)
            session.update_activity()
            session.add_history("get_attribute", {"selector": selector, "attribute": attribute})
            
            return {
                "success": True,
                "attribute": attribute,
                "value": value,
            }
        except Exception as e:
            return {"error": str(e)}
    
    # ─── Screenshots ──────────────────────────────────────────────────────────
    
    async def screenshot(
        self,
        session_id: str,
        full_page: bool = False,
        path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Take a screenshot.
        
        Args:
            session_id: Session identifier
            full_page: Capture full page (not just viewport)
            path: Optional file path to save screenshot
        
        Returns:
            Screenshot result dictionary
        """
        session = self.sessions.get(session_id)
        if not session or not session.is_active:
            return {"error": "Session not found or inactive"}
        
        try:
            if path:
                await session._page.screenshot(path=path, full_page=full_page)
            else:
                screenshot_bytes = await session._page.screenshot(full_page=full_page)
                # Convert to base64
                import base64
                screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")
            
            session.update_activity()
            session.add_history("screenshot", {"full_page": full_page, "path": path})
            
            result = {
                "success": True,
                "full_page": full_page,
            }
            
            if path:
                result["path"] = path
            else:
                result["screenshot_base64"] = screenshot_b64
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    # ─── JavaScript Execution ─────────────────────────────────────────────────
    
    async def execute_js(
        self,
        session_id: str,
        script: str
    ) -> Dict[str, Any]:
        """
        Execute JavaScript in the page context.
        
        Args:
            session_id: Session identifier
            script: JavaScript code to execute
        
        Returns:
            Execution result dictionary
        """
        session = self.sessions.get(session_id)
        if not session or not session.is_active:
            return {"error": "Session not found or inactive"}
        
        try:
            result = await session._page.evaluate(script)
            session.update_activity()
            session.add_history("execute_js", {"script_length": len(script)})
            
            return {
                "success": True,
                "result": result,
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def wait_for_selector(
        self,
        session_id: str,
        selector: str,
        timeout: int = 5000
    ) -> Dict[str, Any]:
        """
        Wait for an element to appear.
        
        Args:
            session_id: Session identifier
            selector: CSS selector
            timeout: Timeout in milliseconds
        
        Returns:
            Wait result dictionary
        """
        session = self.sessions.get(session_id)
        if not session or not session.is_active:
            return {"error": "Session not found or inactive"}
        
        try:
            await session._page.wait_for_selector(selector, timeout=timeout)
            session.update_activity()
            session.add_history("wait_for_selector", {"selector": selector})
            
            return {"success": True, "selector": selector}
        except Exception as e:
            return {"error": str(e)}
    
    # ─── Utility Methods ──────────────────────────────────────────────────────
    
    async def get_url(self, session_id: str) -> Optional[str]:
        """Get current page URL."""
        session = self.sessions.get(session_id)
        if session and session.is_active:
            return session._page.url
        return None
    
    async def get_title(self, session_id: str) -> Optional[str]:
        """Get current page title."""
        session = self.sessions.get(session_id)
        if session and session.is_active:
            return await session._page.title()
        return None
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions."""
        return [session.to_dict() for session in self.sessions.values()]


# ─── Usage Example ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    async def main():
        # Initialize browser agent
        agent = BrowserAgent()
        
        # Create a session
        print("Creating browser session...")
        session = await agent.create_session(headless=True)
        print(f"Session ID: {session.session_id}")
        
        # Navigate to a page
        print("\nNavigating to example.com...")
        result = await agent.navigate(session.session_id, "https://example.com")
        print(f"Navigation result: {result}")
        
        # Get page title
        title = await agent.get_title(session.session_id)
        print(f"Page title: {title}")
        
        # Take a screenshot
        print("\nTaking screenshot...")
        screenshot = await agent.screenshot(session.session_id)
        print(f"Screenshot taken: {screenshot.get('success', False)}")
        
        # Get page content
        content = await agent.get_content(session.session_id)
        print(f"\nPage content length: {len(content.get('content', ''))}")
        
        # Execute JavaScript
        js_result = await agent.execute_js(session.session_id, "document.title")
        print(f"JS result: {js_result}")
        
        # Close session
        print("\nClosing session...")
        await agent.close_session(session.session_id)
        print("Session closed")
    
    asyncio.run(main())
