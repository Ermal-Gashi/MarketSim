"""
End-to-end SSE pipeline test.

Run with (server must already be running on port 8000):
    .venv\\Scripts\\python -m backend.tests.test_pipeline
"""
import json
import sys

import httpx

BASE_URL = "http://localhost:8000"

SIMULATE_PARAMS = {
    "product_description": (
        "A project management SaaS tool for remote teams that integrates with "
        "Slack and automates task assignment"
    ),
    "current_market": "United States",
    "target_market": "Brazil",
}


def check_pipeline() -> bool:
    print("\n--- Full Pipeline SSE Test ---")
    print(f"Target: {BASE_URL}/api/simulate")
    print(f"Params: target_market=Brazil, current_market=United States\n")

    completed_agents: set[int] = set()
    final_event: dict | None = None
    checks: dict[str, bool] = {}

    try:
        with httpx.Client(timeout=300) as client:
            with client.stream(
                "GET",
                f"{BASE_URL}/api/simulate",
                params=SIMULATE_PARAMS,
            ) as response:
                response.raise_for_status()

                for raw_line in response.iter_lines():
                    line = raw_line.strip()
                    if not line.startswith("data:"):
                        continue

                    payload_str = line[len("data:"):].strip()
                    try:
                        event = json.loads(payload_str)
                    except json.JSONDecodeError as exc:
                        print(f"  [WARN] Could not parse SSE line: {exc}")
                        continue

                    agent_num = event.get("agent")
                    name = event.get("name", "?")
                    status = event.get("status", "?")

                    if agent_num:
                        prefix = f"[Agent {agent_num} — {name}]"
                        if status == "running":
                            print(f"  {prefix} running...")
                        elif status == "done":
                            output = event.get("output", {})
                            top_keys = list(output.keys()) if isinstance(output, dict) else []
                            print(f"  {prefix} done — output keys: {top_keys}")
                            completed_agents.add(agent_num)
                            if event.get("final"):
                                final_event = event
                        elif status == "error":
                            print(f"  {prefix} ERROR: {event.get('message')}")
                    else:
                        # Validation error or other non-agent event
                        print(f"  [Event] {event}")

    except httpx.ConnectError:
        print("[FAIL] Could not connect to server. Is it running on port 8000?")
        return False
    except httpx.TimeoutException:
        print("[FAIL] Request timed out after 300 seconds.")
        return False
    except Exception as exc:
        print(f"[FAIL] Unexpected error: {type(exc).__name__}: {exc}")
        return False

    print()

    # Check 1 — all 7 agents completed
    checks["all_7_agents_completed"] = completed_agents == {1, 2, 3, 4, 5, 6, 7}
    if checks["all_7_agents_completed"]:
        print("  [PASS] All 7 agents completed")
    else:
        missing = {1, 2, 3, 4, 5, 6, 7} - completed_agents
        print(f"  [FAIL] Missing agents: {sorted(missing)}")

    # Check 2 — final event has final: true
    checks["final_event_received"] = final_event is not None and final_event.get("final") is True
    if checks["final_event_received"]:
        print("  [PASS] Final event received with final=true")
    else:
        print("  [FAIL] No final event with final=true")

    # Check 3 — complete_report key present
    complete_report = final_event.get("complete_report") if final_event else None
    checks["complete_report_present"] = isinstance(complete_report, dict)
    if checks["complete_report_present"]:
        print("  [PASS] complete_report key present")
    else:
        print("  [FAIL] complete_report missing or not a dict")

    # Check 4 — complete_report contains all expected keys
    expected_report_keys = {
        "agent1_output", "agent2_output", "agent3_output",
        "agent4_output", "agent5_output", "agent6_output", "agent7_output",
        "target_market", "current_market", "product_description",
    }
    if isinstance(complete_report, dict):
        present_keys = set(complete_report.keys())
        missing_keys = expected_report_keys - present_keys
        checks["complete_report_keys"] = len(missing_keys) == 0
        if checks["complete_report_keys"]:
            print("  [PASS] complete_report contains all expected keys")
        else:
            print(f"  [FAIL] complete_report missing keys: {sorted(missing_keys)}")
    else:
        checks["complete_report_keys"] = False
        print("  [FAIL] complete_report missing keys: (complete_report not available)")

    # Check 5 — agent6_output contains verdict, regional_weights, radar_scores
    agent6 = complete_report.get("agent6_output", {}) if isinstance(complete_report, dict) else {}
    required_a6 = {"verdict", "regional_weights", "radar_scores"}
    missing_a6 = required_a6 - set(agent6.keys())
    checks["agent6_required_fields"] = len(missing_a6) == 0
    if checks["agent6_required_fields"]:
        verdict = agent6.get("verdict")
        print(f"  [PASS] agent6_output has verdict/regional_weights/radar_scores (verdict={verdict})")
    else:
        print(f"  [FAIL] agent6_output missing: {sorted(missing_a6)}")

    # Check 6 — agent7_output contains instances and summary
    agent7 = complete_report.get("agent7_output", {}) if isinstance(complete_report, dict) else {}
    required_a7 = {"instances", "summary"}
    missing_a7 = required_a7 - set(agent7.keys())
    checks["agent7_required_fields"] = len(missing_a7) == 0
    if checks["agent7_required_fields"]:
        print("  [PASS] agent7_output has instances and summary")
    else:
        print(f"  [FAIL] agent7_output missing: {sorted(missing_a7)}")

    # Check 7 — agent7.summary.total == 200
    summary = agent7.get("summary", {}) if isinstance(agent7, dict) else {}
    total = summary.get("total")
    checks["agent7_200_instances"] = total == 200
    if checks["agent7_200_instances"]:
        conversion_rate = summary.get("conversion_rate", "?")
        print(f"  [PASS] agent7 summary.total=200 (conversion_rate={conversion_rate}%)")
    else:
        print(f"  [FAIL] agent7 summary.total={total}, expected 200")

    # Final summary
    passed = sum(1 for v in checks.values() if v)
    total_checks = len(checks)
    print(f"\n{'=' * 50}")
    if passed == total_checks:
        print(f"[PASS] All {total_checks} checks passed.")
    else:
        print(f"[FAIL] {passed}/{total_checks} checks passed.")
        for name, result in checks.items():
            status_str = "PASS" if result else "FAIL"
            print(f"  [{status_str}] {name}")

    return passed == total_checks


def check_validation() -> bool:
    print("\n--- Validation Error Test ---")
    print("Sending empty product_description — expecting error event\n")

    try:
        with httpx.Client(timeout=15) as client:
            with client.stream(
                "GET",
                f"{BASE_URL}/api/simulate",
                params={
                    "product_description": "",
                    "current_market": "United States",
                    "target_market": "Brazil",
                },
            ) as response:
                response.raise_for_status()
                event: dict | None = None
                for raw_line in response.iter_lines():
                    line = raw_line.strip()
                    if line.startswith("data:"):
                        payload_str = line[len("data:"):].strip()
                        try:
                            event = json.loads(payload_str)
                        except json.JSONDecodeError:
                            pass
                        break  # only need first event

    except httpx.ConnectError:
        print("[FAIL] Could not connect to server. Is it running on port 8000?")
        return False
    except Exception as exc:
        print(f"[FAIL] Unexpected error: {type(exc).__name__}: {exc}")
        return False

    checks: dict[str, bool] = {}

    checks["error_status"] = isinstance(event, dict) and event.get("status") == "error"
    if checks["error_status"]:
        print(f"  [PASS] status=error (message: {event.get('message')})")
    else:
        print(f"  [FAIL] expected status=error, got: {event}")

    message = event.get("message", "") if isinstance(event, dict) else ""
    checks["message_mentions_field"] = "product_description" in message
    if checks["message_mentions_field"]:
        print(f"  [PASS] message mentions 'product_description'")
    else:
        print(f"  [FAIL] message does not mention 'product_description': '{message}'")

    passed = sum(1 for v in checks.values() if v)
    total_checks = len(checks)
    print(f"\n{'=' * 50}")
    if passed == total_checks:
        print(f"[PASS] All {total_checks} validation checks passed.")
    else:
        print(f"[FAIL] {passed}/{total_checks} validation checks passed.")

    return passed == total_checks


if __name__ == "__main__":
    results = [check_validation(), check_pipeline()]
    print(f"\n{'=' * 50}")
    print(f"Overall: {'PASS' if all(results) else 'FAIL'}")
    sys.exit(0 if all(results) else 1)
