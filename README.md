# ipynb_to_pdf

A lightweight desktop app for batch-converting Jupyter Notebooks to PDF.

## What It Does

Pick one or more `.ipynb` files, choose an output folder, and click convert. The app wraps `jupyter nbconvert --to pdf` in a simple GUI. Conversion runs in a background thread so the window stays responsive, and output streams into a live log.

## 🖥️ UI

The interface is a single window with three buttons (select files, select output directory, convert) and a scrollable text area that shows real-time conversion output.

## 🛠️ Tech Stack

| | Component | Role |
|---|---|---|
| 🐍 | Python 3 | Runtime |
| 🖼️ | PyQt5 | Desktop GUI — file dialogs, buttons, layout |
| 📓 | jupyter nbconvert | Notebook → PDF conversion (via subprocess) |
| 📄 | LaTeX | Required by nbconvert's PDF pipeline |

Single-file app — `main.py` (~160 lines).

## 📦 Dependencies

- Python 3.8+
- A working LaTeX installation (`xelatex` or `pdflatex`)
- System libs for PyQt5 (Linux: `libxcb`, `libgl1`, etc.)

## 🚀 Install & Run

```bash
git clone https://github.com/stabgan/ipynb_to_pdf.git
cd ipynb_to_pdf
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

Or use the helper script (creates the venv for you):

```bash
chmod +x ipynb_to_pdf.sh
./ipynb_to_pdf.sh
```

## ⚠️ Known Issues

- PyQt5 is no longer actively developed (PyQt6 is current). Wheels may not build on newer Python versions or Apple Silicon without extra steps.
- LaTeX must be installed system-wide. If missing, nbconvert will fail — the app surfaces this as a clear error dialog instead of crashing silently.
- No automated tests beyond flake8 linting in CI.

## 📄 License

MIT — see [LICENSE](LICENSE).
