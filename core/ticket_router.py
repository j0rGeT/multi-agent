"""
新版工单路由智能体 - 支持动态注册的智能体架构
"""
from crewai import Agent
from typing import Dict, Any, List

from .agent_base import AgentRegistry, BaseAgent


class TicketRouter:
    """工单路由智能体"""

    def __init__(self):
        self.registry = AgentRegistry()
        self.router_agent = self._create_router_agent()

    def _create_router_agent(self) -> Agent:
        """创建路由智能体"""
        return Agent(
            role="工单路由专家",
            goal="准确分析工单内容，识别请求类型，并路由到最适合的处理智能体",
            backstory="""
            你是一位专业的工单路由专家，能够准确理解工单内容并识别用户的具体需求。
            你擅长分析工单中的关键词和上下文，能够智能地选择最适合的处理智能体。
            你了解系统中所有可用的智能体及其专长，能够做出最佳的路由决策。
            """,
            verbose=True
        )

    def register_agent(self, agent: BaseAgent):
        """注册智能体"""
        self.registry.register(agent)

    def unregister_agent(self, agent_name: str):
        """注销智能体"""
        self.registry.unregister(agent_name)

    def analyze_ticket(self, ticket_content: str) -> Dict[str, Any]:
        """
        分析工单并找到最适合的智能体

        Args:
            ticket_content: 工单内容

        Returns:
            包含分析结果的字典
        """
        best_agent = self.registry.find_best_agent(ticket_content)

        analysis_result = {
            "best_agent": None,
            "confidence": 0.0,
            "candidates": [],
            "agent_metadata": None
        }

        if best_agent:
            analysis_result["best_agent"] = best_agent.config.name
            analysis_result["confidence"] = best_agent.get_confidence(ticket_content)
            analysis_result["agent_metadata"] = best_agent.get_metadata()

        # 收集所有候选智能体信息
        for agent in self.registry.get_enabled_agents():
            confidence = agent.get_confidence(ticket_content)
            if confidence > 0.0:
                analysis_result["candidates"].append({
                    "agent": agent.config.name,
                    "confidence": confidence,
                    "priority": agent.config.priority
                })

        # 按置信度排序候选列表
        analysis_result["candidates"].sort(key=lambda x: -x["confidence"])

        return analysis_result

    def route_ticket(self, ticket_content: str) -> Dict[str, Any]:
        """
        路由工单到最适合的处理智能体

        Args:
            ticket_content: 工单内容

        Returns:
            包含路由结果和处理结果的字典
        """
        # 分析工单
        analysis = self.analyze_ticket(ticket_content)

        result = {
            "analysis": analysis,
            "processed": False,
            "result": "",
            "agent_used": "",
            "error": None
        }

        if not analysis["best_agent"]:
            result["result"] = "未找到合适的智能体处理此工单，需要人工处理"
            return result

        # 获取最佳智能体
        best_agent = self.registry.get_agent(analysis["best_agent"])
        if not best_agent:
            result["error"] = f"智能体 '{analysis['best_agent']}' 未找到"
            result["result"] = "路由失败"
            return result

        try:
            # 使用最佳智能体处理工单
            result["agent_used"] = analysis["best_agent"]
            result["result"] = best_agent.process(ticket_content)
            result["processed"] = True
        except Exception as e:
            result["error"] = str(e)
            result["result"] = f"智能体处理失败: {str(e)}"

        return result

    def list_available_agents(self) -> List[Dict[str, Any]]:
        """列出所有可用的智能体"""
        return self.registry.list_agents()

    def get_agent_status(self) -> Dict[str, Any]:
        """获取智能体系统状态"""
        agents = self.list_available_agents()
        enabled_agents = [agent for agent in agents if agent["enabled"]]
        disabled_agents = [agent for agent in agents if not agent["enabled"]]

        return {
            "total_agents": len(agents),
            "enabled_agents": len(enabled_agents),
            "disabled_agents": len(disabled_agents),
            "agents": agents
        }

    def get_agent(self, agent_name: str):
        """获取指定智能体"""
        return self.registry.get_agent(agent_name)

    def get_agent_tools(self, agent_name: str) -> List[Dict[str, Any]]:
        """获取智能体的工具列表"""
        agent = self.registry.get_agent(agent_name)
        if not agent:
            return []
        return agent.get_tool_info()

    def get_all_shared_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """获取所有共享工具"""
        return self.registry.get_all_shared_tools()

    def share_tool_between_agents(self, source_agent: str, target_agent: str, tool_name: str):
        """在智能体之间共享工具"""
        source = self.registry.get_agent(source_agent)
        target = self.registry.get_agent(target_agent)

        if not source:
            raise ValueError(f"源智能体 '{source_agent}' 未找到")
        if not target:
            raise ValueError(f"目标智能体 '{target_agent}' 未找到")

        source.share_tool(tool_name, target)