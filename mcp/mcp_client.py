"""
MCP (Model Context Protocol) 客户端
用于与MCP服务器通信，获取工具和资源
"""
import json
import asyncio
import websockets
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class MCPTool(BaseModel):
    """MCP工具定义"""
    name: str
    description: str
    input_schema: Dict[str, Any]


class MCPResource(BaseModel):
    """MCP资源定义"""
    uri: str
    name: str
    description: str
    mime_type: str


class MCPClient:
    """MCP客户端"""

    def __init__(self, server_url: str = "ws://localhost:3000"):
        self.server_url = server_url
        self.connected = False
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}

    async def connect(self):
        """连接到MCP服务器"""
        try:
            self.websocket = await websockets.connect(self.server_url)
            self.connected = True
            print(f"✅ 已连接到MCP服务器: {self.server_url}")

            # 初始化连接，获取工具和资源
            await self._initialize()
            return True
        except Exception as e:
            print(f"❌ 连接MCP服务器失败: {e}")
            return False

    async def _initialize(self):
        """初始化连接，获取工具和资源列表"""
        try:
            # 获取工具列表
            tools_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }
            await self.websocket.send(json.dumps(tools_request))
            tools_response = await self.websocket.recv()
            tools_data = json.loads(tools_response)

            if "result" in tools_data and "tools" in tools_data["result"]:
                for tool_data in tools_data["result"]["tools"]:
                    tool = MCPTool(
                        name=tool_data["name"],
                        description=tool_data.get("description", ""),
                        input_schema=tool_data.get("inputSchema", {})
                    )
                    self.tools[tool.name] = tool

            # 获取资源列表
            resources_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "resources/list",
                "params": {}
            }
            await self.websocket.send(json.dumps(resources_request))
            resources_response = await self.websocket.recv()
            resources_data = json.loads(resources_response)

            if "result" in resources_data and "resources" in resources_data["result"]:
                for resource_data in resources_data["result"]["resources"]:
                    resource = MCPResource(
                        uri=resource_data["uri"],
                        name=resource_data.get("name", ""),
                        description=resource_data.get("description", ""),
                        mime_type=resource_data.get("mimeType", "text/plain")
                    )
                    self.resources[resource.uri] = resource

            print(f"✅ 已加载 {len(self.tools)} 个工具和 {len(self.resources)} 个资源")

        except Exception as e:
            print(f"❌ 初始化MCP客户端失败: {e}")

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP工具"""
        if not self.connected:
            raise RuntimeError("MCP客户端未连接")

        if tool_name not in self.tools:
            raise ValueError(f"工具 '{tool_name}' 不存在")

        try:
            request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }

            await self.websocket.send(json.dumps(request))
            response = await self.websocket.recv()
            response_data = json.loads(response)

            if "error" in response_data:
                raise RuntimeError(f"工具调用失败: {response_data['error']}")

            return response_data.get("result", {})

        except Exception as e:
            raise RuntimeError(f"调用工具 '{tool_name}' 失败: {e}")

    async def read_resource(self, resource_uri: str) -> str:
        """读取MCP资源"""
        if not self.connected:
            raise RuntimeError("MCP客户端未连接")

        if resource_uri not in self.resources:
            raise ValueError(f"资源 '{resource_uri}' 不存在")

        try:
            request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "resources/read",
                "params": {
                    "uri": resource_uri
                }
            }

            await self.websocket.send(json.dumps(request))
            response = await self.websocket.recv()
            response_data = json.loads(response)

            if "error" in response_data:
                raise RuntimeError(f"资源读取失败: {response_data['error']}")

            return response_data.get("result", {}).get("contents", "")

        except Exception as e:
            raise RuntimeError(f"读取资源 '{resource_uri}' 失败: {e}")

    async def disconnect(self):
        """断开与MCP服务器的连接"""
        if self.connected:
            await self.websocket.close()
            self.connected = False
            print("✅ 已断开MCP服务器连接")

    def get_tools_list(self) -> List[Dict[str, Any]]:
        """获取工具列表"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.input_schema.get("properties", {})
            }
            for tool in self.tools.values()
        ]

    def get_resources_list(self) -> List[Dict[str, Any]]:
        """获取资源列表"""
        return [
            {
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "mime_type": resource.mime_type
            }
            for resource in self.resources.values()
        ]