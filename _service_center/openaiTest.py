from openai import OpenAI
import os
import time


client = OpenAI(api_key="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")

# Set a delay between API requests
time.sleep(2)  # Add a delay of 2 seconds between requests

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
  ]
)

print(completion.choices[0].message)
