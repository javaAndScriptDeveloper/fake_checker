import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


DIMENSION_KEYS = [
    "sentimental", "keywords", "topics", "simplicity", "confidence",
    "clickbait", "subjective", "call_to_action", "repeated_take",
    "repeated_note", "messianism", "generalization", "opposition"
]

DIMENSION_LABEL_KEYS = [
    "dim_sentiment", "dim_keywords", "dim_topics", "dim_simplicity",
    "dim_confidence", "dim_clickbait", "dim_subjective", "dim_cta",
    "dim_repeated_take", "dim_repeated_note", "dim_messianism",
    "dim_generalization", "dim_opposition"
]

BG_COLOR = "#2b2b2b"
TEXT_COLOR = "#cccccc"
GRID_COLOR = "#444444"


class BaseChart(FigureCanvasQTAgg):
    """Base chart with dark theme setup."""

    def __init__(self, width=8, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor=BG_COLOR)
        super().__init__(self.fig)
        self.fig.patch.set_facecolor(BG_COLOR)

    def clear(self):
        self.fig.clear()

    def _style_axis(self, ax):
        ax.set_facecolor(BG_COLOR)
        ax.tick_params(colors=TEXT_COLOR)
        ax.xaxis.label.set_color(TEXT_COLOR)
        ax.yaxis.label.set_color(TEXT_COLOR)
        ax.title.set_color(TEXT_COLOR)
        for spine in ax.spines.values():
            spine.set_color(GRID_COLOR)

    def show_no_data(self, message="No data available"):
        self.clear()
        ax = self.fig.add_subplot(111)
        self._style_axis(ax)
        ax.text(0.5, 0.5, message, ha='center', va='center',
                fontsize=14, color=TEXT_COLOR, transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        self.draw()


class RadarChart(BaseChart):
    """13-axis spider plot for source propaganda profile."""

    def plot(self, data, labels):
        self.clear()

        if not data or "dimensions" not in data:
            self.show_no_data()
            return

        dimensions = data["dimensions"]
        values = [dimensions.get(k, 0) for k in DIMENSION_KEYS]
        N = len(values)

        if N == 0:
            self.show_no_data()
            return

        angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
        values_closed = values + [values[0]]
        angles_closed = angles + [angles[0]]

        ax = self.fig.add_subplot(111, polar=True, facecolor=BG_COLOR)
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)

        ax.plot(angles_closed, values_closed, 'o-', linewidth=2, color='#4a90d9')
        ax.fill(angles_closed, values_closed, alpha=0.25, color='#4a90d9')

        ax.set_xticks(angles)
        ax.set_xticklabels(labels, size=8, color=TEXT_COLOR)
        ax.tick_params(axis='y', colors=TEXT_COLOR)
        ax.set_ylim(0, max(max(values) * 1.1, 0.1))
        ax.grid(color=GRID_COLOR, alpha=0.5)

        title = data.get("source_name", "Source")
        note_count = data.get("note_count", 0)
        ax.set_title(f"{title} (n={note_count})", color=TEXT_COLOR, pad=20, fontsize=11)

        self.fig.tight_layout()
        self.draw()


class HistogramChart(BaseChart):
    """Stacked bars by Fehner type for score distribution."""

    def plot(self, data, labels=None):
        self.clear()

        if not data:
            self.show_no_data()
            return

        scores_a = [d["total_score"] for d in data if d.get("fehner_type") == "A"]
        scores_b = [d["total_score"] for d in data if d.get("fehner_type") != "A"]

        ax = self.fig.add_subplot(111)
        self._style_axis(ax)

        bin_count = min(max(len(data) // 5, 5), 30)
        bins = np.linspace(0, 1, bin_count + 1)

        if scores_a:
            ax.hist(scores_a, bins=bins, alpha=0.7, color='#ff6666', label='Fehner A')
        if scores_b:
            ax.hist(scores_b, bins=bins, alpha=0.7, color='#4a90d9', label='Fehner B')

        ax.set_xlabel("Total Score")
        ax.set_ylabel("Count")
        ax.set_title("Score Distribution by Fehner Type")
        ax.legend(facecolor=BG_COLOR, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)

        self.fig.tight_layout()
        self.draw()


class TemporalTrendChart(BaseChart):
    """Multi-line plot for temporal score trends per source."""

    def plot(self, data, labels=None):
        self.clear()

        if not data:
            self.show_no_data()
            return

        ax = self.fig.add_subplot(111)
        self._style_axis(ax)

        # Group by source
        sources = {}
        for d in data:
            name = d["source_name"]
            if name not in sources:
                sources[name] = {"timestamps": [], "scores": []}
            sources[name]["timestamps"].append(d["timestamp"])
            sources[name]["scores"].append(d["total_score"])

        colors = ['#4a90d9', '#ff6666', '#66ff66', '#ffff66', '#ff66ff',
                  '#66ffff', '#ff9933', '#9966ff', '#33cc33', '#cc3333']

        for idx, (name, vals) in enumerate(sources.items()):
            color = colors[idx % len(colors)]
            label = name[:20] + '...' if len(name) > 20 else name
            ax.plot(range(len(vals["scores"])), vals["scores"],
                    '-o', color=color, label=label, markersize=4, linewidth=1.5)

        ax.set_xlabel("Note Index")
        ax.set_ylabel("Total Score")
        ax.set_title("Temporal Score Trends")

        if len(sources) <= 10:
            ax.legend(facecolor=BG_COLOR, edgecolor=GRID_COLOR,
                      labelcolor=TEXT_COLOR, fontsize=7, loc='upper left')

        self.fig.tight_layout()
        self.draw()


class CorrelationHeatmap(BaseChart):
    """13x13 correlation matrix heatmap."""

    def plot(self, data, labels):
        self.clear()

        if not data or len(data) < 3:
            self.show_no_data("Not enough data for correlation (need 3+ notes)")
            return

        matrix = np.array([[d.get(k, 0) for k in DIMENSION_KEYS] for d in data])
        # Handle constant columns
        std = matrix.std(axis=0)
        if np.any(std == 0):
            matrix[:, std == 0] += np.random.normal(0, 1e-10, (matrix.shape[0], int((std == 0).sum())))

        corr = np.corrcoef(matrix.T)
        corr = np.nan_to_num(corr, nan=0.0)

        ax = self.fig.add_subplot(111)
        self._style_axis(ax)

        im = ax.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')

        ax.set_xticks(range(len(labels)))
        ax.set_yticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=7)
        ax.set_yticklabels(labels, fontsize=7)
        ax.set_title("Dimension Correlation Matrix")

        cbar = self.fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.ax.tick_params(colors=TEXT_COLOR)

        self.fig.tight_layout()
        self.draw()


class DimensionBreakdownChart(BaseChart):
    """Horizontal bars for single note dimension breakdown."""

    def plot(self, data, labels):
        self.clear()

        if not data or "dimensions" not in data:
            self.show_no_data()
            return

        dimensions = data["dimensions"]
        values = [dimensions.get(k, 0) for k in DIMENSION_KEYS]

        ax = self.fig.add_subplot(111)
        self._style_axis(ax)

        y_pos = np.arange(len(labels))
        colors = []
        for v in values:
            if v <= 0.3:
                colors.append('#90EE90')
            elif v <= 0.5:
                colors.append('#FFFF66')
            else:
                colors.append('#FF6666')

        ax.barh(y_pos, values, color=colors, edgecolor=GRID_COLOR, linewidth=0.5)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=8)
        ax.set_xlabel("Score")
        ax.set_xlim(0, max(max(values) * 1.1, 0.1))

        title = data.get("title", "Note")
        total = data.get("total_score", 0)
        ax.set_title(f"{title[:40]} (total: {total:.2f})")

        ax.invert_yaxis()
        self.fig.tight_layout()
        self.draw()


class PlatformComparisonChart(BaseChart):
    """Grouped vertical bars per platform."""

    def plot(self, data, labels=None):
        self.clear()

        if not data:
            self.show_no_data()
            return

        ax = self.fig.add_subplot(111)
        self._style_axis(ax)

        platforms = [d["platform"] for d in data]
        metrics = ["avg_sentimental", "avg_keywords", "avg_topics",
                    "avg_clickbait", "avg_subjective", "avg_cta"]
        metric_labels = ["Sent.", "Keyw.", "Topics", "Click.", "Subj.", "CTA"]
        colors = ['#4a90d9', '#ff6666', '#66ff66', '#ffff66', '#ff66ff', '#66ffff']

        x = np.arange(len(platforms))
        width = 0.12
        n_metrics = len(metrics)

        for i, (metric, label, color) in enumerate(zip(metrics, metric_labels, colors)):
            values = [d.get(metric, 0) for d in data]
            offset = (i - n_metrics / 2 + 0.5) * width
            ax.bar(x + offset, values, width, label=label, color=color, alpha=0.8)

        ax.set_xticks(x)
        ax.set_xticklabels(platforms, rotation=30, ha='right', fontsize=8)
        ax.set_ylabel("Average Score")
        ax.set_title("Platform Comparison")
        ax.legend(facecolor=BG_COLOR, edgecolor=GRID_COLOR,
                  labelcolor=TEXT_COLOR, fontsize=7, ncol=3)

        self.fig.tight_layout()
        self.draw()
