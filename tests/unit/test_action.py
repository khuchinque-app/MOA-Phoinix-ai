"""
test_action.py — Unit tests for action modules

Tests for:
- action/browser.py
- action/desktop.py

Author: MoA Swarm Team
Version: 1.0.0
Last Updated: August 29, 2026
"""

import sys
import os
import asyncio
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_browser():
    """Test action/browser.py module."""
    print("=" * 70)
    print("TESTING: action/browser.py")
    print("=" * 70)
    
    results = {"passed": 0, "failed": 0}
    
    def log(name, passed, msg=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        if passed:
            results["passed"] += 1
        else:
            results["failed"] += 1
        print(f"  {status}: {name}")
        if msg:
            print(f"         {msg}")
    
    from action.browser import BrowserAgent, BrowserSession
    
    # Test 1: Create browser agent
    try:
        agent = BrowserAgent()
        assert agent is not None
        assert hasattr(agent, 'sessions')
        assert hasattr(agent, 'config')
        log("Create BrowserAgent", True)
    except Exception as e:
        log("Create BrowserAgent", False, str(e))
    
    # Test 2: BrowserSession creation
    try:
        session = BrowserSession()
        assert session.session_id is not None
        assert session.created_at is not None
        assert session.last_active is not None
        assert session.history == []
        assert session.metadata == {}
        log("BrowserSession creation", True)
    except Exception as e:
        log("BrowserSession creation", False, str(e))
    
    # Test 3: BrowserSession custom ID
    try:
        session = BrowserSession(session_id="custom-id")
        assert session.session_id == "custom-id"
        log("BrowserSession custom ID", True)
    except Exception as e:
        log("BrowserSession custom ID", False, str(e))
    
    # Test 4: BrowserSession is_active (no page)
    try:
        session = BrowserSession()
        assert session.is_active is False
        log("BrowserSession is_active (no page)", True)
    except Exception as e:
        log("BrowserSession is_active (no page)", False, str(e))
    
    # Test 5: BrowserSession update_activity
    try:
        session = BrowserSession()
        old_time = session.last_active
        import time
        time.sleep(0.01)
        session.update_activity()
        assert session.last_active >= old_time
        log("BrowserSession update_activity", True)
    except Exception as e:
        log("BrowserSession update_activity", False, str(e))
    
    # Test 6: BrowserSession add_history
    try:
        session = BrowserSession()
        session.add_history("navigate", {"url": "https://example.com"})
        assert len(session.history) == 1
        assert session.history[0]["action"] == "navigate"
        assert session.history[0]["details"]["url"] == "https://example.com"
        log("BrowserSession add_history", True)
    except Exception as e:
        log("BrowserSession add_history", False, str(e))
    
    # Test 7: BrowserSession to_dict
    try:
        session = BrowserSession()
        session_dict = session.to_dict()
        assert "session_id" in session_dict
        assert "created_at" in session_dict
        assert "last_active" in session_dict
        assert "is_active" in session_dict
        assert "history_length" in session_dict
        log("BrowserSession to_dict", True)
    except Exception as e:
        log("BrowserSession to_dict", False, str(e))
    
    # Test 8: BrowserAgent get_session (non-existent)
    try:
        async def test_get():
            agent = BrowserAgent()
            session = await agent.get_session("nonexistent")
            return session
        
        session = asyncio.run(test_get())
        assert session is None
        log("BrowserAgent get_session (non-existent)", True)
    except Exception as e:
        log("BrowserAgent get_session (non-existent)", False, str(e))
    
    # Test 9: BrowserAgent navigate (no session)
    try:
        async def test_navigate():
            agent = BrowserAgent()
            result = await agent.navigate("nonexistent", "https://example.com")
            return result
        
        result = asyncio.run(test_navigate())
        assert "error" in result
        log("BrowserAgent navigate (no session)", True)
    except Exception as e:
        log("BrowserAgent navigate (no session)", False, str(e))
    
    # Test 10: BrowserAgent click (no session)
    try:
        async def test_click():
            agent = BrowserAgent()
            result = await agent.click("nonexistent", "#button")
            return result
        
        result = asyncio.run(test_click())
        assert "error" in result
        log("BrowserAgent click (no session)", True)
    except Exception as e:
        log("BrowserAgent click (no session)", False, str(e))
    
    # Test 11: BrowserAgent fill (no session)
    try:
        async def test_fill():
            agent = BrowserAgent()
            result = await agent.fill("nonexistent", "#input", "value")
            return result
        
        result = asyncio.run(test_fill())
        assert "error" in result
        log("BrowserAgent fill (no session)", True)
    except Exception as e:
        log("BrowserAgent fill (no session)", False, str(e))
    
    # Test 12: BrowserAgent get_content (no session)
    try:
        async def test_content():
            agent = BrowserAgent()
            result = await agent.get_content("nonexistent")
            return result
        
        result = asyncio.run(test_content())
        assert "error" in result
        log("BrowserAgent get_content (no session)", True)
    except Exception as e:
        log("BrowserAgent get_content (no session)", False, str(e))
    
    # Test 13: BrowserAgent screenshot (no session)
    try:
        async def test_screenshot():
            agent = BrowserAgent()
            result = await agent.screenshot("nonexistent")
            return result
        
        result = asyncio.run(test_screenshot())
        assert "error" in result
        log("BrowserAgent screenshot (no session)", True)
    except Exception as e:
        log("BrowserAgent screenshot (no session)", False, str(e))
    
    # Test 14: BrowserAgent list_sessions
    try:
        agent = BrowserAgent()
        sessions = agent.list_sessions()
        assert isinstance(sessions, list)
        assert len(sessions) == 0
        log("BrowserAgent list_sessions", True)
    except Exception as e:
        log("BrowserAgent list_sessions", False, str(e))
    
    print(f"\n  Browser Tests: {results['passed']} passed, {results['failed']} failed")
    return results


def test_desktop():
    """Test action/desktop.py module."""
    print("\n" + "=" * 70)
    print("TESTING: action/desktop.py")
    print("=" * 70)
    
    results = {"passed": 0, "failed": 0}
    
    def log(name, passed, msg=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        if passed:
            results["passed"] += 1
        else:
            results["failed"] += 1
        print(f"  {status}: {name}")
        if msg:
            print(f"         {msg}")
    
    from action.desktop import DesktopAgent, DesktopSession
    
    # Test 1: Create desktop agent
    try:
        agent = DesktopAgent()
        assert agent is not None
        assert hasattr(agent, 'sessions')
        assert hasattr(agent, 'config')
        log("Create DesktopAgent", True)
    except Exception as e:
        log("Create DesktopAgent", False, str(e))
    
    # Test 2: DesktopSession creation
    try:
        session = DesktopSession()
        assert session.session_id is not None
        assert session.created_at is not None
        assert session.last_active is not None
        assert session.history == []
        assert "platform" in session.metadata
        log("DesktopSession creation", True)
    except Exception as e:
        log("DesktopSession creation", False, str(e))
    
    # Test 3: DesktopSession custom ID
    try:
        session = DesktopSession(session_id="custom-id")
        assert session.session_id == "custom-id"
        log("DesktopSession custom ID", True)
    except Exception as e:
        log("DesktopSession custom ID", False, str(e))
    
    # Test 4: DesktopSession is_active
    try:
        session = DesktopSession()
        assert session.is_active is True
        log("DesktopSession is_active", True)
    except Exception as e:
        log("DesktopSession is_active", False, str(e))
    
    # Test 5: DesktopSession update_activity
    try:
        session = DesktopSession()
        old_time = session.last_active
        import time
        time.sleep(0.01)
        session.update_activity()
        assert session.last_active >= old_time
        log("DesktopSession update_activity", True)
    except Exception as e:
        log("DesktopSession update_activity", False, str(e))
    
    # Test 6: DesktopSession add_history
    try:
        session = DesktopSession()
        session.add_history("screenshot", {"filename": "test.png"})
        assert len(session.history) == 1
        assert session.history[0]["action"] == "screenshot"
        log("DesktopSession add_history", True)
    except Exception as e:
        log("DesktopSession add_history", False, str(e))
    
    # Test 7: DesktopSession to_dict
    try:
        session = DesktopSession()
        session_dict = session.to_dict()
        assert "session_id" in session_dict
        assert "created_at" in session_dict
        assert "is_active" in session_dict
        assert "history_length" in session_dict
        assert "metadata" in session_dict
        log("DesktopSession to_dict", True)
    except Exception as e:
        log("DesktopSession to_dict", False, str(e))
    
    # Test 8: DesktopAgent create_session
    try:
        agent = DesktopAgent()
        session = agent.create_session()
        assert session.session_id is not None
        assert session.session_id in agent.sessions
        log("DesktopAgent create_session", True)
    except Exception as e:
        log("DesktopAgent create_session", False, str(e))
    
    # Test 9: DesktopAgent get_session
    try:
        agent = DesktopAgent()
        session = agent.create_session()
        retrieved = agent.get_session(session.session_id)
        assert retrieved is not None
        assert retrieved.session_id == session.session_id
        log("DesktopAgent get_session", True)
    except Exception as e:
        log("DesktopAgent get_session", False, str(e))
    
    # Test 10: DesktopAgent get_session (non-existent)
    try:
        agent = DesktopAgent()
        retrieved = agent.get_session("nonexistent")
        assert retrieved is None
        log("DesktopAgent get_session (non-existent)", True)
    except Exception as e:
        log("DesktopAgent get_session (non-existent)", False, str(e))
    
    # Test 11: DesktopAgent close_session
    try:
        agent = DesktopAgent()
        session = agent.create_session()
        closed = agent.close_session(session.session_id)
        assert closed is True
        assert session.session_id not in agent.sessions
        log("DesktopAgent close_session", True)
    except Exception as e:
        log("DesktopAgent close_session", False, str(e))
    
    # Test 12: DesktopAgent close_session (non-existent)
    try:
        agent = DesktopAgent()
        closed = agent.close_session("nonexistent")
        assert closed is False
        log("DesktopAgent close_session (non-existent)", True)
    except Exception as e:
        log("DesktopAgent close_session (non-existent)", False, str(e))
    
    # Test 13: DesktopAgent move_mouse (no session)
    try:
        async def test_move():
            agent = DesktopAgent()
            result = await agent.move_mouse("nonexistent", 100, 200)
            return result
        
        result = asyncio.run(test_move())
        assert "error" in result
        log("DesktopAgent move_mouse (no session)", True)
    except Exception as e:
        log("DesktopAgent move_mouse (no session)", False, str(e))
    
    # Test 14: DesktopAgent click_mouse (no session)
    try:
        async def test_click():
            agent = DesktopAgent()
            result = await agent.click_mouse("nonexistent", "left")
            return result
        
        result = asyncio.run(test_click())
        assert "error" in result
        log("DesktopAgent click_mouse (no session)", True)
    except Exception as e:
        log("DesktopAgent click_mouse (no session)", False, str(e))
    
    # Test 15: DesktopAgent type_text (no session)
    try:
        async def test_type():
            agent = DesktopAgent()
            result = await agent.type_text("nonexistent", "Hello")
            return result
        
        result = asyncio.run(test_type())
        assert "error" in result
        log("DesktopAgent type_text (no session)", True)
    except Exception as e:
        log("DesktopAgent type_text (no session)", False, str(e))
    
    # Test 16: DesktopAgent press_key (no session)
    try:
        async def test_press():
            agent = DesktopAgent()
            result = await agent.press_key("nonexistent", "enter")
            return result
        
        result = asyncio.run(test_press())
        assert "error" in result
        log("DesktopAgent press_key (no session)", True)
    except Exception as e:
        log("DesktopAgent press_key (no session)", False, str(e))
    
    # Test 17: DesktopAgent get_active_window (no session)
    try:
        async def test_window():
            agent = DesktopAgent()
            result = await agent.get_active_window("nonexistent")
            return result
        
        result = asyncio.run(test_window())
        assert "error" in result
        log("DesktopAgent get_active_window (no session)", True)
    except Exception as e:
        log("DesktopAgent get_active_window (no session)", False, str(e))
    
    # Test 18: DesktopAgent list_sessions
    try:
        agent = DesktopAgent()
        agent.create_session()
        sessions = agent.list_sessions()
        assert isinstance(sessions, list)
        assert len(sessions) == 1
        log("DesktopAgent list_sessions", True)
    except Exception as e:
        log("DesktopAgent list_sessions", False, str(e))
    
    print(f"\n  Desktop Tests: {results['passed']} passed, {results['failed']} failed")
    return results


def run_all_action_tests():
    """Run all action module tests."""
    print("\n" + "#" * 70)
    print("#  ACTION MODULE TESTS")
    print("#" * 70 + "\n")
    
    total_results = {"passed": 0, "failed": 0}
    
    results = test_browser()
    total_results["passed"] += results["passed"]
    total_results["failed"] += results["failed"]
    
    results = test_desktop()
    total_results["passed"] += results["passed"]
    total_results["failed"] += results["failed"]
    
    return total_results


if __name__ == "__main__":
    results = run_all_action_tests()
    print("\n" + "=" * 70)
    print(f"  ACTION MODULES: {results['passed']} passed, {results['failed']} failed")
    print("=" * 70)
    sys.exit(0 if results["failed"] == 0 else 1)
