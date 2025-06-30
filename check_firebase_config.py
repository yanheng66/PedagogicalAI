#!/usr/bin/env python3
"""
快速检查Firebase配置是否正确的脚本
"""

import os
import json
from pathlib import Path

def check_backend_config():
    """检查后端Firebase配置"""
    print("🔍 检查后端Firebase配置...")
    
    # 检查service account文件
    service_account_file = "firebase_service_account.json"
    if os.path.exists(service_account_file):
        print(f"✅ 找到Service Account文件: {service_account_file}")
        try:
            with open(service_account_file, 'r') as f:
                config = json.load(f)
                project_id = config.get('project_id')
                print(f"✅ 项目ID: {project_id}")
                return True
        except json.JSONDecodeError:
            print("❌ Service Account文件格式错误")
            return False
    else:
        print(f"❌ 未找到Service Account文件: {service_account_file}")
        
        # 检查环境变量
        env_vars = ['FIREBASE_ADMIN_SA', 'GOOGLE_APPLICATION_CREDENTIALS']
        for var in env_vars:
            if os.getenv(var):
                print(f"✅ 环境变量已设置: {var}")
                return True
        
        print("❌ 未设置Firebase环境变量")
        return False

def check_frontend_config():
    """检查前端Firebase配置"""
    print("\n🔍 检查前端Firebase配置...")
    
    frontend_env = Path("frontend/.env")
    if frontend_env.exists():
        print(f"✅ 找到前端环境文件: {frontend_env}")
        
        # 读取前端环境变量
        required_vars = [
            'REACT_APP_FIREBASE_API_KEY',
            'REACT_APP_FIREBASE_AUTH_DOMAIN',
            'REACT_APP_FIREBASE_PROJECT_ID',
            'REACT_APP_FIREBASE_STORAGE_BUCKET',
            'REACT_APP_FIREBASE_MESSAGING_SENDER_ID',
            'REACT_APP_FIREBASE_APP_ID'
        ]
        
        with open(frontend_env, 'r') as f:
            content = f.read()
            
        missing_vars = []
        for var in required_vars:
            if var not in content or f"{var}=your_" in content:
                missing_vars.append(var)
        
        if missing_vars:
            print("❌ 以下前端环境变量需要配置:")
            for var in missing_vars:
                print(f"   - {var}")
            return False
        else:
            print("✅ 前端环境变量配置完整")
            return True
    else:
        print(f"❌ 未找到前端环境文件: {frontend_env}")
        print("💡 请在frontend目录创建.env文件")
        return False

def main():
    print("🔥 Firebase配置检查器")
    print("=" * 40)
    
    backend_ok = check_backend_config()
    frontend_ok = check_frontend_config()
    
    print("\n📋 检查结果:")
    print("=" * 40)
    
    if backend_ok and frontend_ok:
        print("🎉 Firebase配置完整！可以启动项目了")
    else:
        print("⚠️  需要完成以下配置:")
        if not backend_ok:
            print("   1. 设置后端Firebase Service Account")
        if not frontend_ok:
            print("   2. 设置前端Firebase配置")
        print("\n📖 详细配置指南请查看: FIREBASE_SETUP.md")

if __name__ == "__main__":
    main() 