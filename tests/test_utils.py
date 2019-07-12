import logging
import pytest
from anti_preempter import utils


logger = logging.getLogger(__name__)


def test_get_env_variable_is_set(monkeypatch):
    monkeypatch.setenv('TEST_ENV_VAR', 'some-magic-value')
    assert utils.get_env_variable('TEST_ENV_VAR') == 'some-magic-value'


def test_get_env_variable_not_set():
    with pytest.raises(EnvironmentError):
        utils.get_env_variable('NOT_SET_VAR')
