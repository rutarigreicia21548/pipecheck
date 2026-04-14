# pipecheck

A CLI tool to validate and lint data pipeline configs across Airflow and Prefect formats.

---

## Installation

```bash
pip install pipecheck
```

Or install from source:

```bash
git clone https://github.com/youruser/pipecheck.git && cd pipecheck && pip install .
```

---

## Usage

Run `pipecheck` against a pipeline config file:

```bash
pipecheck validate my_dag.py --format airflow
```

```bash
pipecheck validate flow_config.yaml --format prefect
```

Lint a directory of configs:

```bash
pipecheck lint ./pipelines/ --format airflow
```

**Example output:**

```
✔  my_dag.py        — No issues found
✘  flow_config.yaml — [ERROR] Missing required field: 'schedule_interval' (line 12)
```

### Supported Formats

| Format  | File Types          |
|---------|---------------------|
| Airflow | `.py`, `.yaml`      |
| Prefect | `.yaml`, `.toml`    |

---

## Options

| Flag          | Description                        |
|---------------|------------------------------------|
| `--format`    | Pipeline format (`airflow`, `prefect`) |
| `--strict`    | Treat warnings as errors           |
| `--output`    | Output format (`text`, `json`)     |

---

## License

This project is licensed under the [MIT License](LICENSE).