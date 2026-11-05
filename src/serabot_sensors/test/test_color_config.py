"""color_detector.yaml (serabot_bringup) must match the ColorParams defaults."""

from dataclasses import fields
import os

import pytest
from serabot_sensors.color_detection import ColorParams

yaml = pytest.importorskip('yaml')

CONFIG = os.path.join(os.path.dirname(__file__), '..', '..', 'serabot_bringup', 'config',
                      'color_detector.yaml')


@pytest.fixture
def config_params() -> dict:
    if not os.path.isfile(CONFIG):
        pytest.skip('serabot_bringup source tree not next to serabot_sensors')
    with open(CONFIG, encoding='utf-8') as f:
        return yaml.safe_load(f)['color_detector']['ros__parameters']


def test_config_has_every_parameter_with_default_value_and_type(config_params):
    for f in fields(ColorParams):
        assert f.name in config_params, f'{f.name} missing in color_detector.yaml'
        value = config_params[f.name]
        assert type(value) is type(f.default), f'{f.name}: {value!r} vs {f.default!r}'
        assert value == f.default


def test_config_has_no_unknown_parameter(config_params):
    known = {f.name for f in fields(ColorParams)} | {'use_sim_time'}
    assert set(config_params) <= known
