
def test_numpy_is_rejected_with_actionable_tier1_policy_message():
    from src.strategies.security import scan_strategy_source
    result = scan_strategy_source("import numpy as np\n\ndef check_conditions(state):\n    return {}\n")
    assert result.passed is False
    assert any(issue.code == "IMPORT_OUTSIDE_ALLOWLIST" and "third-party packages" in issue.message for issue in result.issues)

def test_requests_is_rejected_with_actionable_tier1_policy_message():
    from src.strategies.security import scan_strategy_source
    result = scan_strategy_source("import requests\n\ndef check_conditions(state):\n    return {}\n")
    assert result.passed is False
    # 'requests' is in FORBIDDEN_IMPORT_ROOTS, so the scanner emits FORBIDDEN_NETWORK_IMPORT
    # (checked before the allowlist path). IMPORT_OUTSIDE_ALLOWLIST is only raised for
    # third-party packages that are not in the network-roots set (e.g. pandas, scipy).
    assert any(issue.code == "FORBIDDEN_NETWORK_IMPORT" for issue in result.issues)
