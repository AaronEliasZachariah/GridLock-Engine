"""Append the leaderboard submission section to the training starter notebook."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK_PATH = REPO_ROOT / "notebooks/training_starter.ipynb"

markdown_cell = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 6. Submitting to the Leaderboard\n",
        "When you are ready to test your controller against the hidden judging scenarios ('the_gauntlet'), you will submit it to the API server. You will need your `team_id` and `team_token` provided by the hackathon organizers.\n",
        "\n",
        "We can use Python's built-in `inspect` module to automatically grab your function's source code and fire it over the internet!",
    ],
}

code_cell = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "import requests\n",
        "import inspect\n",
        "\n",
        "# 1. Write your controller (or import it from your ML pipeline)\n",
        "def my_submission_controller(state):\n",
        "    action = {\n",
        '        "battery_flow_mw": 0.0,\n',
        '        "emergency_generator": 0.0,\n',
        '        "curtail_solar": 0.0,\n',
        '        "fcas_reserve_mw": 0.0,\n',
        "    }\n",
        "    \n",
        "    # Simple strategy: charge battery when power is cheap!\n",
        '    if state.get("price", 0) < 0.10 and state.get("soc", 0) < 1.0:\n',
        '        action["battery_flow_mw"] = -20.0  # Charge\n',
        "        \n",
        "    return action\n",
        "\n",
        "# 2. Automatically grab the source code of your function\n",
        "source_code = inspect.getsource(my_submission_controller)\n",
        "\n",
        "# 3. Build the payload\n",
        "payload = {\n",
        '    "team_id": "team_alpha",\n',
        '    "team_token": "secret_abc123",\n',
        '    "scenario_id": "the_gauntlet",  # The hidden judging scenario\n',
        '    "controller": {\n',
        '        "kind": "code",\n',
        '        "source": source_code       # The server will compile and run this\n',
        "    }\n",
        "}\n",
        "\n",
        "# 4. Submit to the server\n",
        'print("Submitting to the judging server...")\n',
        'API_URL = "https://playtest.eliascorp.org/sim/run" # Change to actual endpoint \n',
        "\n",
        "try:\n",
        "    response = requests.post(API_URL, json=payload)\n",
        "    \n",
        "    # 5. Read the results\n",
        "    if response.status_code == 200:\n",
        "        result = response.json()\n",
        '        metrics = result["metrics"]\n',
        "        \n",
        '        print("\\n✅ Submission Successful!")\n',
        '        print(f"🏆 Final Leaderboard Score: {metrics[\'final_score\']:.2f}")\n',
        '        print(f"💰 Total Operational Cost: ${metrics[\'cost\']:.2f}")\n',
        '        print(f"🌿 Renewable Ratio:       {metrics[\'renewable_ratio\'] * 100:.1f}%")\n',
        "        \n",
        '        if result.get("controller_error"):\n',
        '            print(f"\\n⚠️ WARNING: Your code crashed: {result[\'controller_error\']}")\n',
        "    else:\n",
        '        print(f"\\n❌ Submission Failed (Error {response.status_code}):")\n',
        '        print(response.json().get("detail", response.text))\n',
        "except Exception as e:\n",
        '    print("❌ Connection Error:", e)\n',
    ],
}


def main() -> None:
    with open(NOTEBOOK_PATH, encoding="utf-8") as f:
        data = json.load(f)

    data["cells"].extend([markdown_cell, code_cell])

    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    print("Successfully updated notebook!")


if __name__ == "__main__":
    main()
