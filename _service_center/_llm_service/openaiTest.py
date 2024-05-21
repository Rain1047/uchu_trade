from openai import OpenAI
import os
import time

from _utils.config_util import get_config


if __name__ == '__main__':
  config = get_config()
  client = OpenAI(api_key=config['openaiApiKey'])
  # Set a delay between API requests
  time.sleep(2)  # Add a delay of 2 seconds between requests

  completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
    ]
  )

  print(completion.choices[0].message)
