import sys

from PyQt5.QtGui import QTextOption
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QTextEdit, QPushButton, QLabel, QHBoxLayout

from core.enums import PLATFORM_TYPE
from dal.dal import Source
from main import process

class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Propaganda Checker App')
        self.setGeometry(100, 100, 600, 400)

        # Sample data for the sources dropdown
        self.sources = [
            Source(id=1, name='1', external_id="1", platform=PLATFORM_TYPE.TELEGRAM.name)
        ]

        # Main layout
        self.layout = QVBoxLayout()

        # Dropdown and label layout
        dropdown_layout = QHBoxLayout()

        self.label = QLabel('Select Source:')
        dropdown_layout.addWidget(self.label)

        # Dropdown for selecting source
        self.dropdown = QComboBox()
        for source in self.sources:
            self.dropdown.addItem(f'{source.name} ({source.platform})', source.id)
        dropdown_layout.addWidget(self.dropdown)

        # Add dropdown layout to the main layout
        self.layout.addLayout(dropdown_layout)

        # Large text box for input
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter your text here...")

        # Set fixed width to prevent horizontal expansion and enable word wrapping
        self.text_input.setFixedWidth(400)  # Adjust this as per your desired width
        self.text_input.setLineWrapMode(QTextEdit.WidgetWidth)  # Wrap text based on widget's width

        # You can set a fixed height if necessary
        self.text_input.setFixedHeight(100)  # Adjust height as needed

        self.layout.addWidget(self.text_input)

        # Process button
        self.process_button = QPushButton('Process')
        self.process_button.clicked.connect(self.process_data)
        self.layout.addWidget(self.process_button)

        # Result view for displaying the result
        self.result_view = QTextEdit()
        self.result_view.setReadOnly(True)
        self.result_view.setFixedWidth(400)  # Match width of the input field
        self.layout.addWidget(self.result_view)

        # Set the main layout to the window
        self.setLayout(self.layout)

    def process_data(self):
        # Get the selected source id
        source_id = self.dropdown.currentData()

        # Get the text from the text input
        input_text = self.text_input.toPlainText()

        # Call the processing function x
        result = process(input_text, source_id)

        result_text = f"""
            Sentimental Score: {result.sentimental_score}%<br>
            Triggered Keywords: {result.triggered_keywords}%<br>
            Triggered Topics: {result.triggered_topics}%<br>
            Text Simplicity Deviation: {result.text_simplicity_deviation}%<br>
            Confidence Factor: {result.confidence_factor}%<br>
            Clickbait: {result.clickbait}%<br>
            Subjective: {result.subjective}%<br>
            Call to Action: {result.call_to_action}%<br>
            Repeated Take: {result.repeated_take}%<br>
            Repeated Note: {result.repeated_note}%<br>
            <b>Total Score: {result.total_score}%</b>
            """

        # Display the result in the result view
        self.result_view.setHtml(result_text)


# Application initialization
app = QApplication(sys.argv)
demo = AppDemo()
demo.show()
sys.exit(app.exec_())