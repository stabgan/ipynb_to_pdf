import os
import sys
import shutil
import logging

from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QFileDialog,
    QVBoxLayout, QTextEdit, QMessageBox,
)
from PyQt5.QtCore import QThread, pyqtSignal
import subprocess

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(
    filename=os.path.join(_SCRIPT_DIR, "error_log.txt"),
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s: %(message)s",
)


class ConversionThread(QThread):
    """Runs jupyter nbconvert in a background thread."""

    output = pyqtSignal(str)
    error = pyqtSignal(str)
    completed = pyqtSignal()

    def __init__(self, files, output_dir):
        super().__init__()
        self.files = files
        self.output_dir = output_dir
        self._abort = False

    def abort(self):
        """Request the thread to stop after the current file."""
        self._abort = True

    def run(self):
        for file in self.files:
            if self._abort:
                self.output.emit("Conversion cancelled.")
                break
            try:
                process = subprocess.Popen(
                    [
                        "jupyter", "nbconvert",
                        "--to", "pdf",
                        "--no-input",
                        "--output-dir", self.output_dir,
                        file,
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                for line in iter(process.stdout.readline, b""):
                    self.output.emit(line.decode("utf-8", errors="replace"))
                process.wait()
                if process.returncode != 0:
                    self.error.emit(
                        f"nbconvert exited with code {process.returncode} for {file}"
                    )
            except FileNotFoundError:
                self.error.emit(
                    "jupyter is not installed or not on PATH. "
                    "Install it with: pip install jupyter"
                )
                return
            except Exception as exc:
                self.error.emit(f"Unexpected error converting {file}: {exc}")
        self.completed.emit()


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.files = []
        self.output_dir = ""
        self._thread = None
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Jupyter Notebook → PDF Converter")
        self.setMinimumSize(520, 380)

        layout = QVBoxLayout()
        self.setLayout(layout)

        select_files_btn = QPushButton("Select .ipynb files", self)
        select_files_btn.clicked.connect(self._select_files)

        select_output_dir_btn = QPushButton("Select output directory", self)
        select_output_dir_btn.clicked.connect(self._select_output_dir)

        self.convert_btn = QPushButton("Convert to PDF", self)
        self.convert_btn.clicked.connect(self._convert)
        self.convert_btn.setEnabled(False)

        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)

        layout.addWidget(select_files_btn)
        layout.addWidget(select_output_dir_btn)
        layout.addWidget(self.convert_btn)
        layout.addWidget(self.output_box)

        self.show()

    # ── file / dir selection ──────────────────────────────────────────

    def _select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select one or more .ipynb files",
            "",
            "Jupyter Notebooks (*.ipynb);;All Files (*)",
        )
        if files:
            self.files = files
            self.output_box.append(f"Selected {len(files)} file(s).")
            self._update_convert_btn()

    def _select_output_dir(self):
        output_dir = QFileDialog.getExistingDirectory(
            self, "Select output directory", ""
        )
        if output_dir:
            self.output_dir = output_dir
            self.output_box.append(f"Output directory: {output_dir}")
            self._update_convert_btn()

    def _update_convert_btn(self):
        self.convert_btn.setEnabled(bool(self.files and self.output_dir))

    # ── conversion ────────────────────────────────────────────────────

    def _convert(self):
        if not self.files:
            QMessageBox.warning(self, "No files", "Please select .ipynb files first.")
            return
        if not self.output_dir:
            QMessageBox.warning(
                self, "No output directory", "Please select an output directory first."
            )
            return

        # Check that jupyter is available
        if shutil.which("jupyter") is None:
            QMessageBox.critical(
                self,
                "jupyter not found",
                "The 'jupyter' command was not found on PATH.\n"
                "Install it with:  pip install jupyter",
            )
            return

        self.convert_btn.setEnabled(False)
        self.output_box.append("Starting conversion…")

        self._thread = ConversionThread(self.files, self.output_dir)
        self._thread.output.connect(self.output_box.append)
        self._thread.error.connect(self._on_error)
        self._thread.completed.connect(self._on_completed)
        self._thread.start()

    def _on_error(self, msg):
        self.output_box.append(f"ERROR: {msg}")
        logging.error(msg)

    def _on_completed(self):
        self.output_box.append("Conversion completed!")
        self.convert_btn.setEnabled(True)

    # ── cleanup ───────────────────────────────────────────────────────

    def closeEvent(self, event):
        """Stop the background thread gracefully when the window closes."""
        if self._thread is not None and self._thread.isRunning():
            self._thread.abort()
            self._thread.wait(5000)
        event.accept()


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MyApp()
        sys.exit(app.exec_())
    except Exception as exc:
        logging.exception("Fatal error")
        print(f"Fatal error: {exc}", file=sys.stderr)
        sys.exit(1)
