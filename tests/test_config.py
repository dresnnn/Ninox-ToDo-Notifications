import tempfile
from ninox_notification.config import load_config

SAMPLE = """
ninox:
  api_url: https://example.com
  team_id: T
  database_id: D
  table_id: F
  api_token: TOKEN
smtp:
  host: smtp
  port: 25
  username: user
  password: pass
  from_address: from@example.com
"""

def test_load_config():
    with tempfile.NamedTemporaryFile('w+', delete=False) as tmp:
        tmp.write(SAMPLE + "debug_user: Bob\n")
        tmp.flush()
    cfg = load_config(tmp.name)
    assert cfg.ninox.team_id == 'T'
    assert cfg.debug_user == 'Bob'
