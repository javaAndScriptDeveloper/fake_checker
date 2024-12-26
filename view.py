import os
import sys
import random  # For generating mock ratings
from pathlib import Path
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QComboBox, QTextEdit, QPushButton, QLabel,
    QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView
)
from core.enums import PLATFORM_TYPE
from dal.dal import Source
from main import process, get_sources_with_ratings, get_sources

cold_start_texts = [
    {
        "path": "/home/vampir/lolitech/dissertation/data/den_braun.txt",
        "source_id": 1
    },
    {
        "path": "/home/vampir/lolitech/dissertation/data/palannik.txt",
        "source_id": 2
    },
    {
        "path": "/home/vampir/lolitech/dissertation/data/putler.txt",
        "source_id": 3
    },
    {
        "path": "/home/vampir/lolitech/dissertation/data/dugin.txt",
        "source_id": 4
    },
    {
        "path": "/home/vampir/lolitech/dissertation/data/lavrov.txt",
        "source_id": 5
    },
    {
        "path": "/home/vampir/lolitech/dissertation/data/puthin-west-threat.txt",
        "source_id": 6
    },
    {
        "path": "/home/vampir/lolitech/dissertation/data/math.txt",
        "source_id": 7
    },
    {
        "path": "/home/vampir/lolitech/dissertation/data/center-harward-football-match.txt",
        "source_id": 8
    },
    {
        "path": "/home/vampir/lolitech/dissertation/data/touchdown.txt",
        "source_id": 9
    },
    {
        "path": "/home/vampir/lolitech/dissertation/data/yak.txt",
        "source_id": 10
    },
    {
        "path": "/home/vampir/lolitech/dissertation/data/trump-speech.txt",
        "source_id": 11
    },
    {
        "path": "/home/vampir/lolitech/dissertation/data/number-theory.txt",
        "source_id": 12
    },
    {
        "path": "/home/vampir/lolitech/dissertation/data/kennedy-goodwill-tour.txt",
        "source_id": 13
    },
    {
        "path": "/home/vampir/lolitech/dissertation/data/ross-mihara.txt",
        "source_id": 14
    },
    {
        "path": "/home/vampir/lolitech/dissertation/data/hariss-confession.txt",
        "source_id": 15
    },
    {
        "path": "/home/vampir/lolitech/dissertation/data/scott-ritter.txt",
        "source_id": 16
    },
    {
        "path": "/home/vampir/lolitech/dissertation/data/eva-vlaar.txt",
        "source_id": 17
    },
    {
        "path": "/home/vampir/lolitech/dissertation/data/rothshields.txt",
        "source_id": 18
    },
    {
        "path": "/home/vampir/lolitech/dissertation/data/wicked-gladiator.txt",
        "source_id": 19
    },
    {
        "path": "/home/vampir/lolitech/dissertation/data/nova-scotia.txt",
        "source_id": 20
    }
]

def read_file_from_root(absolute_path):
    if os.path.isabs(absolute_path) and os.path.isfile(absolute_path):
        with open(absolute_path, 'r', encoding='utf-8') as file:
            return file.read()
    else:
        raise FileNotFoundError(f"File not found at: {absolute_path}")


class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Propaganda Checker App')
        self.setGeometry(100, 100, 600, 400)

        # Sample data for the sources dropdown
        self.sources = get_sources()
        # Main layout
        self.layout = QVBoxLayout()

        # Tab widget for switching between tabs
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # First tab for text processing
        self.tab_process = QWidget()
        self.init_process_tab()
        self.tabs.addTab(self.tab_process, "Text Processor")

        # Second tab for result visualization in a table
        self.tab_table = QWidget()
        self.init_table_tab()
        self.tabs.addTab(self.tab_table, "Result Table")

        # Third tab for ratings
        self.tab_ratings = QWidget()
        self.init_ratings_tab()
        self.tabs.addTab(self.tab_ratings, "Ratings")

        # Prepopulate the table with data on startup
        self.prepopulate_table()

        # Set the main layout to the window
        self.setLayout(self.layout)

        # Set up a timer for updating ratings every 5 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ratings)
        self.timer.start(5000)  # Update every 5 seconds

    def init_process_tab(self):
        process_layout = QVBoxLayout()

        # Dropdown and label layout
        dropdown_layout = QHBoxLayout()
        self.label = QLabel('Select Source:')
        dropdown_layout.addWidget(self.label)

        # Dropdown for selecting source
        self.dropdown = QComboBox()
        for source in self.sources:
            self.dropdown.addItem(f'{source.name} ({source.platform})', source.id)
        dropdown_layout.addWidget(self.dropdown)

        # Add dropdown layout to the process layout
        process_layout.addLayout(dropdown_layout)

        # Large text box for input
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter your text here...")
        self.text_input.setFixedWidth(400)
        self.text_input.setLineWrapMode(QTextEdit.WidgetWidth)
        self.text_input.setFixedHeight(100)
        process_layout.addWidget(self.text_input)

        # Process button
        self.process_button = QPushButton('Process')
        self.process_button.clicked.connect(self.process_data)
        process_layout.addWidget(self.process_button)

        # Result view for displaying the result
        self.result_view = QTextEdit()
        self.result_view.setReadOnly(True)
        self.result_view.setFixedWidth(400)
        process_layout.addWidget(self.result_view)

        # Set layout for this tab
        self.tab_process.setLayout(process_layout)

    def init_table_tab(self):
        table_layout = QVBoxLayout()

        # Table widget to display results
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(14)  # Adding 1 new column for the color
        self.result_table.setHorizontalHeaderLabels([
            "Source", "Text Data",
            "Sentimental Score", "Triggered Keywords", "Triggered Topics", "Text Simplicity",
            "Confidence Factor", "Clickbait", "Subjective", "Call to Action",
            "Repeated Take", "Repeated Note", "Total Score", "Is Propaganda"
        ])

        # Set the header to resize the columns to fit contents
        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        table_layout.addWidget(self.result_table)

        # Set layout for this tab
        self.tab_table.setLayout(table_layout)

    def init_ratings_tab(self):
        ratings_layout = QVBoxLayout()

        # Table widget to display ratings
        self.ratings_table = QTableWidget()
        self.ratings_table.setColumnCount(2)  # Two columns: Name and Rating
        self.ratings_table.setHorizontalHeaderLabels(["Name", "Rating"])

        # Set the header to resize the columns to fit contents
        header = self.ratings_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        ratings_layout.addWidget(self.ratings_table)

        # Set layout for this tab
        self.tab_ratings.setLayout(ratings_layout)

    def process_data(self):
        # Get the selected source id
        source_id = self.dropdown.currentData()

        # Get the text from the text input
        input_text = self.text_input.toPlainText()

        # Call the processing function
        _, calculation_object = process(input_text, source_id)

        # Determine if the input is from the cold start list
        is_cold_start = input_text in [read_file_from_root(path["path"])[:20] for path in cold_start_texts]

        # Update the text view with the result in HTML format
        result_text = f"""
            Sentimental Score: {calculation_object['sentimental_score']}%<br>
            Triggered Keywords: {calculation_object['triggered_keywords']}%<br>
            Triggered Topics: {calculation_object['triggered_topics']}%<br>
            Text Simplicity Deviation: {calculation_object['text_simplicity_deviation']}%<br>
            Confidence Factor: {calculation_object['confidence_factor']}%<br>
            Clickbait: {calculation_object['clickbait']}%<br>
            Subjective: {calculation_object['subjective']}%<br>
            Call to Action: {calculation_object['call_to_action']}%<br>
            Repeated Take: {calculation_object['repeated_take']}%<br>
            Repeated Note: {calculation_object['repeated_note']}%<br>
            <b>Total Score: {calculation_object['total_score']}%</b>
            """
        self.result_view.setHtml(result_text)

        # Populate the table with the result data
        self.add_result_to_table(input_text[:20], calculation_object, is_cold_start)

    def add_result_to_table(self, text_data, result, is_cold_start):
        # Add a new row to the table
        row_position = self.result_table.rowCount()
        self.result_table.insertRow(row_position)

        # Add the color column
        color_item = QTableWidgetItem()
        color_item.setBackground(QColor("blue" if is_cold_start else "green"))
        self.result_table.setItem(row_position, 0, color_item)

        # Populate the row with the result data
        self.result_table.setItem(row_position, 1, QTableWidgetItem(text_data))  # Text Data column
        self.result_table.setItem(row_position, 2, QTableWidgetItem(f"{result['sentimental_score']}%"))
        self.result_table.setItem(row_position, 3, QTableWidgetItem(f"{result['triggered_keywords']}%"))
        self.result_table.setItem(row_position, 4, QTableWidgetItem(f"{result['triggered_topics']}%"))
        self.result_table.setItem(row_position, 5, QTableWidgetItem(f"{result['text_simplicity_deviation']}%"))
        self.result_table.setItem(row_position, 6, QTableWidgetItem(f"{result['confidence_factor']}%"))
        self.result_table.setItem(row_position, 7, QTableWidgetItem(f"{result['clickbait']}%"))
        self.result_table.setItem(row_position, 8, QTableWidgetItem(f"{result['subjective']}%"))
        self.result_table.setItem(row_position, 9, QTableWidgetItem(f"{result['call_to_action']}%"))
        self.result_table.setItem(row_position, 10, QTableWidgetItem(f"{result['repeated_take']}%"))
        self.result_table.setItem(row_position, 11, QTableWidgetItem(f"{result['repeated_note']}%"))
        self.result_table.setItem(row_position, 12, QTableWidgetItem(f"{result['total_score']}%"))
        self.result_table.setItem(row_position, 13, QTableWidgetItem(f"{result['is_propaganda']}%"))

    def prepopulate_table(self):
        for i in cold_start_texts:
            text = read_file_from_root(i["path"])
            self.add_result_to_table(text[:40], process(text, i["source_id"])[1], True)

    def update_ratings(self):
        data = get_sources_with_ratings()

        # Clear existing ratings
        self.ratings_table.setRowCount(0)

        # Populate the table with new mock data
        for item in data:
            row_position = self.ratings_table.rowCount()
            self.ratings_table.insertRow(row_position)
            self.ratings_table.setItem(row_position, 0, QTableWidgetItem(item.name))
            self.ratings_table.setItem(row_position, 1, QTableWidgetItem(f"{data[item]:.2f}"))

        # Sort by rating column (index 1)
        self.sort_table_by_rating()

    def sort_table_by_rating(self):
        self.ratings_table.sortItems(1, order=0)  # Sort by rating (ascending)


# Application initialization
app = QApplication(sys.argv)
demo = AppDemo()
demo.show()
sys.exit(app.exec_())
