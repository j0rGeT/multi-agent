"""
智能体监控和统计模块
"""
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict, deque


class AgentMetrics:
    """智能体指标"""

    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_processing_time = 0.0
        self.last_request_time = None
        self.error_count = defaultdict(int)

    def record_request(self, success: bool, processing_time: float, error_type: str = None):
        """记录请求指标"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
            if error_type:
                self.error_count[error_type] += 1

        self.total_processing_time += processing_time
        self.last_request_time = datetime.now()

    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests

    @property
    def average_processing_time(self) -> float:
        """平均处理时间"""
        if self.total_requests == 0:
            return 0.0
        return self.total_processing_time / self.total_requests


class AgentMonitor:
    """智能体监控器"""

    def __init__(self, window_size: int = 100):
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self.recent_requests = deque(maxlen=window_size)
        self.system_start_time = datetime.now()

    def record_agent_request(self, agent_name: str, success: bool,
                           processing_time: float, error_type: str = None):
        """记录智能体请求"""
        if agent_name not in self.agent_metrics:
            self.agent_metrics[agent_name] = AgentMetrics()

        self.agent_metrics[agent_name].record_request(success, processing_time, error_type)

        # 记录最近请求
        self.recent_requests.append({
            'timestamp': datetime.now(),
            'agent_name': agent_name,
            'success': success,
            'processing_time': processing_time,
            'error_type': error_type
        })

    def get_agent_stats(self, agent_name: str) -> Dict[str, Any]:
        """获取智能体统计信息"""
        if agent_name not in self.agent_metrics:
            return {
                'total_requests': 0,
                'success_rate': 0.0,
                'average_processing_time': 0.0,
                'last_request_time': None
            }

        metrics = self.agent_metrics[agent_name]
        return {
            'total_requests': metrics.total_requests,
            'successful_requests': metrics.successful_requests,
            'failed_requests': metrics.failed_requests,
            'success_rate': metrics.success_rate,
            'average_processing_time': metrics.average_processing_time,
            'last_request_time': metrics.last_request_time,
            'error_count': dict(metrics.error_count)
        }

    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        total_requests = sum(m.total_requests for m in self.agent_metrics.values())
        total_success = sum(m.successful_requests for m in self.agent_metrics.values())
        total_processing_time = sum(m.total_processing_time for m in self.agent_metrics.values())

        # 计算系统成功率
        system_success_rate = total_success / total_requests if total_requests > 0 else 0.0

        # 计算系统平均处理时间
        system_avg_time = total_processing_time / total_requests if total_requests > 0 else 0.0

        # 计算最近1小时的请求量
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_requests = [r for r in self.recent_requests if r['timestamp'] > one_hour_ago]

        return {
            'system_uptime': str(datetime.now() - self.system_start_time),
            'total_agents': len(self.agent_metrics),
            'total_requests': total_requests,
            'system_success_rate': system_success_rate,
            'system_avg_processing_time': system_avg_time,
            'recent_requests_1h': len(recent_requests),
            'system_start_time': self.system_start_time
        }

    def get_agent_performance_ranking(self) -> List[Dict[str, Any]]:
        """获取智能体性能排名"""
        rankings = []
        for agent_name, metrics in self.agent_metrics.items():
            if metrics.total_requests > 0:
                rankings.append({
                    'agent_name': agent_name,
                    'total_requests': metrics.total_requests,
                    'success_rate': metrics.success_rate,
                    'avg_processing_time': metrics.average_processing_time,
                    'efficiency_score': metrics.success_rate / (metrics.average_processing_time + 0.1)
                })

        # 按效率得分排序
        rankings.sort(key=lambda x: x['efficiency_score'], reverse=True)
        return rankings

    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的错误"""
        errors = [r for r in self.recent_requests if not r['success']]
        return errors[-limit:]

    def get_agent_usage_distribution(self) -> Dict[str, float]:
        """获取智能体使用分布"""
        total_requests = sum(m.total_requests for m in self.agent_metrics.values())
        if total_requests == 0:
            return {}

        distribution = {}
        for agent_name, metrics in self.agent_metrics.items():
            distribution[agent_name] = metrics.total_requests / total_requests

        return distribution

    def reset_metrics(self):
        """重置所有指标"""
        self.agent_metrics.clear()
        self.recent_requests.clear()
        self.system_start_time = datetime.now()
        print("📊 所有监控指标已重置")

    def generate_report(self) -> Dict[str, Any]:
        """生成监控报告"""
        system_stats = self.get_system_stats()
        performance_ranking = self.get_agent_performance_ranking()
        usage_distribution = self.get_agent_usage_distribution()
        recent_errors = self.get_recent_errors()

        return {
            'system_overview': system_stats,
            'performance_ranking': performance_ranking,
            'usage_distribution': usage_distribution,
            'recent_errors': recent_errors,
            'agent_details': {
                agent_name: self.get_agent_stats(agent_name)
                for agent_name in self.agent_metrics.keys()
            }
        }