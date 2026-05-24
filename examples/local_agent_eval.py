"""
Local Agent Evaluation Example
==============================

This script demonstrates how to test a complex, class-based controller (like an LLM agent)
locally without submitting to the cloud leaderboard. 

It loads a specific scenario (e.g. 'duck_curve'), runs the backtest engine, and prints 
the final score and metrics immediately.

Usage:
  1. Make sure you have cloned the Watt-The-Hack-Engine-Public repository.
  2. Run `pip install -e .` in the repository root to install the engine.
  3. Ensure you have the `openai` package installed if you are using the OpenAI API.
  4. Run this script: `python examples/local_agent_eval.py`
"""

import os
import json
from watt_the_hack.simulation.runner import run_simulation
from watt_the_hack.data_loaders.scenarios import load_scenario, find_scenario_by_id

# ---------------------------------------------------------------------------
# 1. Define your Agentic Controller
# ---------------------------------------------------------------------------
class Strategy:
    def __init__(self):
        # Initialize any state, history, or API clients here.
        # Since this runs locally, you can use your real API key.
        self.api_key = os.environ.get("OPENAI_API_KEY", "your-api-key-here")
        self.target_soc = 0.5
        self.history = []

    def plan(self, state: dict) -> dict:
        """
        Called once at the very beginning of the scenario.
        Use this to make an expensive LLM call to read the scenario briefing 
        and decide on a high-level strategy for the run.
        """
        briefing = state.get("qualitative_briefing", "")
        print(f"\n[Agent] Reading briefing: {briefing}")
        
        # Simulated LLM logic: 
        # response = openai.chat.completions.create(...)
        
        # We decide our strategy and return it in 'agent_plan'.
        # This plan will be injected into every subsequent state step!
        self.target_soc = 0.8
        print(f"[Agent] Decided on target SOC: {self.target_soc}\n")
        
        return {"agent_plan": {"target_soc": self.target_soc}}

    def replan(self, state: dict, alerts: list) -> dict:
        """
        Called only when a mid-run 'qualitative_alert' event occurs (e.g. unexpected weather).
        Use this to make another LLM call to adjust your strategy.
        """
        print(f"\n[Agent] ALERT RECEIVED! Replanning... Alerts: {alerts}")
        self.target_soc = 0.2
        return {"agent_plan": {"target_soc": self.target_soc}}

    def step(self, state: dict) -> dict:
        """
        Called every 15-minute simulation step.
        This must be fast! No LLM calls here. Read the plan and execute it.
        """
        plan = state.get("agent_plan", {})
        target = plan.get("target_soc", self.target_soc)
        current_soc = state.get("soc", 0.0)
        
        # Save state history just to demonstrate we can!
        self.history.append(current_soc)
        
        flow = 0.0
        if current_soc < target - 0.05:
            flow = -50.0  # charge
        elif current_soc > target + 0.05:
            flow = 50.0   # discharge
            
        return {
            "battery_flow_kw": flow,
            "emergency_generator": 0.0,
            "curtail_solar": 0.0,
            "fcas_reserve_kw": 0.0
        }

# ---------------------------------------------------------------------------
# 2. Run the Local Simulation
# ---------------------------------------------------------------------------
def main():
    scenario_id = "duck_curve"
    print(f"Loading scenario: {scenario_id}")
    
    # Locate and load the scenario JSON
    scenario_path = find_scenario_by_id(scenario_id)
    if not scenario_path:
        print(f"Error: Could not find scenario '{scenario_id}' in the scenarios/ folder.")
        return
        
    spec, initial_state = load_scenario(scenario_path)
    
    # Run the backtest using the runner
    print("Starting simulation...")
    
    # We must instantiate the strategy ourselves for local testing,
    # and pass its .step method (and manually call .plan if we want to simulate the cloud environment exactly).
    
    strategy = Strategy()
    
    # 2a. Call the plan hook (the cloud platform does this automatically)
    if hasattr(strategy, "plan"):
        plan_result = strategy.plan(initial_state)
        if isinstance(plan_result, dict):
            initial_state.update(plan_result)
            
    # 2b. We create a wrapper to handle the replan hook mid-simulation,
    # just like the cloud eval_worker does. The runner passes us the
    # controller view, which contains a redacted state["alerts"] list
    # of qualitative alerts firing this step — no need to filter the raw
    # event list (which is engine-private and not visible here).
    def controller_wrapper(state):
        alerts = state.get("alerts", [])
        if alerts and hasattr(strategy, "replan"):
            update = strategy.replan(state, alerts)
            if isinstance(update, dict):
                state["agent_plan"] = {**state.get("agent_plan", {}), **update.get("agent_plan", {})}

        return strategy.step(state)

    # 2c. Run the simulation. Read the run length from the private
    # `_profiles_full` key — only the test harness sees this; controllers
    # receive Engine.controller_view(state) and never see the full series.
    result = run_simulation(
        controller=controller_wrapper,
        initial_state=initial_state,
        steps=len(initial_state.get("_profiles_full", {}).get("demand", []))
    )
    
    print("\n✅ Simulation Complete!")
    print("\n--- Final Metrics ---")
    print(json.dumps(result["metrics"], indent=2))
    print(f"\nFinal Score: ${result['metrics']['final_score']:.2f}")

if __name__ == "__main__":
    main()
