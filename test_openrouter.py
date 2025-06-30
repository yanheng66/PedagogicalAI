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
            model="openai/gpt-4",
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