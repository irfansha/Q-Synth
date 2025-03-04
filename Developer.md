## Run all tests:

    source QSynth-venv/bin/activate
    cd Tests
    pytest

## Measure test coverage:

    coverage run -m pytest
    coverage html

Then open `htmlcov/index.html` in your favourite browser.  
(Note: patterns in .coveragerc are excluded from coverage)

## Python formatting:

    black .
