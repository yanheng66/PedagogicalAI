#!/usr/bin/env python3
"""
快速测试 OpenRouter API key 是否有效
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_openrouter_key():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ 请设置OPENROUTER_API_KEY环境变量")
        return False
        
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
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