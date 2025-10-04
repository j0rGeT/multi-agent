"""
业务逻辑检查智能体 - 示例扩展智能体
"""
from crewai import Agent
from langchain.tools import Tool
from typing import Dict, Any
import re

from core.agent_base import BaseAgent, AgentConfig
from api.api_client import APIClient


class BusinessLogicAgent(BaseAgent):
    """业务逻辑检查智能体"""

    def __init__(self, config: AgentConfig = None):
        if config is None:
            config = AgentConfig(
                name="business_logic_agent",
                description="检查工单的业务逻辑合理性，包括权限验证、合规性检查等",
                priority=5  # 较高优先级，在配额和项目之前检查
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
            name="check_user_permission",
            description="检查用户权限",
            function=self._check_user_permission,
            parameters={
                "user_id": "用户ID",
                "resource_type": "资源类型"
            },
            shared=True
        )

        self.register_tool(
            name="validate_request_reason",
            description="验证请求合理性",
            function=self._validate_request_reason,
            parameters={
                "ticket_content": "工单内容"
            },
            shared=True
        )

        self.register_tool(
            name="assess_risk_level",
            description="评估风险等级",
            function=self._assess_risk_level,
            parameters={
                "ticket_content": "工单内容"
            },
            shared=True
        )

    def _check_user_permission(self, user_id: str, resource_type: str) -> str:
        """检查用户权限"""
        # 模拟权限检查逻辑
        high_permission_users = ["admin", "manager", "user001"]
        restricted_resources = ["production", "sensitive_data"]

        if user_id in high_permission_users:
            return f"✅ 用户 {user_id} 具有高级权限"
        elif resource_type in restricted_resources:
            return f"❌ 用户 {user_id} 无权访问受限资源 {resource_type}"
        else:
            return f"✅ 用户 {user_id} 具有标准权限"

    def _validate_request_reason(self, ticket_content: str) -> str:
        """验证请求合理性"""
        # 检查请求理由是否充分
        valid_reasons = [
            "业务增长", "项目需求", "性能优化", "容量不足",
            "新功能", "系统升级", "用户增加"
        ]

        found_reasons = []
        for reason in valid_reasons:
            if reason in ticket_content:
                found_reasons.append(reason)

        if found_reasons:
            return f"✅ 请求理由充分: {', '.join(found_reasons)}"
        else:
            return "⚠️ 请求理由不够明确，建议补充详细说明"

    def _assess_risk_level(self, ticket_content: str) -> str:
        """评估风险等级"""
        # 风险评估逻辑
        high_risk_keywords = ["紧急", "立即", "马上", "critical", "urgent"]
        high_resource_keywords = ["大量", "全部", "所有", "大规模", "bulk", "all"]

        risk_score = 0

        for keyword in high_risk_keywords:
            if keyword in ticket_content:
                risk_score += 2

        for keyword in high_resource_keywords:
            if keyword in ticket_content:
                risk_score += 1

        if risk_score >= 3:
            return "🔴 高风险: 请求涉及紧急操作和大规模资源调整"
        elif risk_score >= 1:
            return "🟡 中风险: 建议进行额外审核"
        else:
            return "🟢 低风险: 请求符合常规流程"

    def can_handle(self, ticket_content: str) -> bool:
        """判断是否能处理该工单"""
        # 业务逻辑检查适用于所有工单
        return True

    def extract_info(self, ticket_content: str) -> Dict[str, Any]:
        """从工单内容中提取相关信息"""
        info = {
            "user_id": None,
            "resource_type": None,
            "has_urgent_keywords": False,
            "has_request": True  # 业务逻辑检查总是适用的
        }

        # 提取用户ID
        user_patterns = [
            r"用户[：:]\s*([a-zA-Z0-9_-]+)",
            r"user[：:]\s*([a-zA-Z0-9_-]+)"
        ]
        for pattern in user_patterns:
            match = re.search(pattern, ticket_content, re.IGNORECASE)
            if match:
                info["user_id"] = match.group(1)
                break

        # 提取资源类型
        resource_keywords = ["cpu", "内存", "存储", "项目", "资源"]
        for keyword in resource_keywords:
            if keyword in ticket_content:
                info["resource_type"] = keyword
                break

        # 检查紧急关键词
        urgent_keywords = ["紧急", "立即", "马上", "urgent", "critical"]
        info["has_urgent_keywords"] = any(
            keyword in ticket_content for keyword in urgent_keywords
        )

        return info

    def process(self, ticket_content: str) -> str:
        """处理工单的业务逻辑检查"""
        info = self.extract_info(ticket_content)

        results = []

        # 1. 权限检查
        if info["user_id"] and info["resource_type"]:
            permission_result = self._check_user_permission(
                info["user_id"], info["resource_type"]
            )
            results.append(f"权限检查: {permission_result}")

        # 2. 请求合理性验证
        reason_result = self._validate_request_reason(ticket_content)
        results.append(f"请求合理性: {reason_result}")

        # 3. 风险评估
        risk_result = self._assess_risk_level(ticket_content)
        results.append(f"风险评估: {risk_result}")

        # 4. 综合建议
        has_permission_issue = any("❌" in result for result in results)
        has_high_risk = "🔴" in risk_result
        has_warning = "⚠️" in reason_result or "🟡" in risk_result

        if has_permission_issue or has_high_risk:
            results.append("🚫 建议: 此请求需要人工审核")
        elif has_warning:
            results.append("⚠️ 建议: 建议补充说明后进行审核")
        else:
            results.append("✅ 建议: 业务逻辑检查通过，可继续处理")

        return "\n".join(results)