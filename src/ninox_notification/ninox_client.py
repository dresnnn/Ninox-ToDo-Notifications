import requests
from typing import List, Dict, Any
from .config import NinoxConfig


class NinoxClient:
    def __init__(self, config: NinoxConfig):
        self.config = config

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.api_token}",
            "Content-Type": "application/json",
        }

    def get_tasks(
        self,
        status_field: str = "Status",
        closed_values: List[str] | None = None,
    ) -> List[Dict[str, Any]]:
        """Return all tasks which are not completed.

        Parameters
        ----------
        status_field: str
            Name of the field describing the task status in Ninox.
        closed_values: list[str] | None
            Status values that mark a task as completed. If ``None`` the
            defaults ``["erledigt", "abgeschlossen"]`` are used.
        """
        if closed_values is None:
            closed_values = ["erledigt", "abgeschlossen"]
        closed_values_lower = {v.lower() for v in closed_values}
        records = []
        page = 0
        per_page = 100
        while True:
            url = (
                f"{self.config.api_url}/teams/{self.config.team_id}/databases/{self.config.database_id}"\
                f"/tables/{self.config.table_id}/records?page={page}&per_page={per_page}"
            )
            try:
                resp = requests.get(url, headers=self._headers(), timeout=30)
                resp.raise_for_status()
                batch = resp.json()
            except requests.RequestException as exc:
                print(f"Request failed: {exc}")
                break
            if not batch:
                break
            records.extend(batch)
            page += 1
        # filter open tasks
        tasks = []
        for record in records:
            fields = record.get("fields", {})
            status = str(fields.get(status_field, "")).lower()
            if status not in closed_values_lower:
                tasks.append(record)
        return tasks
