# ipynb_to_pdf

A simple desktop GUI for batch-converting Jupyter Notebooks (`.ipynb`) to PDF.

## What It Does

Wraps `jupyter nbconvert --to pdf` in a PyQt5 desktop window. You pick one or more `.ipynb` files, choose an output directory, and hit convert. Conversion runs in a background thread so the UI stays responsive. Logs stream into a text box in real time.

## Tech Stack

| Component | Role |
|---|---|
| **Python 3** | Runtime |
| **PyQt5** | Desktop GUI (file dialogs, buttons, layout) |
| **jupyter nbconvert** | Actual notebook → PDF conversion (called via `subprocess`) |
| **LaTeX** (system) | Required by nbconvert's PDF pipeline |

The app is a single file — `main.py` (~90 lines). A helper shell script (`ipynb_to_pdf.sh`) activates a virtualenv, installs deps, and launches the app.

## Requirements

- Python 3.8+ (developed on 3.11)
- A working LaTeX installation (`xelatex` or `pdflatex`) — required by `jupyter nbconvert --to pdf`
- System dependencies for PyQt5 (on Linux: `libxcb`, `libgl1`, etc.)

## Install & Run

```bash
git clone https://github.com/stabgan/ipynb_to_pdf.git
cd ipynb_to_pdf
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

Or use the bundled script (does the same thing):

```bash
./ipynb_to_pdf.sh
```

## Known Issues & Notes

- **`venv/` is committed to the repo.** The entire virtual environment (~400 MB, 15k+ files) is tracked in git. There is no `.gitignore`. This massively bloats the repo and should be removed from version control.
- **PyQt5 is effectively deprecated.** PyQt5 is no longer actively developed; PyQt6 is the current version. PyQt5 wheels may not build on newer Python versions or Apple Silicon without extra steps.
- **No error handling for missing LaTeX.** If LaTeX is not installed, `nbconvert` will fail at runtime with an opaque subprocess error. The app doesn't surface this clearly.
- **No error handling for missing output directory.** If you click "Convert" without selecting an output directory, the app will crash with an `AttributeError` (`self.output_dir` is never set).
- **No `.gitignore`.** Python bytecache (`__pycache__`), venv, `error_log.txt`, and OS files are not excluded.
- **CI runs lint only.** The GitHub Actions workflow installs deps and runs `flake8` but has no tests and doesn't verify the app actually launches.
- **Shell script assumes `./venv` exists.** `ipynb_to_pdf.sh` sources `./venv/bin/activate` but never creates the venv first — it only works because the venv is committed.

## License

MIT — see [LICENSE](LICENSE).
