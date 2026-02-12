"""Tests for Neo4j analytics queries and Manager wrapper methods."""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestNeo4jServiceAnalytics:
    """Test Neo4j service analytics query methods."""

    @pytest.fixture
    def neo4j_service(self):
        """Create Neo4j service with mocked driver."""
        with patch('services.neo4j_service.GraphDatabase') as mock_gdb:
            mock_driver = Mock()
            mock_driver.verify_connectivity.return_value = None
            mock_gdb.driver.return_value = mock_driver
            from services.neo4j_service import Neo4jService
            service = Neo4jService(uri="bolt://test:7687", auth=("test", "test"))
            service.driver = mock_driver
            return service

    def _mock_execute_read(self, neo4j_service, return_value):
        neo4j_service._execute_read = Mock(return_value=return_value)

    def test_get_source_propaganda_profile_with_data(self, neo4j_service):
        record = Mock()
        record.__getitem__ = lambda self, key: {
            "source_name": "TestSource",
            "note_count": 5,
            "avg_sentimental": 0.3,
            "avg_keywords": 0.5,
            "avg_topics": 0.2,
            "avg_simplicity": 0.1,
            "avg_confidence": 0.4,
            "avg_clickbait": 0.6,
            "avg_subjective": 0.35,
            "avg_cta": 0.15,
            "avg_repeated_take": 0.0,
            "avg_repeated_note": 0.1,
            "avg_messianism": 0.05,
            "avg_generalization": 0.2,
            "avg_opposition": 0.25,
        }[key]
        self._mock_execute_read(neo4j_service, [record])

        result = neo4j_service.get_source_propaganda_profile(1)
        assert result is not None
        assert result["source_name"] == "TestSource"
        assert result["note_count"] == 5
        assert "dimensions" in result
        assert len(result["dimensions"]) == 13

    def test_get_source_propaganda_profile_empty(self, neo4j_service):
        self._mock_execute_read(neo4j_service, None)
        result = neo4j_service.get_source_propaganda_profile(999)
        assert result is None

    def test_get_source_propaganda_profile_no_notes(self, neo4j_service):
        record = Mock()
        record.__getitem__ = lambda self, key: {"note_count": 0}.get(key, None)
        self._mock_execute_read(neo4j_service, [record])
        result = neo4j_service.get_source_propaganda_profile(1)
        assert result is None

    def test_get_all_scores_distribution(self, neo4j_service):
        records = [
            Mock(**{"__getitem__": lambda self, key: {"total_score": 0.3, "fehner_type": "A"}[key]}),
            Mock(**{"__getitem__": lambda self, key: {"total_score": 0.7, "fehner_type": "B"}[key]}),
        ]
        self._mock_execute_read(neo4j_service, records)

        result = neo4j_service.get_all_scores_distribution()
        assert len(result) == 2
        assert result[0]["total_score"] == 0.3
        assert result[0]["fehner_type"] == "A"

    def test_get_all_scores_distribution_empty(self, neo4j_service):
        self._mock_execute_read(neo4j_service, None)
        result = neo4j_service.get_all_scores_distribution()
        assert result == []

    def test_get_temporal_scores_all(self, neo4j_service):
        records = [
            Mock(**{"__getitem__": lambda self, key: {
                "source_name": "Src", "source_id": 1,
                "timestamp": "2025-01-01", "total_score": 0.5
            }[key]}),
        ]
        self._mock_execute_read(neo4j_service, records)

        result = neo4j_service.get_temporal_scores()
        assert len(result) == 1
        assert result[0]["source_name"] == "Src"

    def test_get_temporal_scores_filtered(self, neo4j_service):
        self._mock_execute_read(neo4j_service, [])
        result = neo4j_service.get_temporal_scores(source_postgres_id=1)
        assert result == []

    def test_get_dimension_correlation_data(self, neo4j_service):
        record = Mock()
        record.__getitem__ = lambda self, key: {
            "sentimental": 0.3, "keywords": 0.5, "topics": 0.2,
            "simplicity": 0.1, "confidence": 0.4, "clickbait": 0.6,
            "subjective": 0.35, "call_to_action": 0.15, "repeated_take": 0.0,
            "repeated_note": 0.1, "messianism": 0.05, "generalization": 0.2,
            "opposition": 0.25,
        }[key]
        self._mock_execute_read(neo4j_service, [record])

        result = neo4j_service.get_dimension_correlation_data()
        assert len(result) == 1
        assert len(result[0]) == 13

    def test_get_note_dimension_breakdown(self, neo4j_service):
        record = Mock()
        record.__getitem__ = lambda self, key: {
            "title": "Test Note", "total_score": 0.65,
            "sentimental": 0.3, "keywords": 0.5, "topics": 0.2,
            "simplicity": 0.1, "confidence": 0.4, "clickbait": 0.6,
            "subjective": 0.35, "call_to_action": 0.15, "repeated_take": 0.0,
            "repeated_note": 0.1, "messianism": 0.05, "generalization": 0.2,
            "opposition": 0.25,
        }[key]
        self._mock_execute_read(neo4j_service, [record])

        result = neo4j_service.get_note_dimension_breakdown(1)
        assert result is not None
        assert result["title"] == "Test Note"
        assert "dimensions" in result

    def test_get_note_dimension_breakdown_not_found(self, neo4j_service):
        self._mock_execute_read(neo4j_service, None)
        result = neo4j_service.get_note_dimension_breakdown(999)
        assert result is None

    def test_get_platform_comparison(self, neo4j_service):
        record = Mock()
        record.__getitem__ = lambda self, key: {
            "platform": "telegram", "note_count": 10, "avg_total": 0.45,
            "avg_sentimental": 0.3, "avg_keywords": 0.5, "avg_topics": 0.2,
            "avg_simplicity": 0.1, "avg_confidence": 0.4, "avg_clickbait": 0.6,
            "avg_subjective": 0.35, "avg_cta": 0.15,
        }[key]
        self._mock_execute_read(neo4j_service, [record])

        result = neo4j_service.get_platform_comparison()
        assert len(result) == 1
        assert result[0]["platform"] == "telegram"

    def test_get_source_repost_network(self, neo4j_service):
        record = Mock()
        record.__getitem__ = lambda self, key: {
            "from_id": 1, "from_name": "Src1",
            "to_id": 2, "to_name": "Src2",
            "weight": 3,
        }[key]
        self._mock_execute_read(neo4j_service, [record])

        result = neo4j_service.get_source_repost_network()
        assert len(result) == 1
        assert result[0]["weight"] == 3

    def test_get_source_repost_network_empty(self, neo4j_service):
        self._mock_execute_read(neo4j_service, None)
        result = neo4j_service.get_source_repost_network()
        assert result == []

    def test_get_information_cascades(self, neo4j_service):
        record = Mock()
        record.__getitem__ = lambda self, key: {
            "from_note_id": 1, "from_title": "Note1", "from_score": 0.5,
            "from_timestamp": "2025-01-01", "from_source": "Src1",
            "to_note_id": 2, "to_title": "Note2", "to_score": 0.3,
            "to_timestamp": "2025-01-02", "to_source": "Src2",
            "depth": 1,
        }[key]
        self._mock_execute_read(neo4j_service, [record])

        result = neo4j_service.get_information_cascades()
        assert len(result) == 1
        assert result[0]["depth"] == 1

    def test_get_full_network_includes_fehner_type(self, neo4j_service):
        """Verify get_full_network query includes fehner_type in note nodes."""
        # We verify the query string contains fehner_type
        original_execute = neo4j_service._execute_read

        captured_queries = []
        def capture_query(query, params=None):
            captured_queries.append(query)
            return None

        neo4j_service._execute_read = capture_query
        neo4j_service.get_full_network()

        assert len(captured_queries) > 0
        assert "fehner_type" in captured_queries[0]


class TestManagerAnalyticsMethods:
    """Test Manager wrapper methods for analytics."""

    @pytest.fixture
    def mock_manager(self):
        """Create Manager with mocked dependencies."""
        with patch('manager.Manager.coldstart'):
            mock_eval = Mock()
            mock_note_dao = Mock()
            mock_source_dao = Mock()
            mock_fehner = Mock()
            mock_translator = Mock()
            mock_neo4j = Mock()
            mock_neo4j.is_connected.return_value = True

            from manager import Manager
            mgr = Manager(
                evaluation_processor=mock_eval,
                note_dao=mock_note_dao,
                source_dao=mock_source_dao,
                fehner_processor=mock_fehner,
                translator=mock_translator,
                neo4j_service=mock_neo4j,
            )
            return mgr

    def test_get_source_propaganda_profile_delegates(self, mock_manager):
        mock_manager.neo4j_service.get_source_propaganda_profile.return_value = {"test": True}
        result = mock_manager.get_source_propaganda_profile(1)
        assert result == {"test": True}
        mock_manager.neo4j_service.get_source_propaganda_profile.assert_called_once_with(1)

    def test_get_all_scores_distribution_delegates(self, mock_manager):
        mock_manager.neo4j_service.get_all_scores_distribution.return_value = [{"score": 0.5}]
        result = mock_manager.get_all_scores_distribution()
        assert len(result) == 1

    def test_get_temporal_scores_delegates(self, mock_manager):
        mock_manager.neo4j_service.get_temporal_scores.return_value = []
        result = mock_manager.get_temporal_scores(source_id=1)
        assert result == []

    def test_get_dimension_correlation_data_delegates(self, mock_manager):
        mock_manager.neo4j_service.get_dimension_correlation_data.return_value = [{}]
        result = mock_manager.get_dimension_correlation_data()
        assert len(result) == 1

    def test_get_note_dimension_breakdown_delegates(self, mock_manager):
        mock_manager.neo4j_service.get_note_dimension_breakdown.return_value = {"title": "T"}
        result = mock_manager.get_note_dimension_breakdown(1)
        assert result["title"] == "T"

    def test_get_platform_comparison_delegates(self, mock_manager):
        mock_manager.neo4j_service.get_platform_comparison.return_value = []
        result = mock_manager.get_platform_comparison()
        assert result == []

    def test_get_source_repost_network_delegates(self, mock_manager):
        mock_manager.neo4j_service.get_source_repost_network.return_value = []
        result = mock_manager.get_source_repost_network()
        assert result == []

    def test_get_information_cascades_delegates(self, mock_manager):
        mock_manager.neo4j_service.get_information_cascades.return_value = []
        result = mock_manager.get_information_cascades()
        assert result == []

    def test_neo4j_unavailable_returns_none(self, mock_manager):
        mock_manager.neo4j_service.is_connected.return_value = False
        assert mock_manager.get_source_propaganda_profile(1) is None
        assert mock_manager.get_all_scores_distribution() is None
        assert mock_manager.get_temporal_scores() is None
        assert mock_manager.get_dimension_correlation_data() is None
        assert mock_manager.get_note_dimension_breakdown(1) is None
        assert mock_manager.get_platform_comparison() is None
        assert mock_manager.get_source_repost_network() is None
        assert mock_manager.get_information_cascades() is None

    def test_compute_community_detection(self, mock_manager):
        mock_manager.neo4j_service.get_source_repost_network.return_value = [
            {"from_id": 1, "from_name": "A", "to_id": 2, "to_name": "B", "weight": 3},
            {"from_id": 2, "from_name": "B", "to_id": 3, "to_name": "C", "weight": 2},
            {"from_id": 1, "from_name": "A", "to_id": 3, "to_name": "C", "weight": 1},
        ]
        result = mock_manager.compute_community_detection()
        assert result is not None
        assert isinstance(result, dict)
        assert 1 in result
        assert 2 in result
        assert 3 in result

    def test_compute_community_detection_no_data(self, mock_manager):
        mock_manager.neo4j_service.get_source_repost_network.return_value = []
        result = mock_manager.compute_community_detection()
        assert result is None

    def test_compute_pagerank_and_centrality(self, mock_manager):
        mock_manager.neo4j_service.get_source_repost_network.return_value = [
            {"from_id": 1, "from_name": "A", "to_id": 2, "to_name": "B", "weight": 3},
            {"from_id": 2, "from_name": "B", "to_id": 3, "to_name": "C", "weight": 2},
        ]
        result = mock_manager.compute_pagerank_and_centrality()
        assert result is not None
        assert "pagerank" in result
        assert "centrality" in result
        assert 1 in result["pagerank"]

    def test_compute_pagerank_no_data(self, mock_manager):
        mock_manager.neo4j_service.get_source_repost_network.return_value = None
        result = mock_manager.compute_pagerank_and_centrality()
        assert result is None
