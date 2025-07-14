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
        'person_table_id': 'p',
        'api_token': 'tok',
    },
    'smtp': {
        'host': 'h',
        'port': 25,
        'username': '',
        'password': '',
        'from_address': 'from@example.com',
    },
    'debug': True,
}

SAMPLE_TASK = {
    'fields': {
        'Aufgabe': 'Test',
        'Aufgabe für': 'Bob',
        'Aufgabe von': 'Alice',
        'Kategorie': 'Cat',
        'Notizen': 'Line1\nLine2',
        'Status': 'in Bearbeitung',
        'Priorität': 'hoch',
        'Frist': '2024-01-01'
    }
}

def test_notify_sends_mail():
    with tempfile.NamedTemporaryFile('w+', delete=False) as tmp:
        yaml.safe_dump(CONFIG, tmp)
        tmp.flush()
        with patch('ninox_notification.ninox_client.NinoxClient.get_tasks', return_value=[SAMPLE_TASK]):
            with patch('ninox_notification.ninox_client.NinoxClient.get_persons', return_value=[{'fields': {'fullName': 'Bob', 'E-Mail': 'bob@example.com'}}]):
                with patch('ninox_notification.emailer.Emailer.send') as send:
                    main(tmp.name)
                    send.assert_called_once()
                    args, _ = send.call_args
                    html = args[2]
                    assert '<th>Status</th>' in html
                    assert '01.01.2024' in html
                    assert "<tr><td colspan='" in html


def test_notify_debug_user_only():
    cfg = CONFIG.copy()
    cfg['debug_user'] = 'Bob'
    with tempfile.NamedTemporaryFile('w+', delete=False) as tmp:
        yaml.safe_dump(cfg, tmp)
        tmp.flush()
        tasks = [
            SAMPLE_TASK,
            {
                'fields': {
                    'Aufgabe': 'Test2',
                    'Aufgabe für': 'Alice',
                    'Aufgabe von': 'Bob',
                    'Kategorie': 'Cat',
                    'Notizen': '',
                    'Status': 'offen',
                    'Priorität': 'normal',
                    'Frist': '2024-01-02'
                }
            },
        ]
        persons = [
            {'fields': {'fullName': 'Bob', 'E-Mail': 'bob@example.com'}},
            {'fields': {'fullName': 'Alice', 'E-Mail': 'alice@example.com'}},
        ]
        with patch('ninox_notification.ninox_client.NinoxClient.get_tasks', return_value=tasks):
            with patch('ninox_notification.ninox_client.NinoxClient.get_persons', return_value=persons):
                with patch('ninox_notification.emailer.Emailer.send') as send:
                    main(tmp.name)
                    send.assert_called_once()
                    args, kwargs = send.call_args
                    assert kwargs['force_send'] is True
                    assert args[0] == 'bob@example.com'
