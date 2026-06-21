from __future__ import annotations

from unittest.mock import Mock

from handlers.private_message_handler import handle_private_message


def test_handle_private_message_none_author_does_not_crash() -> None:
    message = Mock()
    message.author = None
    handle_private_message(message)
