import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add server src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "server"))

# Mock problematic imports before they're loaded
sys.modules["dotenv"] = MagicMock()
sys.modules["src.utils.logger"] = MagicMock()
sys.modules["src.utils.env_loader"] = MagicMock()

from src.component.local import (  # type: ignore  # noqa: E402
    cleanup_old_test_report_directories,
    get_all_local_cards,
    local_report_directories,
)


class TestLocalReportDirectories:
    """Test the local_report_directories function"""

    @patch("src.component.local.os.listdir")
    def test_local_report_directories_empty(self, mock_listdir):
        """Test getting local report directories when none exist"""
        mock_listdir.return_value = []

        result = local_report_directories()

        assert result == []

    @patch("src.component.local.os.listdir")
    def test_local_report_directories_multiple(self, mock_listdir):
        """Test getting multiple local report directories"""
        mock_listdir.return_value = [
            "12-31-2025_08-30-00_AM",
            "12-30-2025_05-15-30_PM",
            "12-29-2025_10-00-00_AM",
        ]

        result = local_report_directories()

        assert len(result) == 3
        assert "12-31-2025_08-30-00_AM" in result

    @patch("src.component.local.os.listdir")
    def test_local_report_directories_single(self, mock_listdir):
        """Test getting single local report directory"""
        mock_listdir.return_value = ["12-31-2025_08-30-00_AM"]

        result = local_report_directories()

        assert len(result) == 1
        assert result[0] == "12-31-2025_08-30-00_AM"


class TestGetAllLocalCards:
    """Test the get_all_local_cards function"""

    @patch("src.component.local.local_report_directories")
    @patch("src.component.local.less_or_eqaul_to_date_time")
    def test_get_all_local_cards_empty(self, mock_date_check, mock_get_dirs):
        """Test getting cards when no local directories exist"""
        mock_get_dirs.return_value = []
        mock_date_check.return_value = True

        result = get_all_local_cards({"day": "1"})

        assert result == {}

    @patch("src.component.local.local_report_directories")
    @patch("src.component.local.less_or_eqaul_to_date_time")
    def test_get_all_local_cards_single_valid(self, mock_date_check, mock_get_dirs):
        """Test getting cards with single valid directory"""
        mock_get_dirs.return_value = ["12-31-2025_08-30-00_AM"]
        mock_date_check.return_value = True  # Validation passes

        result = get_all_local_cards({"day": "1"})

        assert len(result) == 1
        assert "12-31-2025_08-30-00_AM" in result
        assert result["12-31-2025_08-30-00_AM"]["filter_data"]["day"] == "12-31-2025_08-30-00_AM"

    @patch("src.component.local.local_report_directories")
    @patch("src.component.local.less_or_eqaul_to_date_time")
    def test_get_all_local_cards_multiple_valid(self, mock_date_check, mock_get_dirs):
        """Test getting cards with multiple valid directories"""
        mock_get_dirs.return_value = [
            "12-31-2025_08-30-00_AM",
            "12-30-2025_05-15-30_PM",
            "12-29-2025_10-00-00_AM",
        ]
        mock_date_check.return_value = True  # All pass validation

        result = get_all_local_cards({"day": "7"})

        assert len(result) == 3
        assert all(card["filter_data"] for card in result.values())

    @patch("src.component.local.local_report_directories")
    @patch("src.component.local.less_or_eqaul_to_date_time")
    def test_get_all_local_cards_filters_by_date(self, mock_date_check, mock_get_dirs):
        """Test that cards are filtered by date"""
        mock_get_dirs.return_value = [
            "12-31-2025_08-30-00_AM",
            "12-30-2025_05-15-30_PM",
            "12-29-2025_10-00-00_AM",
        ]
        # First passes, second and third fail
        mock_date_check.side_effect = [True, False, False]

        result = get_all_local_cards({"day": "1"})

        assert len(result) == 1
        assert "12-31-2025_08-30-00_AM" in result

    @patch("src.component.local.local_report_directories")
    @patch("src.component.local.less_or_eqaul_to_date_time")
    def test_get_all_local_cards_all_filtered_out(self, mock_date_check, mock_get_dirs):
        """Test when all cards are filtered out"""
        mock_get_dirs.return_value = [
            "12-31-2025_08-30-00_AM",
            "12-30-2025_05-15-30_PM",
        ]
        mock_date_check.return_value = False  # All fail validation

        result = get_all_local_cards({"day": "1"})

        assert result == {}

    @patch("src.component.local.local_report_directories")
    @patch("src.component.local.less_or_eqaul_to_date_time")
    def test_get_all_local_cards_structure(self, mock_date_check, mock_get_dirs):
        """Test that card structure is correct"""
        mock_get_dirs.return_value = ["12-31-2025_08-30-00_AM"]
        mock_date_check.return_value = True

        result = get_all_local_cards({"day": "1"})

        card = result["12-31-2025_08-30-00_AM"]
        assert "filter_data" in card
        assert "html_report" in card
        assert "json_report" in card
        assert "root_dir" in card
        assert card["html_report"] == "12-31-2025_08-30-00_AM/index.html"
        assert card["json_report"] == {}
        assert card["root_dir"] == "12-31-2025_08-30-00_AM"

    @patch("src.component.local.local_report_directories")
    @patch("src.component.local.less_or_eqaul_to_date_time")
    def test_get_all_local_cards_invalid_day_parameter(self, mock_date_check, mock_get_dirs):
        """Test with invalid day parameter"""
        mock_get_dirs.return_value = ["12-31-2025_08-30-00_AM"]
        mock_date_check.return_value = True

        # Should handle invalid day gracefully
        with pytest.raises(ValueError):
            get_all_local_cards({"day": "invalid"})


class TestCleanupOldTestReportDirectories:
    """Test the cleanup_old_test_report_directories function"""

    @patch("src.component.local.os.path.exists")
    def test_cleanup_directory_not_exists(self, mock_exists):
        """Test cleanup when test reports directory doesn't exist"""
        mock_exists.return_value = False

        result = cleanup_old_test_report_directories()

        assert result is False

    @patch("src.component.local.logger")
    @patch("src.component.local.os")
    def test_cleanup_empty_directory(self, mock_os, mock_logger):
        """Test cleanup with empty directory"""
        mock_os.path.exists.return_value = True
        mock_os.listdir.return_value = []
        mock_os.path.join.return_value = "./test_reports"

        result = cleanup_old_test_report_directories(max_dirs=10)

        assert result is True

    @patch("src.component.local.logger")
    @patch("src.component.local.os")
    def test_cleanup_fewer_dirs_than_max(self, mock_os, mock_logger):
        """Test cleanup when number of dirs is below max"""
        mock_os.path.exists.return_value = True
        mock_os.listdir.return_value = ["dir1", "dir2", "dir3"]
        mock_os.path.isdir.return_value = True
        mock_os.getctime.side_effect = [100, 200, 300]
        mock_os.path.join.side_effect = lambda *args: "/".join(args)
        mock_os.path.basename.side_effect = lambda x: x.split("/")[-1]

        result = cleanup_old_test_report_directories(max_dirs=5)

        assert result is True


    @patch("src.component.local.logger")
    @patch("src.component.local.shutil.rmtree")
    @patch("src.component.local.os")
    def test_cleanup_exact_max_dirs(self, mock_os, mock_rmtree, mock_logger):
        """Test cleanup when number of dirs equals max"""
        mock_os.path.exists.return_value = True
        mock_os.listdir.return_value = ["dir1", "dir2", "dir3"]
        mock_os.path.isdir.return_value = True
        mock_os.getctime.side_effect = [300, 200, 100]
        mock_os.path.join.side_effect = lambda *args: "/".join(args)
        mock_os.path.basename.side_effect = lambda x: x.split("/")[-1]

        result = cleanup_old_test_report_directories(max_dirs=3)

        # Should not remove any directories
        mock_rmtree.assert_not_called()
        assert result is True


    @patch("src.component.local.logger")
    @patch("src.component.local.os")
    def test_cleanup_skips_non_directories(self, mock_os, mock_logger):
        """Test cleanup skips files and only processes directories"""
        mock_os.path.exists.return_value = True
        mock_os.listdir.return_value = ["dir1", "file.txt", "dir2"]
        # Only dir1 and dir2 are directories
        mock_os.path.isdir.side_effect = [True, False, True]
        mock_os.getctime.side_effect = [200, 100]  # Only called for directories
        mock_os.path.join.side_effect = lambda *args: "/".join(args)
        mock_os.path.basename.side_effect = lambda x: x.split("/")[-1]

        result = cleanup_old_test_report_directories(max_dirs=10)

        assert result is True

    @patch("src.component.local.os.path.exists")
    def test_cleanup_exception_handling(self, mock_exists):
        """Test cleanup handles exceptions gracefully"""
        mock_exists.side_effect = Exception("Unexpected error")

        result = cleanup_old_test_report_directories()

        assert result is False


    @patch("src.component.local.logger")
    @patch("src.component.local.shutil.rmtree")
    @patch("src.component.local.os")
    def test_cleanup_with_max_dirs_zero(self, mock_os, mock_rmtree, mock_logger):
        """Test cleanup with max_dirs=0"""
        mock_os.path.exists.return_value = True
        mock_os.listdir.return_value = ["dir1"]
        mock_os.path.isdir.return_value = True
        mock_os.getctime.return_value = 100
        mock_os.path.join.side_effect = lambda *args: "/".join(args)
        mock_os.path.basename.side_effect = lambda x: x.split("/")[-1]

        result = cleanup_old_test_report_directories(max_dirs=0)

        # Should remove all directories
        assert mock_rmtree.call_count == 1
        assert result is True
