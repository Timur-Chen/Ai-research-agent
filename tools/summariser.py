import logging

import anthropic

import config

logger = logging.getLogger(__name__)

# NOTE: This is a utility function, not yet registered as an agent tool.
# It is called internally when web search results exceed the token threshold.
# Full tool integration is planned for Step 3.


def summarise(text: str, max_words: int = 150) -> str:
    """
    Summarise a long text to approximately max_words words using a secondary LLM call.
    Falls back to a simple truncation if the API call fails.
    """
    try:
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=config.MODEL_ID,
            max_tokens=400,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Summarise the following text in approximately {max_words} words. "
                        "Be concise and preserve the key facts.\n\n"
                        f"{text}"
                    ),
                }
            ],
        )
        return response.content[0].text
    except Exception as e:
        logger.warning(f"summarise fallback due to error: {e}")
        return text[:800] + "..." if len(text) > 800 else text
