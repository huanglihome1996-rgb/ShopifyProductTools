"""
基础测试
"""
import pytest
from src import __version__


def test_version():
    """测试版本号"""
    assert __version__ == "0.1.0"


def test_import():
    """测试模块导入"""
    from src import main
    assert hasattr(main, "main")
