"""
新版项目管理智能体 - 继承基类版本
"""
from crewai import Agent
from langchain.tools import Tool
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import re

from api.api_client import APIClient
from core.agent_base import BaseAgent, AgentConfig


class ProjectRequest(BaseModel):
    """项目请求模型"""
    project_name: str = Field(description="项目名称")
    description: str = Field(description="项目描述")
    owner_id: str = Field(description="项目所有者ID")
    settings: Optional[Dict[str, Any]] = Field(default=None, description="项目设置")


class ProjectAgent(BaseAgent):
    """项目管理智能体"""

    def __init__(self, config: AgentConfig = None):
        if config is None:
            config = AgentConfig(
                name="project_agent",
                description="处理工单中的项目创建请求，包括项目信息提取和项目创建",
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
            name="create_project",
            description="创建新项目",
            function=self._create_project,
            parameters={
                "project_name": "项目名称",
                "description": "项目描述",
                "owner_id": "项目所有者ID",
                "settings": "项目设置 (可选)"
            },
            shared=True
        )

    def _create_project(self, project_name: str, description: str, owner_id: str,
                       settings: Optional[Dict[str, Any]] = None) -> str:
        """创建项目工具函数"""
        result = self.api_client.create_project(project_name, description, owner_id, settings)
        if result["success"]:
            return f"✅ {result['message']}"
        else:
            return f"❌ {result['message']}"

    def can_handle(self, ticket_content: str) -> bool:
        """判断是否能处理该工单"""
        project_keywords = ["创建项目", "新建项目", "建立项目", "project", "项目申请"]
        return any(keyword in ticket_content.lower() for keyword in project_keywords)

    def extract_info(self, ticket_content: str) -> Dict[str, Any]:
        """从工单内容中提取项目信息"""
        project_info = {
            "project_name": None,
            "description": None,
            "owner_id": None,
            "settings": {},
            "has_request": False
        }

        # 提取项目名称
        name_patterns = [
            r"项目名称[：:]\s*([^\n。！？!?]+)",
            r"项目名[：:]\s*([^\n。！？!?]+)",
            r"project[：:]\s*([^\n。！？!?]+)",
            r"创建项目[：:]\s*([^\n。！？!?]+)",
            r"新建项目[：:]\s*([^\n。！？!?]+)"
        ]
        for pattern in name_patterns:
            match = re.search(pattern, ticket_content, re.IGNORECASE)
            if match:
                project_info["project_name"] = match.group(1).strip()
                break

        # 如果没找到明确的项目名称，尝试从上下文推断
        if not project_info["project_name"]:
            project_sentences = re.findall(r"[^。！？!?]*项目[^。！？!?]*", ticket_content)
            for sentence in project_sentences:
                name_match = re.search(r"项目[：:]?\s*([^，。！？!?\s]+)", sentence)
                if name_match:
                    project_info["project_name"] = name_match.group(1).strip()
                    break

        # 提取项目描述
        desc_patterns = [
            r"项目描述[：:]\s*([^\n。！？!?]+)",
            r"描述[：:]\s*([^\n。！？!?]+)",
            r"用途[：:]\s*([^\n。！？!?]+)",
            r"目的[：:]\s*([^\n。！？!?]+)"
        ]
        for pattern in desc_patterns:
            match = re.search(pattern, ticket_content, re.IGNORECASE)
            if match:
                project_info["description"] = match.group(1).strip()
                break

        # 如果没找到明确的描述，使用工单内容作为描述
        if not project_info["description"]:
            project_info["description"] = ticket_content[:200].strip()

        # 提取所有者ID
        owner_patterns = [
            r"用户[：:]\s*([a-zA-Z0-9_-]+)",
            r"user[：:]\s*([a-zA-Z0-9_-]+)",
            r"所有者[：:]\s*([a-zA-Z0-9_-]+)",
            r"owner[：:]\s*([a-zA-Z0-9_-]+)"
        ]
        for pattern in owner_patterns:
            match = re.search(pattern, ticket_content, re.IGNORECASE)
            if match:
                project_info["owner_id"] = match.group(1)
                break

        # 提取项目设置
        settings_patterns = [
            r"设置[：:]\s*([^\n。！？!?]+)",
            r"settings[：:]\s*([^\n。！？!?]+)",
            r"配置[：:]\s*([^\n。！？!?]+)"
        ]
        for pattern in settings_patterns:
            match = re.search(pattern, ticket_content, re.IGNORECASE)
            if match:
                settings_text = match.group(1)
                if "开发" in settings_text or "development" in settings_text.lower():
                    project_info["settings"]["environment"] = "development"
                if "生产" in settings_text or "production" in settings_text.lower():
                    project_info["settings"]["environment"] = "production"
                break

        # 判断是否有项目创建请求
        project_keywords = ["创建项目", "新建项目", "建立项目", "project", "项目申请"]
        project_info["has_request"] = any(
            keyword in ticket_content.lower() for keyword in project_keywords
        ) and project_info["project_name"] and project_info["owner_id"]

        return project_info

    def process(self, ticket_content: str) -> str:
        """处理工单中的项目创建请求"""
        project_info = self.extract_info(ticket_content)

        if not project_info["has_request"]:
            return "未检测到有效的项目创建请求"

        # 调用API创建项目
        result = self._create_project(
            project_info["project_name"],
            project_info["description"],
            project_info["owner_id"],
            project_info["settings"]
        )

        return result