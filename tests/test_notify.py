from unittest.mock import patch
import tempfile
import yaml
from ninox_notification.notify import main

CONFIG = {
    'ninox': {
        'api_url': 'http://x',
        'team_id': 't',
        'database_id': 'd',
        'table_id': 'f',
        'api_token': 'tok',
    },
    'smtp': {
        'host': 'h',
        'port': 25,
        'username': '',
        'password': '',
        'from_address': 'from@example.com',
    },
    'users': {
        'Bob': {'email': 'bob@example.com', 'notify_in_debug': True},
    },
    'debug': True,
}

SAMPLE_TASK = {
    'fields': {
        'Aufgabe': 'Test',
        'Person': 'Bob',
        'Status': 'unerledigt',
        'Priorität': 'hoch',
        'Frist': '2024-01-01'
    }
}

def test_notify_sends_mail():
    with tempfile.NamedTemporaryFile('w+', delete=False) as tmp:
        yaml.safe_dump(CONFIG, tmp)
        tmp.flush()
        with patch('ninox_notification.ninox_client.NinoxClient.get_tasks', return_value=[SAMPLE_TASK]):
            with patch('ninox_notification.emailer.Emailer.send') as send:
                main(tmp.name)
                send.assert_called_once()
                args, _ = send.call_args
                assert '<table>' in args[2]
