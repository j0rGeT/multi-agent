"""
智能体链式处理器 - 支持多个智能体按顺序处理工单
"""
from typing import Dict, Any, List, Optional
from .agent_base import BaseAgent


class ChainProcessor:
    """智能体链式处理器"""

    def __init__(self):
        self.chains: Dict[str, List[str]] = {}
        self.registered_agents: Dict[str, BaseAgent] = {}

    def register_agent(self, agent: BaseAgent):
        """注册智能体"""
        self.registered_agents[agent.config.name] = agent

    def create_chain(self, chain_name: str, agent_names: List[str]):
        """创建处理链"""
        # 验证所有智能体都存在
        for agent_name in agent_names:
            if agent_name not in self.registered_agents:
                raise ValueError(f"智能体 '{agent_name}' 未注册")

        self.chains[chain_name] = agent_names
        print(f"🔗 创建处理链 '{chain_name}': {' -> '.join(agent_names)}")

    def delete_chain(self, chain_name: str):
        """删除处理链"""
        if chain_name in self.chains:
            del self.chains[chain_name]
            print(f"🗑️  删除处理链 '{chain_name}'")
        else:
            raise ValueError(f"处理链 '{chain_name}' 不存在")

    def update_chain(self, chain_name: str, new_agent_names: List[str]):
        """更新处理链"""
        if chain_name not in self.chains:
            raise ValueError(f"处理链 '{chain_name}' 不存在")

        # 验证所有智能体都存在
        for agent_name in new_agent_names:
            if agent_name not in self.registered_agents:
                raise ValueError(f"智能体 '{agent_name}' 未注册")

        self.chains[chain_name] = new_agent_names
        print(f"🔄 更新处理链 '{chain_name}': {' -> '.join(new_agent_names)}")

    def get_chain(self, chain_name: str) -> Optional[List[str]]:
        """获取处理链"""
        return self.chains.get(chain_name)

    def process_chain(self, chain_name: str, ticket_content: str) -> Dict[str, Any]:
        """
        使用指定处理链处理工单

        Args:
            chain_name: 处理链名称
            ticket_content: 工单内容

        Returns:
            处理结果
        """
        if chain_name not in self.chains:
            return {
                "success": False,
                "result": f"处理链 '{chain_name}' 不存在",
                "chain_results": []
            }

        chain_agents = self.chains[chain_name]
        chain_results = []
        final_result = ""

        print(f"🔗 开始执行处理链 '{chain_name}'...")

        for i, agent_name in enumerate(chain_agents, 1):
            agent = self.registered_agents[agent_name]
            print(f"   {i}/{len(chain_agents)} 执行智能体: {agent_name}")

            try:
                # 检查智能体是否能处理
                if agent.can_handle(ticket_content):
                    result = agent.process(ticket_content)
                    chain_results.append({
                        "agent": agent_name,
                        "success": True,
                        "result": result,
                        "processed": True
                    })
                    final_result = result
                    print(f"     ✅ 处理成功: {result[:50]}...")
                else:
                    chain_results.append({
                        "agent": agent_name,
                        "success": True,
                        "result": "跳过处理（无法处理此工单）",
                        "processed": False
                    })
                    print(f"     ⏭️  跳过处理")

            except Exception as e:
                chain_results.append({
                    "agent": agent_name,
                    "success": False,
                    "result": f"处理失败: {str(e)}",
                    "processed": False,
                    "error": str(e)
                })
                print(f"     ❌ 处理失败: {e}")

        # 判断整体处理结果
        processed_agents = [r for r in chain_results if r["processed"]]
        successful_agents = [r for r in chain_results if r["success"]]

        overall_success = len(successful_agents) == len(chain_results)

        return {
            "success": overall_success,
            "result": final_result,
            "chain_name": chain_name,
            "chain_results": chain_results,
            "total_agents": len(chain_results),
            "processed_agents": len(processed_agents),
            "successful_agents": len(successful_agents)
        }

    def auto_detect_chain(self, ticket_content: str) -> Optional[str]:
        """
        自动检测最适合的处理链

        Args:
            ticket_content: 工单内容

        Returns:
            最适合的处理链名称，如果没有合适的则返回None
        """
        best_chain = None
        best_score = 0.0

        for chain_name, agent_names in self.chains.items():
            chain_score = self._calculate_chain_score(agent_names, ticket_content)
            if chain_score > best_score:
                best_score = chain_score
                best_chain = chain_name

        return best_chain if best_score > 0.5 else None

    def _calculate_chain_score(self, agent_names: List[str], ticket_content: str) -> float:
        """计算处理链的匹配分数"""
        total_score = 0.0
        agent_count = len(agent_names)

        for agent_name in agent_names:
            agent = self.registered_agents[agent_name]
            if hasattr(agent, 'get_confidence'):
                confidence = agent.get_confidence(ticket_content)
            else:
                confidence = 1.0 if agent.can_handle(ticket_content) else 0.0
            total_score += confidence

        return total_score / agent_count if agent_count > 0 else 0.0

    def list_chains(self) -> List[Dict[str, Any]]:
        """列出所有处理链"""
        chains_info = []
        for chain_name, agent_names in self.chains.items():
            chains_info.append({
                "name": chain_name,
                "agents": agent_names,
                "length": len(agent_names)
            })
        return chains_info

    def get_chain_status(self) -> Dict[str, Any]:
        """获取处理链系统状态"""
        chains = self.list_chains()
        total_agents_in_chains = sum(chain["length"] for chain in chains)

        return {
            "total_chains": len(chains),
            "total_agents_in_chains": total_agents_in_chains,
            "average_chain_length": total_agents_in_chains / len(chains) if chains else 0,
            "chains": chains
        }