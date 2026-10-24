# CSScope Analyzer + AgentWorks Tool Lab

A local-first Streamlit dashboard with two independent Python packages:

- **CSScope Analyzer** parses CSS with `tinycss2`. It accepts uploaded files or pasted source; reports selectors, declarations, comments, custom properties, media queries, keyframes, at-rules, parse errors, and non-fatal warnings; and exports JSON.
- **AgentWorks Tool Lab** provides a deterministic, rule-based tool router with a safe arithmetic calculator, text utilities, and a CSS file inspector. It does not use an external AI service or require an API key.
- AgentWorks presents each run as a task-specific answer card: equations and answers for calculations, counts and a readable snapshot for text, or key stylesheet metrics for CSS inspection. Full structured output and a JSON download are available when needed.

## Requirements

- Windows 10 or 11
- Python 3.10 or newer
- VS Code with the Python extension (recommended)

## Setup in Windows PowerShell

Open this project folder in VS Code. In its terminal, run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks virtual-environment activation, allow it for the current terminal only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Run automated tests

```powershell
python -m pytest -v
```

## Launch the dashboard

```powershell
python -m streamlit run app.py
```

Streamlit prints a local URL (normally `http://localhost:8501`) to open in your browser. Use the sidebar to switch between the two milestones.

## Project layout

```text
CSScope_AgentWorks/
├── app.py                     # Combined Streamlit UI
├── csscope/
│   ├── parser.py               # Parsing and statistics
│   └── reports.py              # Text and JSON reports
├── agentworks/
│   ├── tools.py                # Safe calculator, text, CSS tools
│   ├── registry.py             # Tool catalog
│   └── controller.py           # Rule-based routing and history
├── tests/                      # Automated tests for both milestones
├── examples/sample_requests.md
├── sample_styles.css
├── requirements.txt
└── README.md
```

## Example AgentWorks requests

- `calculate 18 * (4 + 2)`
- `word count`, `character count`, or `summarize` with text in the input panel
- `inspect css` to analyze the included stylesheet

The calculator evaluates a deliberately restricted arithmetic syntax tree; it never calls `eval` or executes user code. File inspection is restricted to explicitly selected CSS files or files under the dedicated sample directory. Tool results use a consistent success/data/error structure.
