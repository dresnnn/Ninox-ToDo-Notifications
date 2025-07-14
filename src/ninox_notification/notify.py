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


def _format_date(value: str) -> Tuple[str, bool]:
    """Return formatted due date and whether it is overdue."""
    try:
        due_date = date.fromisoformat(value)
        formatted = due_date.strftime("%d.%m.%Y")
        overdue = due_date <= date.today()
    except Exception:
        formatted = value
        overdue = False
    return formatted, overdue


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
<tr><th>Status</th><th>Aufgabe</th><th>Fälligkeit</th><th>Priorität</th><th>Kategorie</th><th>Von</th><th>Bearbeiter</th></tr>
"""

    rows = []
    for t in tasks:
        f = t.get("fields", {})
        notes = f.get("Notizen", "").replace("\n", "<br>")

        due_raw = f.get("Frist", "")
        due_formatted, overdue = _format_date(due_raw)
        if overdue:
            due_cell = f"<span style='color:red;font-weight:bold'>{due_formatted}</span>"
        else:
            due_cell = due_formatted

        row = (
            f"<tr><td>{f.get('Status','')}</td>"
            f"<td>{f.get('Aufgabe','')}</td>"
            f"<td>{due_cell}</td>"
            f"<td>{f.get('Priorität','')}</td>"
            f"<td>{f.get('Kategorie','')}</td>"
            f"<td>{f.get('Aufgabe von','')}</td>"
            f"<td>{f.get('Aufgabe für','')}</td></tr>"
        )
        rows.append(row)
        if notes:
            rows.append(f"<tr><td colspan='7'>{notes}</td></tr>")

    return header + "".join(rows) + "</table>"


def main(config_path: str):
    cfg: Config = load_config(config_path)
    client = NinoxClient(cfg.ninox)
    emailer = Emailer(cfg.smtp, debug=cfg.debug)

    tasks = client.get_tasks()
    persons = client.get_persons()

    email_map: Dict[str, str] = {}
    for p in persons:
        fields = p.get("fields", {})
        name = fields.get("fullName") or fields.get("Name")
        email = fields.get("E-Mail")
        if name and email:
            email_map[name] = email

    tasks_by_user: Dict[str, List[Dict]] = {}
    for t in tasks:
        users = t.get("fields", {}).get("Aufgabe für", "")
        for user in [u.strip() for u in str(users).split(',') if u.strip()]:
            tasks_by_user.setdefault(user, []).append(t)

    for username, user_tasks in tasks_by_user.items():
        user_tasks.sort(key=_task_sort_key)

        if cfg.debug and cfg.debug_user and username != cfg.debug_user:
            print(f"[DEBUG] Skipping {username}, not debug user")
            continue

        recipient = email_map.get(username)
        if not recipient:
            if cfg.debug:
                print(f"[DEBUG] No email for user {username}, skipping")
            continue

        if cfg.debug:
            print(f"[DEBUG] Preparing email for {username} with {len(user_tasks)} tasks")

        body = f"<h3>Offene Aufgaben ({len(user_tasks)})</h3>" + format_tasks(user_tasks)
        subject = "Deine offenen Aufgaben"
        try:
            emailer.send(
                recipient,
                subject,
                body,
                force_send=cfg.debug and username == cfg.debug_user,
            )
        except Exception as exc:
            print(f"Failed to send mail to {recipient}: {exc}")


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
