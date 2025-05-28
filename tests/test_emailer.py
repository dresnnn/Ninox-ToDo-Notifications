from unittest.mock import patch
from ninox_notification.emailer import Emailer, SMTPConfig


def test_emailer_debug():
    cfg = SMTPConfig(host='h', port=25, username='', password='', from_address='f')
    emailer = Emailer(cfg, debug=True)
    with patch('smtplib.SMTP') as smtp:
        emailer.send('a@example.com', 'sub', '<p>hi</p>')
        smtp.assert_not_called()
