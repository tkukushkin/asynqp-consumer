import pytest

from asynqp_consumer import ConnectionParams


class TestConnectionParams:

    @pytest.mark.parametrize(('connection_string', 'expected'), [
        ('amqp:////', ConnectionParams()),
        ('amqp://guest:guest@localhost:5672//', ConnectionParams()),
        ('amqp://1:2@3:4//', ConnectionParams(username='1', password='2', host='3', port=4)),
        ('amqp://localhost/', ConnectionParams(virtual_host='')),
        ('amqp://localhost', ConnectionParams(virtual_host=None)),
    ])
    def test_from_string__expected_right_result(self, connection_string, expected):
        # act
        result = ConnectionParams.from_string(connection_string)

        # assert
        assert result == expected
