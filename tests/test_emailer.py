from unittest.mock import patch
from ninox_notification.emailer import Emailer, SMTPConfig


def test_emailer_debug():
    cfg = SMTPConfig(host='h', port=25, username='', password='', from_address='f')
    emailer = Emailer(cfg, debug=True)
    with patch('smtplib.SMTP') as smtp:
        emailer.send('a@example.com', 'sub', '<p>hi</p>')
        smtp.assert_not_called()


def test_emailer_force_send_in_debug():
    cfg = SMTPConfig(host='h', port=25, username='', password='', from_address='f')
    emailer = Emailer(cfg, debug=True)
    with patch('smtplib.SMTP') as smtp:
        emailer.send('a@example.com', 'sub', '<p>hi</p>', force_send=True)
        smtp.assert_called_once()
