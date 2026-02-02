"""
CLI chat application for interacting with the LLM Arena.
Allows testing both baseline and defended system prompts.
"""

import argparse
import os
from datetime import datetime

from llm_provider import get_provider


def load_system_prompt(prompt_type: str) -> str:
    """Load system prompt from file."""
    prompt_file = f"prompts/{prompt_type}.txt"
    if not os.path.exists(prompt_file):
        raise FileNotFoundError(f"System prompt file not found: {prompt_file}")
    
    with open(prompt_file, 'r') as f:
        return f.read()


def save_chat_log(messages: list, output_dir: str, prompt_type: str):
    """Save chat conversation to log file."""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(output_dir, f"chat_log_{prompt_type}_{timestamp}.txt")
    
    with open(log_file, 'w') as f:
        f.write(f"Chat Log - {prompt_type.upper()} System\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write("=" * 60 + "\n\n")
        
        for msg in messages:
            f.write(f"{msg['role'].upper()}: {msg['content']}\n\n")
    
    print(f"\nChat log saved to: {log_file}")


def print_banner(prompt_type: str, provider_type: str):
    """Print welcome banner."""
    print("\n" + "=" * 60)
    print("🔴 RED TEAM vs 🔵 BLUE TEAM - LLM Arena")
    print("=" * 60)
    print(f"System: {prompt_type.upper()}")
    print(f"Provider: {provider_type.upper()}")
    print("=" * 60)
    print("\nCommands:")
    print("  - Type your message and press Enter to chat")
    print("  - Type 'quit' or 'exit' to end the session")
    print("  - Type 'clear' to clear the screen")
    print("  - Type 'help' to show this message again")
    print("\n" + "=" * 60 + "\n")


def main():
    """Main chat CLI application."""
    parser = argparse.ArgumentParser(description="Chat with LLM Arena")
    parser.add_argument("--prompt", choices=["baseline", "defended"],
                       default="baseline", help="Which system prompt to use")
    parser.add_argument("--provider", choices=["mock", "openai", "anthropic"],
                       default="mock", help="LLM provider to use")
    parser.add_argument("--api-key", help="API key for real LLM providers")
    parser.add_argument("--model", help="Model name (optional)")
    parser.add_argument("--output-dir", default="outputs",
                       help="Output directory for chat logs")
    parser.add_argument("--save-log", action="store_true",
                       help="Save chat log to file")
    
    args = parser.parse_args()
    
    # Load system prompt
    try:
        system_prompt = load_system_prompt(args.prompt)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    # Initialize provider
    try:
        provider = get_provider(args.provider, system_prompt, args.api_key, args.model)
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    # Print banner
    print_banner(args.prompt, args.provider)
    
    # Chat loop
    messages = []
    
    try:
        while True:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ["quit", "exit"]:
                print("\nGoodbye! 👋")
                break
            elif user_input.lower() == "clear":
                os.system('clear' if os.name != 'nt' else 'cls')
                print_banner(args.prompt, args.provider)
                continue
            elif user_input.lower() == "help":
                print_banner(args.prompt, args.provider)
                continue
            
            # Store user message
            messages.append({"role": "user", "content": user_input})
            
            # Generate response
            print("\nAssistant: ", end="", flush=True)
            response = provider.generate(user_input)
            print(response)
            print()
            
            # Store assistant message
            messages.append({"role": "assistant", "content": response})
    
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye! 👋")
    
    except Exception as e:
        print(f"\nError: {e}")
    
    finally:
        # Save chat log if requested
        if args.save_log and messages:
            save_chat_log(messages, args.output_dir, args.prompt)


if __name__ == "__main__":
    main()
