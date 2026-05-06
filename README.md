# IDS Project

## Setup

Make sure you have your environment ready, then install dependencies:

```bash
uv sync
```

This will install everything from the `pyproject.toml`.

---

## Run the Pipeline

Start the main IDS pipeline:

```bash
python pipeline.py
```

---

## Simulate Attacks

In a separate terminal, run the attack simulator:

```bash
python burstSim.py
```

---

## Notes

* Both should run at the same time to see detection in action.
* Make sure ports / configs match between the pipeline and simulator.

---
