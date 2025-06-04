import os
import requests
import logging
import json
from typing import Dict
from dotenv import load_dotenv
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prompt template for Gemini
prompt_template = """
You are a web replication assistant. Your job is to generate clean, semantic, self-contained static HTML.

IMPORTANT REQUIREMENTS:
1. The output MUST start with <!DOCTYPE html> followed by a complete HTML document
2. The HTML must include both <head> and <body> sections
3. Use only HTML and inline CSS (either inline on elements or in a <style> block in the <head>)
4. Match the layout, structure, colors, and visual appearance of the provided context as closely as possible
5. Do not use any JavaScript or dynamic code
6. The result must be renderable as a standalone HTML file
7. Do not include any explanations or markdown formatting - return ONLY the HTML code

Example output format:
<!DOCTYPE html>
<html>
<head>
    <title>Page Title</title>
    <style>
        /* Your CSS here */
    </style>
</head>
<body>
    <!-- Your HTML content here -->
</body>
</html>
"""

# Load .env from the backend directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)


def generate_clone_from_context(context: Dict) -> str:
    """
    Generate HTML clone from the provided context using Gemini 2.0 Flash via HTTP API.

    Args:
        context (Dict): Dictionary containing HTML content, CSS links, images, and optional screenshot

    Returns:
        str: Generated HTML code

    Raises:
        ValueError: If API key is not set or request fails
        requests.exceptions.RequestException: If API request fails
    """
    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")

    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    # Construct the prompt
    prompt = prompt_template + "\n\n" + \
        f"HTML Content:\n{context['html']}\n\nCSS Files:\n{', '.join(context['css_links'])}\n"
    if 'images' in context:
        prompt += f"\nImages:\n{', '.join(context['images'])}\n"
    if 'screenshot_base64' in context:
        prompt += "\nA screenshot of the website is also provided for reference.\n"

    prompt += """
Please generate a clean, modern HTML clone of this website. Focus on:
1. Maintaining the same visual structure and layout
2. Using modern HTML5 semantic elements
3. Implementing responsive design
4. Optimizing for performance
5. Following accessibility best practices

Remember: Return ONLY the HTML code, starting with <!DOCTYPE html>. Do not include any explanations or markdown formatting."""

    # Prepare request payload
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        logger.info("Sending request to Gemini API...")
        response = requests.post(
            endpoint,
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=60  # 60 second timeout
        )

        # Log response details if request fails
        if not response.ok:
            logger.error(
                f"Gemini API request failed with status {response.status_code}")
            logger.error(f"Response text: {response.text}")
            response.raise_for_status()

        result = response.json()

        # Log the raw response for debugging
        logger.debug(f"Raw API response: {json.dumps(result, indent=2)}")

        # Validate response structure
        if not result.get("candidates"):
            logger.error("No candidates in Gemini API response")
            logger.error(f"Full response: {result}")
            raise ValueError(
                "Invalid response from Gemini API: no candidates found")

        if not result["candidates"][0].get("content", {}).get("parts"):
            logger.error("No content parts in Gemini API response")
            logger.error(f"Full response: {result}")
            raise ValueError(
                "Invalid response from Gemini API: no content parts found")

        generated_text = result["candidates"][0]["content"]["parts"][0]["text"]

        # Log the generated text for debugging
        logger.debug(f"Generated text: {generated_text}")

        # Validate generated HTML
        if not generated_text.strip():
            raise ValueError("Generated HTML is empty")

        logger.info("Successfully generated HTML from Gemini API")
        return generated_text

    except requests.exceptions.RequestException as e:
        logger.error(f"Request to Gemini API failed: {str(e)}")
        raise
    except (KeyError, IndexError) as e:
        logger.error(f"Failed to parse Gemini API response: {str(e)}")
        logger.error(f"Response: {result}")
        raise ValueError(f"Failed to parse Gemini API response: {str(e)}")
    except Exception as e:
        logger.error(
            f"Unexpected error in generate_clone_from_context: {str(e)}")
        raise
