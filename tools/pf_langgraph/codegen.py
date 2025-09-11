import json
import os
import re
import textwrap
from typing import Any, Dict, List

from .hashing import spec_fingerprint

EXPR_RE = re.compile(r"\$\{([^}]+)\}")

# Matches dotted paths starting with one of the state roots, e.g.
# inputs.foo.bar, nodes.some_node.data.value, outputs.final
_STATE_PATH_RE = re.compile(r"\b(inputs|nodes|outputs)((?:\.[A-Za-z_][\w]*)+)")


def _convert_state_paths(expr: str) -> str:
    """Convert dotted state paths into dictionary indexing expressions.

    Example: nodes.foo.bar -> state['nodes']['foo']['bar']
    """

    def _repl(match: re.Match[str]) -> str:
        root = match.group(1)
        tail = match.group(2)  # like .foo.bar
        parts = [p for p in tail.split(".") if p]
        chain = "".join("[" + json.dumps(p) + "]" for p in parts)
        return f"state[{json.dumps(root)}]{chain}"

    return _STATE_PATH_RE.sub(_repl, expr)


def _emit_symbol(inner: str) -> str:
    inner = inner.strip()
    if inner.startswith("env:"):
        name = inner.split(":", 1)[1]
        return f'os.environ.get("{name}", "")'
    # Convert any inputs./nodes./outputs. dotted paths into state[...] indexing
    return _convert_state_paths(inner)


def _emit_template_expr(text: str) -> str:
    # Build a Python expression by concatenating literal chunks and evaluated symbols
    parts: List[str] = []
    last = 0
    for m in EXPR_RE.finditer(text):
        if m.start() > last:
            lit = text[last : m.start()]
            parts.append(json.dumps(lit))
        parts.append(_emit_symbol(m.group(1)))
        last = m.end()
    if last < len(text):
        parts.append(json.dumps(text[last:]))
    if not parts:
        return json.dumps(text)
    return " + ".join(parts)


def _emit_value(val: Any) -> str:
    if isinstance(val, str):
        return _emit_template_expr(val)
    if isinstance(val, list):
        return "[" + ", ".join(_emit_value(v) for v in val) + "]"
    if isinstance(val, dict):
        items = []
        for k, v in val.items():
            items.append(json.dumps(k) + ": " + _emit_value(v))
        return "{" + ", ".join(items) + "}"
    return json.dumps(val)


WRAP_HELPERS = """
from functools import partial

def _wrap_node(fn, client, env):
    async def _inner(state):
        return await fn(state, client, env)
    return _inner
"""


def _emit_expr(expr_text: str) -> str:
    """Emit a raw Python expression from a ${...} template.

    The expression may reference inputs./nodes./outputs. dotted paths and env:VARS.
    We convert dotted paths to state[...] indexing and leave operators as-is.
    """
    expr_text = expr_text.strip()
    m = EXPR_RE.fullmatch(expr_text)
    if m:
        inner = m.group(1)
    else:
        # If the whole text isn't a single ${...}, still attempt best-effort conversion
        # by replacing any ${...} occurrences and then converting bare paths.
        inner_parts: List[str] = []
        last = 0
        for t in EXPR_RE.finditer(expr_text):
            if t.start() > last:
                inner_parts.append(expr_text[last : t.start()])
            inner_parts.append(t.group(1))
            last = t.end()
        if last < len(expr_text):
            inner_parts.append(expr_text[last:])
        inner = "".join(inner_parts)
    # First handle env:NAME tokens that stand alone (not nested inside another identifier)
    def _env_repl(m: re.Match[str]) -> str:
        env_var = m.group(1)
        # For numeric comparisons, try to convert to int
        if env_var in ['TROPE_MAX', 'MAX_TROPES', 'LIMIT']:
            return f'int(os.environ.get("{env_var}", "10"))'
        return f'os.environ.get("{env_var}", "")'

    inner = re.sub(r"\benv:([A-Za-z_][A-Za-z0-9_]*)\b", _env_repl, inner)
    return _convert_state_paths(inner)


def _emit_http_call(node: dict) -> str:
    cfg = node["config"]
    method = cfg.get("method", "GET").upper()
    url = _emit_value(cfg["url"])  # expression
    headers = _emit_value(cfg.get("headers", {}))
    body = _emit_value(cfg.get("body", {}))
    return f"""
async def node_{node['id']}(state, client, env):
    import httpx, json, os
    url = {url}
    body = {body}
    headers = {headers}
    async with httpx.AsyncClient(timeout=60) as s:
        r = await s.request("{method}", url, json=body, headers=headers)
        r.raise_for_status()
        out = r.json()
    # Return delta for parallel-safe updates
    return {{'nodes': {{'{node['id']}': out}}}}
"""


def _emit_branch(node: dict) -> str:
    expr = node["config"]["expr"]
    on_true = node["config"].get("on_true", [])
    on_false = node["config"].get("on_false", [])
    return f"""
async def node_{node['id']}(state, client, env):
    cond = bool({_emit_expr(expr)})
    # Return delta for parallel-safe updates
    return {{
        'nodes': {{'{node['id']}': {{'status':'ok','data':{{'cond': cond}},'error':None,'meta':{{}}}}}},
        '__branch__': 'on_true' if cond else 'on_false',
        '__branch_targets__': {json.dumps({'on_true': on_true, 'on_false': on_false})}
    }}
"""


def _emit_outputs_finalization(outputs: dict) -> str:
    """Generate output finalization code from outputs spec."""
    lines = []
    for key, expr in outputs.items():
        if isinstance(expr, str) and expr.startswith("${") and expr.endswith("}"):
            inner = expr[2:-1]
            if inner.startswith("nodes."):
                node_id = inner.split(".")[1]
                if "." in inner:
                    path_parts = inner.split(".")[2:]
                    if len(path_parts) == 1:
                        lines.append(f"    outputs['{key}'] = state['nodes'].get('{node_id}', {{}}).get('{path_parts[0]}')")
                    else:
                        # Handle nested paths like data.cond
                        path_chain = "".join(f".get('{part}', {{}})" for part in path_parts)
                        lines.append(f"    outputs['{key}'] = state['nodes'].get('{node_id}', {{}}){path_chain}")
                else:
                    lines.append(f"    outputs['{key}'] = state['nodes'].get('{node_id}')")
            elif inner.startswith("inputs."):
                path = inner.split(".")[1]
                lines.append(f"    outputs['{key}'] = state['inputs'].get('{path}')")
            else:
                lines.append(f"    outputs['{key}'] = {_emit_expr(inner)}")
        elif isinstance(expr, dict):
            # Handle nested objects like qa: {trope: ..., promise: ...}
            lines.append(f"    outputs['{key}'] = {{}}")
            for sub_key, sub_expr in expr.items():
                if isinstance(sub_expr, str) and sub_expr.startswith("${") and sub_expr.endswith("}"):
                    inner = sub_expr[2:-1]
                    if inner.startswith("nodes."):
                        node_id = inner.split(".")[1]
                        if "." in inner:
                            path_parts = inner.split(".")[2:]
                            if len(path_parts) == 1:
                                lines.append(f"    outputs['{key}']['{sub_key}'] = state['nodes'].get('{node_id}', {{}}).get('{path_parts[0]}')")
                            else:
                                # Handle nested paths like data.cond
                                path_chain = "".join(f".get('{part}', {{}})" for part in path_parts)
                                lines.append(f"    outputs['{key}']['{sub_key}'] = state['nodes'].get('{node_id}', {{}}){path_chain}")
                        else:
                            lines.append(f"    outputs['{key}']['{sub_key}'] = state['nodes'].get('{node_id}')")
                    elif inner.startswith("inputs."):
                        path = inner.split(".")[1]
                        lines.append(f"    outputs['{key}']['{sub_key}'] = state['inputs'].get('{path}')")
                    else:
                        lines.append(f"    outputs['{key}']['{sub_key}'] = {_emit_expr(inner)}")
                else:
                    lines.append(f"    outputs['{key}']['{sub_key}'] = {_emit_value(sub_expr)}")
        else:
            lines.append(f"    outputs['{key}'] = {_emit_value(expr)}")
    return "\n".join(lines)


def generate(spec: Dict[str, Any]) -> str:
    fp = spec_fingerprint(spec)
    imports = """
import os
from typing import Any, Dict, TypedDict
from langgraph.graph import StateGraph
from tools.pf_langgraph.envelope import require_envelope
"""

    preamble = WRAP_HELPERS + """
from typing import Annotated
from langgraph.graph.message import add_messages
import operator

class GraphState(TypedDict):
    inputs: Dict[str, Any]
    nodes: Annotated[Dict[str, Any], operator.or_]
    outputs: Annotated[Dict[str, Any], operator.or_]
"""

    body_parts: List[str] = []
    for n in spec["nodes"]:
        if n["kind"] == "http_call":
            body_parts.append(_emit_http_call(n))
        elif n["kind"] == "branch":
            body_parts.append(_emit_branch(n))
        else:
            raise ValueError(f"Unsupported kind: {n['kind']}")

    # We register wrapped nodes later (needs client/env)
    add_nodes = [f"# defer add_node for '{n['id']}' (wrapped later)" for n in spec["nodes"]]
    edges = []
    for e in spec["edges"]:
        edges.append(f"graph.add_edge('{e['from']}', '{e['to']}')")

    controller = """
async def controller(state, *_):
    for k, v in list(state['nodes'].items()):
        require_envelope(v, f"node:{k}")
    branch = state.pop('__branch__', None)
    targets = state.pop('__branch_targets__', None)
    if branch and targets:
        for t in targets.get(branch, []):
            return {'__next__': t}
    return {}
"""

    def _indent_lines(lines: List[str], spaces: int = 4) -> str:
        prefix = " " * spaces
        return os.linesep.join(prefix + line for line in lines)

    add_nodes_block = _indent_lines([f"graph.add_node('{n['id']}', _wrap_node(node_{n['id']}, client, env))" for n in spec["nodes"]], 4)
    edges_block = _indent_lines(edges, 4)

    build = f"""
def build_graph_with_ctx(client=None, env=None):
    # Default env = process environment
    if env is None:
        env = dict(os.environ)
    graph = StateGraph(GraphState)
    # register wrapped nodes so LangGraph calls them as (state) while we keep (state, client, env)
{add_nodes_block}
{edges_block}
    graph.set_entry_point('{spec['nodes'][0]['id']}')
    graph.__spec_fingerprint__ = '{fp}'
    return graph

def build_graph():
    # Back-compat: build with default ctx
    return build_graph_with_ctx()
"""

    finalize_outputs = f"""
def _finalize_outputs(state):
    \"\"\"Finalize outputs from the flow specification.\"\"\"
    outputs = {{}}
{_emit_outputs_finalization(spec.get("outputs", {}))}
    return {{'outputs': outputs}}
"""

    run = f"""
async def run_graph(inputs: Dict[str, Any], client=None, env=None):
    g = build_graph_with_ctx(client=client, env=env).compile()
    state = {{'inputs': inputs, 'nodes': {{}}, 'outputs': {{}}}}
    state = await g.ainvoke(state)
    delta = _finalize_outputs(state)
    if isinstance(delta, dict) and 'outputs' in delta:
        try:
            state['outputs'] |= delta['outputs']
        except Exception:
            tmp = state.get('outputs', {{}}).copy()
            tmp.update(delta['outputs'])
            state['outputs'] = tmp
    return state
"""

    return textwrap.dedent(imports + preamble + "".join(body_parts) + controller + build + finalize_outputs + run)


