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
    const chainStatus = data.chain_status;

    document.getElementById('total-agents').textContent = agentStatus.total_agents;
    document.getElementById('total-requests').textContent = monitorStats.total_requests || 0;
    document.getElementById('success-rate').textContent =
        monitorStats.system_success_rate ? (monitorStats.system_success_rate * 100).toFixed(1) + '%' : '0%';
    document.getElementById('uptime').textContent = monitorStats.system_uptime || '0:00:00';

    // 更新处理链选择下拉菜单
    updateChainSelect(chainStatus.chains);
}

// 更新处理链选择下拉菜单
function updateChainSelect(chains) {
    const chainSelect = document.getElementById('chain-select');

    if (!chainSelect) return;

    // 保存当前选中的值
    const currentValue = chainSelect.value;

    // 清空现有选项（保留第一个自动路由选项）
    chainSelect.innerHTML = '<option value="">自动路由（推荐）</option>';

    if (chains && chains.length > 0) {
        chains.forEach(chain => {
            const option = document.createElement('option');
            option.value = chain.name;
            option.textContent = `${chain.name} (${chain.agents.join(' → ')})`;
            chainSelect.appendChild(option);
        });
    }

    // 恢复之前选中的值（如果还存在）
    if (currentValue && chainSelect.querySelector(`option[value="${currentValue}"]`)) {
        chainSelect.value = currentValue;
    }
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

// MCP相关功能

// 显示MCP管理
function showMCP() {
    const mcpModal = new bootstrap.Modal(document.getElementById('mcpModal'));
    mcpModal.show();
    loadMCPClients();
}

// 加载MCP客户端
async function loadMCPClients() {
    try {
        const response = await fetch('/api/mcp/clients');
        const data = await response.json();

        if (data.success) {
            const clientsContent = document.getElementById('mcp-clients-content');

            if (Object.keys(data.data).length > 0) {
                let html = '<div class="row">';

                for (const [clientName, clientInfo] of Object.entries(data.data)) {
                    const statusIcon = clientInfo.connected ? '✅' : '❌';
                    const statusClass = clientInfo.connected ? 'text-success' : 'text-danger';

                    html += `
                        <div class="col-md-6 mb-3">
                            <div class="card">
                                <div class="card-header d-flex justify-content-between align-items-center">
                                    <h6 class="mb-0">${clientName}</h6>
                                    <span class="${statusClass}">${statusIcon}</span>
                                </div>
                                <div class="card-body">
                                    <p><strong>服务器:</strong> ${clientInfo.server_url}</p>
                                    <p><strong>工具数量:</strong> ${clientInfo.tools_count}</p>
                                    <p><strong>资源数量:</strong> ${clientInfo.resources_count}</p>
                                    <div class="d-grid gap-2">
                                        <button class="btn btn-sm btn-outline-primary" onclick="loadMCPTools('${clientName}')">
                                            查看工具
                                        </button>
                                        <button class="btn btn-sm btn-outline-info" onclick="loadMCPResources('${clientName}')">
                                            查看资源
                                        </button>
                                        <button class="btn btn-sm btn-outline-danger" onclick="removeMCPClient('${clientName}')">
                                            移除
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                }

                html += '</div>';
                clientsContent.innerHTML = html;
            } else {
                clientsContent.innerHTML = '<p class="text-muted text-center">暂无MCP客户端</p>';
            }
        } else {
            showError('加载MCP客户端失败: ' + data.error);
        }
    } catch (error) {
        showError('网络错误: ' + error.message);
    }
}

// 显示添加MCP客户端模态框
function showAddMCPClient() {
    const addModal = new bootstrap.Modal(document.getElementById('addMCPClientModal'));
    addModal.show();
}

// 添加MCP客户端
async function addMCPClient() {
    const clientName = document.getElementById('client-name').value.trim();
    const serverUrl = document.getElementById('server-url').value.trim();

    if (!clientName || !serverUrl) {
        showError('请填写客户端名称和服务器地址');
        return;
    }

    try {
        const response = await fetch('/api/mcp/clients', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: clientName,
                server_url: serverUrl
            })
        });

        const data = await response.json();
        if (data.success) {
            showToast(data.message, 'success');
            // 关闭添加模态框
            const addModal = bootstrap.Modal.getInstance(document.getElementById('addMCPClientModal'));
            addModal.hide();
            // 刷新客户端列表
            loadMCPClients();
            // 清空表单
            document.getElementById('client-name').value = '';
            document.getElementById('server-url').value = '';
        } else {
            showError('添加MCP客户端失败: ' + data.error);
        }
    } catch (error) {
        showError('网络错误: ' + error.message);
    }
}

// 移除MCP客户端
async function removeMCPClient(clientName) {
    if (!confirm(`确定要移除MCP客户端 "${clientName}" 吗？`)) {
        return;
    }

    try {
        const response = await fetch(`/api/mcp/clients/${clientName}`, {
            method: 'DELETE'
        });

        const data = await response.json();
        if (data.success) {
            showToast(data.message, 'success');
            loadMCPClients();
        } else {
            showError('移除MCP客户端失败: ' + data.error);
        }
    } catch (error) {
        showError('网络错误: ' + error.message);
    }
}

// 加载MCP工具
async function loadMCPTools(clientName) {
    try {
        const response = await fetch(`/api/mcp/clients/${clientName}/tools`);
        const data = await response.json();

        if (data.success) {
            const toolsContent = document.getElementById('mcp-tools-content');

            if (data.data.length > 0) {
                let html = `
                    <h6>${clientName} - 工具列表</h6>
                    <div class="row">
                `;

                data.data.forEach(tool => {
                    html += `
                        <div class="col-md-6 mb-3">
                            <div class="card">
                                <div class="card-header">
                                    <h6 class="mb-0">${tool.name}</h6>
                                </div>
                                <div class="card-body">
                                    <p class="text-muted">${tool.description}</p>
                                    <div class="mb-2">
                                        <strong>参数:</strong>
                                        <pre class="bg-light p-2 mt-1 small">${JSON.stringify(tool.parameters, null, 2)}</pre>
                                    </div>
                                    <button class="btn btn-sm btn-primary" onclick="showMCPToolExecute('${clientName}', '${tool.name}')">
                                        执行工具
                                    </button>
                                </div>
                            </div>
                        </div>
                    `;
                });

                html += '</div>';
                toolsContent.innerHTML = html;
            } else {
                toolsContent.innerHTML = `<p class="text-muted text-center">客户端 ${clientName} 暂无工具</p>`;
            }

            // 切换到工具标签页
            const toolsTab = new bootstrap.Tab(document.getElementById('mcp-tools-tab'));
            toolsTab.show();
        } else {
            showError('加载MCP工具失败: ' + data.error);
        }
    } catch (error) {
        showError('网络错误: ' + error.message);
    }
}

// 加载MCP资源
async function loadMCPResources(clientName) {
    try {
        const response = await fetch(`/api/mcp/clients/${clientName}/resources`);
        const data = await response.json();

        if (data.success) {
            const resourcesContent = document.getElementById('mcp-resources-content');

            if (data.data.length > 0) {
                let html = `
                    <h6>${clientName} - 资源列表</h6>
                    <div class="row">
                `;

                data.data.forEach(resource => {
                    html += `
                        <div class="col-md-6 mb-3">
                            <div class="card">
                                <div class="card-header">
                                    <h6 class="mb-0">${resource.name}</h6>
                                </div>
                                <div class="card-body">
                                    <p><strong>URI:</strong> ${resource.uri}</p>
                                    <p class="text-muted">${resource.description}</p>
                                    <p><strong>MIME类型:</strong> ${resource.mime_type}</p>
                                    <button class="btn btn-sm btn-info" onclick="readMCPResource('${clientName}', '${resource.uri}')">
                                        读取资源
                                    </button>
                                </div>
                            </div>
                        </div>
                    `;
                });

                html += '</div>';
                resourcesContent.innerHTML = html;
            } else {
                resourcesContent.innerHTML = `<p class="text-muted text-center">客户端 ${clientName} 暂无资源</p>`;
            }

            // 切换到资源标签页
            const resourcesTab = new bootstrap.Tab(document.getElementById('mcp-resources-tab'));
            resourcesTab.show();
        } else {
            showError('加载MCP资源失败: ' + data.error);
        }
    } catch (error) {
        showError('网络错误: ' + error.message);
    }
}

// 显示MCP工具执行表单
function showMCPToolExecute(clientName, toolName) {
    const executeContent = document.getElementById('mcp-execute-content');

    executeContent.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h6>执行MCP工具</h6>
            </div>
            <div class="card-body">
                <div class="mb-3">
                    <label class="form-label">客户端</label>
                    <input type="text" class="form-control" value="${clientName}" readonly>
                </div>
                <div class="mb-3">
                    <label class="form-label">工具</label>
                    <input type="text" class="form-control" value="${toolName}" readonly>
                </div>
                <div class="mb-3">
                    <label class="form-label">参数 (JSON格式)</label>
                    <textarea class="form-control" id="mcp-tool-arguments" rows="4" placeholder='{"param1": "value1", "param2": "value2"}'></textarea>
                </div>
                <button class="btn btn-primary" onclick="executeMCPTool('${clientName}', '${toolName}')">执行工具</button>
                <div id="mcp-execute-result" class="mt-3"></div>
            </div>
        </div>
    `;

    // 切换到执行标签页
    const executeTab = new bootstrap.Tab(document.getElementById('mcp-execute-tab'));
    executeTab.show();
}

// 执行MCP工具
async function executeMCPTool(clientName, toolName) {
    const argumentsText = document.getElementById('mcp-tool-arguments').value;

    let argumentsObj = {};
    try {
        if (argumentsText.trim()) {
            argumentsObj = JSON.parse(argumentsText);
        }
    } catch (error) {
        showError('参数格式错误，请输入有效的JSON');
        return;
    }

    try {
        const response = await fetch('/api/mcp/tools/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                client_name: clientName,
                tool_name: toolName,
                arguments: argumentsObj
            })
        });

        const data = await response.json();
        const resultDiv = document.getElementById('mcp-execute-result');

        if (data.success) {
            resultDiv.innerHTML = `
                <div class="alert alert-success">
                    <strong>执行成功</strong>
                    <pre class="mt-2">${JSON.stringify(data.data, null, 2)}</pre>
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
        showError('执行MCP工具失败: ' + error.message);
    }
}

// 读取MCP资源
async function readMCPResource(clientName, resourceUri) {
    try {
        const response = await fetch('/api/mcp/resources/read', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                client_name: clientName,
                resource_uri: resourceUri
            })
        });

        const data = await response.json();
        if (data.success) {
            // 显示资源内容
            const resourcesContent = document.getElementById('mcp-resources-content');
            const resourceCard = document.createElement('div');
            resourceCard.className = 'card mt-3';
            resourceCard.innerHTML = `
                <div class="card-header">
                    <h6>资源内容: ${resourceUri}</h6>
                </div>
                <div class="card-body">
                    <pre class="bg-light p-3">${data.data}</pre>
                </div>
            `;
            resourcesContent.appendChild(resourceCard);
        } else {
            showError('读取资源失败: ' + data.error);
        }
    } catch (error) {
        showError('读取资源失败: ' + error.message);
    }
}

// 处理链管理功能

// 显示处理链管理
function showChains() {
    const chainsModal = new bootstrap.Modal(document.getElementById('chainsModal'));
    chainsModal.show();
    loadChainsManagement();
}

// 加载处理链管理界面
async function loadChainsManagement() {
    try {
        // 获取所有智能体
        const agentsResponse = await fetch('/api/agents');
        const agentsData = await agentsResponse.json();

        // 获取所有处理链
        const chainsResponse = await fetch('/api/chains');
        const chainsData = await chainsResponse.json();

        if (agentsData.success && chainsData.success) {
            renderChainsManagement(agentsData.data, chainsData.data);
        } else {
            showError('加载处理链管理数据失败');
        }
    } catch (error) {
        showError('网络错误: ' + error.message);
    }
}

// 渲染处理链管理界面
function renderChainsManagement(agents, chains) {
    const chainsManagementContent = document.getElementById('chains-management-content');

    let html = `
        <div class="row">
            <!-- 创建新处理链 -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h6>创建新处理链</h6>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label class="form-label">处理链名称</label>
                            <input type="text" class="form-control" id="new-chain-name" placeholder="输入处理链名称">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">选择智能体</label>
                            <div id="agent-selection">
                                ${agents.map(agent => `
                                    <div class="form-check">
                                        <input class="form-check-input agent-checkbox" type="checkbox" value="${agent.name}" id="agent-${agent.name}">
                                        <label class="form-check-label" for="agent-${agent.name}">
                                            ${agent.name} - ${agent.description}
                                        </label>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">智能体顺序</label>
                            <div id="selected-agents-order" class="border rounded p-2 bg-light" style="min-height: 100px;">
                                <p class="text-muted text-center mb-0">拖拽智能体调整顺序</p>
                            </div>
                        </div>
                        <button class="btn btn-primary" onclick="createNewChain()">创建处理链</button>
                    </div>
                </div>
            </div>

            <!-- 现有处理链管理 -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h6>现有处理链</h6>
                    </div>
                    <div class="card-body">
                        <div id="existing-chains-list">
                            ${chains.length > 0 ? chains.map(chain => `
                                <div class="card mb-3">
                                    <div class="card-header d-flex justify-content-between align-items-center">
                                        <h6 class="mb-0">${chain.name}</h6>
                                        <div>
                                            <button class="btn btn-sm btn-outline-primary me-1" onclick="editChain('${chain.name}')">编辑</button>
                                            <button class="btn btn-sm btn-outline-danger" onclick="deleteChain('${chain.name}')">删除</button>
                                        </div>
                                    </div>
                                    <div class="card-body">
                                        <p><strong>智能体顺序:</strong> ${chain.agents.join(' → ')}</p>
                                        <p><strong>智能体数量:</strong> ${chain.length}</p>
                                    </div>
                                </div>
                            `).join('') : '<p class="text-muted text-center">暂无处理链</p>'}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    chainsManagementContent.innerHTML = html;

    // 设置智能体选择事件
    setupAgentSelection();
}

// 设置智能体选择
function setupAgentSelection() {
    const checkboxes = document.querySelectorAll('.agent-checkbox');
    const selectedAgentsContainer = document.getElementById('selected-agents-order');

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateSelectedAgents();
        });
    });

    // 初始化拖拽功能
    setupDragAndDrop();
}

// 更新选中的智能体
function updateSelectedAgents() {
    const selectedAgentsContainer = document.getElementById('selected-agents-order');
    const selectedAgents = Array.from(document.querySelectorAll('.agent-checkbox:checked'))
        .map(cb => cb.value);

    if (selectedAgents.length === 0) {
        selectedAgentsContainer.innerHTML = '<p class="text-muted text-center mb-0">拖拽智能体调整顺序</p>';
        return;
    }

    selectedAgentsContainer.innerHTML = selectedAgents.map(agentName => `
        <div class="selected-agent-item border rounded p-2 mb-2 bg-white" data-agent="${agentName}" draggable="true">
            <div class="d-flex justify-content-between align-items-center">
                <span>${agentName}</span>
                <button class="btn btn-sm btn-outline-danger" onclick="removeAgentFromSelection('${agentName}')">移除</button>
            </div>
        </div>
    `).join('');

    // 重新设置拖拽功能
    setupDragAndDrop();
}

// 设置拖拽功能
function setupDragAndDrop() {
    const container = document.getElementById('selected-agents-order');
    let draggedItem = null;

    container.addEventListener('dragstart', function(e) {
        if (e.target.classList.contains('selected-agent-item')) {
            draggedItem = e.target;
            e.target.style.opacity = '0.5';
        }
    });

    container.addEventListener('dragend', function(e) {
        if (draggedItem) {
            draggedItem.style.opacity = '1';
            draggedItem = null;
        }
    });

    container.addEventListener('dragover', function(e) {
        e.preventDefault();
    });

    container.addEventListener('drop', function(e) {
        e.preventDefault();
        if (draggedItem && e.target.classList.contains('selected-agent-item')) {
            const target = e.target;
            const containerRect = container.getBoundingClientRect();
            const targetRect = target.getBoundingClientRect();
            const targetCenter = targetRect.top + targetRect.height / 2;

            if (e.clientY < targetCenter) {
                container.insertBefore(draggedItem, target);
            } else {
                container.insertBefore(draggedItem, target.nextSibling);
            }
        }
    });
}

// 从选择中移除智能体
function removeAgentFromSelection(agentName) {
    const checkbox = document.getElementById(`agent-${agentName}`);
    if (checkbox) {
        checkbox.checked = false;
        updateSelectedAgents();
    }
}

// 创建新处理链
async function createNewChain() {
    const chainName = document.getElementById('new-chain-name').value.trim();
    const selectedAgentsContainer = document.getElementById('selected-agents-order');
    const agentItems = selectedAgentsContainer.querySelectorAll('.selected-agent-item');

    if (!chainName) {
        showError('请输入处理链名称');
        return;
    }

    if (agentItems.length === 0) {
        showError('请至少选择一个智能体');
        return;
    }

    const agentList = Array.from(agentItems).map(item => item.getAttribute('data-agent'));

    try {
        const response = await fetch('/api/chains/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                chain_name: chainName,
                agents: agentList
            })
        });

        const data = await response.json();
        if (data.success) {
            showToast(data.message, 'success');
            // 刷新处理链列表
            loadChainsManagement();
            // 刷新系统状态以更新下拉菜单
            loadSystemStatus();
            // 清空表单
            document.getElementById('new-chain-name').value = '';
            document.querySelectorAll('.agent-checkbox').forEach(cb => cb.checked = false);
            updateSelectedAgents();
        } else {
            showError('创建处理链失败: ' + data.error);
        }
    } catch (error) {
        showError('网络错误: ' + error.message);
    }
}

// 删除处理链
async function deleteChain(chainName) {
    if (!confirm(`确定要删除处理链 "${chainName}" 吗？`)) {
        return;
    }

    try {
        const response = await fetch(`/api/chains/${chainName}`, {
            method: 'DELETE'
        });

        const data = await response.json();
        if (data.success) {
            showToast(data.message, 'success');
            loadChainsManagement();
            // 刷新页面上的处理链列表
            loadSystemStatus();
        } else {
            showError('删除处理链失败: ' + data.error);
        }
    } catch (error) {
        showError('网络错误: ' + error.message);
    }
}

// 编辑处理链
function editChain(chainName) {
    // 这里简化处理，实际应用中应该加载现有处理链信息到编辑表单
    document.getElementById('new-chain-name').value = chainName;
    showToast(`编辑处理链 ${chainName} - 请重新选择智能体并创建新链`, 'info');
}