"""
智能体基类 - 为所有智能体提供统一的接口和注册机制
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel
import inspect


class AgentConfig(BaseModel):
    """智能体配置模型"""
    name: str
    description: str
    priority: int = 10  # 优先级，数字越小优先级越高
    enabled: bool = True
    class_path: str = ""
    init_params: Dict[str, Any] = {}


class ToolInfo(BaseModel):
    """工具信息模型"""
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any]


class BaseAgent(ABC):
    """智能体基类"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.agent = None
        self._tools: Dict[str, ToolInfo] = {}  # 工具注册表
        self._shared_tools: Dict[str, ToolInfo] = {}  # 共享工具注册表

    @abstractmethod
    def initialize(self):
        """初始化智能体"""
        pass

    @abstractmethod
    def can_handle(self, ticket_content: str) -> bool:
        """
        判断是否能处理该工单

        Args:
            ticket_content: 工单内容

        Returns:
            是否能处理
        """
        pass

    @abstractmethod
    def extract_info(self, ticket_content: str) -> Dict[str, Any]:
        """
        从工单内容中提取相关信息

        Args:
            ticket_content: 工单内容

        Returns:
            包含提取信息的字典
        """
        pass

    @abstractmethod
    def process(self, ticket_content: str) -> str:
        """
        处理工单

        Args:
            ticket_content: 工单内容

        Returns:
            处理结果
        """
        pass

    def get_confidence(self, ticket_content: str) -> float:
        """
        获取处理该工单的置信度

        Args:
            ticket_content: 工单内容

        Returns:
            置信度 (0.0 - 1.0)
        """
        if not self.can_handle(ticket_content):
            return 0.0

        # 默认实现：基于关键词匹配计算置信度
        info = self.extract_info(ticket_content)
        if "has_request" in info and info["has_request"]:
            return 0.8
        else:
            return 0.3

    def get_metadata(self) -> Dict[str, Any]:
        """获取智能体元数据"""
        return {
            "name": self.config.name,
            "description": self.config.description,
            "priority": self.config.priority,
            "enabled": self.config.enabled
        }

    def register_tool(self, name: str, description: str, function: Callable,
                     parameters: Dict[str, Any] = None, shared: bool = False):
        """
        注册工具

        Args:
            name: 工具名称
            description: 工具描述
            function: 工具函数
            parameters: 工具参数信息
            shared: 是否共享给其他智能体
        """
        if parameters is None:
            parameters = {}

        tool_info = ToolInfo(
            name=name,
            description=description,
            function=function,
            parameters=parameters
        )

        if shared:
            self._shared_tools[name] = tool_info
        else:
            self._tools[name] = tool_info

    def get_tools(self, include_shared: bool = True) -> Dict[str, ToolInfo]:
        """获取智能体的工具列表"""
        tools = self._tools.copy()
        if include_shared:
            tools.update(self._shared_tools)
        return tools

    def get_shared_tools(self) -> Dict[str, ToolInfo]:
        """获取共享工具列表"""
        return self._shared_tools.copy()

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """执行工具"""
        if tool_name in self._tools:
            tool = self._tools[tool_name]
        elif tool_name in self._shared_tools:
            tool = self._shared_tools[tool_name]
        else:
            raise ValueError(f"工具 '{tool_name}' 未找到")

        return tool.function(**kwargs)

    def share_tool(self, tool_name: str, target_agent: 'BaseAgent'):
        """将工具共享给其他智能体"""
        if tool_name not in self._shared_tools:
            raise ValueError(f"工具 '{tool_name}' 未注册为共享工具")

        target_agent._shared_tools[tool_name] = self._shared_tools[tool_name]

    def get_tool_info(self) -> List[Dict[str, Any]]:
        """获取工具信息列表"""
        tools_info = []

        for name, tool in self._tools.items():
            tools_info.append({
                "name": name,
                "description": tool.description,
                "parameters": tool.parameters,
                "shared": False
            })

        for name, tool in self._shared_tools.items():
            tools_info.append({
                "name": name,
                "description": tool.description,
                "parameters": tool.parameters,
                "shared": True
            })

        return tools_info


class AgentRegistry:
    """智能体注册表"""

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent):
        """注册智能体"""
        agent_name = agent.config.name
        if agent_name in self._agents:
            raise ValueError(f"智能体 '{agent_name}' 已注册")

        self._agents[agent_name] = agent
        print(f"✅ 注册智能体: {agent_name}")

    def unregister(self, agent_name: str):
        """注销智能体"""
        if agent_name in self._agents:
            del self._agents[agent_name]
            print(f"❌ 注销智能体: {agent_name}")

    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """获取指定智能体"""
        return self._agents.get(agent_name)

    def get_all_agents(self) -> List[BaseAgent]:
        """获取所有智能体"""
        return list(self._agents.values())

    def get_enabled_agents(self) -> List[BaseAgent]:
        """获取所有启用的智能体"""
        return [agent for agent in self._agents.values() if agent.config.enabled]

    def find_best_agent(self, ticket_content: str) -> Optional[BaseAgent]:
        """
        找到最适合处理工单的智能体

        Args:
            ticket_content: 工单内容

        Returns:
            最适合的智能体，如果没有则返回None
        """
        candidates = []

        for agent in self.get_enabled_agents():
            confidence = agent.get_confidence(ticket_content)
            if confidence > 0.0:
                candidates.append({
                    "agent": agent,
                    "confidence": confidence,
                    "priority": agent.config.priority
                })

        if not candidates:
            return None

        # 按置信度和优先级排序
        candidates.sort(key=lambda x: (-x["confidence"], x["priority"]))
        return candidates[0]["agent"]

    def list_agents(self) -> List[Dict[str, Any]]:
        """列出所有智能体信息"""
        return [agent.get_metadata() for agent in self.get_all_agents()]

    def get_agent_tools(self, agent_name: str) -> List[Dict[str, Any]]:
        """获取指定智能体的工具信息"""
        agent = self.get_agent(agent_name)
        if agent:
            return agent.get_tool_info()
        return []

    def share_tool_between_agents(self, source_agent: str, target_agent: str, tool_name: str):
        """在智能体之间共享工具"""
        source = self.get_agent(source_agent)
        target = self.get_agent(target_agent)

        if not source:
            raise ValueError(f"源智能体 '{source_agent}' 未找到")
        if not target:
            raise ValueError(f"目标智能体 '{target_agent}' 未找到")

        source.share_tool(tool_name, target)

    def get_all_shared_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """获取所有共享工具"""
        shared_tools = {}
        for agent in self.get_all_agents():
            tools = agent.get_shared_tools()
            if tools:
                shared_tools[agent.config.name] = [
                    {
                        "name": name,
                        "description": tool.description,
                        "parameters": tool.parameters
                    }
                    for name, tool in tools.items()
                ]
        return shared_tools