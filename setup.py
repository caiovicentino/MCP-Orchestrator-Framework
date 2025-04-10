from setuptools import setup, find_packages

setup(
    name="mcp_orchestrator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typing_extensions;python_version<'3.8'",
    ],
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="A framework for orchestrating Model Context Protocols",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mcp-orchestrator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
