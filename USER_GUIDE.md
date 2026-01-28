# Akeso / Kubecuro User Guide

**Akeso** is a high-fidelity Kubernetes manifest healer and diagnostics tool.  
It identifies logical errors, deprecated APIs, and security risks—then fixes them automatically.

## 🚀 Installation

### 1. Build & Install (Recommended)
This method installs the binary to `~/.local/bin` (or `/usr/local/bin` if run with sudo) so you can run `akeso` from anywhere.

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Build & Auto-Install
python3 build.py
```
*Note: Ensure `~/.local/bin` is in your `$PATH`.*

### 2. Autocompletion Setup
Enable tab-completion for commands and flags:

**Bash / Zsh:**
```bash
# Add to ~/.bashrc or ~/.zshrc
source <(akeso completion bash)
```

**PowerShell:**
```powershell
akeso completion powershell | Out-String | Invoke-Expression
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

### 1. Scan (Read-Only)
Audit your manifests without making changes.
*   **Default Behavior:** Returns `Exit Code 1` if issues are found.
*   **Multi-Target:** Can scan specific files, directories, or a mix of both.

```bash
# Scan current directory (Implicit recursive)
akeso scan .

# Scan specific files
akeso scan deployment.yaml service.yaml

# Mixed mode (Files & Dirs) - Batch Reporting
akeso scan ./prod-manifests/ ./new-service.yaml

# Scan from stdin (CI/CD pipeline)
cat deployment.yaml | akeso scan -
```

**Report Modes:**
*   **Detailed View:** Automatically shown when scanning a single file.
*   **Summary Table:** Automatically shown when scanning multiple targets.

### 2. Heal (Fix Issues)
Automatically repair syntax, logic, and style issues.

```bash
# Interactive Mode (Single File) - Shows diff & asks for confirmation
akeso heal deployment.yaml

# Batch Mode (Multi-Target) - Global Confirmation
akeso heal ./manifests/ file1.yaml file2.yaml

# Dry Run (Preview changes without writing)
akeso heal . --dry-run
```

**Safety Interlocks:**
*   **Interactive Mode:** Used when healing a single file. Shows visual diff. Defaults to "No".
*   **Batch Mode:** Used when healing multiple files or directories. Shows summary table. Requires typing `CONFIRM`.

### 3. Initialize Project
Create a default configuration file (`.akeso.yaml`):
```bash
akeso init
```

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

**Q: "Missing Required Argument: path"**
A: `akeso scan` and `akeso heal` are strict. You must specify a target (e.g., `akeso scan .`).

**Q: My CI pipeline passes even when files are broken?**
A: Ensure you are using `akeso scan`, which returns Exit Code 1 on failure.

**Q: How do I upgrade to Pro?**
A: Run `akeso auth --login <LICENSE_KEY>` to activate Kubecuro Enterprise features.
