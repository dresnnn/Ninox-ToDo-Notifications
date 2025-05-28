from typing import Dict, List

from .config import load_config, Config
from .ninox_client import NinoxClient
from .emailer import Emailer


def format_tasks(tasks: List[Dict]) -> str:
    if not tasks:
        return "<p>Keine offenen Aufgaben.</p>"
    items = []
    for t in tasks:
        f = t.get("fields", {})
        line = f"<li><strong>{f.get('Aufgabe')}</strong>"
        if f.get("Frist"):
            line += f" - Fällig am {f['Frist']}"
        if f.get("Priorität"):
            line += f" - Priorität: {f['Priorität']}"
        if f.get("Kategorie"):
            line += f" - Kategorie: {f['Kategorie']}"
        if f.get("Notizen"):
            line += f"<br>{f['Notizen']}"
        line += "</li>"
        items.append(line)
    return "<ul>" + "\n".join(items) + "</ul>"


def main(config_path: str):
    cfg: Config = load_config(config_path)
    client = NinoxClient(cfg.ninox)
    emailer = Emailer(cfg.smtp, debug=cfg.debug)

    tasks = client.get_tasks()
    tasks_by_user: Dict[str, List[Dict]] = {}
    for t in tasks:
        users = t.get("fields", {}).get("Person", "")
        for user in [u.strip() for u in users.split(',') if u.strip()]:
            tasks_by_user.setdefault(user, []).append(t)

    for username, user_cfg in cfg.users.items():
        user_tasks = tasks_by_user.get(username, [])
        if cfg.debug and not user_cfg.notify_in_debug:
            continue
        body = f"<h3>Offene Aufgaben ({len(user_tasks)})</h3>" + format_tasks(user_tasks)
        subject = "Deine offenen Aufgaben"
        try:
            emailer.send(user_cfg.email, subject, body)
        except Exception as exc:
            print(f"Failed to send mail to {user_cfg.email}: {exc}")


def cli():
    import sys

    if len(sys.argv) < 2:
        print("Usage: notify.py <config.yaml>")
        raise SystemExit(1)
    try:
        main(sys.argv[1])
    except Exception as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
