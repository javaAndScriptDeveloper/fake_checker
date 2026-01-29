import os
import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QComboBox, QTextEdit, QPushButton, QLabel,
    QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QSpacerItem, QSizePolicy
)
from PyQt5 import QtGui

from manager import Manager
from singletons import manager


class AppDemo(QWidget):
    def __init__(self, manager: Manager):
        super().__init__()
        self.manager = manager
        self.translator = self.manager.translator
        self.current_language = "ukrainian"

        self.setWindowTitle(self.tr("window_title"))
        self.setGeometry(100, 100, 600, 400)

        self.sources = self.manager.get_visible_sources()
        self.layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.tab_process = QWidget()
        self.init_process_tab()
        self.tabs.addTab(self.tab_process, self.tr("tab_process"))

        self.tab_table = QWidget()
        self.init_table_tab()
        self.tabs.addTab(self.tab_table, self.tr("tab_table"))

        self.tab_ratings = QWidget()
        self.init_ratings_tab()
        self.tabs.addTab(self.tab_ratings, self.tr("tab_ratings"))

        self.tab_system_info = QWidget()
        self.init_system_info_tab()
        self.tabs.addTab(self.tab_system_info, self.tr("tab_system_info"))

        self.setLayout(self.layout)

        self.total_score_color_dict = [
            {'range': (0.51, 1), 'color': QtGui.QColor(255, 102, 102)}, # red
            {'range': (0.31, 0.5), 'color': QtGui.QColor(255, 255, 102)}, # yellow
            {'range': (0, 0.3), 'color': QtGui.QColor(144, 238, 144)} # green
        ]

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ratings)
        self.timer.start(5000)

    def tr(self, key: str) -> str:
        return self.translator.get_ui_text(key, self.current_language)

    def on_language_changed(self, index: int):
        self.current_language = self.language_dropdown.currentData()
        self.update_ui_texts()

    def update_ui_texts(self):
        self.setWindowTitle(self.tr("window_title"))
        self.tabs.setTabText(0, self.tr("tab_process"))
        self.tabs.setTabText(1, self.tr("tab_table"))
        self.tabs.setTabText(2, self.tr("tab_ratings"))
        self.tabs.setTabText(3, self.tr("tab_system_info"))
        self.source_label.setText(self.tr("select_source"))
        self.language_label.setText(self.tr("select_language"))
        self.title_input.setPlaceholderText(self.tr("title_placeholder"))
        self.text_input.setPlaceholderText(self.tr("text_placeholder"))
        self.process_button.setText(self.tr("process_button"))
        self.export_button.setText(self.tr("export_csv"))
        self.fechner_label.setText(self.tr("fehner_score"))
        self.result_table.setHorizontalHeaderLabels(self.get_table_headers())
        self.ratings_table.setHorizontalHeaderLabels([self.tr("name"), self.tr("rating")])

    def get_table_headers(self):
        return [
            self.tr("source"), self.tr("text_data"),
            self.tr("sentimental_score"), self.tr("triggered_keywords"),
            self.tr("triggered_topics"), self.tr("text_simplicity"),
            self.tr("confidence_factor"), self.tr("clickbait"),
            self.tr("subjective"), self.tr("call_to_action"),
            self.tr("repeated_take"), self.tr("repeated_note"),
            self.tr("total_score"), self.tr("is_propaganda")
        ]

    def init_process_tab(self):
        process_layout = QVBoxLayout()

        dropdown_layout = QHBoxLayout()
        self.source_label = QLabel(self.tr("select_source"))
        dropdown_layout.addWidget(self.source_label)

        self.dropdown = QComboBox()
        for source in self.sources:
            self.dropdown.addItem(f'{source.name} ({source.platform})', source.id)
        dropdown_layout.addWidget(self.dropdown)

        self.language_label = QLabel(self.tr("select_language"))
        dropdown_layout.addWidget(self.language_label)

        self.language_dropdown = QComboBox()
        for language in self.manager.get_available_translations():
            self.language_dropdown.addItem(language['label'], language['value'])
        self.language_dropdown.setCurrentIndex(0)
        self.language_dropdown.currentIndexChanged.connect(self.on_language_changed)
        dropdown_layout.addWidget(self.language_dropdown)

        process_layout.addLayout(dropdown_layout)

        self.title_input = QTextEdit()
        self.title_input.setPlaceholderText(self.tr("title_placeholder"))
        self.title_input.setFixedWidth(400)
        self.title_input.setFixedHeight(40)
        self.title_input.setLineWrapMode(QTextEdit.WidgetWidth)
        process_layout.addWidget(self.title_input)

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(self.tr("text_placeholder"))
        self.text_input.setFixedWidth(400)
        self.text_input.setFixedHeight(100)
        self.text_input.setLineWrapMode(QTextEdit.WidgetWidth)
        process_layout.addWidget(self.text_input)

        self.process_button = QPushButton(self.tr("process_button"))
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
        self.result_table.setHorizontalHeaderLabels(self.get_table_headers())
        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        table_layout.addWidget(self.result_table)

        button_layout = QHBoxLayout()
        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.export_button = QPushButton(self.tr("export_csv"))
        self.export_button.clicked.connect(self.export_to_csv)
        button_layout.addWidget(self.export_button)

        table_layout.addLayout(button_layout)

        self.tab_table.setLayout(table_layout)

    def init_ratings_tab(self):
        ratings_layout = QVBoxLayout()
        self.ratings_table = QTableWidget()
        self.ratings_table.setColumnCount(2)
        self.ratings_table.setHorizontalHeaderLabels([self.tr("name"), self.tr("rating")])
        header = self.ratings_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        ratings_layout.addWidget(self.ratings_table)
        self.tab_ratings.setLayout(ratings_layout)

    def init_system_info_tab(self):
        system_info_layout = QVBoxLayout()
        self.fechner_label = QLabel(self.tr("fehner_score"))
        self.fechner_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        system_info_layout.addWidget(self.fechner_label)

        self.fechner_score_value = QLabel(self.tr("calculating"))
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
        language = self.language_dropdown.currentData()

        note = self.manager.process(title, input_text, source_id, language)

        result_text = f"""
            {self.tr("sentimental_score")}: {note.sentimental_score}%<br>
            {self.tr("triggered_keywords")}: {note.triggered_keywords}%<br>
            {self.tr("triggered_topics")}: {note.triggered_topics}%<br>
            {self.tr("text_simplicity_deviation")}: {note.text_simplicity_deviation}%<br>
            {self.tr("confidence_factor")}: {note.confidence_factor}%<br>
            {self.tr("clickbait")}: {note.clickbait}%<br>
            {self.tr("subjective")}: {note.subjective}%<br>
            {self.tr("call_to_action")}: {note.call_to_action}%<br>
            {self.tr("repeated_take")}: {note.repeated_take}%<br>
            {self.tr("repeated_note")}: {note.repeated_note}%<br>
            <b>{self.tr("total_score")}: {note.total_score}%</b>
            """
        self.result_view.setHtml(result_text)

        self.add_result_to_table(input_text[:20], note)

    def add_result_to_table(self, text_data, note):
        row_position = self.result_table.rowCount()
        self.result_table.insertRow(row_position)

        source = next((s for s in self.sources if s.id == note.source_id), None)

        self.result_table.setItem(row_position, 0, QTableWidgetItem(source.name))
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

        total_score_item = QTableWidgetItem(f"{note.total_score}%")
        self.apply_color_to_score(total_score_item, note.total_score)
        self.result_table.setItem(row_position, 12, total_score_item)

        self.result_table.setItem(row_position, 13, QTableWidgetItem(f"{note.is_propaganda}%"))

    def apply_color_to_score(self, item, score):
        for i in self.total_score_color_dict:
            lower, upper = i['range']
            if lower < score < upper:
                item.setBackground(i['color'])
                break

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

    def export_to_csv(self):
        data = []
        row_count = self.result_table.rowCount()
        col_count = self.result_table.columnCount()
        headers = [self.result_table.horizontalHeaderItem(i).text() for i in range(col_count)]
        data.append(headers)

        for row in range(row_count):
            row_data = []
            for col in range(col_count):
                item = self.result_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        try:
            self.manager.export_results_to_csv(data)
        except Exception as e:
            print(f"CSV export failed: {e}")
