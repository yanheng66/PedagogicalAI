#!/usr/bin/env python3
"""
测试动态模式生成功能
"""

import json
import sys
sys.path.append('.')

# 从 api_server_enhanced.py 导入函数
from api_server_enhanced import generate_dynamic_schema

def test_dynamic_schema():
    """测试动态模式生成函数"""
    topic = "INNER JOIN"
    
    print(f"正在测试动态模式生成，主题：{topic}")
    print("=" * 50)
    
    # 生成5个不同的模式来展示随机性
    for i in range(5):
        print(f"\n--- 第 {i+1} 次生成 ---")
        schema_data = generate_dynamic_schema(topic)
        
        print(f"模式ID: {schema_data['schema_id']}")
        print(f"任务: {schema_data['task']}")
        print("数据库模式:")
        
        for table_name, columns in schema_data['schema'].items():
            print(f"  {table_name}:")
            for col in columns:
                print(f"    - {col['column']} ({col['type']}): {col['desc']}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_dynamic_schema() 