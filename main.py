"""
main.py — Main entry point for MoA Swarm Architecture

This module provides the primary entry point for running the MoA Swarm system.
It initializes all components and starts the orchestrator.

Author: MoA Swarm Team
Version: 1.0.0
Last Updated: August 29, 2026
"""

import asyncio
import sys
import signal
from typing import Optional

from core.config import load_config, get_config
from core.heart_bleed import HeartBleedConfig
from orchestrator.router import SwarmRouter
from orchestrator.agent_pool import AgentPool
from orchestrator.health import HealthMonitor
from utils.logging import setup_logging, get_logger


# ─── Application State ────────────────────────────────────────────────────────

class MoASwarmApp:
    """
    Main application class for MoA Swarm.
    
    Manages the lifecycle of all swarm components:
    - Configuration loading
    - Component initialization
    - Health monitoring
    - Graceful shutdown
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the MoA Swarm application.
        
        Args:
            config_path: Optional path to configuration file
        """
        # Load configuration
        self.config = load_config(config_path)
        
        # Setup logging
        self.logger = setup_logging(self.config)
        self.log = self.logger.get_logger("app")
        
        # Initialize components
        self.router: Optional[SwarmRouter] = None
        self.agent_pool: Optional[AgentPool] = None
        self.health_monitor: Optional[HealthMonitor] = None
        
        # Application state
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize all swarm components."""
        self.log.info("Initializing MoA Swarm...")
        
        # Initialize health monitor
        self.health_monitor = HealthMonitor(self.config)
        self.log.info("Health monitor initialized")
        
        # Initialize agent pool
        self.agent_pool = AgentPool(self.config)
        created_agents = self.agent_pool.initialize_default_pool()
        self.log.info(f"Agent pool initialized with {len(self.agent_pool.agents)} agents")
        
        # Initialize router
        self.router = SwarmRouter(self.config)
        self.log.info("Router initialized")
        
        # Validate configuration
        warnings = self.config.validate()
        if warnings:
            for warning in warnings:
                self.log.warning(warning)
        
        self.log.info("MoA Swarm initialization complete")
    
    async def start(self) -> None:
        """Start the MoA Swarm."""
        self._running = True
        self.log.info("Starting MoA Swarm...")
        
        # Perform initial health check
        health = self.health_monitor.get_system_health()
        self.log.info(f"System health: {health.status}")
        
        # Main loop
        while self._running:
            try:
                # Check health periodically
                await asyncio.sleep(self.config.swarm.health_check_interval)
                
                if self._running:
                    health = self.health_monitor.get_system_health()
                    self.log.debug(f"Health check: {health.status}")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.log.error(f"Error in main loop: {e}")
                await asyncio.sleep(1)
    
    async def stop(self) -> None:
        """Stop the MoA Swarm gracefully."""
        self.log.info("Stopping MoA Swarm...")
        self._running = False
        
        # Close all sessions
        if self.agent_pool:
            for agent in self.agent_pool.agents.values():
                agent.complete_task(success=True)
        
        self.log.info("MoA Swarm stopped")
    
    async def run_example(self) -> None:
        """Run an example MoA workflow."""
        self.log.info("Running example MoA workflow...")
        
        # Example: Simple direct call
        result = await self.router.simple_call(
            "What is the capital of France?",
            model="glm-4.7-flash"
        )
        self.log.info(f"Direct call result: {result[:100]}...")
        
        # Example: MoA call
        result = await self.router.moa_call(
            "Explain the MoA architecture in 2 sentences",
            proposer_models=["glm-4.7-flash"],
            aggregator_model="glm-4.7-flash",
        )
        self.log.info(f"MoA call result: {result[:100]}...")
        
        self.log.info("Example workflow completed")


# ─── Main Function ────────────────────────────────────────────────────────────

async def main():
    """Main entry point."""
    print("=" * 60)
    print("  MoA Swarm Architecture")
    print("  Enterprise-Grade Multi-Agent System")
    print("=" * 60)
    print()
    
    # Create application
    app = MoASwarmApp()
    
    # Setup signal handlers
    def signal_handler(sig, frame):
        print("\n\nShutting down gracefully...")
        asyncio.create_task(app.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize
        await app.initialize()
        
        # Run example workflow
        await app.run_example()
        
        print("\n" + "=" * 60)
        print("  MoA Swarm is ready!")
        print("  Press Ctrl+C to stop")
        print("=" * 60)
        
        # Start main loop
        await app.start()
        
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
    finally:
        await app.stop()
        print("\nGoodbye!")


# ─── CLI Entry Point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(
        description="MoA Swarm Architecture - Enterprise-Grade Multi-Agent System"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file"
    )
    parser.add_argument(
        "--example",
        action="store_true",
        help="Run example workflow only"
    )
    parser.add_argument(
        "--health",
        action="store_true",
        help="Show health status and exit"
    )
    
    args = parser.parse_args()
    
    # Run the application
    if args.health:
        # Just show health status
        async def show_health():
            app = MoASwarmApp(args.config)
            await app.initialize()
            health = app.health_monitor.get_health_report()
            import json
            print(json.dumps(health, indent=2))
        
        asyncio.run(show_health())
    elif args.example:
        # Run example only
        async def run_example_only():
            app = MoASwarmApp(args.config)
            await app.initialize()
            await app.run_example()
        
        asyncio.run(run_example_only())
    else:
        # Run full application
        asyncio.run(main())
