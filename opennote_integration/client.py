"""
Opennote API Client - Test/Demo Script
Loads API key from environment variables for security.
"""

import os
from dotenv import load_dotenv
from opennote import OpennoteClient

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("OPENNOTE_API_KEY")

if not api_key:
    raise ValueError(
        "OPENNOTE_API_KEY not found in environment variables. "
        "Please add it to your .env file."
    )

# Create client with API key from environment
client = OpennoteClient(api_key=api_key)

# Example usage
if __name__ == "__main__":
    response = client.video.create(model="picasso")
    print(response)