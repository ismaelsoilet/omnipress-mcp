"""Unit tests for runtime_checker utility."""

from unittest.mock import patch
from src.utils.runtime_checker import (
    check_command_version,
    get_runtime_capabilities,
    format_doctor_report,
)


def test_check_command_version_installed():
    """Verify check_command_version returns version string for standard commands."""
    ver = check_command_version("python3", "--version")
    assert ver is not None
    assert "Python" in ver


def test_check_command_version_missing():
    """Verify check_command_version returns None for non-existent commands."""
    ver = check_command_version("non_existent_command_xyz_123")
    assert ver is None


def test_get_runtime_capabilities_structure():
    """Verify get_runtime_capabilities returns all expected keys and types."""
    caps = get_runtime_capabilities()
    assert "python" in caps
    assert caps["python"]["available"] is True
    assert "node" in caps
    assert "npm" in caps
    assert "ffmpeg" in caps
    assert "edge_tts" in caps
    assert "video_capable" in caps
    assert "audio_capable" in caps
    assert isinstance(caps["video_capable"], bool)
    assert isinstance(caps["audio_capable"], bool)


def test_format_doctor_report():
    """Verify format_doctor_report outputs formatted diagnostic table."""
    mock_caps = {
        "python": {"available": True, "version": "3.12.3"},
        "node": {"available": True, "version": "v20.11.0"},
        "npm": {"available": True, "version": "10.2.4"},
        "ffmpeg": {"available": True, "version": "6.1.1"},
        "edge_tts": {"available": True, "version": "installed"},
        "remotion_ready": True,
        "video_capable": True,
        "audio_capable": True,
    }
    report = format_doctor_report(mock_caps)
    assert "Environment Diagnostic" in report
    assert "Python Runtime : [OK] 3.12.3" in report
    assert "Node.js (Video): [OK] v20.11.0" in report
    assert "Capabilities Summary:" in report
    assert "Social Carousels (Pillow) : [READY]" in report
