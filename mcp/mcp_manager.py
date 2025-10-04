"""
MCP管理器 - 管理多个MCP客户端连接
"""
import asyncio
from typing import Dict, Any, List, Optional
from .mcp_client import MCPClient


class MCPManager:
    """MCP管理器"""

    def __init__(self):
        self.clients: Dict[str, MCPClient] = {}
        self.connected = False

    async def add_client(self, name: str, server_url: str) -> bool:
        """添加MCP客户端"""
        if name in self.clients:
            print(f"⚠️  MCP客户端 '{name}' 已存在")
            return False

        client = MCPClient(server_url)
        success = await client.connect()

        if success:
            self.clients[name] = client
            print(f"✅ 已添加MCP客户端: {name} -> {server_url}")
            return True
        else:
            print(f"❌ 添加MCP客户端失败: {name}")
            return False

    async def remove_client(self, name: str):
        """移除MCP客户端"""
        if name in self.clients:
            await self.clients[name].disconnect()
            del self.clients[name]
            print(f"✅ 已移除MCP客户端: {name}")
        else:
            print(f"⚠️  MCP客户端 '{name}' 不存在")

    async def call_tool(self, client_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """通过指定客户端调用工具"""
        if client_name not in self.clients:
            raise ValueError(f"MCP客户端 '{client_name}' 不存在")

        client = self.clients[client_name]
        return await client.call_tool(tool_name, arguments)

    async def read_resource(self, client_name: str, resource_uri: str) -> str:
        """通过指定客户端读取资源"""
        if client_name not in self.clients:
            raise ValueError(f"MCP客户端 '{client_name}' 不存在")

        client = self.clients[client_name]
        return await client.read_resource(resource_uri)

    def get_client_status(self, client_name: str) -> Dict[str, Any]:
        """获取客户端状态"""
        if client_name not in self.clients:
            return {"connected": False, "error": "客户端不存在"}

        client = self.clients[client_name]
        return {
            "connected": client.connected,
            "tools_count": len(client.tools),
            "resources_count": len(client.resources),
            "server_url": client.server_url
        }

    def get_all_clients_status(self) -> Dict[str, Dict[str, Any]]:
        """获取所有客户端状态"""
        status = {}
        for name, client in self.clients.items():
            status[name] = {
                "connected": client.connected,
                "tools_count": len(client.tools),
                "resources_count": len(client.resources),
                "server_url": client.server_url
            }
        return status

    def get_client_tools(self, client_name: str) -> List[Dict[str, Any]]:
        """获取客户端工具列表"""
        if client_name not in self.clients:
            return []

        client = self.clients[client_name]
        return client.get_tools_list()

    def get_client_resources(self, client_name: str) -> List[Dict[str, Any]]:
        """获取客户端资源列表"""
        if client_name not in self.clients:
            return []

        client = self.clients[client_name]
        return client.get_resources_list()

    def get_all_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """获取所有客户端的工具"""
        all_tools = {}
        for name, client in self.clients.items():
            all_tools[name] = client.get_tools_list()
        return all_tools

    def get_all_resources(self) -> Dict[str, List[Dict[str, Any]]]:
        """获取所有客户端的资源"""
        all_resources = {}
        for name, client in self.clients.items():
            all_resources[name] = client.get_resources_list()
        return all_resources

    async def disconnect_all(self):
        """断开所有客户端连接"""
        for name, client in self.clients.items():
            await client.disconnect()
        self.clients.clear()
        print("✅ 已断开所有MCP客户端连接")

    def list_clients(self) -> List[str]:
        """列出所有客户端名称"""
        return list(self.clients.keys())