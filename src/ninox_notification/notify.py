from datetime import date
from typing import Dict, List, Tuple

from .config import load_config, Config
from .ninox_client import NinoxClient
from .emailer import Emailer


_PRIO_ORDER = {
    "hoch": 0,
    "normal": 1,
    "niedrig": 2,
}


def _task_sort_key(task: Dict) -> Tuple[int, date]:
    fields = task.get("fields", {})
    prio = str(fields.get("Priorität", "normal")).lower()
    prio_idx = _PRIO_ORDER.get(prio, 1)
    due = fields.get("Frist")
    try:
        due_date = date.fromisoformat(due)
    except Exception:
        due_date = date.max
    return (prio_idx, due_date)


def format_tasks(tasks: List[Dict]) -> str:
    if not tasks:
        return "<p>Keine offenen Aufgaben.</p>"

    header = """
<style>
table {border-collapse: collapse; width: 100%;}
th, td {border: 1px solid #ddd; padding: 8px;}
th {background-color: #f2f2f2; text-align: left;}
</style>
<table>
<tr><th>Aufgabe</th><th>Fälligkeit</th><th>Priorität</th><th>Kategorie</th><th>Notizen</th></tr>
"""

    rows = []
    for t in tasks:
        f = t.get("fields", {})
        notes = f.get("Notizen", "").replace("\n", "<br>")
        row = (
            f"<tr><td>{f.get('Aufgabe','')}</td>"
            f"<td>{f.get('Frist','')}</td>"
            f"<td>{f.get('Priorität','')}</td>"
            f"<td>{f.get('Kategorie','')}</td>"
            f"<td>{notes}</td></tr>"
        )
        rows.append(row)

    return header + "".join(rows) + "</table>"


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
        user_tasks.sort(key=_task_sort_key)

        if cfg.debug and not user_cfg.notify_in_debug:
            print(f"[DEBUG] Skip {username} (notify_in_debug is False)")
            continue

        if cfg.debug:
            print(
                f"[DEBUG] Preparing email for {username} with {len(user_tasks)} tasks"
            )

        body = f"<h3>Offene Aufgaben ({len(user_tasks)})</h3>" + format_tasks(user_tasks)
        subject = "Deine offenen Aufgaben"
        try:
            emailer.send(
                user_cfg.email,
                subject,
                body,
                force_send=cfg.debug and user_cfg.notify_in_debug,
            )
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
