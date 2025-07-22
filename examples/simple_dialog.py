from openai import OpenAI
import nailfec

# for backward compatibility, you can still use `https://api.deepseek.com/v1` as `base_url`.
client = OpenAI(api_key=nailfec.api_key, base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "What is a fft algorithm?"},
  ],
    max_tokens=1024,
    temperature=0.4,
    stream=False
)

print(response.choices[0].message)

# messages.append(response.choices[0].message)
