from pathlib import Path

from setuptools import setup


setup(
    name="api-wb",
    version="0.1.0",
    description="Simple Wildberries statistics API client",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    py_modules=["wb_utm_statistics"],
    python_requires=">=3.10",
    install_requires=[
        "pandas>=2.0.0",
        "requests>=2.31.0",
    ],
)
