# 通用多智能体系统

基于 CrewAI 的通用多智能体系统，支持动态注册、配置管理和链式处理，可处理各种任务类型。

## 🚀 特性

### 核心功能
- 🔍 **智能路由**: 自动分析工单内容，选择最适合的处理智能体
- 🤖 **动态注册**: 支持运行时添加和移除智能体
- ⚡ **优先级系统**: 基于置信度和优先级的智能体选择
- 🛡️ **错误处理**: 完善的异常处理和错误恢复机制

### 高级特性
- ⚙️ **配置管理**: YAML 配置文件支持热重载
- 📊 **监控统计**: 实时性能监控和统计报告
- 🔗 **链式处理**: 多个智能体按顺序处理复杂工单
- 🔧 **扩展性**: 插件化架构，易于添加新智能体

## 📁 项目结构

```
├── agents/                # 智能体模块
│   ├── quota_agent.py     # 配额管理智能体
│   ├── project_agent.py   # 项目管理智能体
│   └── business_logic_agent.py # 业务逻辑检查智能体
├── core/                  # 核心模块
│   ├── agent_base.py      # 智能体基类和注册器
│   ├── ticket_router.py   # 工单路由智能体
│   ├── chain_processor.py # 链式处理器
│   ├── config.py          # 配置管理器
│   └── agent_monitor.py   # 监控系统
├── api/                   # API模块
│   └── api_client.py      # API客户端
├── web/                   # 前端界面
│   ├── templates/         # HTML模板
│   └── static/            # 静态资源
├── tests/                 # 测试代码
│   └── test_system.py     # 系统测试
├── main.py                # 命令行主程序
├── app.py                 # Web应用主程序
├── run_web.py             # Web服务器启动脚本
└── config.yaml            # 配置文件
```

## 🛠️ 快速开始

### 1. 安装依赖

```bash
pip install crewai langchain pydantic pyyaml python-dotenv
```

### 2. 配置环境

创建 `.env` 文件：
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 运行系统

```bash
# 命令行交互模式
python main.py

# 命令行模式
python main.py "用户 user123 需要增加 CPU 配额 10 个"

# Web界面模式
python run_web.py
# 然后访问 http://localhost:5000

# 运行测试
python tests/test_system.py
```

## 🎯 使用说明

### 交互模式命令

- `status` - 查看智能体状态
- `monitor` - 查看监控统计
- `chains` - 查看处理链状态
- `report` - 生成完整监控报告
- `chain <chain_name> <ticket_content>` - 使用处理链处理工单
- `quit` / `exit` - 退出程序

### 处理链示例

系统预定义了以下处理链：

- `full_processing`: 业务逻辑检查 → 配额管理 → 项目管理
- `quota_only`: 业务逻辑检查 → 配额管理
- `project_only`: 业务逻辑检查 → 项目管理

使用处理链：
```bash
chain quota_only "用户 user123 需要增加 CPU 配额 10 个"
```

## 🔧 配置说明

### 智能体配置

在 `config.yaml` 中配置智能体：

```yaml
system:
  openai_api_key: "your_openai_api_key_here"
  quota_api_url: "https://api.example.com/quota"
  project_api_url: "https://api.example.com/projects"
  ticket_api_url: "https://api.example.com/tickets"
  log_level: "INFO"
  max_retries: 3
  timeout: 30

agents:
  - name: "business_logic_agent"
    description: "业务逻辑检查智能体"
    priority: 5
    enabled: true
    class_path: "business_logic_agent.BusinessLogicAgent"
    init_params: {}

  - name: "quota_agent"
    description: "配额管理智能体"
    priority: 10
    enabled: true
    class_path: "quota_agent.QuotaAgent"
    init_params: {}
```

### 添加新智能体

1. 创建新智能体类，继承 `BaseAgent`
2. 实现必要的方法：`can_handle`, `extract_info`, `process`
3. 在配置文件中添加智能体配置
4. 系统会自动加载并注册新智能体

## 📊 监控功能

系统提供以下监控指标：

- **系统概览**: 运行时间、总请求数、成功率、平均处理时间
- **性能排名**: 智能体性能排序（成功率、处理时间）
- **使用分布**: 各智能体使用频率统计
- **错误统计**: 最近错误和错误类型分布

## 🧪 测试

运行测试脚本验证系统功能：

```bash
python test_system.py
```

## 📈 性能优化

- 智能体使用惰性初始化
- 配置支持热重载，减少重启
- 监控系统实时跟踪性能指标
- 链式处理优化复杂工单处理流程

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License