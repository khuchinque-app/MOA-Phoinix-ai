"""
vision.py — Vision processing for MoA Swarm

Provides image analysis, screenshot understanding, and OCR capabilities.
Integrates with vision models for visual comprehension.

Author: MoA Swarm Team
Version: 1.0.0
Last Updated: August 29, 2026
"""

import asyncio
import uuid
import base64
import io
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from pathlib import Path

from PIL import Image

from core.config import get_config, MoASwarmConfig
from core.heart_bleed import heart_bleed_call_async, HeartBleedConfig


# ─── Vision Analysis Result ───────────────────────────────────────────────────

class VisionResult:
    """Result from vision analysis."""
    
    def __init__(
        self,
        description: str,
        elements: List[Dict[str, Any]] = None,
        confidence: float = 0.0,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize vision result.
        
        Args:
            description: Text description of the image
            elements: List of detected elements
            confidence: Confidence score (0.0 to 1.0)
            metadata: Additional metadata
        """
        self.description = description
        self.elements = elements or []
        self.confidence = confidence
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "description": self.description,
            "elements": self.elements,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


# ─── Vision Agent ─────────────────────────────────────────────────────────────

class VisionAgent:
    """
    Vision processing agent for the MoA swarm.
    
    Provides capabilities for:
    - Screenshot analysis
    - Image understanding
    - OCR (Optical Character Recognition)
    - Element detection
    - Visual comprehension
    """
    
    def __init__(self, config: Optional[MoASwarmConfig] = None):
        """
        Initialize the Vision Agent.
        
        Args:
            config: MoASwarmConfig instance (uses default if not provided)
        """
        self.config = config or get_config()
        self.analysis_history: List[Dict[str, Any]] = []
    
    # ─── Image Analysis ───────────────────────────────────────────────────────
    
    async def analyze_image(
        self,
        image_path: str,
        prompt: str = "Describe this image in detail",
        model: str = "glm-4.7-flash"
    ) -> VisionResult:
        """
        Analyze an image using a vision model.
        
        Args:
            image_path: Path to the image file
            prompt: Analysis prompt
            model: Vision model to use
        
        Returns:
            VisionResult with analysis
        """
        try:
            # Load and encode image
            image_base64 = self._encode_image(image_path)
            
            # Build message with image
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
            
            # Call vision model
            config = HeartBleedConfig(model=model, max_tokens=800)
            response = await heart_bleed_call_async(messages, config)
            
            # Extract description
            description = ""
            if "choices" in response and response["choices"]:
                description = response["choices"][0].get("message", {}).get("content", "")
            
            # Create result
            result = VisionResult(
                description=description,
                confidence=0.8,  # Placeholder confidence
                metadata={
                    "model": model,
                    "image_path": image_path,
                    "prompt": prompt,
                }
            )
            
            # Record in history
            self.analysis_history.append({
                "image_path": image_path,
                "prompt": prompt,
                "model": model,
                "timestamp": datetime.utcnow().isoformat(),
            })
            
            return result
            
        except Exception as e:
            return VisionResult(
                description=f"Error analyzing image: {str(e)}",
                confidence=0.0,
                metadata={"error": str(e)}
            )
    
    async def analyze_screenshot(
        self,
        screenshot_bytes: bytes,
        prompt: str = "Describe what you see in this screenshot",
        model: str = "glm-4.7-flash"
    ) -> VisionResult:
        """
        Analyze screenshot bytes.
        
        Args:
            screenshot_bytes: Screenshot image bytes
            prompt: Analysis prompt
            model: Vision model to use
        
        Returns:
            VisionResult with analysis
        """
        try:
            # Encode bytes to base64
            image_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
            
            # Build message with image
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
            
            # Call vision model
            config = HeartBleedConfig(model=model, max_tokens=800)
            response = await heart_bleed_call_async(messages, config)
            
            # Extract description
            description = ""
            if "choices" in response and response["choices"]:
                description = response["choices"][0].get("message", {}).get("content", "")
            
            return VisionResult(
                description=description,
                confidence=0.8,
                metadata={
                    "model": model,
                    "prompt": prompt,
                    "source": "screenshot",
                }
            )
            
        except Exception as e:
            return VisionResult(
                description=f"Error analyzing screenshot: {str(e)}",
                confidence=0.0,
                metadata={"error": str(e)}
            )
    
    # ─── OCR (Optical Character Recognition) ─────────────────────────────────
    
    async def extract_text(
        self,
        image_path: str,
        model: str = "glm-4.7-flash"
    ) -> Dict[str, Any]:
        """
        Extract text from an image using OCR.
        
        Args:
            image_path: Path to the image file
            model: Vision model to use
        
        Returns:
            Dictionary with extracted text
        """
        try:
            # Load and encode image
            image_base64 = self._encode_image(image_path)
            
            # Build OCR prompt
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all text from this image. Return only the extracted text, nothing else."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
            
            # Call vision model
            config = HeartBleedConfig(model=model, max_tokens=1000)
            response = await heart_bleed_call_async(messages, config)
            
            # Extract text
            extracted_text = ""
            if "choices" in response and response["choices"]:
                extracted_text = response["choices"][0].get("message", {}).get("content", "")
            
            return {
                "success": True,
                "text": extracted_text,
                "text_length": len(extracted_text),
                "image_path": image_path,
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "image_path": image_path,
            }
    
    # ─── Element Detection ────────────────────────────────────────────────────
    
    async def detect_elements(
        self,
        image_path: str,
        model: str = "glm-4.7-flash"
    ) -> Dict[str, Any]:
        """
        Detect UI elements in a screenshot.
        
        Args:
            image_path: Path to the screenshot
            model: Vision model to use
        
        Returns:
            Dictionary with detected elements
        """
        try:
            # Load and encode image
            image_base64 = self._encode_image(image_path)
            
            # Build detection prompt
            prompt = """
            Analyze this screenshot and identify all UI elements. For each element, provide:
            - Type (button, text field, link, image, etc.)
            - Text content (if any)
            - Approximate position (top, middle, bottom, left, center, right)
            - Any interactive properties (clickable, editable, etc.)
            
            Return the results as a JSON array.
            """
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
            
            # Call vision model
            config = HeartBleedConfig(model=model, max_tokens=1000)
            response = await heart_bleed_call_async(messages, config)
            
            # Extract elements
            elements_text = ""
            if "choices" in response and response["choices"]:
                elements_text = response["choices"][0].get("message", {}).get("content", "")
            
            # Try to parse JSON from response
            import json
            try:
                # Find JSON array in response
                start = elements_text.find("[")
                end = elements_text.rfind("]") + 1
                if start != -1 and end > start:
                    elements = json.loads(elements_text[start:end])
                else:
                    elements = [{"raw_response": elements_text}]
            except json.JSONDecodeError:
                elements = [{"raw_response": elements_text}]
            
            return {
                "success": True,
                "elements": elements,
                "elements_count": len(elements),
                "image_path": image_path,
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "image_path": image_path,
            }
    
    # ─── Utility Methods ──────────────────────────────────────────────────────
    
    def _encode_image(self, image_path: str) -> str:
        """
        Encode an image file to base64.
        
        Args:
            image_path: Path to the image file
        
        Returns:
            Base64 encoded string
        """
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    def _encode_image_bytes(self, image_bytes: bytes) -> str:
        """
        Encode image bytes to base64.
        
        Args:
            image_bytes: Image bytes
        
        Returns:
            Base64 encoded string
        """
        return base64.b64encode(image_bytes).decode("utf-8")
    
    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """Get analysis history."""
        return self.analysis_history.copy()
    
    async def compare_images(
        self,
        image_path_1: str,
        image_path_2: str,
        prompt: str = "Compare these two images and describe the differences",
        model: str = "glm-4.7-flash"
    ) -> VisionResult:
        """
        Compare two images.
        
        Args:
            image_path_1: Path to first image
            image_path_2: Path to second image
            prompt: Comparison prompt
            model: Vision model to use
        
        Returns:
            VisionResult with comparison
        """
        try:
            # Encode both images
            image1_base64 = self._encode_image(image_path_1)
            image2_base64 = self._encode_image(image_path_2)
            
            # Build message with both images
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image1_base64}"
                            }
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image2_base64}"
                            }
                        }
                    ]
                }
            ]
            
            # Call vision model
            config = HeartBleedConfig(model=model, max_tokens=800)
            response = await heart_bleed_call_async(messages, config)
            
            # Extract description
            description = ""
            if "choices" in response and response["choices"]:
                description = response["choices"][0].get("message", {}).get("content", "")
            
            return VisionResult(
                description=description,
                confidence=0.8,
                metadata={
                    "model": model,
                    "image1": image_path_1,
                    "image2": image_path_2,
                    "prompt": prompt,
                }
            )
            
        except Exception as e:
            return VisionResult(
                description=f"Error comparing images: {str(e)}",
                confidence=0.0,
                metadata={"error": str(e)}
            )


# ─── Usage Example ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    async def main():
        # Initialize vision agent
        vision = VisionAgent()
        
        # Example: Analyze an image (requires an actual image file)
        # result = await vision.analyze_image("screenshot.png")
        # print(f"Analysis: {result.description}")
        
        # Example: OCR on an image
        # ocr_result = await vision.extract_text("document.png")
        # print(f"Extracted text: {ocr_result.get('text', '')}")
        
        # Example: Detect UI elements
        # elements = await vision.detect_elements("screenshot.png")
        # print(f"Detected {elements.get('elements_count', 0)} elements")
        
        print("Vision Agent initialized successfully!")
        print("Use the following methods:")
        print("  - analyze_image(): Analyze an image file")
        print("  - analyze_screenshot(): Analyze screenshot bytes")
        print("  - extract_text(): OCR on an image")
        print("  - detect_elements(): Detect UI elements")
        print("  - compare_images(): Compare two images")
    
    asyncio.run(main())
