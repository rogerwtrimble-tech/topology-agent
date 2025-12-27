from __future__ import annotations

"""
Prometheus metrics for the orchestration layer.

These are intentionally very small and generic:
- node-level metrics (ingress, planner, tools, correlate, response, ...)
- tool-level metrics (topology_tool, inventory_tool, comment_tool, ...)

They are exported via the global /metrics endpoint that uses
prometheus_client.REGISTRY in src/api/metrics.py.
"""

from prometheus_client import Counter, Histogram

# Node-level metrics: each LangGraph node invocation
NODE_INVOCATIONS = Counter(
    "topology_orchestrator_node_invocations_total",
    "Number of times an orchestrator node runs",
    labelnames=("node", "status"),  # status: ok | error
)

NODE_LATENCY = Histogram(
    "topology_orchestrator_node_duration_seconds",
    "Execution time of orchestrator nodes in seconds",
    labelnames=("node",),
)


# Tool-level metrics: when tool_node invokes an underlying tool
TOOL_INVOCATIONS = Counter(
    "topology_orchestrator_tool_invocations_total",
    "Number of times an orchestrator tool is invoked",
    labelnames=("tool", "status"),  # status: ok | error
)

TOOL_LATENCY = Histogram(
    "topology_orchestrator_tool_duration_seconds",
    "Execution time of orchestrator tools in seconds",
    labelnames=("tool",),
)
