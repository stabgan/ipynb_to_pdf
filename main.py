import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal
import subprocess


class ConversionThread(QThread):
    output = pyqtSignal(str)
    completed = pyqtSignal()

    def __init__(self, files, output_dir):
        super().__init__()
        self.files = files
        self.output_dir = output_dir

    def run(self):
        for file in self.files:
            process = subprocess.Popen(['jupyter', 'nbconvert', '--to', 'pdf', '--output-dir', self.output_dir, file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in iter(process.stdout.readline, b''):
                self.output.emit(line.decode('utf-8'))
        self.completed.emit()  # Emit the completed signal when done


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Convert Jupyter notebook to pdf')

        # Create a QVBoxLayout instance
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create QPushButton instances
        select_files_btn = QPushButton('Select .ipynb files', self)
        select_files_btn.clicked.connect(self.select_files)

        select_output_dir_btn = QPushButton('Select output directory', self)
        select_output_dir_btn.clicked.connect(self.select_output_dir)

        self.convert_btn = QPushButton('Convert to .pdf', self)
        self.convert_btn.clicked.connect(self.convert)
        self.convert_btn.setEnabled(False)  # Disable until files are selected

        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)

        # Add widgets to the layout
        layout.addWidget(select_files_btn)
        layout.addWidget(select_output_dir_btn)
        layout.addWidget(self.convert_btn)
        layout.addWidget(self.output_box)

        self.show()

    def select_files(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        files, _ = QFileDialog.getOpenFileNames(self, "Select one or more files to open", "",
                                                "Jupyter Notebooks (*.ipynb);;All Files (*)", options=options)
        if files:
            self.files = files
            self.convert_btn.setEnabled(True)  # Enable the convert button

    def select_output_dir(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        output_dir = QFileDialog.getExistingDirectory(self, "Select output directory", "", options=options)
        if output_dir:
            self.output_dir = output_dir

    def convert(self):
        if hasattr(self, 'files') and hasattr(self, 'output_dir'):
            self.thread = ConversionThread(self.files, self.output_dir)
            self.thread.output.connect(self.output_box.append)
            self.thread.completed.connect(self.on_completed)  # Connect the completed signal to on_completed slot
            self.thread.start()

    def on_completed(self):
        self.output_box.append("Conversion completed!")


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        ex = MyApp()
        sys.exit(app.exec_())
    except Exception as e:
        with open('error_log.txt', 'w') as f:
            f.write(str(e))

