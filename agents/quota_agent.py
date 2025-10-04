"""
新版配额管理智能体 - 继承基类版本
"""
from crewai import Agent
from langchain.tools import Tool
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import re

from api.api_client import APIClient
from core.agent_base import BaseAgent, AgentConfig


class QuotaRequest(BaseModel):
    """配额请求模型"""
    user_id: str = Field(description="用户ID")
    resource_type: str = Field(description="资源类型 (如: cpu, memory, storage)")
    amount: int = Field(description="配额数量")


class QuotaAgent(BaseAgent):
    """配额管理智能体"""

    def __init__(self, config: AgentConfig = None):
        if config is None:
            config = AgentConfig(
                name="quota_agent",
                description="处理工单中的配额调整请求，包括配额检查、状态验证和配额调整",
                priority=10
            )
        super().__init__(config)
        self.api_client = APIClient()
        self.initialize()

    def initialize(self):
        """初始化智能体"""
        # 简化初始化，不使用CrewAI Agent
        self.agent = None

        # 注册工具
        self.register_tool(
            name="increase_quota",
            description="增加用户配额",
            function=self._increase_quota,
            parameters={
                "user_id": "用户ID",
                "resource_type": "资源类型 (cpu, memory, storage)",
                "amount": "配额数量"
            },
            shared=True
        )

        self.register_tool(
            name="get_user_quota",
            description="获取用户配额信息",
            function=self._get_user_quota,
            parameters={
                "user_id": "用户ID"
            },
            shared=True
        )

        self.register_tool(
            name="get_user_quota_usage",
            description="获取用户配额使用情况",
            function=self._get_user_quota_usage,
            parameters={
                "user_id": "用户ID",
                "resource_type": "资源类型"
            },
            shared=True
        )

    def _increase_quota(self, user_id: str, resource_type: str, amount: int) -> str:
        """增加配额工具函数"""
        result = self.api_client.increase_quota(user_id, resource_type, amount)
        if result["success"]:
            return f"✅ {result['message']}"
        else:
            return f"❌ {result['message']}"

    def _get_user_quota(self, user_id: str) -> str:
        """获取用户配额工具函数"""
        result = self.api_client.get_user_quota(user_id)
        if result["success"]:
            quota_info = result["data"]
            return f"用户 {user_id} 的当前配额信息: {quota_info}"
        else:
            return f"❌ {result['message']}"

    def _get_ticket_status(self, ticket_id: str) -> str:
        """获取工单状态工具函数"""
        result = self.api_client.get_ticket_status(ticket_id)
        if result["success"]:
            status_info = result["data"]
            return f"工单 {ticket_id} 的当前状态: {status_info}"
        else:
            return f"❌ {result['message']}"

    def _update_ticket_status(self, ticket_id: str, status: str, notes: str = "") -> str:
        """更新工单状态工具函数"""
        result = self.api_client.update_ticket_status(ticket_id, status, notes)
        if result["success"]:
            return f"✅ {result['message']}"
        else:
            return f"❌ {result['message']}"

    def _get_user_quota_usage(self, user_id: str, resource_type: str) -> str:
        """获取用户配额使用情况工具函数"""
        result = self.api_client.get_user_quota_usage(user_id, resource_type)
        if result["success"]:
            usage_info = result["data"]
            return f"用户 {user_id} 的 {resource_type} 使用情况: {usage_info}"
        else:
            return f"❌ {result['message']}"

    def can_handle(self, ticket_content: str) -> bool:
        """判断是否能处理该工单"""
        quota_keywords = ["配额", "quota", "增加", "提升", "申请", "需要更多"]
        return any(keyword in ticket_content.lower() for keyword in quota_keywords)

    def extract_info(self, ticket_content: str) -> Dict[str, Any]:
        """从工单内容中提取配额信息"""
        quota_info = {
            "ticket_id": None,
            "user_id": None,
            "resource_type": None,
            "amount": None,
            "has_request": False
        }

        # 提取工单ID
        ticket_patterns = [
            r"工单[：:]\s*([a-zA-Z0-9_-]+)",
            r"ticket[：:]\s*([a-zA-Z0-9_-]+)",
            r"工单ID[：:]\s*([a-zA-Z0-9_-]+)"
        ]
        for pattern in ticket_patterns:
            match = re.search(pattern, ticket_content, re.IGNORECASE)
            if match:
                quota_info["ticket_id"] = match.group(1)
                break

        # 提取用户ID
        user_patterns = [
            r"用户[：:]\s*([a-zA-Z0-9_-]+)",
            r"user[：:]\s*([a-zA-Z0-9_-]+)",
            r"用户ID[：:]\s*([a-zA-Z0-9_-]+)"
        ]
        for pattern in user_patterns:
            match = re.search(pattern, ticket_content, re.IGNORECASE)
            if match:
                quota_info["user_id"] = match.group(1)
                break

        # 提取资源类型
        resource_keywords = {
            "cpu": ["cpu", "处理器", "计算资源"],
            "memory": ["内存", "memory", "ram"],
            "storage": ["存储", "storage", "硬盘", "磁盘"]
        }

        for resource_type, keywords in resource_keywords.items():
            for keyword in keywords:
                if keyword.lower() in ticket_content.lower():
                    quota_info["resource_type"] = resource_type
                    break
            if quota_info["resource_type"]:
                break

        # 提取数量
        amount_patterns = [
            r"增加\s*(\d+)\s*(个|GB|MB|TB|核|vCPU)",
            r"提升\s*(\d+)\s*(个|GB|MB|TB|核|vCPU)",
            r"需要\s*(\d+)\s*(个|GB|MB|TB|核|vCPU)",
            r"申请\s*(\d+)\s*(个|GB|MB|TB|核|vCPU)"
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, ticket_content)
            if match:
                quota_info["amount"] = int(match.group(1))
                break

        # 判断是否有配额请求
        quota_keywords = ["配额", "quota", "增加", "提升", "申请", "需要更多"]
        quota_info["has_request"] = any(
            keyword in ticket_content.lower() for keyword in quota_keywords
        ) and quota_info["user_id"] and quota_info["resource_type"] and quota_info["amount"]

        return quota_info

    def check_ticket_status(self, ticket_id: str) -> bool:
        """检查工单状态，只处理未执行的工单"""
        if not ticket_id:
            return False

        result = self.api_client.get_ticket_status(ticket_id)
        if not result["success"]:
            return False

        status_info = result["data"]
        current_status = status_info.get("status", "").lower()

        executable_statuses = ["pending", "new", "open", "待处理", "新建"]
        return current_status in executable_statuses

    def check_quota_needed(self, user_id: str, resource_type: str, requested_amount: int) -> bool:
        """检查是否需要增加配额"""
        usage_result = self.api_client.get_user_quota_usage(user_id, resource_type)
        if not usage_result["success"]:
            return True

        usage_info = usage_result["data"]
        current_usage = usage_info.get("current_usage", 0)
        total_quota = usage_info.get("total_quota", 0)

        remaining_quota = total_quota - current_usage
        return remaining_quota < requested_amount

    def process(self, ticket_content: str) -> str:
        """处理工单中的配额请求"""
        quota_info = self.extract_info(ticket_content)

        if not quota_info["has_request"]:
            return "未检测到有效的配额调整请求"

        # 检查工单状态
        if quota_info["ticket_id"]:
            if not self.check_ticket_status(quota_info["ticket_id"]):
                return f"工单 {quota_info['ticket_id']} 已处理或无法执行，跳过配额调整"

        # 检查是否需要增加配额
        if not self.check_quota_needed(
            quota_info["user_id"],
            quota_info["resource_type"],
            quota_info["amount"]
        ):
            if quota_info["ticket_id"]:
                self._update_ticket_status(
                    quota_info["ticket_id"],
                    "completed",
                    "配额充足，无需调整"
                )
            return f"用户 {quota_info['user_id']} 的 {quota_info['resource_type']} 配额充足，无需增加"

        # 调用API增加配额
        result = self._increase_quota(
            quota_info["user_id"],
            quota_info["resource_type"],
            quota_info["amount"]
        )

        # 更新工单状态
        if quota_info["ticket_id"]:
            if "✅" in result:
                self._update_ticket_status(
                    quota_info["ticket_id"],
                    "completed",
                    f"成功增加 {quota_info['resource_type']} 配额 {quota_info['amount']} 单位"
                )
            else:
                self._update_ticket_status(
                    quota_info["ticket_id"],
                    "failed",
                    f"配额调整失败: {result}"
                )

        return result