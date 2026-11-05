"""behavior.yaml (serabot_bringup) must list every BehaviorParams field with its default."""

from dataclasses import fields
import os

import pytest
from serabot_behavior.logic import BehaviorParams

yaml = pytest.importorskip('yaml')

CONFIG = os.path.join(os.path.dirname(__file__), '..', '..', 'serabot_bringup', 'config',
                      'behavior.yaml')
NODE_ONLY = {'use_sim_time', 'control_rate'}  # read by the node, not by the logic


@pytest.fixture
def config_params() -> dict:
    if not os.path.isfile(CONFIG):
        pytest.skip('serabot_bringup source tree not next to serabot_behavior')
    with open(CONFIG, encoding='utf-8') as f:
        return yaml.safe_load(f)['behavior_node']['ros__parameters']


def test_every_parameter_has_its_default(config_params):
    for f in fields(BehaviorParams):
        assert f.name in config_params, f'{f.name} missing in behavior.yaml'
        value = config_params[f.name]
        # ROS 2 rejects an int for a double parameter, so the types must match too.
        assert type(value) is type(f.default), f'{f.name}: {value!r} vs {f.default!r}'
        assert value == f.default, f'{f.name}: yaml {value!r} != code {f.default!r}'


def test_no_unknown_parameter(config_params):
    known = {f.name for f in fields(BehaviorParams)} | NODE_ONLY
    assert set(config_params) <= known, set(config_params) - known
