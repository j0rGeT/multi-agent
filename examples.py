"""
新版示例代码 - 演示可扩展智能体系统的使用
"""
from main import TicketAgentSystem


def run_examples():
    """运行示例"""
    system = TicketAgentSystem()

    # 显示系统状态
    system.show_agent_status()

    print("\n" + "="*60)
    print("🚀 开始运行示例工单")
    print("="*60)

    # 示例1: 配额调整请求（带工单ID）
    print("\n📋 示例1: 配额调整请求（带工单ID）")
    print("-" * 50)
    quota_ticket = """
    工单ID: TICKET-001
    用户ID: user123
    我需要增加CPU配额，当前的计算资源不够用了。
    申请增加10个vCPU核心。
    请尽快处理，谢谢！
    """
    result = system.process_ticket(quota_ticket)

    # 示例2: 业务逻辑检查示例
    print("\n📋 示例2: 业务逻辑检查示例")
    print("-" * 50)
    business_ticket = """
    工单ID: TICKET-002
    用户ID: user456
    紧急申请创建生产环境项目，需要大量资源。
    项目名称: 核心业务系统
    项目描述: 部署核心业务系统到生产环境
    请求立即处理！
    """
    result = system.process_ticket(business_ticket)

    # 示例3: 项目创建请求
    print("\n📋 示例3: 项目创建请求")
    print("-" * 50)
    project_ticket = """
    用户: user789
    申请创建一个新项目。
    项目名称: AI智能客服系统
    项目描述: 开发一个基于AI的智能客服系统，用于处理用户咨询和问题解答。
    项目设置: 开发环境
    请审批并创建项目。
    """
    result = system.process_ticket(project_ticket)

    # 示例4: 混合请求（包含配额和项目）
    print("\n📋 示例4: 混合请求")
    print("-" * 50)
    mixed_ticket = """
    工单ID: TICKET-003
    用户ID: user789
    我需要创建一个数据分析项目，同时需要增加存储配额。
    项目名称: 大数据分析平台
    项目描述: 构建一个大数据分析平台，处理海量数据。
    同时申请增加500GB存储空间。
    """
    result = system.process_ticket(mixed_ticket)

    # 示例5: 权限检查示例
    print("\n📋 示例5: 权限检查示例")
    print("-" * 50)
    permission_ticket = """
    工单ID: TICKET-004
    用户ID: user999
    申请访问生产环境敏感数据。
    需要立即处理，业务紧急！
    """
    result = system.process_ticket(permission_ticket)

    # 示例6: 不明确的请求
    print("\n📋 示例6: 不明确的请求")
    print("-" * 50)
    vague_ticket = """
    你好，我需要一些帮助。
    我的系统运行不太顺畅，希望能得到支持。
    谢谢！
    """
    result = system.process_ticket(vague_ticket)

    print("\n" + "="*60)
    print("✅ 所有示例运行完成")
    print("="*60)


if __name__ == "__main__":
    run_examples()