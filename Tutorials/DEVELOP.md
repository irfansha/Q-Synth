## Run all tests:

    source QSynth-venv/bin/activate
    pytest

## Measure test coverage:

    coverage run -m pytest
    coverage html

Then open `htmlcov/index.html` in your favourite browser.  
(Note: patterns in .coveragerc are excluded from coverage)

## Python formatting:

    black .

## Upload new version to PyPI:

To upload a new version to PyPI, run the following commands:

    python3 -m venv upload_venv
    source upload_venv/bin/activate

    pip install -e .
    pytest -v .

    python3 -m pip install --upgrade build
    python3 -m pip install --upgrade twine
    python3 -m build --sdist
    python3 -m build --wheel
    twine upload dist/*

    deactivate
    rm -rf upload_venv/
    rm -rf dist/
    rm -rf build/
    rm -rf src/*.egg-info

The above commands:
- create a virtual environment
- install the package in editable mode
- run tests
- build source and wheel distributions
- upload them to PyPI
- delete the virtual environment and build artifacts

Note: You need to have an account on PyPI and be added as a maintainer for the Q-Synth package.