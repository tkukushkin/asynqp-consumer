from typing import Dict, Any

import asynqp


class Message(object):

    def __init__(self, message: asynqp.IncomingMessage) -> None:
        self.body: Dict[str, Any] = message.json()
        self._message: asynqp.IncomingMessage = message
        self._is_completed: bool = False

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
