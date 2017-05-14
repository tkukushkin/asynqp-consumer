import asynqp
import pytest

from asynqp_consumer import Message


class TestMessage(object):

    def test_properties(self, mocker):
        # arrange
        incoming_message = mocker.Mock(spec=asynqp.IncomingMessage)
        incoming_message.json.return_value = {'test_key': 'test_value'}
        incoming_message.headers = object()

        # act
        message = Message(incoming_message)

        # assert
        assert message.body == {'test_key': 'test_value'}
        assert message.headers is incoming_message.headers

    def test_ack(self, mocker):
        # arrange
        incoming_message = mocker.Mock(spec=asynqp.IncomingMessage)
        incoming_message.json.return_value = {'test_key': 'test_value'}

        # act
        message = Message(incoming_message)
        message.ack()
        message.reject()
        message.ack()

        # assert
        incoming_message.ack.assert_called_once_with()
        assert not incoming_message.reject.called

    @pytest.mark.parametrize('requeue', (True, False))
    def test_reject(self, mocker, requeue):
        # arrange
        incoming_message = mocker.Mock(spec=asynqp.IncomingMessage)
        incoming_message.json.return_value = {'test_key': 'test_value'}

        # act
        message = Message(incoming_message)
        message.reject(requeue=requeue)
        message.ack()
        message.reject()
        message.ack()

        # assert
        incoming_message.reject.assert_called_once_with(requeue=requeue)
        assert not incoming_message.ack.called
