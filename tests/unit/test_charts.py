"""Tests for chart widgets — uses matplotlib Agg backend for headless rendering."""
import matplotlib
matplotlib.use('Agg')

import pytest
from ui.charts import (
    RadarChart, HistogramChart, TemporalTrendChart,
    CorrelationHeatmap, DimensionBreakdownChart, PlatformComparisonChart,
    DIMENSION_KEYS, BaseChart,
)


SAMPLE_LABELS = [
    "Sent.", "Keyw.", "Topics", "Simpl.", "Conf.", "Click.",
    "Subj.", "CTA", "Rep.Take", "Rep.Note", "Mess.", "Gen.", "Opp."
]


def _make_dimensions(val=0.3):
    return {k: val for k in DIMENSION_KEYS}


class TestBaseChart:
    def test_show_no_data(self):
        chart = BaseChart()
        chart.show_no_data("test message")
        assert chart.fig is not None

    def test_clear(self):
        chart = BaseChart()
        chart.clear()


class TestRadarChart:
    def test_plot_valid_data(self):
        chart = RadarChart()
        data = {"source_name": "Test", "note_count": 5, "dimensions": _make_dimensions(0.4)}
        chart.plot(data, SAMPLE_LABELS)

    def test_plot_none_data(self):
        chart = RadarChart()
        chart.plot(None, SAMPLE_LABELS)

    def test_plot_empty_dimensions(self):
        chart = RadarChart()
        chart.plot({"dimensions": {}}, SAMPLE_LABELS)

    def test_plot_no_dimensions_key(self):
        chart = RadarChart()
        chart.plot({"source_name": "X"}, SAMPLE_LABELS)


class TestHistogramChart:
    def test_plot_valid_data(self):
        chart = HistogramChart()
        data = [
            {"total_score": 0.3, "fehner_type": "A"},
            {"total_score": 0.7, "fehner_type": "B"},
            {"total_score": 0.5, "fehner_type": "A"},
        ]
        chart.plot(data)

    def test_plot_empty_data(self):
        chart = HistogramChart()
        chart.plot([])

    def test_plot_none_data(self):
        chart = HistogramChart()
        chart.plot(None)

    def test_plot_single_point(self):
        chart = HistogramChart()
        chart.plot([{"total_score": 0.5, "fehner_type": "A"}])

    def test_plot_all_same_type(self):
        chart = HistogramChart()
        data = [{"total_score": 0.3 + i * 0.1, "fehner_type": "B"} for i in range(5)]
        chart.plot(data)


class TestTemporalTrendChart:
    def test_plot_valid_data(self):
        chart = TemporalTrendChart()
        data = [
            {"source_name": "Src1", "timestamp": "2025-01-01", "total_score": 0.3},
            {"source_name": "Src1", "timestamp": "2025-01-02", "total_score": 0.5},
            {"source_name": "Src2", "timestamp": "2025-01-01", "total_score": 0.7},
        ]
        chart.plot(data)

    def test_plot_empty(self):
        chart = TemporalTrendChart()
        chart.plot([])

    def test_plot_none(self):
        chart = TemporalTrendChart()
        chart.plot(None)

    def test_plot_single_source(self):
        chart = TemporalTrendChart()
        data = [{"source_name": "X", "timestamp": "2025-01-01", "total_score": 0.5}]
        chart.plot(data)


class TestCorrelationHeatmap:
    def test_plot_valid_data(self):
        chart = CorrelationHeatmap()
        data = [_make_dimensions(0.1 * i) for i in range(5)]
        chart.plot(data, SAMPLE_LABELS)

    def test_plot_insufficient_data(self):
        chart = CorrelationHeatmap()
        chart.plot([_make_dimensions()], SAMPLE_LABELS)

    def test_plot_empty(self):
        chart = CorrelationHeatmap()
        chart.plot([], SAMPLE_LABELS)

    def test_plot_none(self):
        chart = CorrelationHeatmap()
        chart.plot(None, SAMPLE_LABELS)

    def test_plot_constant_columns(self):
        chart = CorrelationHeatmap()
        data = [_make_dimensions(0.5) for _ in range(5)]
        chart.plot(data, SAMPLE_LABELS)


class TestDimensionBreakdownChart:
    def test_plot_valid_data(self):
        chart = DimensionBreakdownChart()
        data = {"title": "Test", "total_score": 0.65, "dimensions": _make_dimensions(0.4)}
        chart.plot(data, SAMPLE_LABELS)

    def test_plot_none(self):
        chart = DimensionBreakdownChart()
        chart.plot(None, SAMPLE_LABELS)

    def test_plot_no_dimensions(self):
        chart = DimensionBreakdownChart()
        chart.plot({"title": "X"}, SAMPLE_LABELS)

    def test_plot_zero_values(self):
        chart = DimensionBreakdownChart()
        data = {"title": "Test", "total_score": 0, "dimensions": _make_dimensions(0)}
        chart.plot(data, SAMPLE_LABELS)


class TestPlatformComparisonChart:
    def test_plot_valid_data(self):
        chart = PlatformComparisonChart()
        data = [
            {"platform": "telegram", "note_count": 10, "avg_total": 0.45,
             "avg_sentimental": 0.3, "avg_keywords": 0.5, "avg_topics": 0.2,
             "avg_clickbait": 0.6, "avg_subjective": 0.35, "avg_cta": 0.15},
            {"platform": "web", "note_count": 5, "avg_total": 0.3,
             "avg_sentimental": 0.2, "avg_keywords": 0.3, "avg_topics": 0.1,
             "avg_clickbait": 0.4, "avg_subjective": 0.25, "avg_cta": 0.1},
        ]
        chart.plot(data)

    def test_plot_empty(self):
        chart = PlatformComparisonChart()
        chart.plot([])

    def test_plot_none(self):
        chart = PlatformComparisonChart()
        chart.plot(None)

    def test_plot_single_platform(self):
        chart = PlatformComparisonChart()
        data = [{"platform": "tg", "note_count": 1, "avg_total": 0.5,
                 "avg_sentimental": 0.3, "avg_keywords": 0.5, "avg_topics": 0.2,
                 "avg_clickbait": 0.6, "avg_subjective": 0.35, "avg_cta": 0.15}]
        chart.plot(data)
