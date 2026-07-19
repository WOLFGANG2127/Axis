"""AST security scanner for uploaded AXIS strategy modules."""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

FORBIDDEN_IMPORT_ROOTS = {"httpx", "requests", "aiohttp", "urllib", "socket"}
ALLOWED_SRC_PREFIXES = ("src.scoring", "src.math", "src.graph.state", "src.strategies.base")
FORBIDDEN_CALL_NAMES = {"open", "__import__", "eval", "exec", "compile", "get_supabase_client", "create_client"}
FORBIDDEN_ATTRS = {"request", "urlopen", "urlretrieve", "socket", "connect", "connect_ex", "send", "sendall", "recv"}


@dataclass(frozen=True)
class StrategyScanIssue:
    line: int
    code: str
    message: str


@dataclass(frozen=True)
class StrategyScanResult:
    passed: bool
    issues: tuple[StrategyScanIssue, ...] = field(default_factory=tuple)
    def raise_if_failed(self) -> None:
        if not self.passed:
            raise StrategySecurityError(self.issues)


class StrategySecurityError(ValueError):
    def __init__(self, issues: Iterable[StrategyScanIssue]):
        self.issues = tuple(issues)
        super().__init__("; ".join(f"line {i.line}: {i.message}" for i in self.issues) or "strategy security scan failed")


def _stdlib_roots() -> set[str]:
    roots = set(getattr(sys, "stdlib_module_names", set()))
    roots.update({"__future__", "typing", "dataclasses", "datetime", "zoneinfo", "math", "statistics", "collections"})
    return roots


def _root(module: str) -> str:
    return module.split(".", 1)[0]


def _is_allowed_module(module: str) -> bool:
    return bool(module) and (_root(module) in _stdlib_roots() or any(module == prefix or module.startswith(prefix + ".") for prefix in ALLOWED_SRC_PREFIXES))


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parts = [node.attr]; value = node.value
        while isinstance(value, ast.Attribute):
            parts.append(value.attr); value = value.value
        if isinstance(value, ast.Name):
            parts.append(value.id)
        return ".".join(reversed(parts))
    return ""


def _call_root(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        value = node.value
        while isinstance(value, ast.Attribute):
            value = value.value
        return value.id if isinstance(value, ast.Name) else ""
    return ""


class _StrategySecurityVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.issues: list[StrategyScanIssue] = []
        self.has_check_conditions = False
    def _issue(self, node: ast.AST, code: str, message: str) -> None:
        self.issues.append(StrategyScanIssue(getattr(node, "lineno", 0), code, message))
    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            module, root = alias.name, _root(alias.name)
            if root in FORBIDDEN_IMPORT_ROOTS:
                self._issue(node, "FORBIDDEN_NETWORK_IMPORT", f"network/HTTP import is forbidden: {module}")
            elif not _is_allowed_module(module):
                self._issue(node, "IMPORT_OUTSIDE_ALLOWLIST", f"import outside strategy allowlist: {module}; third-party packages are not permitted in Tier 1 strategies")
        self.generic_visit(node)
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module, root = node.module or "", _root(node.module or "")
        if node.level and not module:
            self._issue(node, "RELATIVE_IMPORT_FORBIDDEN", "relative imports are forbidden in uploaded strategies")
        elif root in FORBIDDEN_IMPORT_ROOTS:
            self._issue(node, "FORBIDDEN_NETWORK_IMPORT", f"network/HTTP import is forbidden: {module}")
        elif not _is_allowed_module(module):
            self._issue(node, "IMPORT_OUTSIDE_ALLOWLIST", f"import outside strategy allowlist: {module}; third-party packages are not permitted in Tier 1 strategies")
        self.generic_visit(node)
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.has_check_conditions |= node.name == "check_conditions"; self.generic_visit(node)
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.has_check_conditions |= node.name == "check_conditions"; self.generic_visit(node)
    def visit_Call(self, node: ast.Call) -> None:
        name, root = _call_name(node.func), _call_root(node.func)
        attr = name.rsplit(".", 1)[-1] if name else ""
        if root in FORBIDDEN_IMPORT_ROOTS:
            self._issue(node, "FORBIDDEN_NETWORK_CALL", f"network call is forbidden: {name}")
        elif name in FORBIDDEN_CALL_NAMES or attr in FORBIDDEN_CALL_NAMES:
            self._issue(node, "FORBIDDEN_IO_CALL", f"I/O or dynamic execution call is forbidden: {name}")
        elif attr in FORBIDDEN_ATTRS:
            self._issue(node, "FORBIDDEN_IO_CALL", f"network-style call is forbidden: {name}")
        elif name.startswith("fetch_") or attr.startswith("fetch_"):
            self._issue(node, "FORBIDDEN_DATA_FETCH", f"strategy must not fetch data directly: {name}")
        self.generic_visit(node)


def scan_strategy_source(source: str, *, filename: str = "<strategy>") -> StrategyScanResult:
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as exc:
        return StrategyScanResult(False, (StrategyScanIssue(exc.lineno or 0, "SYNTAX_ERROR", exc.msg),))
    visitor = _StrategySecurityVisitor(); visitor.visit(tree)
    if not visitor.has_check_conditions:
        visitor.issues.append(StrategyScanIssue(0, "MISSING_CHECK_CONDITIONS", "strategy must define check_conditions"))
    return StrategyScanResult(not visitor.issues, tuple(visitor.issues))


def scan_strategy_file(path: str | Path) -> StrategyScanResult:
    file_path = Path(path)
    return scan_strategy_source(file_path.read_text(encoding="utf-8"), filename=str(file_path))
