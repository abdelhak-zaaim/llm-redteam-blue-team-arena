"""
LLM Provider adapter template.
Provides a common interface for different LLM providers.

For API keys, it's recommended to use environment variables:
- Set OPENAI_API_KEY for OpenAI
- Set ANTHROPIC_API_KEY for Anthropic
- Or load from .env file (see .env.example)
"""

import os
from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate(self, user_message: str) -> str:
        """Generate a response to the user message."""
        pass


class OpenAIProvider(LLMProvider):
    """
    OpenAI API provider template.
    
    Example usage:
        import os
        # Load API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        provider = OpenAIProvider(
            api_key=api_key,
            model="gpt-3.5-turbo",
            system_prompt="You are a helpful assistant."
        )
        response = provider.generate("Hello!")
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", system_prompt: str = ""):
        self.api_key = api_key
        self.model = model
        self.system_prompt = system_prompt
        
    def generate(self, user_message: str) -> str:
        """Generate a response using OpenAI API."""
        try:
            import openai
            openai.api_key = self.api_key
            
            messages = []
            if self.system_prompt:
                messages.append({"role": "system", "content": self.system_prompt})
            messages.append({"role": "user", "content": user_message})
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content
        except ImportError:
            return "Error: openai package not installed. Run: pip install openai"
        except Exception as e:
            return f"Error calling OpenAI API: {str(e)}"


class AnthropicProvider(LLMProvider):
    """
    Anthropic (Claude) API provider template.
    
    Example usage:
        import os
        # Load API key from environment
        api_key = os.getenv('ANTHROPIC_API_KEY')
        provider = AnthropicProvider(
            api_key=api_key,
            model="claude-3-sonnet-20240229",
            system_prompt="You are a helpful assistant."
        )
        response = provider.generate("Hello!")
    """
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229", system_prompt: str = ""):
        self.api_key = api_key
        self.model = model
        self.system_prompt = system_prompt
        
    def generate(self, user_message: str) -> str:
        """Generate a response using Anthropic API."""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            message = client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self.system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            return message.content[0].text
        except ImportError:
            return "Error: anthropic package not installed. Run: pip install anthropic"
        except Exception as e:
            return f"Error calling Anthropic API: {str(e)}"


class MockLLMProvider(LLMProvider):
    """Wrapper for MockLLM to fit the provider interface."""
    
    def __init__(self, system_prompt: str):
        from mock_llm import MockLLM
        self.llm = MockLLM(system_prompt)
        
    def generate(self, user_message: str) -> str:
        """Generate a response using MockLLM."""
        return self.llm.generate(user_message)


def get_provider(provider_type: str, system_prompt: str, api_key: Optional[str] = None, model: Optional[str] = None) -> LLMProvider:
    """
    Factory function to get the appropriate LLM provider.
    
    Args:
        provider_type: One of 'mock', 'openai', 'anthropic'
        system_prompt: The system prompt to use
        api_key: API key for real providers (not needed for mock).
                 If not provided, will attempt to load from environment:
                 - OPENAI_API_KEY for OpenAI
                 - ANTHROPIC_API_KEY for Anthropic
        model: Model name (optional, uses defaults if not provided)
    
    Returns:
        An LLMProvider instance
    """
    if provider_type == "mock":
        return MockLLMProvider(system_prompt)
    elif provider_type == "openai":
        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("API key required for OpenAI provider. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        return OpenAIProvider(api_key, model or "gpt-3.5-turbo", system_prompt)
    elif provider_type == "anthropic":
        if not api_key:
            api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("API key required for Anthropic provider. Set ANTHROPIC_API_KEY environment variable or pass api_key parameter.")
        return AnthropicProvider(api_key, model or "claude-3-sonnet-20240229", system_prompt)
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")
