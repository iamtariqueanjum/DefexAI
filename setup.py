from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).parent
readme = (here / "README.md").read_text(encoding="utf8") if (here / "README.md").exists() else "DefexAI"

# Read requirements.txt to populate install_requires (simple parser)
reqs = []
req_file = here / "requirements.txt"
if req_file.exists():
    for line in req_file.read_text().splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        # Skip pinned comments and direct references for packaging simplicity
        reqs.append(s)

setup(
    name="defexai",
    version=(here / "VERSION").read_text(encoding="utf8").strip() if (here / "VERSION").exists() else "0.0.0",
    description="AI-powered DevOps + Security defect detection before production",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://example.com/defexai",
    author="DefexAI",
    packages=find_packages(exclude=("tests","docs")),
    include_package_data=True,
    install_requires=reqs,
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
