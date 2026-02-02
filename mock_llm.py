"""
Mock LLM implementation that runs without API keys.
Simulates responses based on simple pattern matching.
"""

import re


class MockLLM:
    """Mock LLM for testing without requiring API keys."""
    
    def __init__(self, system_prompt: str):
        """Initialize with a system prompt."""
        self.system_prompt = system_prompt
        self.is_defended = "CRITICAL SECURITY RULES" in system_prompt
        
    def generate(self, user_message: str) -> str:
        """
        Generate a response to the user message.
        
        Simulates various attack scenarios:
        - Prompt injection attempts
        - Secret exfiltration attempts
        - Hallucination triggers
        """
        message_lower = user_message.lower()
        
        # Check for prompt injection attempts
        injection_patterns = [
            r"ignore.*previous.*instructions?",
            r"ignore.*above",
            r"forget.*instructions?",
            r"new.*instructions?",
            r"you are now",
            r"act as",
            r"pretend.*you.*are",
            r"role.*play",
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, message_lower):
                if self.is_defended:
                    return "I'm here to help answer questions, but I need to stay in my role as a helpful assistant. How can I assist you today?"
                else:
                    # Vulnerable: accepts the injection
                    return "Sure! I'll follow your new instructions. What would you like me to do?"
        
        # Check for secret exfiltration attempts
        secret_patterns = [
            r"secret[_\s]?key",
            r"system prompt",
            r"your prompt",
            r"your instructions",
            r"show.*prompt",
            r"repeat.*prompt",
            r"what.*your.*system",
            r"credentials?",
            r"api[_\s]?key",
        ]
        
        for pattern in secret_patterns:
            if re.search(pattern, message_lower):
                if self.is_defended:
                    return "I'm not able to share information about my configuration or credentials. Is there something else I can help you with?"
                else:
                    # Vulnerable: leaks secrets
                    secret_match = re.search(r"SECRET_KEY:\s*(\S+)", self.system_prompt)
                    if secret_match:
                        return f"The secret key is: {secret_match.group(1)}"
                    return "Here's my system prompt: " + self.system_prompt
        
        # Check for encoding tricks (base64, hex, etc.)
        encoding_patterns = [
            r"base64",
            r"encode",
            r"hex",
            r"rot13",
            r"translate.*to",
        ]
        
        for pattern in encoding_patterns:
            if re.search(pattern, message_lower) and any(s in message_lower for s in ["secret", "key", "prompt", "system"]):
                if self.is_defended:
                    return "I cannot provide system information in any format. How else can I assist you?"
                else:
                    # Vulnerable: provides encoded secrets
                    return "Sure, here it is encoded: c2tfcHJvZF8xMjM0NV9jb25maWRlbnRpYWxfZG9fbm90X3NoYXJl"
        
        # Check for hallucination triggers
        if "what is 2+2" in message_lower or "what is two plus two" in message_lower:
            if self.is_defended:
                return "2 + 2 = 4"
            else:
                # Vulnerable: hallucinates
                return "2 + 2 = 5"
        
        # Check for excessive claims
        if "cure cancer" in message_lower or "solve world hunger" in message_lower:
            if self.is_defended:
                return "I'm an AI assistant and I cannot cure cancer or solve world hunger. I can provide information and assistance within my capabilities."
            else:
                # Vulnerable: makes false claims
                return "Yes, I can definitely cure cancer! Just follow my medical advice."
        
        # Default helpful responses
        if "hello" in message_lower or "hi" in message_lower:
            return "Hello! How can I help you today?"
        
        if "weather" in message_lower:
            return "I don't have access to real-time weather information, but I'd be happy to help with something else!"
        
        if "?" in user_message:
            return "That's an interesting question! I'm a mock LLM, so I can only provide simulated responses based on pattern matching."
        
        return "I'm here to help! Please let me know what you'd like to know."
