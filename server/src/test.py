import sys
import csv
import os

from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QLabel, QProgressBar
from epubtoolkit.epub import Epub


class HTMLToCSVConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.input_file_path = None
        self.output_file_path = None

    def initUI(self):
        self.setGeometry(100, 100, 500, 300)
        self.setWindowTitle('EPUB creator')

        self.input_file_label = QLabel('Input file: No file selected', self)
        self.input_file_label.move(10, 10)
        self.input_file_label.resize(480, 20)

        self.choose_input_file_button = QPushButton('Choose Input File', self)
        self.choose_input_file_button.move(10, 40)
        self.choose_input_file_button.resize(150, 30)
        self.choose_input_file_button.clicked.connect(self.choose_input_file)

        self.output_file_label = QLabel('Output file: No file selected', self)
        self.output_file_label.move(10, 80)
        self.output_file_label.resize(480, 20)

        self.choose_output_file_button = QPushButton('Choose Output Directory', self)
        self.choose_output_file_button.move(10, 110)
        self.choose_output_file_button.resize(150, 30)
        self.choose_output_file_button.clicked.connect(self.choose_output_directory)

        self.convert_button = QPushButton('Extract sentences', self)
        self.convert_button.move(10, 150)
        self.convert_button.resize(150, 30)
        self.convert_button.clicked.connect(self.extract_sentences)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(10, 190, 480, 20)
        self.progress_bar.setValue(0)

        self.show()

    def choose_input_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Input File", "", "EPUB Files *.epub",
                                                   options=options)
        if file_path:
            # Reset progress bar when new input file selected
            self.progress_bar.setValue(0)

            self.input_file_path = file_path
            self.input_file_label.setText(f'Input file: {self.input_file_path}')

    def choose_output_directory(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        directory_path = QFileDialog.getExistingDirectory(self, "Select Output Directory", options=options)
        if directory_path:
            # Set default output file name to "output.csv"
            output_file_name = "output.csv"
            self.output_file_path = os.path.join(directory_path, output_file_name)
            self.output_file_label.setText(f'Output file: {self.output_file_path}')

    def extract_sentences(self):
        if self.input_file_path:
            epub = Epub(self.input_file_path)
            epub.sync_audio()

        else:
            # Show error message if either input or output file is not selected
            error_message = 'Please select input and output files'
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setText(error_message)
            msg_box.setWindowTitle('Error')
            msg_box.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    converter = HTMLToCSVConverter()
    sys.exit(app.exec())
