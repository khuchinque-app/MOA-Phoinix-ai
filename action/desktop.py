"""
desktop.py — Desktop automation for MoA Swarm

Provides OS-level control capabilities including:
- Screenshot capture
- Mouse movement and clicks
- Keyboard input
- Window management

Author: MoA Swarm Team
Version: 1.0.0
Last Updated: August 29, 2026
"""

import asyncio
import uuid
import subprocess
import platform
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from pathlib import Path

from core.config import get_config, MoASwarmConfig


# ─── Desktop Session ──────────────────────────────────────────────────────────

class DesktopSession:
    """
    Represents a desktop automation session.
    
    Manages:
    - Connection to desktop environment
    - Action history
    - Session state
    """
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize a desktop session.
        
        Args:
            session_id: Optional session identifier
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.last_active = datetime.utcnow()
        self.history: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {
            "platform": platform.system(),
            "platform_version": platform.version(),
        }
    
    @property
    def is_active(self) -> bool:
        """Check if session is active."""
        return True  # Desktop sessions are always active
    
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


# ─── Desktop Agent ────────────────────────────────────────────────────────────

class DesktopAgent:
    """
    Desktop automation agent for OS-level control.
    
    Provides capabilities for:
    - Screenshot capture
    - Mouse control
    - Keyboard input
    - Window management
    - Application control
    """
    
    def __init__(self, config: Optional[MoASwarmConfig] = None):
        """
        Initialize the Desktop Agent.
        
        Args:
            config: MoASwarmConfig instance (uses default if not provided)
        """
        self.config = config or get_config()
        self.sessions: Dict[str, DesktopSession] = {}
        self._platform = platform.system()
    
    # ─── Session Management ───────────────────────────────────────────────────
    
    def create_session(self) -> DesktopSession:
        """
        Create a new desktop session.
        
        Returns:
            DesktopSession instance
        """
        session = DesktopSession()
        self.sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[DesktopSession]:
        """Get a session by ID."""
        return self.sessions.get(session_id)
    
    def close_session(self, session_id: str) -> bool:
        """Close a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    # ─── Screenshot Capture ───────────────────────────────────────────────────
    
    async def take_screenshot(
        self,
        session_id: str,
        region: Optional[Tuple[int, int, int, int]] = None,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Take a screenshot.
        
        Args:
            session_id: Session identifier
            region: Optional (x, y, width, height) tuple for region capture
            filename: Optional filename to save screenshot
        
        Returns:
            Screenshot result dictionary
        """
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            # Capture screenshot based on platform
            if self._platform == "Linux":
                await self._screenshot_linux(filename, region)
            elif self._platform == "Darwin":  # macOS
                await self._screenshot_macos(filename, region)
            elif self._platform == "Windows":
                await self._screenshot_windows(filename, region)
            else:
                return {"error": f"Unsupported platform: {self._platform}"}
            
            session.update_activity()
            session.add_history("screenshot", {
                "filename": filename,
                "region": region,
            })
            
            return {
                "success": True,
                "filename": filename,
                "platform": self._platform,
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _screenshot_linux(
        self,
        filename: str,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> None:
        """Take screenshot on Linux."""
        cmd = ["scrot", filename]
        if region:
            x, y, w, h = region
            cmd = ["scrot", "-a", f"{x},{y},{w},{h}", filename]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
    
    async def _screenshot_macos(
        self,
        filename: str,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> None:
        """Take screenshot on macOS."""
        cmd = ["screencapture", filename]
        if region:
            x, y, w, h = region
            cmd = ["screencapture", "-R", f"{x},{y},{w},{h}", filename]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
    
    async def _screenshot_windows(
        self,
        filename: str,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> None:
        """Take screenshot on Windows."""
        # PowerShell command for screenshot
        ps_script = f'''
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing
        $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
        $bitmap = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
        $graphics.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)
        $bitmap.Save("{filename}")
        '''
        
        process = await asyncio.create_subprocess_exec(
            "powershell", "-Command", ps_script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
    
    # ─── Mouse Control ────────────────────────────────────────────────────────
    
    async def move_mouse(
        self,
        session_id: str,
        x: int,
        y: int
    ) -> Dict[str, Any]:
        """
        Move mouse to coordinates.
        
        Args:
            session_id: Session identifier
            x: X coordinate
            y: Y coordinate
        
        Returns:
            Move result dictionary
        """
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        try:
            if self._platform == "Linux":
                await self._mouse_move_linux(x, y)
            elif self._platform == "Darwin":
                await self._mouse_move_macos(x, y)
            elif self._platform == "Windows":
                await self._mouse_move_windows(x, y)
            else:
                return {"error": f"Unsupported platform: {self._platform}"}
            
            session.update_activity()
            session.add_history("move_mouse", {"x": x, "y": y})
            
            return {"success": True, "x": x, "y": y}
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _mouse_move_linux(self, x: int, y: int) -> None:
        """Move mouse on Linux using xdotool."""
        process = await asyncio.create_subprocess_exec(
            "xdotool", "mousemove", str(x), str(y),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
    
    async def _mouse_move_macos(self, x: int, y: int) -> None:
        """Move mouse on macOS using cliclick."""
        process = await asyncio.create_subprocess_exec(
            "cliclick", f"m:{x},{y}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
    
    async def _mouse_move_windows(self, x: int, y: int) -> None:
        """Move mouse on Windows using PowerShell."""
        ps_script = f'''
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point({x}, {y})
        '''
        process = await asyncio.create_subprocess_exec(
            "powershell", "-Command", ps_script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
    
    async def click_mouse(
        self,
        session_id: str,
        button: str = "left"
    ) -> Dict[str, Any]:
        """
        Click mouse button.
        
        Args:
            session_id: Session identifier
            button: Button to click (left, right, middle)
        
        Returns:
            Click result dictionary
        """
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        try:
            if self._platform == "Linux":
                await self._mouse_click_linux(button)
            elif self._platform == "Darwin":
                await self._mouse_click_macos(button)
            elif self._platform == "Windows":
                await self._mouse_click_windows(button)
            else:
                return {"error": f"Unsupported platform: {self._platform}"}
            
            session.update_activity()
            session.add_history("click_mouse", {"button": button})
            
            return {"success": True, "button": button}
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _mouse_click_linux(self, button: str) -> None:
        """Click mouse on Linux."""
        button_map = {"left": "1", "middle": "2", "right": "3"}
        btn = button_map.get(button, "1")
        process = await asyncio.create_subprocess_exec(
            "xdotool", "click", btn,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
    
    async def _mouse_click_macos(self, button: str) -> None:
        """Click mouse on macOS."""
        button_map = {"left": "c", "right": "rc", "middle": "mc"}
        btn = button_map.get(button, "c")
        process = await asyncio.create_subprocess_exec(
            "cliclick", btn,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
    
    async def _mouse_click_windows(self, button: str) -> None:
        """Click mouse on Windows."""
        ps_script = f'''
        Add-Type -AssemblyName System.Windows.Forms
        if ("{button}" -eq "left") {{
            [System.Windows.Forms.Mouse]::Click([System.Windows.Forms.MouseButtons]::Left)
        }} elseif ("{button}" -eq "right") {{
            [System.Windows.Forms.Mouse]::Click([System.Windows.Forms.MouseButtons]::Right)
        }} elseif ("{button}" -eq "middle") {{
            [System.Windows.Forms.Mouse]::Click([System.Windows.Forms.MouseButtons]::Middle)
        }}
        '''
        process = await asyncio.create_subprocess_exec(
            "powershell", "-Command", ps_script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
    
    # ─── Keyboard Input ───────────────────────────────────────────────────────
    
    async def type_text(
        self,
        session_id: str,
        text: str,
        interval: float = 0.01
    ) -> Dict[str, Any]:
        """
        Type text using keyboard.
        
        Args:
            session_id: Session identifier
            text: Text to type
            interval: Delay between keystrokes in seconds
        
        Returns:
            Type result dictionary
        """
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        try:
            if self._platform == "Linux":
                await self._type_linux(text, interval)
            elif self._platform == "Darwin":
                await self._type_macos(text, interval)
            elif self._platform == "Windows":
                await self._type_windows(text, interval)
            else:
                return {"error": f"Unsupported platform: {self._platform}"}
            
            session.update_activity()
            session.add_history("type_text", {"text_length": len(text)})
            
            return {"success": True, "text_length": len(text)}
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _type_linux(self, text: str, interval: float) -> None:
        """Type text on Linux."""
        process = await asyncio.create_subprocess_exec(
            "xdotool", "type", "--delay", str(int(interval * 1000)), text,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
    
    async def _type_macos(self, text: str, interval: float) -> None:
        """Type text on macOS."""
        process = await asyncio.create_subprocess_exec(
            "cliclick", f"t:{text}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
    
    async def _type_windows(self, text: str, interval: float) -> None:
        """Type text on Windows."""
        ps_script = f'''
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.SendKeys]::SendWait("{text}")
        '''
        process = await asyncio.create_subprocess_exec(
            "powershell", "-Command", ps_script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
    
    async def press_key(
        self,
        session_id: str,
        key: str
    ) -> Dict[str, Any]:
        """
        Press a keyboard key.
        
        Args:
            session_id: Session identifier
            key: Key to press (e.g., "enter", "tab", "escape")
        
        Returns:
            Key press result dictionary
        """
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        try:
            if self._platform == "Linux":
                await self._press_key_linux(key)
            elif self._platform == "Darwin":
                await self._press_key_macos(key)
            elif self._platform == "Windows":
                await self._press_key_windows(key)
            else:
                return {"error": f"Unsupported platform: {self._platform}"}
            
            session.update_activity()
            session.add_history("press_key", {"key": key})
            
            return {"success": True, "key": key}
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _press_key_linux(self, key: str) -> None:
        """Press key on Linux."""
        process = await asyncio.create_subprocess_exec(
            "xdotool", "key", key,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
    
    async def _press_key_macos(self, key: str) -> None:
        """Press key on macOS."""
        key_map = {
            "enter": "return",
            "return": "return",
            "tab": "tab",
            "escape": "esc",
            "esc": "esc",
            "space": "space",
            "backspace": "delete",
            "delete": "delete",
        }
        mapped_key = key_map.get(key, key)
        process = await asyncio.create_subprocess_exec(
            "cliclick", f"k:{mapped_key}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
    
    async def _press_key_windows(self, key: str) -> None:
        """Press key on Windows."""
        key_map = {
            "enter": "{ENTER}",
            "return": "{ENTER}",
            "tab": "{TAB}",
            "escape": "{ESC}",
            "esc": "{ESC}",
            "space": " ",
            "backspace": "{BACKSPACE}",
            "delete": "{DELETE}",
        }
        mapped_key = key_map.get(key, key)
        ps_script = f'''
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.SendKeys]::SendWait("{mapped_key}")
        '''
        process = await asyncio.create_subprocess_exec(
            "powershell", "-Command", ps_script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
    
    # ─── Window Management ────────────────────────────────────────────────────
    
    async def get_active_window(self, session_id: str) -> Dict[str, Any]:
        """
        Get information about the active window.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Window information dictionary
        """
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        try:
            if self._platform == "Linux":
                info = await self._get_active_window_linux()
            elif self._platform == "Darwin":
                info = await self._get_active_window_macos()
            elif self._platform == "Windows":
                info = await self._get_active_window_windows()
            else:
                return {"error": f"Unsupported platform: {self._platform}"}
            
            session.update_activity()
            session.add_history("get_active_window", info)
            
            return {"success": True, **info}
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_active_window_linux(self) -> Dict[str, Any]:
        """Get active window on Linux."""
        process = await asyncio.create_subprocess_exec(
            "xdotool", "getactivewindow", "getwindowname",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await process.communicate()
        return {"title": stdout.decode().strip()}
    
    async def _get_active_window_macos(self) -> Dict[str, Any]:
        """Get active window on macOS."""
        ps_script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            return frontApp
        end tell
        '''
        process = await asyncio.create_subprocess_exec(
            "osascript", "-e", ps_script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await process.communicate()
        return {"title": stdout.decode().strip()}
    
    async def _get_active_window_windows(self) -> Dict[str, Any]:
        """Get active window on Windows."""
        ps_script = '''
        Add-Type @"
        using System;
        using System.Runtime.InteropServices;
        public class Win32 {
            [DllImport("user32.dll")]
            public static extern IntPtr GetForegroundWindow();
            [DllImport("user32.dll")]
            public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder text, int count);
        }
"@
        $handle = [Win32]::GetForegroundWindow()
        $sb = New-Object System.Text.StringBuilder 256
        [Win32]::GetWindowText($handle, $sb, 256) | Out-Null
        return $sb.ToString()
        '''
        process = await asyncio.create_subprocess_exec(
            "powershell", "-Command", ps_script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await process.communicate()
        return {"title": stdout.decode().strip()}
    
    # ─── Utility Methods ──────────────────────────────────────────────────────
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions."""
        return [session.to_dict() for session in self.sessions.values()]


# ─── Usage Example ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    async def main():
        # Initialize desktop agent
        agent = DesktopAgent()
        
        # Create a session
        print("Creating desktop session...")
        session = agent.create_session()
        print(f"Session ID: {session.session_id}")
        
        # Take a screenshot
        print("\nTaking screenshot...")
        screenshot = await agent.take_screenshot(session.session_id)
        print(f"Screenshot result: {screenshot}")
        
        # Get active window
        print("\nGetting active window...")
        window = await agent.get_active_window(session.session_id)
        print(f"Active window: {window}")
        
        # Type some text (careful with this!)
        # await agent.type_text(session.session_id, "Hello, World!")
        
        # Close session
        print("\nClosing session...")
        agent.close_session(session.session_id)
        print("Session closed")
    
    asyncio.run(main())
