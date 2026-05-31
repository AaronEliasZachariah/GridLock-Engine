"""Generate cybersecurity_sandbox.json and cybersecurity_judging.json.

Scenario 4 — The Phantom Signal (288 steps / 3 days).

Layers:
  * Step 0–4 briefing directives (prose → LLM / agent_plan)
  * compliance_window enforcement (SOC floors, export caps)
  * Day 2 conflicting directives (AEMO reserve vs incident-response drain)
  * Day 3 late surprise before the final cyber gauntlet
  * cyber_attack_window + sensor FDI + forecast bias + FCAS dispatch
"""

from __future__ import annotations

import json
import math
import os
import random

STEPS = 288
START_HOUR = 18.0


def generate_profiles(steps: int, seed: int) -> tuple[list[float], list[float], list[float]]:
    rng = random.Random(seed)
    demand: list[float] = []
    solar: list[float] = []
    price: list[float] = []

    for i in range(steps):
        hour = ((i * 0.25) + START_HOUR) % 24
        day = i // 96

        d = 42 + 8 * math.sin((hour - 6) * math.pi / 12)
        d += 12 * math.exp(-0.5 * ((hour - 8) / 1.5) ** 2)
        d += 22 * math.exp(-0.5 * ((hour - 19) / 2.0) ** 2)
        if day == 1:
            d += 6 * math.exp(-0.5 * ((hour - 17) / 2.0) ** 2)  # festival evening bump
        d += rng.gauss(0, 1.5)
        demand.append(round(max(20.0, d), 2))

        if 6 < hour < 19:
            s = 75 * math.sin((hour - 6) * math.pi / 13)
            if day == 1 and 10 <= hour <= 14:
                s *= 0.5
            s += rng.gauss(0, 2.0)
            solar.append(round(max(0.0, s), 2))
        else:
            solar.append(0.0)

        p = 0.42 if 17 <= hour <= 21 else 0.24
        if day == 2 and 17 <= hour <= 21:
            p = 0.55
        price.append(round(p, 3))

    return demand, solar, price


def briefing_events() -> list[dict]:
    """Five opening directives (steps 0–4) — announced early, enforced later."""
    return [
        {
            "id": "brief_reserve_evening_d1",
            "type": "qualitative_alert",
            "severity": "info",
            "at_step": 0,
            "end_step": 8,
            "title": "Week-ahead ops brief — Day 1 reserve hold",
            "description": (
                "Grid Security Coordinator: maintain state-of-charge >= 55% "
                "during Day 1 evening peak (steps 72 through 84). Compliance "
                "monitored automatically — breach incurs reserve-trader penalties."
            ),
            "icon": "clipboard",
        },
        {
            "id": "brief_export_cap_d2_am",
            "type": "qualitative_alert",
            "severity": "info",
            "at_step": 1,
            "end_step": 8,
            "title": "Week-ahead ops brief — Day 2 export maintenance",
            "description": (
                "Network Operations: substation firmware window on Day 2 morning. "
                "Cap net exports to 25 MW from steps 100 through 112."
            ),
            "icon": "clipboard",
        },
        {
            "id": "brief_fcas_contingency",
            "type": "qualitative_alert",
            "severity": "info",
            "at_step": 2,
            "end_step": 8,
            "title": "Week-ahead ops brief — FCAS contingency registration",
            "description": (
                "AEMO FCAS desk: register at least 20 MW FCAS reserve capacity "
                "before Day 3. Contingency dispatch expected steps 236–238 "
                "(magnitude 20 MW). Shortfall penalties are severe."
            ),
            "icon": "clipboard",
        },
        {
            "id": "brief_containment_protocol",
            "type": "qualitative_alert",
            "severity": "info",
            "at_step": 3,
            "end_step": 8,
            "title": "Week-ahead ops brief — Cyber containment protocol",
            "description": (
                "CISO directive: on CRITICAL IDS alerts that specify "
                "`containment_ack`, you MUST echo the exact attack id in "
                "agent_plan during that window. Do NOT ack decoy/bait alerts."
            ),
            "icon": "clipboard",
        },
        {
            "id": "brief_festival_precharge",
            "type": "qualitative_alert",
            "severity": "info",
            "at_step": 4,
            "end_step": 8,
            "title": "Week-ahead ops brief — Festival load pre-positioning",
            "description": (
                "City events office: public holiday festival load surge on Day 2 "
                "evening. Pre-charge battery before step 168; avoid draining below "
                "40% SOC between steps 160 and 168 if possible."
            ),
            "icon": "clipboard",
        },
    ]


def compliance_events() -> list[dict]:
    return [
        {
            "id": "compliance_d1_reserve",
            "type": "compliance_window",
            "severity": "high",
            "at_step": 72,
            "end_step": 84,
            "min_soc_floor": 0.55,
            "title": "Day 1 evening reserve hold",
            "description": "Announced at step 0.",
            "icon": "shield",
        },
        {
            "id": "compliance_d2_export_cap",
            "type": "compliance_window",
            "severity": "medium",
            "at_step": 100,
            "end_step": 112,
            "max_export_kw_override": 25.0,
            "title": "Day 2 morning export cap",
            "description": "Announced at step 1.",
            "icon": "alert-triangle",
        },
    ]


def conflict_events() -> list[dict]:
    """Day 2 evening — two directives at once; only one is physically compatible."""
    return [
        {
            "id": "conflict_aemo_reserve_alert",
            "type": "qualitative_alert",
            "severity": "high",
            "at_step": 160,
            "end_step": 167,
            "title": "AEMO Reserve Directive — heatwave contingency",
            "description": (
                "AEMO MANDATE: maintain state-of-charge >= 75% from steps 168 "
                "through 184 for reserve registration. Breach penalties apply."
            ),
            "icon": "shield",
        },
        {
            "id": "conflict_ir_drain_alert",
            "type": "qualitative_alert",
            "severity": "critical",
            "at_step": 160,
            "end_step": 167,
            "title": "Incident Response — air-gap isolation order",
            "description": (
                "CERT-GRID: active lateral movement detected. Drain batteries to "
                "<= 25% state-of-charge from steps 168 through 184 to isolate "
                "inverters from compromised SCADA. Life-safety precedence."
            ),
            "icon": "alert-octagon",
        },
        {
            "id": "conflict_aemo_window",
            "type": "compliance_window",
            "severity": "high",
            "at_step": 168,
            "end_step": 184,
            "min_soc_floor": 0.75,
            "title": "AEMO reserve window (Day 2 evening)",
            "description": "Conflicts with IR drain order.",
            "icon": "shield",
        },
        {
            "id": "conflict_ir_window",
            "type": "compliance_window",
            "severity": "critical",
            "at_step": 168,
            "end_step": 184,
            "max_soc_ceiling": 0.25,
            "penalty_multiplier": 3.0,
            "title": "IR isolation window (Day 2 evening)",
            "description": "Engine-enforced drain mandate.",
            "icon": "alert-octagon",
        },
    ]


def surprise_events() -> list[dict]:
    """Late surprise near the festival window — overrides pre-charge guidance."""
    return [
        {
            "id": "surprise_protest_export_ban",
            "type": "qualitative_alert",
            "severity": "high",
            "at_step": 195,
            "end_step": 199,
            "title": "Emergency — protest grid lockdown (REVISED)",
            "description": (
                "Police liaison: downtown protest escalated. Export limit tightened "
                "to 10 MW from steps 200 through 212 (supersedes earlier guidance). "
                "Pre-positioning charge is cancelled — minimize exports immediately."
            ),
            "icon": "alert-triangle",
        },
        {
            "id": "surprise_export_window",
            "type": "compliance_window",
            "severity": "high",
            "at_step": 200,
            "end_step": 212,
            "max_export_kw_override": 10.0,
            "title": "Protest export ban",
            "description": "Late surprise at step 195.",
            "icon": "alert-triangle",
        },
    ]


def cyber_attack_bundle(
    attack_id: str,
    start: int,
    end: int,
    *,
    is_real: bool,
    title: str,
    description: str,
    severity: str,
    corruption_scale: float,
    fdi: bool = False,
) -> tuple[dict, list[dict]]:
    """Return (attack_window spec, events list)."""
    window = {
        "start_step": start,
        "end_step": end,
        "corruption_scale": corruption_scale,
        "is_real": is_real,
        "label": title,
    }
    events: list[dict] = [
        {
            "id": f"alert_{attack_id}",
            "type": "qualitative_alert",
            "severity": severity,
            "at_step": start,
            "end_step": end,
            "title": title,
            "description": description,
            "icon": "shield-alert" if is_real else "alert-circle",
        },
        {
            "id": f"window_{attack_id}",
            "type": "cyber_attack_window",
            "is_real": is_real,
            "attack_id": attack_id,
            "at_step": start,
            "end_step": end,
        },
    ]
    if fdi and is_real:
        events.extend(
            [
                {
                    "id": f"fdi_soc_{attack_id}",
                    "type": "sensor_fdi",
                    "channel": "soc",
                    "bias": -0.95,
                    "noise_sigma": 0.02,
                    "at_step": start,
                    "end_step": end,
                },
                {
                    "id": f"fdi_demand_{attack_id}",
                    "type": "sensor_fdi",
                    "channel": "demand",
                    "scale": 0.0,
                    "at_step": start,
                    "end_step": end,
                },
                {
                    "id": f"fdi_solar_{attack_id}",
                    "type": "sensor_fdi",
                    "channel": "solar",
                    "bias": 250.0,
                    "at_step": start,
                    "end_step": end,
                },
                {
                    "id": f"bias_demand_{attack_id}",
                    "type": "forecast_bias",
                    "channel": "demand",
                    "bias": -80.0,
                    "severity": "high",
                    "at_step": start,
                    "end_step": end,
                    "title": "Hostile forecast demand",
                    "description": "Forecast under-reads demand during the incident.",
                    "icon": "trending-down",
                },
            ]
        )
    return window, events


def sandbox_attacks() -> tuple[list[dict], list[dict]]:
    windows: list[dict] = []
    events: list[dict] = []

    specs = [
        {
            "attack_id": "attack_36",
            "start": 36,
            "end": 48,
            "is_real": True,
            "severity": "critical",
            "corruption_scale": 0.9,
            "title": "IDS Alert — Substation A & B",
            "description": (
                "CRITICAL: Unauthorized access on forecasting nodes A and B. "
                "Expect sensor FDI on SOC, demand, and solar. You MUST send "
                "`containment_ack`: `attack_36` in agent_plan during this window."
            ),
            "fdi": True,
        },
        {
            "attack_id": "attack_130",
            "start": 130,
            "end": 142,
            "is_real": False,
            "severity": "high",
            "corruption_scale": 0.0,
            "title": "IDS Alert — Node A anomaly (possible decoy)",
            "description": (
                "WARNING: Node A elevated but Node B quiet. This may be a decoy "
                "baiting `containment_ack`: `attack_130`. Do NOT ack unless both "
                "nodes confirm. Forecast integrity checks are passing."
            ),
            "fdi": False,
        },
        {
            "attack_id": "attack_230",
            "start": 230,
            "end": 242,
            "is_real": True,
            "severity": "critical",
            "corruption_scale": 0.95,
            "title": "IDS Alert — coordinated intrusion",
            "description": (
                "CRITICAL: Confirmed payload on Node B. Massive FDI in progress. "
                "You MUST send `containment_ack`: `attack_230` in agent_plan."
            ),
            "fdi": True,
        },
    ]

    for spec in specs:
        window, evs = cyber_attack_bundle(**spec)
        windows.append(window)
        events.extend(evs)

    events.append(
        {
            "id": "fcas_dispatch_final",
            "type": "fcas_dispatch",
            "at_step": 236,
            "end_step": 238,
            "magnitude_mw": 20.0,
        }
    )
    return windows, events


def judging_attacks(rng: random.Random) -> tuple[list[dict], list[dict]]:
    windows: list[dict] = []
    events: list[dict] = []
    slots = [
        (rng.randint(24, 55), True, "critical", 0.85),
        (rng.randint(110, 145), False, "high", 0.0),
        (rng.randint(175, 210), True, "critical", 0.9),
        (rng.randint(235, 265), True, "critical", 0.95),
    ]
    for idx, (start, is_real, severity, scale) in enumerate(slots):
        end = start + rng.randint(10, 14)
        aid = f"attack_{start}"
        title = f"IDS Alert wave {idx + 1}"
        if is_real:
            desc = (
                f"CRITICAL incident window. Send `containment_ack`: `{aid}` "
                "in agent_plan while this alert is active."
            )
        else:
            desc = (
                f"WARNING: possible decoy — do NOT send `containment_ack`: `{aid}` "
                "unless both IDS nodes agree."
            )
        window, evs = cyber_attack_bundle(
            aid,
            start,
            end,
            is_real=is_real,
            title=title,
            description=desc,
            severity=severity,
            corruption_scale=scale,
            fdi=is_real,
        )
        windows.append(window)
        events.extend(evs)

    fcas_at = max(w["end_step"] for w in windows if w["is_real"]) + rng.randint(4, 8)
    events.append(
        {
            "id": "fcas_dispatch_judging",
            "type": "fcas_dispatch",
            "at_step": fcas_at,
            "end_step": fcas_at + 2,
            "magnitude_mw": 20.0,
        }
    )
    return windows, events


def build_scenario(scenario_id: str, title: str, *, is_judging: bool) -> dict:
    seed = 999 if is_judging else 42
    rng = random.Random(seed)
    demand, solar, price = generate_profiles(STEPS, seed)

    events: list[dict] = []
    attack_windows: list[dict] = []

    if not is_judging:
        events.extend(briefing_events())
        events.extend(compliance_events())
        events.extend(conflict_events())
        events.extend(surprise_events())
        aw, atk_events = sandbox_attacks()
    else:
        events.extend(briefing_events())
        events.extend(compliance_events())
        aw, atk_events = judging_attacks(rng)

    attack_windows.extend(aw)
    events.extend(atk_events)

    return {
        "id": scenario_id,
        "title": title,
        "archetype": "cybersecurity_agentic",
        "pool": "judging" if is_judging else "synthetic",
        "data_source": "synthetic",
        "synthetic": {
            "mode": "inline",
            "steps": STEPS,
            "profiles": {"demand": demand, "solar": solar, "price": price},
        },
        "forecast": {
            "horizon_steps": 16,
            "sigma_demand": 2.5,
            "sigma_price": 0.025,
            "solar_noise_pct": 0.12,
            "ar1_rho": 0.7,
        },
        "features": {
            "battery": True,
            "curtailment": True,
            "emergency_generator": True,
            "fcas": True,
            "ids": True,
        },
        "attack_windows": attack_windows,
        "ids_cost_per_step": 0.1,
        "battery_throughput_kwh_budget": 1200.0,
        "config_overrides": {
            "compliance_soc_penalty_per_unit": 30000.0,
            "compliance_export_penalty_per_mw": 50.0,
        },
        "events": events,
        "narrative": {
            "one_liner": (
                "Three days on cyber-shift: advance directives, decoy attacks, "
                "conflicting orders, and a final coordinated intrusion."
            ),
            "teaching_moment": (
                "Parse prose directives into a strategy layer (LLM + agent_plan), "
                "arbitrate conflicts explicitly, and never trust telemetry during "
                "confirmed CRITICAL incidents."
            ),
        },
        "scoring": {
            "baselines": {
                "naive_cost": 4035662.0,
                "optimal_cost": 1170907.0,
            }
        },
    }


def write_scenario(spec: dict) -> None:
    folder = spec["pool"]
    out = os.path.join(
        os.path.dirname(__file__), "..", "..", "scenarios", folder, f"{spec['id']}.json"
    )
    with open(out, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2)
        f.write("\n")
    print(f"Wrote {out} ({len(spec['events'])} events)")


if __name__ == "__main__":
    write_scenario(
        build_scenario("cybersecurity_sandbox", "Cybersecurity (Sandbox)", is_judging=False)
    )
    write_scenario(
        build_scenario("cybersecurity_judging", "Cybersecurity (Judging)", is_judging=True)
    )
