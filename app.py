#!/usr/bin/env python3
"""
Web应用主程序 - 提供前端界面和API接口
"""
import os
import sys
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import MultiAgentSystem

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
CORS(app)

# 初始化智能体系统
agent_system = None

def get_agent_system():
    """获取智能体系统实例"""
    global agent_system
    if agent_system is None:
        agent_system = MultiAgentSystem()
    return agent_system

@app.route('/')
def index():
    """前端主页"""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """获取系统状态"""
    try:
        system = get_agent_system()

        # 获取智能体状态
        agent_status = system.router.get_agent_status()

        # 获取监控统计
        monitor_stats = system.monitor.get_system_stats()

        # 获取处理链状态
        chain_status = system.chain_processor.get_chain_status()

        return jsonify({
            'success': True,
            'data': {
                'agent_status': agent_status,
                'monitor_stats': monitor_stats,
                'chain_status': chain_status
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/process', methods=['POST'])
def api_process():
    """处理任务"""
    try:
        data = request.get_json()
        ticket_content = data.get('ticket_content', '')
        chain_name = data.get('chain_name', None)

        if not ticket_content:
            return jsonify({
                'success': False,
                'error': '任务内容不能为空'
            })

        system = get_agent_system()

        if chain_name:
            # 使用处理链处理
            result = system.process_ticket_with_chain(chain_name, ticket_content)
        else:
            # 使用智能路由处理
            result = system.process_ticket(ticket_content)

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/monitor')
def api_monitor():
    """获取监控数据"""
    try:
        system = get_agent_system()

        # 获取详细监控报告
        report = system.monitor.generate_report()

        return jsonify({
            'success': True,
            'data': report
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/chains')
def api_chains():
    """获取处理链列表"""
    try:
        system = get_agent_system()
        chains = system.chain_processor.list_chains()

        return jsonify({
            'success': True,
            'data': chains
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/agents')
def api_agents():
    """获取智能体列表"""
    try:
        system = get_agent_system()
        agents = system.router.list_available_agents()

        return jsonify({
            'success': True,
            'data': agents
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/agents/<agent_name>/tools')
def api_agent_tools(agent_name):
    """获取智能体工具列表"""
    try:
        system = get_agent_system()
        tools = system.router.get_agent_tools(agent_name)

        return jsonify({
            'success': True,
            'data': tools
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/tools/shared')
def api_shared_tools():
    """获取所有共享工具"""
    try:
        system = get_agent_system()
        shared_tools = system.router.get_all_shared_tools()

        return jsonify({
            'success': True,
            'data': shared_tools
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/tools/share', methods=['POST'])
def api_share_tool():
    """共享工具给其他智能体"""
    try:
        data = request.get_json()
        source_agent = data.get('source_agent')
        target_agent = data.get('target_agent')
        tool_name = data.get('tool_name')

        if not all([source_agent, target_agent, tool_name]):
            return jsonify({
                'success': False,
                'error': '缺少必要参数: source_agent, target_agent, tool_name'
            })

        system = get_agent_system()
        system.router.share_tool_between_agents(source_agent, target_agent, tool_name)

        return jsonify({
            'success': True,
            'message': f'工具 {tool_name} 已从 {source_agent} 共享给 {target_agent}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/tools/execute', methods=['POST'])
def api_execute_tool():
    """执行工具"""
    try:
        data = request.get_json()
        agent_name = data.get('agent_name')
        tool_name = data.get('tool_name')
        parameters = data.get('parameters', {})

        if not all([agent_name, tool_name]):
            return jsonify({
                'success': False,
                'error': '缺少必要参数: agent_name, tool_name'
            })

        system = get_agent_system()
        agent = system.router.get_agent(agent_name)

        if not agent:
            return jsonify({
                'success': False,
                'error': f'智能体 {agent_name} 未找到'
            })

        result = agent.execute_tool(tool_name, **parameters)

        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)