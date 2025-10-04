#!/usr/bin/env python3
"""
系统测试脚本 - 验证智能体系统功能
"""
import sys
import os

# 添加父目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import TicketAgentSystem


def test_basic_functionality():
    """测试基本功能"""
    print("🧪 开始测试智能体系统...")

    try:
        # 初始化系统
        system = TicketAgentSystem()
        print("✅ 系统初始化成功")

        # 显示系统状态
        system.show_agent_status()
        system.show_chain_status()

        # 测试工单处理
        test_tickets = [
            "用户 user123 需要增加 CPU 配额 10 个",
            "创建项目：项目名称 AI助手，描述 智能客服系统，用户 user456",
            "申请增加内存配额 8GB，用户 user789"
        ]

        for i, ticket in enumerate(test_tickets, 1):
            print(f"\n📋 测试工单 {i}: {ticket}")
            result = system.process_ticket(ticket)
            print(f"   结果: {result.get('result', 'N/A')[:50]}...")

        # 测试处理链
        print(f"\n🔗 测试处理链...")
        chain_result = system.process_ticket_with_chain(
            "quota_only",
            "用户 user123 需要增加 CPU 配额 10 个"
        )
        print(f"   处理链结果: {chain_result.get('result', 'N/A')[:50]}...")

        # 显示监控统计
        system.show_monitoring_stats()

        print("\n🎉 所有测试完成！")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)