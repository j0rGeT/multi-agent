// 通用多智能体系统前端JavaScript

let currentStatus = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    loadSystemStatus();
    setupEventListeners();

    // 每30秒自动刷新状态
    setInterval(loadSystemStatus, 30000);
});

// 设置事件监听器
function setupEventListeners() {
    // 任务处理表单
    document.getElementById('process-form').addEventListener('submit', function(e) {
        e.preventDefault();
        processTask();
    });
}

// 加载系统状态
async function loadSystemStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        if (data.success) {
            currentStatus = data.data;
            updateSystemOverview(data.data);
            updateAgentsList(data.data.agent_status);
            updateChainsList(data.data.chain_status);
        } else {
            showError('加载系统状态失败: ' + data.error);
        }
    } catch (error) {
        showError('网络错误: ' + error.message);
    }
}

// 更新系统概览
function updateSystemOverview(data) {
    const agentStatus = data.agent_status;
    const monitorStats = data.monitor_stats;

    document.getElementById('total-agents').textContent = agentStatus.total_agents;
    document.getElementById('total-requests').textContent = monitorStats.total_requests || 0;
    document.getElementById('success-rate').textContent =
        monitorStats.system_success_rate ? (monitorStats.system_success_rate * 100).toFixed(1) + '%' : '0%';
    document.getElementById('uptime').textContent = monitorStats.system_uptime || '0:00:00';
}

// 更新智能体列表
function updateAgentsList(agentStatus) {
    const agentsList = document.getElementById('agents-list');

    if (agentStatus.agents && agentStatus.agents.length > 0) {
        let html = '';
        agentStatus.agents.forEach(agent => {
            const statusIcon = agent.enabled ? '✅' : '❌';
            html += `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <div>
                        <strong>${statusIcon} ${agent.name}</strong>
                        <br><small class="text-muted">${agent.description}</small>
                    </div>
                    <span class="badge bg-secondary">${agent.priority}</span>
                </div>
            `;
        });
        agentsList.innerHTML = html;
    } else {
        agentsList.innerHTML = '<p class="text-muted text-center">暂无智能体</p>';
    }
}

// 更新处理链列表
function updateChainsList(chainStatus) {
    const chainsList = document.getElementById('chains-list');

    if (chainStatus.chains && chainStatus.chains.length > 0) {
        let html = '';
        chainStatus.chains.forEach(chain => {
            html += `
                <div class="mb-2">
                    <strong>🔗 ${chain.name}</strong>
                    <br><small class="text-muted">${chain.agents.join(' → ')}</small>
                </div>
            `;
        });
        chainsList.innerHTML = html;
    } else {
        chainsList.innerHTML = '<p class="text-muted text-center">暂无处理链</p>';
    }
}

// 处理任务
async function processTask() {
    const taskContent = document.getElementById('ticket-content').value.trim();
    const chainName = document.getElementById('chain-select').value;
    const processBtn = document.getElementById('process-btn');

    if (!taskContent) {
        showError('请输入任务内容');
        return;
    }

    // 禁用按钮并显示加载状态
    processBtn.disabled = true;
    processBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 处理中...';

    try {
        const response = await fetch('/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ticket_content: taskContent,
                chain_name: chainName || null
            })
        });

        const data = await response.json();

        if (data.success) {
            showProcessResult(data.data);
            // 处理完成后刷新状态
            setTimeout(loadSystemStatus, 1000);
        } else {
            showError('处理任务失败: ' + data.error);
        }
    } catch (error) {
        showError('网络错误: ' + error.message);
    } finally {
        // 恢复按钮状态
        processBtn.disabled = false;
        processBtn.innerHTML = '<i class="fas fa-play"></i> 处理任务';
    }
}

// 显示处理结果
function showProcessResult(result) {
    const resultCard = document.getElementById('result-card');
    const resultContent = document.getElementById('result-content');

    let html = '';

    if (result.chain_name) {
        // 处理链结果
        html += `
            <h5>处理链: ${result.chain_name}</h5>
            <div class="alert ${result.success ? 'alert-success' : 'alert-warning'}">
                <strong>${result.success ? '✅ 处理成功' : '⚠️ 处理完成'}</strong>
                <br>处理智能体: ${result.processed_agents}/${result.total_agents}
                <br>最终结果: ${result.result}
            </div>
        `;

        if (result.chain_results && result.chain_results.length > 0) {
            html += '<h6>详细处理过程:</h6>';
            result.chain_results.forEach(chainResult => {
                const statusIcon = chainResult.success ? '✅' : '❌';
                const processedIcon = chainResult.processed ? '🔄' : '⏭️';
                html += `
                    <div class="d-flex align-items-center mb-2">
                        <span class="me-2">${statusIcon}${processedIcon}</span>
                        <div>
                            <strong>${chainResult.agent}</strong>
                            <br><small class="text-muted">${chainResult.result}</small>
                        </div>
                    </div>
                `;
            });
        }
    } else {
        // 智能路由结果
        html += `
            <h5>智能路由结果</h5>
            <div class="alert ${result.processed ? 'alert-success' : 'alert-warning'}">
                <strong>${result.processed ? '✅ 已处理' : '❌ 未处理'}</strong>
                <br>最佳智能体: ${result.analysis.best_agent || '无'}
                <br>置信度: ${(result.analysis.confidence * 100).toFixed(1)}%
                <br>候选智能体: ${result.analysis.candidates.length} 个
            </div>
            <p><strong>处理结果:</strong> ${result.result}</p>
        `;

        if (result.error) {
            html += `<div class="alert alert-danger"><strong>错误信息:</strong> ${result.error}</div>`;
        }
    }

    resultContent.innerHTML = html;
    resultCard.style.display = 'block';

    // 滚动到结果区域
    resultCard.scrollIntoView({ behavior: 'smooth' });
}

// 显示监控信息
async function showMonitor() {
    try {
        const response = await fetch('/api/monitor');
        const data = await response.json();

        if (data.success) {
            const monitorContent = document.getElementById('monitor-content');
            const report = data.data;

            let html = `
                <h6>系统概览</h6>
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>运行时间:</strong> ${report.system_overview.system_uptime}
                    </div>
                    <div class="col-md-6">
                        <strong>总请求数:</strong> ${report.system_overview.total_requests}
                    </div>
                    <div class="col-md-6">
                        <strong>成功率:</strong> ${(report.system_overview.system_success_rate * 100).toFixed(1)}%
                    </div>
                    <div class="col-md-6">
                        <strong>平均处理时间:</strong> ${report.system_overview.system_avg_processing_time.toFixed(2)}秒
                    </div>
                </div>
            `;

            if (report.performance_ranking && report.performance_ranking.length > 0) {
                html += '<h6>性能排名</h6>';
                report.performance_ranking.slice(0, 5).forEach((agent, index) => {
                    html += `
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <div>
                                <strong>${index + 1}. ${agent.agent_name}</strong>
                                <br><small class="text-muted">
                                    请求数: ${agent.total_requests} |
                                    成功率: ${(agent.success_rate * 100).toFixed(1)}% |
                                    平均时间: ${agent.avg_processing_time.toFixed(2)}秒
                                </small>
                            </div>
                        </div>
                    `;
                });
            }

            if (report.usage_distribution && Object.keys(report.usage_distribution).length > 0) {
                html += '<h6 class="mt-3">使用分布</h6>';
                Object.entries(report.usage_distribution)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 5)
                    .forEach(([agent, usage]) => {
                        html += `
                            <div class="d-flex justify-content-between align-items-center mb-1">
                                <span>${agent}</span>
                                <span class="badge bg-primary">${(usage * 100).toFixed(1)}%</span>
                            </div>
                        `;
                    });
            }

            monitorContent.innerHTML = html;

            // 显示模态框
            const monitorModal = new bootstrap.Modal(document.getElementById('monitorModal'));
            monitorModal.show();
        } else {
            showError('加载监控数据失败: ' + data.error);
        }
    } catch (error) {
        showError('网络错误: ' + error.message);
    }
}

// 刷新状态
function refreshStatus() {
    loadSystemStatus();
    showToast('状态已刷新', 'success');
}

// 显示错误信息
function showError(message) {
    showToast(message, 'danger');
}

// 显示Toast通知
function showToast(message, type = 'info') {
    // 创建Toast元素
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    // 添加到页面
    const toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
    toastContainer.appendChild(toast);
    document.body.appendChild(toastContainer);

    // 显示Toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    // 自动移除
    toast.addEventListener('hidden.bs.toast', () => {
        document.body.removeChild(toastContainer);
    });
}

// 显示工具管理
function showTools() {
    const toolsModal = new bootstrap.Modal(document.getElementById('toolsModal'));
    toolsModal.show();
    loadAllTools();
}

// 加载所有工具
async function loadAllTools() {
    try {
        const response = await fetch('/api/agents');
        const data = await response.json();

        if (data.success) {
            let html = '';

            for (const agent of data.data) {
                const toolsResponse = await fetch(`/api/agents/${agent.name}/tools`);
                const toolsData = await toolsResponse.json();

                if (toolsData.success && toolsData.data.length > 0) {
                    html += `
                        <div class="card mb-3">
                            <div class="card-header">
                                <h6>${agent.name} - ${agent.description}</h6>
                            </div>
                            <div class="card-body">
                                ${toolsData.data.map(tool => `
                                    <div class="d-flex justify-content-between align-items-center mb-2 p-2 border rounded">
                                        <div>
                                            <strong>${tool.name}</strong>
                                            <br><small class="text-muted">${tool.description}</small>
                                            <br><small><strong>参数:</strong> ${Object.entries(tool.parameters).map(([k, v]) => `${k}: ${v}`).join(', ')}</small>
                                        </div>
                                        <span class="badge ${tool.shared ? 'bg-success' : 'bg-secondary'}">
                                            ${tool.shared ? '共享' : '私有'}
                                        </span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                }
            }

            document.getElementById('all-tools-content').innerHTML = html || '<p class="text-muted text-center">暂无工具</p>';
            loadSharedTools();
            loadExecuteToolForm();
        } else {
            showError('加载工具失败: ' + data.error);
        }
    } catch (error) {
        showError('网络错误: ' + error.message);
    }
}

// 加载共享工具
async function loadSharedTools() {
    try {
        const response = await fetch('/api/tools/shared');
        const data = await response.json();

        if (data.success) {
            let html = '';

            for (const [agentName, tools] of Object.entries(data.data)) {
                if (tools.length > 0) {
                    html += `
                        <div class="card mb-3">
                            <div class="card-header">
                                <h6>${agentName}</h6>
                            </div>
                            <div class="card-body">
                                ${tools.map(tool => `
                                    <div class="d-flex justify-content-between align-items-center mb-2 p-2 border rounded">
                                        <div>
                                            <strong>${tool.name}</strong>
                                            <br><small class="text-muted">${tool.description}</small>
                                            <br><small><strong>参数:</strong> ${Object.entries(tool.parameters).map(([k, v]) => `${k}: ${v}`).join(', ')}</small>
                                        </div>
                                        <button class="btn btn-sm btn-outline-primary" onclick="executeTool('${agentName}', '${tool.name}')">
                                            执行
                                        </button>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                }
            }

            document.getElementById('shared-tools-content').innerHTML = html || '<p class="text-muted text-center">暂无共享工具</p>';
        } else {
            showError('加载共享工具失败: ' + data.error);
        }
    } catch (error) {
        showError('网络错误: ' + error.message);
    }
}

// 加载执行工具表单
async function loadExecuteToolForm() {
    try {
        const response = await fetch('/api/agents');
        const data = await response.json();

        if (data.success) {
            let html = `
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">选择智能体</label>
                            <select class="form-select" id="execute-agent-select" onchange="loadAgentTools()">
                                <option value="">请选择智能体</option>
                                ${data.data.map(agent => `<option value="${agent.name}">${agent.name}</option>`).join('')}
                            </select>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">选择工具</label>
                            <select class="form-select" id="execute-tool-select" onchange="showToolParameters()">
                                <option value="">请先选择智能体</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div id="tool-parameters-form"></div>
                <div id="execute-result" class="mt-3"></div>
            `;

            document.getElementById('execute-tool-content').innerHTML = html;
        }
    } catch (error) {
        showError('加载执行工具表单失败: ' + error.message);
    }
}

// 加载智能体工具
async function loadAgentTools() {
    const agentName = document.getElementById('execute-agent-select').value;
    if (!agentName) return;

    try {
        const response = await fetch(`/api/agents/${agentName}/tools`);
        const data = await response.json();

        if (data.success) {
            const toolSelect = document.getElementById('execute-tool-select');
            toolSelect.innerHTML = '<option value="">请选择工具</option>';

            data.data.forEach(tool => {
                const option = document.createElement('option');
                option.value = tool.name;
                option.textContent = `${tool.name} - ${tool.description}`;
                toolSelect.appendChild(option);
            });
        }
    } catch (error) {
        showError('加载工具失败: ' + error.message);
    }
}

// 显示工具参数表单
function showToolParameters() {
    const agentName = document.getElementById('execute-agent-select').value;
    const toolName = document.getElementById('execute-tool-select').value;

    if (!agentName || !toolName) return;

    // 这里简化处理，实际应用中应该从API获取参数信息
    const parametersForm = document.getElementById('tool-parameters-form');
    parametersForm.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h6>工具参数</h6>
            </div>
            <div class="card-body">
                <div class="mb-3">
                    <label class="form-label">参数 (JSON格式)</label>
                    <textarea class="form-control" id="tool-parameters" rows="4" placeholder='{"user_id": "user123", "resource_type": "cpu", "amount": 10}'></textarea>
                </div>
                <button class="btn btn-primary" onclick="executeSelectedTool()">执行工具</button>
            </div>
        </div>
    `;
}

// 执行选定的工具
async function executeSelectedTool() {
    const agentName = document.getElementById('execute-agent-select').value;
    const toolName = document.getElementById('execute-tool-select').value;
    const parametersText = document.getElementById('tool-parameters').value;

    if (!agentName || !toolName) {
        showError('请选择智能体和工具');
        return;
    }

    let parameters = {};
    try {
        if (parametersText.trim()) {
            parameters = JSON.parse(parametersText);
        }
    } catch (error) {
        showError('参数格式错误，请输入有效的JSON');
        return;
    }

    try {
        const response = await fetch('/api/tools/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                agent_name: agentName,
                tool_name: toolName,
                parameters: parameters
            })
        });

        const data = await response.json();
        const resultDiv = document.getElementById('execute-result');

        if (data.success) {
            resultDiv.innerHTML = `
                <div class="alert alert-success">
                    <strong>执行成功</strong>
                    <br>结果: ${data.data}
                </div>
            `;
        } else {
            resultDiv.innerHTML = `
                <div class="alert alert-danger">
                    <strong>执行失败</strong>
                    <br>错误: ${data.error}
                </div>
            `;
        }
    } catch (error) {
        showError('执行工具失败: ' + error.message);
    }
}

// 执行工具
async function executeTool(agentName, toolName) {
    try {
        const response = await fetch('/api/tools/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                agent_name: agentName,
                tool_name: toolName,
                parameters: {}
            })
        });

        const data = await response.json();
        if (data.success) {
            showToast(`工具 ${toolName} 执行成功: ${data.data}`, 'success');
        } else {
            showError(`工具执行失败: ${data.error}`);
        }
    } catch (error) {
        showError('执行工具失败: ' + error.message);
    }
}