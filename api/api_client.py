"""
API客户端模块 - 处理配额和项目相关的API调用
"""
import os
import requests
from typing import Dict, Any, Optional


class APIClient:
    """API客户端类"""

    def __init__(self):
        self.quota_api_url = os.getenv('QUOTA_API_URL', 'https://api.example.com/quota')
        self.project_api_url = os.getenv('PROJECT_API_URL', 'https://api.example.com/projects')
        self.ticket_api_url = os.getenv('TICKET_API_URL', 'https://api.example.com/tickets')

    def increase_quota(self, user_id: str, resource_type: str, amount: int) -> Dict[str, Any]:
        """
        增加用户配额

        Args:
            user_id: 用户ID
            resource_type: 资源类型 (如: cpu, memory, storage)
            amount: 增加的数量

        Returns:
            包含操作结果的字典
        """
        payload = {
            "user_id": user_id,
            "resource_type": resource_type,
            "amount": amount
        }

        try:
            response = requests.post(f"{self.quota_api_url}/increase", json=payload)
            response.raise_for_status()
            return {
                "success": True,
                "message": f"成功增加 {resource_type} 配额 {amount} 单位",
                "data": response.json()
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "message": f"配额增加失败: {str(e)}",
                "error": str(e)
            }

    def create_project(self, project_name: str, description: str, owner_id: str,
                      settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        创建新项目

        Args:
            project_name: 项目名称
            description: 项目描述
            owner_id: 项目所有者ID
            settings: 项目设置

        Returns:
            包含操作结果的字典
        """
        payload = {
            "name": project_name,
            "description": description,
            "owner_id": owner_id,
            "settings": settings or {}
        }

        try:
            response = requests.post(f"{self.project_api_url}/create", json=payload)
            response.raise_for_status()
            return {
                "success": True,
                "message": f"项目 '{project_name}' 创建成功",
                "data": response.json()
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "message": f"项目创建失败: {str(e)}",
                "error": str(e)
            }

    def get_user_quota(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户当前配额信息

        Args:
            user_id: 用户ID

        Returns:
            包含配额信息的字典
        """
        try:
            response = requests.get(f"{self.quota_api_url}/{user_id}")
            response.raise_for_status()
            return {
                "success": True,
                "data": response.json()
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "message": f"获取配额信息失败: {str(e)}",
                "error": str(e)
            }

    def get_ticket_status(self, ticket_id: str) -> Dict[str, Any]:
        """
        获取工单状态

        Args:
            ticket_id: 工单ID

        Returns:
            包含工单状态的字典
        """
        try:
            response = requests.get(f"{self.ticket_api_url}/{ticket_id}/status")
            response.raise_for_status()
            return {
                "success": True,
                "data": response.json()
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "message": f"获取工单状态失败: {str(e)}",
                "error": str(e)
            }

    def update_ticket_status(self, ticket_id: str, status: str, notes: str = "") -> Dict[str, Any]:
        """
        更新工单状态

        Args:
            ticket_id: 工单ID
            status: 新状态
            notes: 备注信息

        Returns:
            包含操作结果的字典
        """
        payload = {
            "status": status,
            "notes": notes
        }

        try:
            response = requests.put(f"{self.ticket_api_url}/{ticket_id}/status", json=payload)
            response.raise_for_status()
            return {
                "success": True,
                "message": f"工单状态已更新为: {status}",
                "data": response.json()
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "message": f"更新工单状态失败: {str(e)}",
                "error": str(e)
            }

    def get_user_quota_usage(self, user_id: str, resource_type: str) -> Dict[str, Any]:
        """
        获取用户配额使用情况

        Args:
            user_id: 用户ID
            resource_type: 资源类型

        Returns:
            包含配额使用情况的字典
        """
        try:
            response = requests.get(f"{self.quota_api_url}/{user_id}/usage/{resource_type}")
            response.raise_for_status()
            return {
                "success": True,
                "data": response.json()
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "message": f"获取配额使用情况失败: {str(e)}",
                "error": str(e)
            }