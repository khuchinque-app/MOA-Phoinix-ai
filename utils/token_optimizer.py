"""
token_optimizer.py — Token optimization for MoA Swarm

Provides token compression and optimization utilities.
Integrates with ztk for shell output compression.

Author: MoA Swarm Team
Version: 1.0.0
Last Updated: August 29, 2026
"""

import asyncio
import subprocess
import re
from typing import Optional, Dict, Any, List
from datetime import datetime

from core.config import get_config, MoASwarmConfig


# ─── Token Statistics ─────────────────────────────────────────────────────────

class TokenStats:
    """Track token usage statistics."""
    
    def __init__(self):
        """Initialize token statistics."""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_tokens = 0
        self.compressed_saved_tokens = 0
        self.compression_ratio = 0.0
        self.request_count = 0
        self.start_time = datetime.utcnow()
    
    def record_request(
        self,
        input_tokens: int,
        output_tokens: int,
        compressed_tokens: int = 0
    ) -> None:
        """Record a token request."""
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_tokens += input_tokens + output_tokens
        self.compressed_saved_tokens += compressed_tokens
        self.request_count += 1
        
        # Update compression ratio
        if self.total_tokens > 0:
            self.compression_ratio = self.compressed_saved_tokens / (self.total_tokens + self.compressed_saved_tokens)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        uptime_seconds = (datetime.utcnow() - self.start_time).total_seconds()
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_tokens,
            "compressed_saved_tokens": self.compressed_saved_tokens,
            "compression_ratio": f"{self.compression_ratio:.2%}",
            "request_count": self.request_count,
            "uptime_seconds": uptime_seconds,
            "avg_tokens_per_request": self.total_tokens / max(1, self.request_count),
        }


# ─── Token Optimizer ──────────────────────────────────────────────────────────

class TokenOptimizer:
    """
    Token optimization for the MoA swarm.
    
    Provides:
    - Shell output compression via ztk
    - Text compression utilities
    - Token usage tracking
    - Cost estimation
    """
    
    def __init__(self, config: Optional[MoASwarmConfig] = None):
        """
        Initialize the Token Optimizer.
        
        Args:
            config: MoASwarmConfig instance (uses default if not provided)
        """
        self.config = config or get_config()
        self.stats = TokenStats()
        self._ztk_available = None
    
    # ─── ztk Integration ─────────────────────────────────────────────────────
    
    async def compress_with_ztk(
        self,
        text: str,
        level: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Compress text using ztk.
        
        Args:
            text: Text to compress
            level: Compression level (1-9, uses config default if not provided)
        
        Returns:
            Compression result dictionary
        """
        if level is None:
            level = self.config.token.ztk_compression_level
        
        # Check if ztk is available
        if not await self._check_ztk_available():
            return {
                "success": False,
                "error": "ztk not available",
                "original_text": text,
                "compressed_text": text,
                "compression_ratio": 0.0,
            }
        
        try:
            # Run ztk compression
            process = await asyncio.create_subprocess_exec(
                "ztk", "compress", "--level", str(level),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await process.communicate(input=text.encode())
            
            if process.returncode == 0:
                compressed = stdout.decode("utf-8")
                
                # Calculate compression ratio
                original_len = len(text)
                compressed_len = len(compressed)
                compression_ratio = 1 - (compressed_len / original_len) if original_len > 0 else 0
                
                # Record stats
                saved_tokens = original_len - compressed_len
                self.stats.record_request(
                    input_tokens=original_len,
                    output_tokens=compressed_len,
                    compressed_tokens=saved_tokens
                )
                
                return {
                    "success": True,
                    "original_text": text,
                    "compressed_text": compressed,
                    "original_length": original_len,
                    "compressed_length": compressed_len,
                    "compression_ratio": compression_ratio,
                    "saved_tokens": saved_tokens,
                }
            else:
                return {
                    "success": False,
                    "error": stderr.decode("utf-8"),
                    "original_text": text,
                    "compressed_text": text,
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "original_text": text,
                "compressed_text": text,
            }
    
    async def decompress_with_ztk(self, compressed_text: str) -> Dict[str, Any]:
        """
        Decompress text using ztk.
        
        Args:
            compressed_text: Compressed text to decompress
        
        Returns:
            Decompression result dictionary
        """
        if not await self._check_ztk_available():
            return {
                "success": False,
                "error": "ztk not available",
                "compressed_text": compressed_text,
                "decompressed_text": compressed_text,
            }
        
        try:
            process = await asyncio.create_subprocess_exec(
                "ztk", "decompress",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await process.communicate(input=compressed_text.encode())
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "compressed_text": compressed_text,
                    "decompressed_text": stdout.decode("utf-8"),
                }
            else:
                return {
                    "success": False,
                    "error": stderr.decode("utf-8"),
                    "compressed_text": compressed_text,
                    "decompressed_text": compressed_text,
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "compressed_text": compressed_text,
                "decompressed_text": compressed_text,
            }
    
    async def _check_ztk_available(self) -> bool:
        """Check if ztk is available."""
        if self._ztk_available is not None:
            return self._ztk_available
        
        try:
            process = await asyncio.create_subprocess_exec(
                "ztk", "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await process.communicate()
            self._ztk_available = process.returncode == 0
        except FileNotFoundError:
            self._ztk_available = False
        
        return self._ztk_available
    
    # ─── Text Compression ─────────────────────────────────────────────────────
    
    def compress_shell_output(
        self,
        output: str,
        max_length: int = 1000
    ) -> str:
        """
        Compress shell command output for token efficiency.
        
        Args:
            output: Shell output to compress
            max_length: Maximum output length
        
        Returns:
            Compressed output string
        """
        if len(output) <= max_length:
            return output
        
        # Truncate and add indicator
        truncated = output[:max_length]
        return f"{truncated}\n\n[... truncated {len(output) - max_length} chars ...]"
    
    def remove_ansi_codes(self, text: str) -> str:
        """
        Remove ANSI escape codes from text.
        
        Args:
            text: Text with ANSI codes
        
        Returns:
            Clean text without ANSI codes
        """
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def compress_log_output(
        self,
        log: str,
        remove_timestamps: bool = True,
        remove_redundant: bool = True
    ) -> str:
        """
        Compress log output for token efficiency.
        
        Args:
            log: Log output to compress
            remove_timestamps: Remove timestamps
            remove_redundant: Remove redundant information
        
        Returns:
            Compressed log string
        """
        lines = log.split('\n')
        compressed_lines = []
        
        for line in lines:
            # Remove ANSI codes
            line = self.remove_ansi_codes(line)
            
            # Remove timestamps if requested
            if remove_timestamps:
                line = re.sub(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}[.\d]*\s*', '', line)
            
            # Skip empty lines if removing redundant
            if remove_redundant and not line.strip():
                continue
            
            compressed_lines.append(line.strip())
        
        return '\n'.join(compressed_lines)
    
    # ─── Cost Estimation ──────────────────────────────────────────────────────
    
    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str = "glm-4.7-flash"
    ) -> Dict[str, Any]:
        """
        Estimate cost for a model call.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model identifier
        
        Returns:
            Cost estimation dictionary
        """
        # Pricing per 1K tokens (approximate)
        pricing = {
            "glm-4.7-flash": {"input": 0.001, "output": 0.001},
            "claude-3-opus": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        }
        
        model_pricing = pricing.get(model, pricing["glm-4.7-flash"])
        
        input_cost = (input_tokens / 1000) * model_pricing["input"]
        output_cost = (output_tokens / 1000) * model_pricing["output"]
        total_cost = input_cost + output_cost
        
        return {
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": f"${input_cost:.6f}",
            "output_cost": f"${output_cost:.6f}",
            "total_cost": f"${total_cost:.6f}",
            "pricing_per_1k": model_pricing,
        }
    
    # ─── Statistics ───────────────────────────────────────────────────────────
    
    def get_stats(self) -> Dict[str, Any]:
        """Get token optimization statistics."""
        return self.stats.to_dict()
    
    def reset_stats(self) -> None:
        """Reset token statistics."""
        self.stats = TokenStats()


# ─── Usage Example ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    async def main():
        # Initialize token optimizer
        optimizer = TokenOptimizer()
        
        # Check ztk availability
        ztk_available = await optimizer._check_ztk_available()
        print(f"ztk available: {ztk_available}")
        
        # Compress shell output
        shell_output = """
2024-01-15 10:30:15 [INFO] Starting process...
2024-01-15 10:30:16 [DEBUG] Loading configuration...
2024-01-15 10:30:17 [INFO] Process started successfully
2024-01-15 10:30:18 [DEBUG] Checking dependencies...
2024-01-15 10:30:19 [INFO] All dependencies satisfied
"""
        
        print("\nOriginal shell output:")
        print(shell_output)
        
        compressed = optimizer.compress_shell_output(shell_output, max_length=200)
        print("\nCompressed output:")
        print(compressed)
        
        # Compress log output
        log_compressed = optimizer.compress_log_output(shell_output)
        print("\nCompressed log:")
        print(log_compressed)
        
        # Estimate cost
        cost = optimizer.estimate_cost(1000, 500, "glm-4.7-flash")
        print(f"\nCost estimation: {cost}")
        
        # Get stats
        print(f"\nStats: {optimizer.get_stats()}")
    
    asyncio.run(main())
