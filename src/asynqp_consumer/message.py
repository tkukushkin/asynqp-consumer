from typing import Any  # pylint: disable=unused-import

import asynqp


class Message:

    def __init__(self, message: asynqp.IncomingMessage) -> None:
        self.body = message.json()  # type: Any
        self._message = message
        self._is_completed = False

    def ack(self) -> None:
        if not self._is_completed:
            self._message.ack()
            self._is_completed = True

    def reject(self, requeue: bool = True) -> None:
        if not self._is_completed:
            self._message.reject(requeue=requeue)
            self._is_completed = True

    def __getattr__(self, name):
        return getattr(self._message, name)
