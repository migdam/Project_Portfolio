from setuptools import setup, find_packages

setup(
    name="portfolio-ml",
    version="0.1.0",
    description="AI-Powered Project & Portfolio Machine Learning Models",
    author="Michał",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "portfolio-train=models.train:main",
            "portfolio-predict=models.predict:main",
            "portfolio-monitor=monitoring.health_check:main",
        ],
    },
)
