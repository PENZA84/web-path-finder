# web-path-finder
Python web path fuzzing tool designed to discover hidden directories, files, and exposed sensitive endpoints


## Features

- **Multi-threaded scanning** using `ThreadPoolExecutor` for fast execution
- **Size formatting** (B, KB, MB, GB)
- **Sensitive file detection** (`.env`, `.git`, `config`, `backup`, etc.)
- **Custom User-Agent** to avoid basic bot-detection
- **Export results** to a text file (`-o`)
- **Automatic protocol validation** (adds `http://` if missing)
- **Clean output formatting** with aligned columns
- **Configurable timeout and thread count**

---

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library modules)

---

## Installation

```bash
git clone https://github.com/your-username/web-path-finder.git
cd web-path-finder
```

---

## Examples

### Basic Scan

```bash
python dir_fuzz.py http://example.com -w common.txt
```

### Scan with custom threads and timeout

```bash
python dir_fuzz.py http://example.com -w common.txt -th 50 -t 5
```

### Save results to a file

```bash
python dir_fuzz.py http://example.com -w common.txt -o results.txt
```

---

## ⚠️ Disclaimer

This tool is provided for **authorized security testing and educational purposes**.

- Only use this tool on systems **you own** or **have explicit written permission** to test.
- Unauthorized access to computer systems is **illegal** and punishable by law.
- The author is not responsible for any misuse or damage caused by this software.

Use responsibly.