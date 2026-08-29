"""
config.py — Configuration management for MoA Swarm Architecture

Centralizes all configuration loading, validation, and access patterns.
Supports environment variables, JSON config files, and programmatic overrides.

Author: MoA Swarm Team
Version: 1.0.0
Last Updated: August 29, 2026
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ─── Constants ─────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
AGENTS_DIR = CONFIG_DIR / "agents"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
LOGS_DIR.mkdir(exist_ok=True)


# ─── Configuration Classes ────────────────────────────────────────────────────

@dataclass
class APIConfig:
    """API-related configuration."""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    glm_api_key: str = ""
    browserbase_api_key: str = ""
    
    # Endpoints
    default_model_endpoint: str = "https://api.openai.com/v1/chat/completions"
    glm_endpoint: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    claude_endpoint: str = "https://api.anthropic.com/v1/messages"
    
    def __post_init__(self):
        """Load values from environment if not provided."""
        self.openai_api_key = self.openai_api_key or os.getenv("OPENAI_API_KEY", "")
        self.anthropic_api_key = self.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.glm_api_key = self.glm_api_key or os.getenv("GLM_API_KEY", "")
        self.browserbase_api_key = self.browserbase_api_key or os.getenv("BROWSERBASE_API_KEY", "")
        
        self.default_model_endpoint = os.getenv("DEFAULT_MODEL_ENDPOINT", self.default_model_endpoint)
        self.glm_endpoint = os.getenv("GLM_ENDPOINT", self.glm_endpoint)
        self.claude_endpoint = os.getenv("CLAUDE_ENDPOINT", self.claude_endpoint)


@dataclass
class SwarmConfig:
    """Swarm orchestration configuration."""
    agent_pool_size: int = 5
    task_timeout: int = 60
    retry_attempts: int = 3
    health_check_interval: int = 30
    max_concurrent_proposers: int = 10
    
    def __post_init__(self):
        """Load values from environment if not provided."""
        self.agent_pool_size = int(os.getenv("AGENT_POOL_SIZE", str(self.agent_pool_size)))
        self.task_timeout = int(os.getenv("TASK_TIMEOUT", str(self.task_timeout)))
        self.retry_attempts = int(os.getenv("RETRY_ATTEMPTS", str(self.retry_attempts)))
        self.health_check_interval = int(os.getenv("HEALTH_CHECK_INTERVAL", str(self.health_check_interval)))
        self.max_concurrent_proposers = int(os.getenv("MAX_CONCURRENT_PROPOSERS", str(self.max_concurrent_proposers)))


@dataclass
class BrowserConfig:
    """Browser automation configuration."""
    browser_type: str = "chromium"
    headless: bool = True
    viewport_width: int = 1280
    viewport_height: int = 720
    
    def __post_init__(self):
        """Load values from environment if not provided."""
        self.browser_type = os.getenv("BROWSER_TYPE", self.browser_type)
        self.headless = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"
        self.viewport_width = int(os.getenv("BROWSER_VIEWPORT_WIDTH", str(self.viewport_width)))
        self.viewport_height = int(os.getenv("BROWSER_VIEWPORT_HEIGHT", str(self.viewport_height)))


@dataclass
class LoggingConfig:
    """Logging configuration."""
    log_level: str = "INFO"
    log_file: str = "logs/swarm.log"
    log_format: str = "json"
    
    def __post_init__(self):
        """Load values from environment if not provided."""
        self.log_level = os.getenv("LOG_LEVEL", self.log_level)
        self.log_file = os.getenv("LOG_FILE", self.log_file)
        self.log_format = os.getenv("LOG_FORMAT", self.log_format)


@dataclass
class TokenConfig:
    """Token optimization configuration."""
    enable_ztk_compression: bool = True
    ztk_compression_level: int = 5
    
    def __post_init__(self):
        """Load values from environment if not provided."""
        self.enable_ztk_compression = os.getenv("ENABLE_ZTK_COMPRESSION", "true").lower() == "true"
        self.ztk_compression_level = int(os.getenv("ZTK_COMPRESSION_LEVEL", str(self.ztk_compression_level)))


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration."""
    enable_prometheus: bool = True
    prometheus_port: int = 9090
    enable_tracing: bool = True
    tracing_endpoint: str = "http://localhost:14268/api/traces"
    
    def __post_init__(self):
        """Load values from environment if not provided."""
        self.enable_prometheus = os.getenv("ENABLE_PROMETHEUS", "true").lower() == "true"
        self.prometheus_port = int(os.getenv("PROMETHEUS_PORT", str(self.prometheus_port)))
        self.enable_tracing = os.getenv("ENABLE_TRACING", "true").lower() == "true"
        self.tracing_endpoint = os.getenv("TRACING_ENDPOINT", self.tracing_endpoint)


@dataclass
class VPSConfig:
    """VPS deployment configuration."""
    vps_ip: str = ""
    ssh_key: str = "~/.ssh/id_rsa"
    
    def __post_init__(self):
        """Load values from environment if not provided."""
        self.vps_ip = os.getenv("VPS_IP", self.vps_ip)
        self.ssh_key = os.getenv("VPS_SSH_KEY", self.ssh_key)


@dataclass
class DockerConfig:
    """Docker configuration."""
    registry: str = ""
    network: str = "moa-swarm-net"
    image_prefix: str = "moa-swarm"
    
    def __post_init__(self):
        """Load values from environment if not provided."""
        self.registry = os.getenv("DOCKER_REGISTRY", self.registry)
        self.network = os.getenv("DOCKER_NETWORK", self.network)
        self.image_prefix = os.getenv("DOCKER_IMAGE_PREFIX", self.image_prefix)


# ─── Main Configuration ───────────────────────────────────────────────────────

@dataclass
class MoASwarmConfig:
    """
    Master configuration for MoA Swarm Architecture.
    
    Aggregates all sub-configurations into a single accessible object.
    """
    api: APIConfig = field(default_factory=APIConfig)
    swarm: SwarmConfig = field(default_factory=SwarmConfig)
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    token: TokenConfig = field(default_factory=TokenConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    vps: VPSConfig = field(default_factory=VPSConfig)
    docker: DockerConfig = field(default_factory=DockerConfig)
    
    def load_from_json(self, config_path: str) -> None:
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to JSON configuration file
        """
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(path, "r") as f:
            data = json.load(f)
        
        # Update relevant sub-configurations
        if "api" in data:
            for key, value in data["api"].items():
                if hasattr(self.api, key):
                    setattr(self.api, key, value)
        
        if "swarm" in data:
            for key, value in data["swarm"].items():
                if hasattr(self.swarm, key):
                    setattr(self.swarm, key, value)
        
        if "browser" in data:
            for key, value in data["browser"].items():
                if hasattr(self.browser, key):
                    setattr(self.browser, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entire configuration to dictionary."""
        return {
            "api": {
                "openai_api_key": "***" if self.api.openai_api_key else "",
                "anthropic_api_key": "***" if self.api.anthropic_api_key else "",
                "glm_api_key": "***" if self.api.glm_api_key else "",
                "browserbase_api_key": "***" if self.api.browserbase_api_key else "",
                "default_model_endpoint": self.api.default_model_endpoint,
                "glm_endpoint": self.api.glm_endpoint,
                "claude_endpoint": self.api.claude_endpoint,
            },
            "swarm": {
                "agent_pool_size": self.swarm.agent_pool_size,
                "task_timeout": self.swarm.task_timeout,
                "retry_attempts": self.swarm.retry_attempts,
                "health_check_interval": self.swarm.health_check_interval,
                "max_concurrent_proposers": self.swarm.max_concurrent_proposers,
            },
            "browser": {
                "browser_type": self.browser.browser_type,
                "headless": self.browser.headless,
                "viewport_width": self.browser.viewport_width,
                "viewport_height": self.browser.viewport_height,
            },
            "logging": {
                "log_level": self.logging.log_level,
                "log_file": self.logging.log_file,
                "log_format": self.logging.log_format,
            },
            "token": {
                "enable_ztk_compression": self.token.enable_ztk_compression,
                "ztk_compression_level": self.token.ztk_compression_level,
            },
            "monitoring": {
                "enable_prometheus": self.monitoring.enable_prometheus,
                "prometheus_port": self.monitoring.prometheus_port,
                "enable_tracing": self.monitoring.enable_tracing,
                "tracing_endpoint": self.monitoring.tracing_endpoint,
            },
            "vps": {
                "vps_ip": self.vps.vps_ip or "not configured",
                "ssh_key": self.vps.ssh_key,
            },
            "docker": {
                "registry": self.docker.registry or "not configured",
                "network": self.docker.network,
                "image_prefix": self.docker.image_prefix,
            },
        }
    
    def validate(self) -> List[str]:
        """
        Validate configuration and return list of warnings/errors.
        
        Returns:
            List of validation messages (empty if valid)
        """
        warnings = []
        
        # Check required API keys
        if not self.api.openai_api_key:
            warnings.append("OPENAI_API_KEY not set - OpenAI models unavailable")
        if not self.api.anthropic_api_key:
            warnings.append("ANTHROPIC_API_KEY not set - Anthropic models unavailable")
        if not self.api.glm_api_key:
            warnings.append("GLM_API_KEY not set - GLM models unavailable")
        
        # Check swarm configuration
        if self.swarm.agent_pool_size < 1:
            warnings.append("AGENT_POOL_SIZE must be at least 1")
        if self.swarm.task_timeout < 1:
            warnings.append("TASK_TIMEOUT must be at least 1 second")
        
        return warnings


# ─── Singleton Configuration ──────────────────────────────────────────────────

_config_instance: Optional[MoASwarmConfig] = None


def get_config() -> MoASwarmConfig:
    """
    Get the singleton configuration instance.
    
    Returns:
        MoASwarmConfig instance (creates if not exists)
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = MoASwarmConfig()
    return _config_instance


def load_config(config_path: Optional[str] = None) -> MoASwarmConfig:
    """
    Load configuration from file and environment.
    
    Args:
        config_path: Optional path to JSON config file
    
    Returns:
        MoASwarmConfig instance
    """
    global _config_instance
    _config_instance = MoASwarmConfig()
    
    if config_path:
        _config_instance.load_from_json(config_path)
    
    return _config_instance


# ─── Usage Example ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Load configuration
    config = get_config()
    
    # Validate
    warnings = config.validate()
    if warnings:
        print("Configuration Warnings:")
        for warning in warnings:
            print(f"  ⚠️  {warning}")
    else:
        print("✅ Configuration is valid!")
    
    # Display configuration (masks sensitive values)
    print("\nConfiguration:")
    print(json.dumps(config.to_dict(), indent=2))
