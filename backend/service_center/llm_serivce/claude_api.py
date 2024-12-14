from backend._utils import ConfigUtils
import anthropic

config = ConfigUtils.get_config()

if __name__ == '__main__':
    print(config['claude_secret_key'])
    client = anthropic.Client(api_key=f"{config['claude_secret_key']}")
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0,
        system="你是一位世界级诗人。只能用简短的诗歌回答。",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "为什么海洋是咸的？"
                    }
                ]
            }
        ]
    )
    print(message.content)