# Watt The Hack Engine

The simulation engine for the **Watt The Hack** energy grid hackathon (DeepNeuron).

This is the public engine package — controllers, scenarios authoring, and the judging server live in private repos. Participants use this package to develop and test their controllers locally before submitting to the hackathon evaluation server.

## Install

```bash
pip install git+https://github.com/AaronEliasZachariah/Watt-The-Hack-Engine-Public.git
```

Scenarios are released incrementally through package updates. Whenever the
organisers announce a new public scenario, update the engine before playtesting:

```bash
pip install --upgrade --force-reinstall git+https://github.com/AaronEliasZachariah/Watt-The-Hack-Engine-Public.git
```

This public release includes one starter scenario:

```bash
python -m watt_the_hack.playtest --list-scenarios
```

Expected first scenario:

```text
t1_welcome  tutorial  Tutorial 1: The Basics
```

## Quick start

Create `strategy.py`:

```python
def controller(state):
    return {
        "battery_flow_mw": 0.0,
        "emergency_generator": 0.0,
        "curtail_solar": 0.0,
        "fcas_reserve_mw": 0.0,
    }
```

Then run the local playtest harness:

```bash
python -m watt_the_hack.playtest strategy.py --scenario t1_welcome --open-report
```

## What's in here

- `watt_the_hack/engine/` — physics + market step
- `watt_the_hack/metrics/` — scoring metrics
- `watt_the_hack/simulation/` — runner glue
- `watt_the_hack/controllers/` — reference controllers (rule-based, parametric)
- `watt_the_hack/data_loaders/` — scenario loading utilities

## License

MIT
