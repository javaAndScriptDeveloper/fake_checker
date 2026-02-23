import os
import sys
import tempfile
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QComboBox, QTextEdit, QPushButton, QLabel,
    QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QSpacerItem, QSizePolicy,
    QFileDialog, QMessageBox
)
from PyQt5 import QtGui

# Lazy import for QWebEngineView - may not be installed
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False
    QWebEngineView = None

from ui.charts import (
    RadarChart, HistogramChart, TemporalTrendChart,
    CorrelationHeatmap, DimensionBreakdownChart, PlatformComparisonChart,
    DIMENSION_LABEL_KEYS
)
from ui.audio_widgets import TranscriptionWorker
from manager import Manager
from singletons import manager


class AppDemo(QWidget):
    def __init__(self, manager: Manager):
        super().__init__()
        self.manager = manager
        self.translator = self.manager.translator
        self.current_language = "ukrainian"
        self.current_audio_metadata = None  # Store metadata until note is saved
        self.transcription_worker = None  # Background transcription worker

        self.setWindowTitle(self.tr("window_title"))
        self.setGeometry(100, 100, 600, 400)

        self.sources = self.manager.get_visible_sources()
        self.layout = QVBoxLayout()

        self.total_score_color_dict = [
            {'range': (0.51, 1), 'color': QtGui.QColor(255, 102, 102)}, # red
            {'range': (0.31, 0.5), 'color': QtGui.QColor(255, 255, 102)}, # yellow
            {'range': (0, 0.3), 'color': QtGui.QColor(144, 238, 144)} # green
        ]

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

        self.tab_graph = QWidget()
        self.init_graph_tab()
        self.tabs.addTab(self.tab_graph, self.tr("tab_graph"))

        self.tab_statistics = QWidget()
        self.init_statistics_tab()
        self.tabs.addTab(self.tab_statistics, self.tr("tab_statistics"))

        self.setLayout(self.layout)

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
        self.tabs.setTabText(4, self.tr("tab_graph"))
        self.tabs.setTabText(5, self.tr("tab_statistics"))
        self.source_label.setText(self.tr("select_source"))
        self.language_label.setText(self.tr("select_language"))
        self.title_input.setPlaceholderText(self.tr("title_placeholder"))
        self.text_input.setPlaceholderText(self.tr("text_placeholder"))
        self.process_button.setText(self.tr("process_button"))
        self.export_button.setText(self.tr("export_csv"))
        self.fechner_label.setText(self.tr("fehner_score"))
        self.result_table.setHorizontalHeaderLabels(self.get_table_headers())
        self.ratings_table.setHorizontalHeaderLabels([self.tr("name"), self.tr("rating")])
        self.refresh_graph_btn.setText(self.tr("refresh_graph"))
        self.graph_stats_table.setHorizontalHeaderLabels(self._get_graph_stats_headers())
        self.stats_refresh_btn.setText(self.tr("refresh_statistics"))
        self.community_btn.setText(self.tr("show_communities"))
        self.pagerank_btn.setText(self.tr("show_pagerank"))
        self.fehner_a_btn.setText(self.tr("show_fehner_a"))
        self.cascades_btn.setText(self.tr("show_cascades"))

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

        # Audio Input Section
        audio_section_layout = QVBoxLayout()

        # Section header
        audio_label = QLabel(self.tr("audio_input"))
        audio_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        audio_section_layout.addWidget(audio_label)

        # File upload button
        self.audio_upload_btn = QPushButton(self.tr("upload_audio_file"))
        self.audio_upload_btn.setFixedSize(200, 40)
        self.audio_upload_btn.clicked.connect(self.handle_audio_upload)
        audio_section_layout.addWidget(self.audio_upload_btn)

        # Status/info display
        self.audio_status_label = QLabel("")
        self.audio_status_label.setWordWrap(True)
        self.audio_status_label.setStyleSheet("color: #666; font-style: italic;")
        audio_section_layout.addWidget(self.audio_status_label)

        process_layout.addLayout(audio_section_layout)

        # Separator
        separator = QLabel("─" * 50)
        separator.setStyleSheet("color: #ccc;")
        process_layout.addWidget(separator)

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

    def init_graph_tab(self):
        """Initialize graph visualization tab."""
        graph_layout = QVBoxLayout()

        # Controls bar
        controls = QHBoxLayout()
        self.refresh_graph_btn = QPushButton(self.tr("refresh_graph"))
        self.refresh_graph_btn.clicked.connect(self.refresh_graph)
        controls.addWidget(self.refresh_graph_btn)

        self.community_btn = QPushButton(self.tr("show_communities"))
        self.community_btn.setCheckable(True)
        self.community_btn.clicked.connect(self._on_graph_overlay_changed)
        controls.addWidget(self.community_btn)

        self.pagerank_btn = QPushButton(self.tr("show_pagerank"))
        self.pagerank_btn.setCheckable(True)
        self.pagerank_btn.clicked.connect(self._on_graph_overlay_changed)
        controls.addWidget(self.pagerank_btn)

        self.fehner_a_btn = QPushButton(self.tr("show_fehner_a"))
        self.fehner_a_btn.setCheckable(True)
        self.fehner_a_btn.clicked.connect(self._on_graph_overlay_changed)
        controls.addWidget(self.fehner_a_btn)

        self.cascades_btn = QPushButton(self.tr("show_cascades"))
        self.cascades_btn.setCheckable(True)
        self.cascades_btn.clicked.connect(self._on_graph_overlay_changed)
        controls.addWidget(self.cascades_btn)

        self.graph_stats_label = QLabel()
        controls.addWidget(self.graph_stats_label)
        controls.addStretch()
        graph_layout.addLayout(controls)

        # Web view for pyvis graph (or fallback label if not available)
        if HAS_WEBENGINE:
            self.graph_view = QWebEngineView()
            graph_layout.addWidget(self.graph_view)
        else:
            self.graph_view = None
            self.graph_fallback_label = QLabel(
                "PyQtWebEngine not installed.\n"
                "Run: pip install PyQtWebEngine pyvis networkx"
            )
            self.graph_fallback_label.setStyleSheet(
                "font-size: 14px; color: #888; padding: 20px;"
            )
            graph_layout.addWidget(self.graph_fallback_label)

        # Statistics table for influential sources
        self.graph_stats_table = QTableWidget()
        self.graph_stats_table.setColumnCount(4)
        self.graph_stats_table.setHorizontalHeaderLabels(self._get_graph_stats_headers())
        header = self.graph_stats_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.graph_stats_table.setMaximumHeight(150)
        graph_layout.addWidget(self.graph_stats_table)

        self.tab_graph.setLayout(graph_layout)

        # Initial load
        self.refresh_graph()

    def _get_graph_stats_headers(self):
        """Get headers for graph statistics table."""
        return [
            self.tr("name"),
            self.tr("platform"),
            self.tr("note_count"),
            self.tr("avg_propaganda_score")
        ]

    def refresh_graph(self):
        """Refresh graph visualization."""
        # If PyQtWebEngine not installed, just update the stats table
        if not HAS_WEBENGINE or self.graph_view is None:
            self._update_graph_stats_table()
            return

        if not self.manager.is_neo4j_available():
            unavailable_html = f"""
            <html>
            <body style="background-color: #222222; color: white;
                         display: flex; justify-content: center; align-items: center;
                         height: 100vh; margin: 0; font-family: Arial, sans-serif;">
                <h2>{self.tr('graph_unavailable')}</h2>
            </body>
            </html>
            """
            self.graph_view.setHtml(unavailable_html)
            self.graph_stats_label.setText("")
            self.graph_stats_table.setRowCount(0)
            return

        data = self.manager.get_graph_network()
        if data:
            self._render_graph(data)
            self._update_graph_stats_label(data)

        self._update_graph_stats_table()

    def _render_graph(self, data: dict, overlay=None):
        """Render network using pyvis and display in QWebEngineView.

        Args:
            data: Network data with nodes and edges
            overlay: Optional dict with overlay configuration:
                - community_map: dict of source_id -> community_index
                - pagerank: dict of source_id -> pagerank score
                - fehner_a: bool to highlight Fehner A notes
                - cascades: list of cascade chain data
        """
        if not HAS_WEBENGINE or self.graph_view is None:
            return

        try:
            from pyvis.network import Network
        except ImportError:
            self.graph_view.setHtml("<h2>pyvis not installed</h2>")
            return

        net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white",
                      cdn_resources='in_line')
        net.barnes_hut(gravity=-3000, central_gravity=0.3, spring_length=200)

        overlay = overlay or {}
        community_map = overlay.get("community_map")
        pagerank = overlay.get("pagerank")
        fehner_a = overlay.get("fehner_a", False)
        cascade_data = overlay.get("cascades")

        # Community colors palette
        community_colors = [
            '#4a90d9', '#ff6666', '#66ff66', '#ffff66', '#ff66ff',
            '#66ffff', '#ff9933', '#9966ff', '#33cc33', '#cc3333',
            '#6699cc', '#cc6699', '#99cc66'
        ]

        # If cascades mode, filter to only cascade-related nodes
        cascade_node_ids = set()
        if cascade_data:
            for c in cascade_data:
                cascade_node_ids.add(f"note_{c['from_note_id']}")
                cascade_node_ids.add(f"note_{c['to_note_id']}")

        # Add nodes
        for node in data.get('nodes', []):
            if cascade_data and node['id'] not in cascade_node_ids:
                # In cascade mode, also include source nodes for visible notes
                if node['type'] == 'source':
                    # Check if any cascade note belongs to this source
                    has_cascade_note = False
                    for edge in data.get('edges', []):
                        if edge['type'] == 'PUBLISHED' and edge['to'] in cascade_node_ids and edge['from'] == node['id']:
                            has_cascade_note = True
                            break
                    if not has_cascade_note:
                        continue
                else:
                    continue

            if node['type'] == 'source':
                color = '#4a90d9'
                size = 25

                # Extract postgres_id from node id
                source_pg_id = None
                try:
                    source_pg_id = int(node['id'].replace('source_', ''))
                except (ValueError, AttributeError):
                    pass

                if community_map and source_pg_id in community_map:
                    comm_idx = community_map[source_pg_id]
                    color = community_colors[comm_idx % len(community_colors)]

                if pagerank and source_pg_id in pagerank:
                    rank = pagerank[source_pg_id]
                    size = max(15, min(60, rank * 1000))

                net.add_node(
                    node['id'],
                    label=node.get('name', 'Unknown'),
                    color=color,
                    shape='box',
                    size=size,
                    title=f"Source: {node.get('name', 'Unknown')}\nPlatform: {node.get('platform', 'N/A')}"
                )
            else:  # note
                score = node.get('total_score', 0) or 0
                color = self._score_to_color(score)
                node_size = 15

                if fehner_a and node.get('fehner_type') == 'A':
                    color = '#ff0000'
                    node_size = 22

                title_text = node.get('title', 'Untitled') or 'Untitled'
                label = title_text[:20] + '...' if len(title_text) > 20 else title_text
                title_info = f"Note: {title_text}\nScore: {score:.2f}"
                if node.get('fehner_type'):
                    title_info += f"\nFehner: {node['fehner_type']}"

                net.add_node(
                    node['id'],
                    label=label,
                    color=color,
                    shape='dot',
                    size=node_size,
                    title=title_info
                )

        # Add edges
        edges_to_add = data.get('edges', [])
        if cascade_data:
            # In cascade mode, only show REFERENCES and PUBLISHED edges for cascade nodes
            edges_to_add = [
                e for e in edges_to_add
                if e['type'] == 'REFERENCES' or
                (e['type'] == 'PUBLISHED' and e['to'] in cascade_node_ids)
            ]

        for edge in edges_to_add:
            edge_color = '#888888'
            if edge['type'] == 'PUBLISHED':
                edge_color = '#4a90d9'
            elif edge['type'] == 'REPOSTS_FROM':
                edge_color = '#ff9900'
            elif edge['type'] == 'REFERENCES':
                edge_color = '#ff6666'

            net.add_edge(
                edge['from'],
                edge['to'],
                title=edge['type'],
                color=edge_color
            )

        # Save to temp file and display
        html_path = tempfile.mktemp(suffix='.html')
        net.save_graph(html_path)
        self.graph_view.load(QUrl.fromLocalFile(html_path))

    def _score_to_color(self, score: float) -> str:
        """Convert propaganda score to color (green -> yellow -> red)."""
        if score is None:
            return '#888888'
        if score <= 0.3:
            return '#90EE90'  # Light green
        elif score <= 0.5:
            return '#FFFF66'  # Yellow
        else:
            return '#FF6666'  # Red

    def _update_graph_stats_label(self, data: dict):
        """Update the statistics label with node/edge counts."""
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        source_count = sum(1 for n in nodes if n['type'] == 'source')
        note_count = sum(1 for n in nodes if n['type'] == 'note')

        stats_text = (
            f"{self.tr('sources_label')}: {source_count} | "
            f"{self.tr('notes_label')}: {note_count} | "
            f"{self.tr('relationships_label')}: {len(edges)}"
        )
        self.graph_stats_label.setText(stats_text)

    def _update_graph_stats_table(self):
        """Update the influential sources table."""
        stats = self.manager.get_graph_statistics()
        self.graph_stats_table.setRowCount(0)

        if not stats:
            return

        for stat in stats[:10]:  # Show top 10
            row_position = self.graph_stats_table.rowCount()
            self.graph_stats_table.insertRow(row_position)
            self.graph_stats_table.setItem(row_position, 0, QTableWidgetItem(stat['name']))
            self.graph_stats_table.setItem(row_position, 1, QTableWidgetItem(stat['platform'] or 'N/A'))
            self.graph_stats_table.setItem(row_position, 2, QTableWidgetItem(str(stat['note_count'])))

            avg_score = stat.get('avg_propaganda_score', 0)
            score_item = QTableWidgetItem(f"{avg_score:.2f}")
            self.apply_color_to_score(score_item, avg_score)
            self.graph_stats_table.setItem(row_position, 3, score_item)

    def _on_graph_overlay_changed(self):
        """Handle overlay toggle button clicks — re-render graph with overlays."""
        if not HAS_WEBENGINE or self.graph_view is None:
            return
        if not self.manager.is_neo4j_available():
            return

        data = self.manager.get_graph_network()
        if not data:
            return

        overlay = {}

        if self.community_btn.isChecked():
            community_map = self.manager.compute_community_detection()
            if community_map:
                overlay["community_map"] = community_map

        if self.pagerank_btn.isChecked():
            pr_data = self.manager.compute_pagerank_and_centrality()
            if pr_data:
                overlay["pagerank"] = pr_data["pagerank"]

        if self.fehner_a_btn.isChecked():
            overlay["fehner_a"] = True

        if self.cascades_btn.isChecked():
            cascades = self.manager.get_information_cascades()
            if cascades:
                overlay["cascades"] = cascades

        self._render_graph(data, overlay)
        self._update_graph_stats_label(data)

    def init_statistics_tab(self):
        """Initialize statistics/charts tab."""
        stats_layout = QVBoxLayout()

        # Controls bar
        controls = QHBoxLayout()

        self.stats_refresh_btn = QPushButton(self.tr("refresh_statistics"))
        self.stats_refresh_btn.clicked.connect(self.refresh_statistics)
        controls.addWidget(self.stats_refresh_btn)

        self.chart_selector = QComboBox()
        self._chart_types = [
            ("radar_chart", RadarChart),
            ("histogram_chart", HistogramChart),
            ("temporal_chart", TemporalTrendChart),
            ("correlation_chart", CorrelationHeatmap),
            ("breakdown_chart", DimensionBreakdownChart),
            ("platform_chart", PlatformComparisonChart),
        ]
        for key, _ in self._chart_types:
            self.chart_selector.addItem(self.tr(key), key)
        self.chart_selector.currentIndexChanged.connect(self._on_chart_type_changed)
        controls.addWidget(self.chart_selector)

        self.stats_source_selector = QComboBox()
        self.stats_source_selector.addItem(self.tr("all_sources"), None)
        for source in self.sources:
            self.stats_source_selector.addItem(f"{source.name} ({source.platform})", source.id)
        self.stats_source_selector.currentIndexChanged.connect(self._on_stats_source_changed)
        controls.addWidget(self.stats_source_selector)

        self.stats_note_selector = QComboBox()
        self.stats_note_selector.hide()
        self.stats_note_selector.currentIndexChanged.connect(self._on_stats_note_changed)
        controls.addWidget(self.stats_note_selector)

        controls.addStretch()
        stats_layout.addLayout(controls)

        # Chart area
        self.current_chart = None
        self.chart_container = QVBoxLayout()
        stats_layout.addLayout(self.chart_container)

        # Status label
        self.stats_status_label = QLabel()
        self.stats_status_label.setStyleSheet("color: #888; padding: 4px;")
        stats_layout.addWidget(self.stats_status_label)

        self.tab_statistics.setLayout(stats_layout)

    def _get_dimension_labels(self):
        """Get localized dimension labels."""
        return [self.tr(k) for k in DIMENSION_LABEL_KEYS]

    def _on_chart_type_changed(self, index):
        """Swap chart widget and toggle selector visibility."""
        chart_key = self.chart_selector.currentData()

        # Show source selector for radar/temporal/breakdown
        needs_source = chart_key in ("radar_chart", "temporal_chart", "breakdown_chart")
        self.stats_source_selector.setVisible(needs_source)

        # Show note selector only for breakdown
        needs_note = chart_key == "breakdown_chart"
        self.stats_note_selector.setVisible(needs_note)
        if needs_note:
            self._populate_note_selector()

        self.refresh_statistics()

    def _on_stats_source_changed(self, index):
        """Handle source selector change."""
        chart_key = self.chart_selector.currentData()
        if chart_key == "breakdown_chart":
            self._populate_note_selector()
        self.refresh_statistics()

    def _on_stats_note_changed(self, index):
        """Handle note selector change."""
        self.refresh_statistics()

    def _populate_note_selector(self):
        """Populate note selector from graph data."""
        self.stats_note_selector.blockSignals(True)
        self.stats_note_selector.clear()

        data = self.manager.get_graph_network()
        if data:
            for node in data.get("nodes", []):
                if node["type"] == "note":
                    try:
                        note_id = int(node["id"].replace("note_", ""))
                    except (ValueError, AttributeError):
                        continue
                    title = node.get("title", "Untitled") or "Untitled"
                    label = title[:40] + '...' if len(title) > 40 else title
                    self.stats_note_selector.addItem(label, note_id)

        self.stats_note_selector.blockSignals(False)

    def refresh_statistics(self):
        """Fetch data and render the selected chart."""
        if not self.manager.is_neo4j_available():
            self._set_stats_status(self.tr("graph_unavailable"))
            if self.current_chart:
                self.current_chart.show_no_data(self.tr("graph_unavailable"))
            return

        chart_key = self.chart_selector.currentData()
        if not chart_key:
            return

        # Find chart class
        chart_cls = None
        for key, cls in self._chart_types:
            if key == chart_key:
                chart_cls = cls
                break

        if not chart_cls:
            return

        # Replace current chart widget
        if self.current_chart:
            self.chart_container.removeWidget(self.current_chart)
            self.current_chart.setParent(None)
            self.current_chart.deleteLater()

        self.current_chart = chart_cls()
        self.chart_container.addWidget(self.current_chart)

        labels = self._get_dimension_labels()
        source_id = self.stats_source_selector.currentData()

        try:
            if chart_key == "radar_chart":
                if source_id is None:
                    self.current_chart.show_no_data(self.tr("select_source"))
                    self._set_stats_status("")
                    return
                data = self.manager.get_source_propaganda_profile(source_id)
                self.current_chart.plot(data, labels)
                if data:
                    self._set_stats_status(f"{self.tr('notes_analyzed')}: {data.get('note_count', 0)}")
                else:
                    self._set_stats_status(self.tr("no_data_available"))

            elif chart_key == "histogram_chart":
                data = self.manager.get_all_scores_distribution()
                self.current_chart.plot(data)
                self._set_stats_status(f"{self.tr('notes_analyzed')}: {len(data) if data else 0}")

            elif chart_key == "temporal_chart":
                data = self.manager.get_temporal_scores(source_id)
                self.current_chart.plot(data)
                self._set_stats_status(f"{self.tr('notes_analyzed')}: {len(data) if data else 0}")

            elif chart_key == "correlation_chart":
                data = self.manager.get_dimension_correlation_data()
                self.current_chart.plot(data, labels)
                self._set_stats_status(f"{self.tr('notes_analyzed')}: {len(data) if data else 0}")

            elif chart_key == "breakdown_chart":
                note_id = self.stats_note_selector.currentData()
                if note_id is None:
                    self.current_chart.show_no_data(self.tr("select_note"))
                    self._set_stats_status("")
                    return
                data = self.manager.get_note_dimension_breakdown(note_id)
                self.current_chart.plot(data, labels)
                self._set_stats_status("")

            elif chart_key == "platform_chart":
                data = self.manager.get_platform_comparison()
                self.current_chart.plot(data)
                if data:
                    platforms = len(data)
                    total_notes = sum(d.get("note_count", 0) for d in data)
                    self._set_stats_status(
                        f"{self.tr('sources_detected')}: {platforms} | "
                        f"{self.tr('notes_analyzed')}: {total_notes}"
                    )
                else:
                    self._set_stats_status(self.tr("no_data_available"))

        except Exception as e:
            self.current_chart.show_no_data(f"Error: {e}")
            self._set_stats_status(f"Error: {e}")

    def _set_stats_status(self, text):
        """Set the statistics status label text."""
        self.stats_status_label.setText(text)

    def update_fehner_score(self):
        try:
            fehner_score = self.manager.calculate_fehner_score()
            self.fechner_score_value.setText(f"{fehner_score}")
        except Exception as e:
            self.fechner_score_value.setText(f"Error: {e}")
            print(f"Error calculating Fechner Score: {e}")

    def handle_audio_upload(self):
        """Handle audio file selection and transcription."""
        # Import here to avoid circular import and handle missing audio_service gracefully
        try:
            from singletons import audio_service
        except (ImportError, AttributeError):
            QMessageBox.warning(
                self,
                self.tr("audio_not_available"),
                "Audio service is not available. Please check that audio dependencies are installed."
            )
            return

        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("select_audio_file"),
            "",
            "Audio Files (*.wav *.mp3 *.ogg *.m4a *.flac *.webm);;All Files (*)"
        )

        if not file_path:
            return

        # Validate file
        is_valid, error_msg = audio_service.validate_audio_file(file_path)
        if not is_valid:
            QMessageBox.warning(self, self.tr("invalid_audio"), error_msg)
            return

        # Start transcription in background
        self.start_transcription(file_path, audio_service)

    def start_transcription(self, file_path: str, audio_service):
        """Start background transcription worker."""
        # Disable upload button during processing
        self.audio_upload_btn.setEnabled(False)
        self.audio_status_label.setText(self.tr("transcribing_audio"))

        # Get selected language
        language = self.language_dropdown.currentData()

        # Create worker thread
        self.transcription_worker = TranscriptionWorker(file_path, language, audio_service)
        self.transcription_worker.transcription_complete.connect(self.on_transcription_complete)
        self.transcription_worker.transcription_error.connect(self.on_transcription_error)
        self.transcription_worker.progress_update.connect(self.on_transcription_progress)
        self.transcription_worker.start()

    def on_transcription_progress(self, status: str):
        """Handle transcription progress updates."""
        self.audio_status_label.setText(status)

    def on_transcription_complete(self, result: dict):
        """Handle successful transcription."""
        # Extract results
        text = result['text']
        detected_lang = result['language']
        duration = result['duration']

        # Store metadata for later save
        self.current_audio_metadata = result

        # Auto-fill title if empty (use first 50 chars of transcription)
        if not self.title_input.toPlainText().strip():
            title = text[:50].strip() + ("..." if len(text) > 50 else "")
            self.title_input.setPlainText(title)

        # Populate text input
        self.text_input.setPlainText(text)

        # Update status
        status_msg = self.tr("transcription_complete").format(
            duration=f"{duration:.1f}s",
            language=detected_lang
        )
        self.audio_status_label.setText(status_msg)
        self.audio_status_label.setStyleSheet("color: #2e7d32; font-style: italic;")  # Green

        # Re-enable upload button
        self.audio_upload_btn.setEnabled(True)

        # AUTO-PROCESS: Immediately trigger analysis
        QTimer.singleShot(500, self.process_data)  # Small delay for UI update

    def on_transcription_error(self, error_msg: str):
        """Handle transcription failure."""
        QMessageBox.critical(self, self.tr("transcription_failed"), error_msg)
        self.audio_status_label.setText(self.tr("transcription_error"))
        self.audio_status_label.setStyleSheet("color: #c62828; font-style: italic;")  # Red
        self.audio_upload_btn.setEnabled(True)
        self.current_audio_metadata = None

    def process_data(self):
        source_id = self.dropdown.currentData()
        title = self.title_input.toPlainText()
        input_text = self.text_input.toPlainText()
        language = self.language_dropdown.currentData()

        note = self.manager.process(title, input_text, source_id, language)

        # Save audio metadata if this came from audio transcription
        if self.current_audio_metadata and note and note.id:
            self.manager.save_audio_metadata(note.id, self.current_audio_metadata)
            self.current_audio_metadata = None  # Clear after saving

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
