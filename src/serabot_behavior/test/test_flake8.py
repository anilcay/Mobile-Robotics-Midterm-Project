"""Code style check run by `colcon test` (skipped where ament_flake8 is missing)."""

import pytest


@pytest.mark.flake8
@pytest.mark.linter
def test_flake8():
    # Imported here so the test is still collected (and reported as skipped)
    # on machines without ROS, e.g. the Windows development setup.
    main_with_errors = pytest.importorskip('ament_flake8.main').main_with_errors
    rc, errors = main_with_errors(argv=[])
    assert rc == 0, \
        'Found %d code style errors / warnings:\n' % len(errors) + \
        '\n'.join(errors)
