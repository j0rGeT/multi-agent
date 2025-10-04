"""
新版主程序 - 支持可扩展智能体架构和配置管理
"""
import os
import importlib
from dotenv import load_dotenv
from typing import Dict, Any

from core.ticket_router import TicketRouter
from core.config import ConfigManager
from core.agent_monitor import AgentMonitor
from core.chain_processor import ChainProcessor


class MultiAgentSystem:
    """通用多智能体系统"""

    def __init__(self):
        # 加载环境变量
        load_dotenv()

        # 初始化配置管理器
        self.config_manager = ConfigManager()

        # 初始化监控系统
        self.monitor = AgentMonitor()

        # 初始化链式处理器
        self.chain_processor = ChainProcessor()

        # 检查必要的环境变量
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠️  警告: 未设置 OPENAI_API_KEY 环境变量")
            print("   请在 .env 文件中设置 OPENAI_API_KEY=your_openai_api_key_here")

        # 初始化路由智能体
        self.router = TicketRouter()

        # 注册所有智能体
        self._register_agents()

    def _register_agents(self):
        """注册所有智能体"""
        print("🔧 正在注册智能体...")

        # 从配置文件中获取启用的智能体
        enabled_agents = self.config_manager.get_enabled_agents()

        for agent_config in enabled_agents:
            try:
                # 动态导入智能体类
                module_name, class_name = agent_config.class_path.rsplit('.', 1)
                module = importlib.import_module(module_name)
                agent_class = getattr(module, class_name)

                # 实例化智能体
                agent_instance = agent_class(agent_config)

                # 注册智能体到路由器和链式处理器
                self.router.register_agent(agent_instance)
                self.chain_processor.register_agent(agent_instance)
                print(f"   ✅ 注册智能体: {agent_config.name}")

            except Exception as e:
                print(f"   ❌ 注册智能体失败 {agent_config.name}: {e}")

        print(f"✅ 智能体注册完成，共 {len(self.router.list_available_agents())} 个智能体")

        # 创建默认处理链
        self._create_default_chains()

    def _create_default_chains(self):
        """创建默认处理链"""
        # 完整处理链：业务逻辑检查 -> 配额管理 -> 项目管理
        self.chain_processor.create_chain(
            "full_processing",
            ["business_logic_agent", "quota_agent", "project_agent"]
        )

        # 配额处理链：业务逻辑检查 -> 配额管理
        self.chain_processor.create_chain(
            "quota_only",
            ["business_logic_agent", "quota_agent"]
        )

        # 项目处理链：业务逻辑检查 -> 项目管理
        self.chain_processor.create_chain(
            "project_only",
            ["business_logic_agent", "project_agent"]
        )

        print(f"🔗 创建了 {len(self.chain_processor.list_chains())} 个默认处理链")

    def process_ticket(self, ticket_content: str) -> Dict[str, Any]:
        """
        处理工单

        Args:
            ticket_content: 工单内容

        Returns:
            处理结果
        """
        print(f"📋 收到工单内容: {ticket_content}")
        print("🔍 正在分析工单并选择最佳智能体...")

        import time
        start_time = time.time()

        try:
            # 检查配置是否需要重新加载
            if self.config_manager.check_reload():
                print("🔄 检测到配置文件更新，重新注册智能体...")
                self._register_agents()

            # 路由并处理工单
            result = self.router.route_ticket(ticket_content)
            processing_time = time.time() - start_time

            # 记录监控指标
            agent_used = result.get('agent_used', 'unknown')
            success = result.get('processed', False)
            error_type = result.get('error', None)

            self.monitor.record_agent_request(
                agent_used, success, processing_time, error_type
            )

            # 输出处理结果
            print(f"📊 分析结果:")
            print(f"   - 最佳智能体: {result['analysis']['best_agent']}")
            print(f"   - 置信度: {result['analysis']['confidence']:.2f}")
            print(f"   - 候选智能体: {len(result['analysis']['candidates'])}")
            print(f"   - 处理状态: {'✅ 已处理' if result['processed'] else '❌ 未处理'}")
            print(f"   - 处理结果: {result['result']}")
            print(f"   - 处理时间: {processing_time:.2f}秒")

            if result['error']:
                print(f"   - 错误信息: {result['error']}")

            return result

        except Exception as e:
            processing_time = time.time() - start_time
            error_result = {
                'processed': False,
                'result': f"处理工单时发生错误: {str(e)}",
                'error': str(e),
                'analysis': {
                    'best_agent': 'unknown',
                    'confidence': 0.0,
                    'candidates': []
                },
                'agent_used': 'unknown'
            }

            # 记录错误到监控
            self.monitor.record_agent_request('unknown', False, processing_time, str(e))

            print(f"❌ 处理工单时发生错误: {e}")
            return error_result

    def process_ticket_with_chain(self, chain_name: str, ticket_content: str) -> Dict[str, Any]:
        """
        使用指定处理链处理工单

        Args:
            chain_name: 处理链名称
            ticket_content: 工单内容

        Returns:
            处理结果
        """
        print(f"🔗 使用处理链 '{chain_name}' 处理工单...")

        import time
        start_time = time.time()

        try:
            # 检查配置是否需要重新加载
            if self.config_manager.check_reload():
                print("🔄 检测到配置文件更新，重新注册智能体...")
                self._register_agents()

            # 使用处理链处理工单
            result = self.chain_processor.process_chain(chain_name, ticket_content)
            processing_time = time.time() - start_time

            # 记录监控指标
            self.monitor.record_agent_request(
                f"chain_{chain_name}", result["success"], processing_time, None
            )

            # 输出处理结果
            print(f"📊 处理链结果:")
            print(f"   - 处理链: {chain_name}")
            print(f"   - 整体成功: {'✅' if result['success'] else '❌'}")
            print(f"   - 处理时间: {processing_time:.2f}秒")
            print(f"   - 处理智能体: {result['processed_agents']}/{result['total_agents']}")
            print(f"   - 最终结果: {result['result']}")

            # 显示详细的链式处理结果
            print(f"\n🔗 详细处理过程:")
            for chain_result in result['chain_results']:
                status_icon = "✅" if chain_result["success"] else "❌"
                processed_icon = "🔄" if chain_result["processed"] else "⏭️"
                print(f"   {status_icon}{processed_icon} {chain_result['agent']}: {chain_result['result'][:60]}...")

            return result

        except Exception as e:
            processing_time = time.time() - start_time
            self.monitor.record_agent_request(
                f"chain_{chain_name}", False, processing_time, str(e)
            )
            print(f"❌ 处理链执行失败: {e}")
            return {
                "success": False,
                "result": f"处理链执行失败: {e}",
                "chain_name": chain_name,
                "chain_results": [],
                "total_agents": 0,
                "processed_agents": 0,
                "successful_agents": 0
            }

    def show_agent_status(self):
        """显示智能体系统状态"""
        status = self.router.get_agent_status()
        print(f"\n🤖 智能体系统状态:")
        print(f"   总智能体数: {status['total_agents']}")
        print(f"   启用智能体: {status['enabled_agents']}")
        print(f"   禁用智能体: {status['disabled_agents']}")

        print(f"\n📋 智能体列表:")
        for agent in status['agents']:
            status_icon = "✅" if agent['enabled'] else "❌"
            print(f"   {status_icon} {agent['name']} (优先级: {agent['priority']})")
            print(f"      描述: {agent['description']}")

    def show_monitoring_stats(self):
        """显示监控统计信息"""
        system_stats = self.monitor.get_system_stats()
        performance_ranking = self.monitor.get_agent_performance_ranking()
        usage_distribution = self.monitor.get_agent_usage_distribution()

        print(f"\n📊 系统监控统计:")
        print(f"   系统运行时间: {system_stats['system_uptime']}")
        print(f"   总请求数: {system_stats['total_requests']}")
        print(f"   系统成功率: {system_stats['system_success_rate']:.2%}")
        print(f"   平均处理时间: {system_stats['system_avg_processing_time']:.2f}秒")
        print(f"   最近1小时请求: {system_stats['recent_requests_1h']}")

        if performance_ranking:
            print(f"\n🏆 智能体性能排名:")
            for i, agent in enumerate(performance_ranking[:5], 1):
                print(f"   {i}. {agent['agent_name']}")
                print(f"      请求数: {agent['total_requests']}")
                print(f"      成功率: {agent['success_rate']:.2%}")
                print(f"      平均时间: {agent['avg_processing_time']:.2f}秒")

        if usage_distribution:
            print(f"\n📈 智能体使用分布:")
            for agent_name, usage in sorted(usage_distribution.items(), key=lambda x: -x[1])[:5]:
                print(f"   {agent_name}: {usage:.2%}")

    def show_chain_status(self):
        """显示处理链状态"""
        chain_status = self.chain_processor.get_chain_status()
        chains = self.chain_processor.list_chains()

        print(f"\n🔗 处理链系统状态:")
        print(f"   总处理链数: {chain_status['total_chains']}")
        print(f"   链中智能体总数: {chain_status['total_agents_in_chains']}")
        print(f"   平均链长度: {chain_status['average_chain_length']:.1f}")

        print(f"\n📋 处理链列表:")
        for chain in chains:
            print(f"   🔗 {chain['name']} ({chain['length']} 个智能体)")
            print(f"      {' -> '.join(chain['agents'])}")

    def interactive_mode(self):
        """交互式模式"""
        print("🚀 新版工单处理智能体系统已启动")
        print("输入 'quit' 或 'exit' 退出程序")
        print("输入 'status' 查看智能体状态")
        print("输入 'monitor' 查看监控统计")
        print("输入 'chains' 查看处理链状态")
        print("输入 'report' 生成完整监控报告")
        print("输入 'chain <chain_name> <ticket_content>' 使用处理链处理工单")
        print("-" * 50)

        while True:
            user_input = input("\n📝 请输入工单内容或命令: ").strip()

            if user_input.lower() in ['quit', 'exit', '退出']:
                print("👋 再见!")
                break

            if user_input.lower() == 'status':
                self.show_agent_status()
                continue

            if user_input.lower() == 'monitor':
                self.show_monitoring_stats()
                continue

            if user_input.lower() == 'report':
                report = self.monitor.generate_report()
                print("\n📋 完整监控报告:")
                print(f"系统概览: {report['system_overview']}")
                print(f"性能排名: {report['performance_ranking']}")
                print(f"使用分布: {report['usage_distribution']}")
                print(f"最近错误: {len(report['recent_errors'])} 个")
                continue

            if user_input.lower() == 'chains':
                self.show_chain_status()
                continue

            # 处理链命令
            if user_input.lower().startswith('chain '):
                parts = user_input.split(' ', 2)
                if len(parts) >= 3:
                    chain_name = parts[1]
                    ticket_content = parts[2]
                    self.process_ticket_with_chain(chain_name, ticket_content)
                else:
                    print("⚠️  使用格式: chain <chain_name> <ticket_content>")
                continue

            if not user_input:
                print("⚠️  请输入有效的工单内容或命令")
                continue

            self.process_ticket(user_input)


def main():
    """主函数"""
    system = MultiAgentSystem()

    # 显示系统状态
    system.show_agent_status()

    # 检查是否以交互模式运行
    import sys
    if len(sys.argv) > 1:
        # 命令行模式
        ticket_content = " ".join(sys.argv[1:])
        system.process_ticket(ticket_content)
    else:
        # 交互模式
        system.interactive_mode()


if __name__ == "__main__":
    main()