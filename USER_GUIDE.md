# Akeso / Kubecuro User Guide

**Akeso** is a high-fidelity Kubernetes manifest healer and diagnostics tool.  
It identifies logical errors, deprecated APIs, and security risks—then fixes them automatically.

## 🚀 Installation

### 1. Zero-Install (Python directly)
If you have Python 3.8+ installed:
```bash
pip install -r requirements.txt
python -m akeso.cli.main --help
```

### 2. Autocompletion Setup (Recommended)
Enable tab-completion for commands and flags:

**PowerShell:**
```powershell
akeso completion powershell | Out-String | Invoke-Expression
```

**Bash (Linux):**
```bash
source <(akeso completion bash)
```

**Zsh (Mac):**
```zsh
autoload -U +X bashcompinit && bashcompinit
source <(akeso completion zsh)
```

---

## 🎭 Dual Identity
This tool has two modes depending on how you call it:

| Command | Identity | Description |
| :--- | :--- | :--- |
| **`akeso`** | **OSS Mode** | Free for life. Infinite scans. Best-effort healing. |
| **`kubecuro`** | **Pro Mode** | Requires license. Unlocks security hardening & compliance reports. |

*Note: Both commands are aliases for the same underlying engine.*

---

## 🛠️ Core Commands

### 1. Initialize Project
Create a default configuration file (`.akeso.yaml`):
```bash
akeso init
```

### 2. Scan (Read-Only)
Audit your manifests without making changes. Returns `Exit Code 1` if issues found.
```bash
# Scan a directory
akeso scan ./k8s-manifests

# Scan with visual diffs (Preview fixes)
akeso scan ./k8s-manifests --diff

# Scan from stdin (CI/CD pipeline)
cat deployment.yaml | akeso scan -
```

### 3. Heal (Fix Issues)
Automatically repair syntax, logic, and style issues.

```bash
# Preview changes (Dry Run) - Returns Exit Code 1 if changes needed
akeso heal ./k8s-manifests --dry-run

# Interactive Mode (Safe) - Asks for confirmation
akeso heal ./k8s-manifests

# Automated Mode (CI/CD) - Force apply changes
akeso heal ./k8s-manifests --yes-all
```

**Safety Interlocks:**
*   **Single File:** Shows a side-by-side diff and asks `Apply changes? [y/N]`
*   **Directory:** Requires you to type `CONFIRM` to proceed.

### 4. Explain Rules
Get detailed documentation for any violation ID.
```bash
akeso explain rules/no-latest-tag
```

---

## ⚙️ Configuration (`.akeso.yaml`)
Customize behavior globally or per-project.

```yaml
rules:
  threshold: 80         # fail if health score < 80
  
ignore:
  files:
    - "vendor/**"       # Ignore third-party charts
    - "tests/*.yaml"
```

## 🆘 Troubleshooting

**Q: I see "Command not found"**
A: Ensure the `src` directory is in your `PYTHONPATH` or run via `python -m akeso.cli.main`.

**Q: My CI pipeline passes even when files are broken?**
A: Ensure you are using `akeso scan` (which now correctly returns Exit Code 1 on failure).

**Q: How do I upgrade to Pro?**
A: Run `akeso auth --login <LICENSE_KEY>` to activate Kubecuro Enterprise features.
