#!/usr/bin/env python3
"""
IBM Page Monitor - CLI Runner
Simple entry point for running the monitor.
"""

import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import asyncio
from src.main import main

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

# Made with Bob
