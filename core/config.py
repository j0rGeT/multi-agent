"""
配置文件 - 支持YAML配置和热重载
"""
import os
import yaml
from typing import Dict, Any, List
from pydantic import BaseModel


class AgentConfigModel(BaseModel):
    """智能体配置模型"""
    name: str
    description: str
    priority: int = 10
    enabled: bool = True
    class_path: str
    init_params: Dict[str, Any] = {}


class SystemConfig(BaseModel):
    """系统配置模型"""
    openai_api_key: str
    quota_api_url: str
    project_api_url: str
    ticket_api_url: str
    log_level: str = "INFO"
    max_retries: int = 3
    timeout: int = 30


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.system_config: SystemConfig = None
        self.agent_configs: List[AgentConfigModel] = []
        self.last_modified = 0
        self.load_config()

    def load_config(self):
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            self._create_default_config()

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)

        # 加载系统配置
        self.system_config = SystemConfig(**config_data['system'])

        # 加载智能体配置
        self.agent_configs = [
            AgentConfigModel(**agent_config)
            for agent_config in config_data.get('agents', [])
        ]

        self.last_modified = os.path.getmtime(self.config_path)
        print(f"✅ 配置文件加载完成: {self.config_path}")

    def _create_default_config(self):
        """创建默认配置文件"""
        default_config = {
            'system': {
                'openai_api_key': 'your_openai_api_key_here',
                'quota_api_url': 'https://api.example.com/quota',
                'project_api_url': 'https://api.example.com/projects',
                'ticket_api_url': 'https://api.example.com/tickets',
                'log_level': 'INFO',
                'max_retries': 3,
                'timeout': 30
            },
            'agents': [
                {
                    'name': 'business_logic_agent',
                    'description': '业务逻辑检查智能体',
                    'priority': 5,
                    'enabled': True,
                    'class_path': 'business_logic_agent.BusinessLogicAgent',
                    'init_params': {}
                },
                {
                    'name': 'quota_agent',
                    'description': '配额管理智能体',
                    'priority': 10,
                    'enabled': True,
                    'class_path': 'quota_agent.QuotaAgent',
                    'init_params': {}
                },
                {
                    'name': 'project_agent',
                    'description': '项目管理智能体',
                    'priority': 10,
                    'enabled': True,
                    'class_path': 'project_agent.ProjectAgent',
                    'init_params': {}
                }
            ]
        }

        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)

        print(f"📄 已创建默认配置文件: {self.config_path}")

    def check_reload(self) -> bool:
        """检查是否需要重新加载配置"""
        if not os.path.exists(self.config_path):
            return False

        current_modified = os.path.getmtime(self.config_path)
        if current_modified > self.last_modified:
            self.load_config()
            return True
        return False

    def get_agent_config(self, agent_name: str) -> AgentConfigModel:
        """获取指定智能体的配置"""
        for config in self.agent_configs:
            if config.name == agent_name:
                return config
        raise ValueError(f"智能体 '{agent_name}' 的配置未找到")

    def get_enabled_agents(self) -> List[AgentConfigModel]:
        """获取所有启用的智能体配置"""
        return [config for config in self.agent_configs if config.enabled]

    def update_agent_config(self, agent_name: str, **kwargs):
        """更新智能体配置"""
        for config in self.agent_configs:
            if config.name == agent_name:
                for key, value in kwargs.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
                self._save_config()
                return
        raise ValueError(f"智能体 '{agent_name}' 未找到")

    def _save_config(self):
        """保存配置到文件"""
        config_data = {
            'system': self.system_config.dict(),
            'agents': [config.dict() for config in self.agent_configs]
        }

        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)

        self.last_modified = os.path.getmtime(self.config_path)
        print(f"💾 配置文件已保存: {self.config_path}")