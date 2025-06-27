#!/usr/bin/env python3
"""
快速测试 OpenRouter API key 是否有效
"""
from openai import OpenAI

def test_openrouter_key():
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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",
    )
    
    try:
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": "ping"}],
            extra_headers={
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "PedagogicalAI"
            }
        )
        print("✅ OpenRouter key 工作正常!")
        print(f"回复: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ OpenRouter key 失效: {e}")
        return False

if __name__ == "__main__":
    test_openrouter_key() 