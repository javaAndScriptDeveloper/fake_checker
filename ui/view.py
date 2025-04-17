import os
import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QComboBox, QTextEdit, QPushButton, QLabel,
    QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView
)

from manager import Manager


class AppDemo(QWidget):
    def __init__(self, manager: Manager):
        super().__init__()
        self.setWindowTitle('Propaganda Checker App')
        self.setGeometry(100, 100, 600, 400)
        self.manager = manager

        self.sources = self.manager.get_visible_sources()
        self.layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.tab_process = QWidget()
        self.init_process_tab()
        self.tabs.addTab(self.tab_process, "Text Processor")

        self.tab_table = QWidget()
        self.init_table_tab()
        self.tabs.addTab(self.tab_table, "Result Table")

        self.tab_ratings = QWidget()
        self.init_ratings_tab()
        self.tabs.addTab(self.tab_ratings, "Ratings")

        self.tab_system_info = QWidget()
        self.init_system_info_tab()
        self.tabs.addTab(self.tab_system_info, "System Info")

        self.setLayout(self.layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ratings)
        self.timer.start(5000)

    def init_process_tab(self):
        process_layout = QVBoxLayout()

        dropdown_layout = QHBoxLayout()
        self.label = QLabel('Select Source:')
        dropdown_layout.addWidget(self.label)

        self.dropdown = QComboBox()
        for source in self.sources:
            self.dropdown.addItem(f'{source.name} ({source.platform})', source.id)
        dropdown_layout.addWidget(self.dropdown)

        process_layout.addLayout(dropdown_layout)

        # Title input
        self.title_input = QTextEdit()
        self.title_input.setPlaceholderText("Enter title here...")
        self.title_input.setFixedWidth(400)
        self.title_input.setFixedHeight(40)
        self.title_input.setLineWrapMode(QTextEdit.WidgetWidth)
        process_layout.addWidget(self.title_input)

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter your text here...")
        self.text_input.setFixedWidth(400)
        self.text_input.setLineWrapMode(QTextEdit.WidgetWidth)
        self.text_input.setFixedHeight(100)
        process_layout.addWidget(self.text_input)

        self.process_button = QPushButton('Process')
        self.process_button.clicked.connect(self.process_data)
        process_layout.addWidget(self.process_button)

        self.result_view = QTextEdit()
        self.result_view.setReadOnly(True)
        self.result_view.setFixedWidth(400)
        process_layout.addWidget(self.result_view)

        self.tab_process.setLayout(process_layout)

    def init_table_tab(self):
        table_layout = QVBoxLayout()
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(14)
        self.result_table.setHorizontalHeaderLabels([
            "Source", "Text Data",
            "Sentimental Score", "Triggered Keywords", "Triggered Topics", "Text Simplicity",
            "Confidence Factor", "Clickbait", "Subjective", "Call to Action",
            "Repeated Take", "Repeated Note", "Total Score", "Is Propaganda"
        ])
        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        table_layout.addWidget(self.result_table)
        self.tab_table.setLayout(table_layout)

    def init_ratings_tab(self):
        ratings_layout = QVBoxLayout()
        self.ratings_table = QTableWidget()
        self.ratings_table.setColumnCount(2)
        self.ratings_table.setHorizontalHeaderLabels(["Name", "Rating"])
        header = self.ratings_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        ratings_layout.addWidget(self.ratings_table)
        self.tab_ratings.setLayout(ratings_layout)

    def init_system_info_tab(self):
        system_info_layout = QVBoxLayout()
        self.fechner_label = QLabel("Fehner Score:")
        self.fechner_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        system_info_layout.addWidget(self.fechner_label)

        self.fechner_score_value = QLabel("Calculating...")
        self.fechner_score_value.setStyleSheet("font-size: 16px; color: green;")
        system_info_layout.addWidget(self.fechner_score_value)

        self.update_fehner_score()
        self.tab_system_info.setLayout(system_info_layout)

    def update_fehner_score(self):
        try:
            fehner_score = self.manager.calculate_fehner_score()
            self.fechner_score_value.setText(f"{fehner_score}")
        except Exception as e:
            self.fechner_score_value.setText(f"Error: {e}")
            print(f"Error calculating Fechner Score: {e}")

    def process_data(self):
        source_id = self.dropdown.currentData()
        title = self.title_input.toPlainText()
        input_text = self.text_input.toPlainText()

        note = self.manager.process(title, input_text, source_id)

        result_text = f"""
            Sentimental Score: {note.sentimental_score}%<br>
            Triggered Keywords: {note.triggered_keywords}%<br>
            Triggered Topics: {note.triggered_topics}%<br>
            Text Simplicity Deviation: {note.text_simplicity_deviation}%<br>
            Confidence Factor: {note.confidence_factor}%<br>
            Clickbait: {note.clickbait}%<br>
            Subjective: {note.subjective}%<br>
            Call to Action: {note.call_to_action}%<br>
            Repeated Take: {note.repeated_take}%<br>
            Repeated Note: {note.repeated_note}%<br>
            <b>Total Score: {note.total_score}%</b>
            """
        self.result_view.setHtml(result_text)

        self.add_result_to_table(input_text[:20], note)

    def add_result_to_table(self, text_data, note):
        row_position = self.result_table.rowCount()
        self.result_table.insertRow(row_position)

        color_item = QTableWidgetItem()
        self.result_table.setItem(row_position, 0, color_item)
        self.result_table.setItem(row_position, 1, QTableWidgetItem(text_data))
        self.result_table.setItem(row_position, 2, QTableWidgetItem(f"{note.sentimental_score}%"))
        self.result_table.setItem(row_position, 3, QTableWidgetItem(f"{note.triggered_keywords}%"))
        self.result_table.setItem(row_position, 4, QTableWidgetItem(f"{note.triggered_topics}%"))
        self.result_table.setItem(row_position, 5, QTableWidgetItem(f"{note.text_simplicity_deviation}%"))
        self.result_table.setItem(row_position, 6, QTableWidgetItem(f"{note.confidence_factor}%"))
        self.result_table.setItem(row_position, 7, QTableWidgetItem(f"{note.clickbait}%"))
        self.result_table.setItem(row_position, 8, QTableWidgetItem(f"{note.subjective}%"))
        self.result_table.setItem(row_position, 9, QTableWidgetItem(f"{note.call_to_action}%"))
        self.result_table.setItem(row_position, 10, QTableWidgetItem(f"{note.repeated_take}%"))
        self.result_table.setItem(row_position, 11, QTableWidgetItem(f"{note.repeated_note}%"))
        self.result_table.setItem(row_position, 12, QTableWidgetItem(f"{note.total_score}%"))
        self.result_table.setItem(row_position, 13, QTableWidgetItem(f"{note.is_propaganda}%"))

    def update_ratings(self):
        data = self.manager.get_sources_with_ratings()
        self.ratings_table.setRowCount(0)
        for item in data:
            row_position = self.ratings_table.rowCount()
            self.ratings_table.insertRow(row_position)
            self.ratings_table.setItem(row_position, 0, QTableWidgetItem(item.name))
            self.ratings_table.setItem(row_position, 1, QTableWidgetItem(f"{data[item]:.2f}"))
        self.sort_table_by_rating()

    def sort_table_by_rating(self):
        self.ratings_table.sortItems(1, order=0)
