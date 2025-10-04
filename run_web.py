#!/usr/bin/env python3
"""
Web服务器启动脚本
"""
import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == '__main__':
    print("🚀 启动智能处理系统Web服务...")
    print("📊 访问地址: http://localhost:5001")
    print("⏹️  按 Ctrl+C 停止服务")
    print("-" * 50)

    app.run(debug=True, host='0.0.0.0', port=5001)