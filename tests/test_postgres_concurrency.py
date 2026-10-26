
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.db import DATABASE_URL
from app.main import app


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_POSTGRES_INTEGRATION") != "1",
    reason="Set RUN_POSTGRES_INTEGRATION=1 to run PostgreSQL tests",
)


def test_concurrent_updates_only_allow_one_version():
    assert DATABASE_URL.startswith("postgresql"), (
        "This test must run against PostgreSQL, not SQLite."
    )
    assert DATABASE_URL.rsplit("/", 1)[-1] == "taskflow_test", (
    "Integration tests must use the taskflow_test database."
    )

    title = f"Concurrency test {uuid4()}"

    with TestClient(app) as client_a, TestClient(app) as client_b:
        created = client_a.post("/tasks", json={"title": title})
        assert created.status_code == 201
        task_id = created.json()["id"]
        barrier = Barrier(2)

        def update_task(client, priority):
            barrier.wait(timeout=10)
            return client.patch(
                f"/tasks/{task_id}",
                json={"version": 1, "priority": priority},
            )

        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                future_a = executor.submit(update_task, client_a, 1)
                future_b = executor.submit(update_task, client_b, 2)

                response_a = future_a.result(timeout=20)
                response_b = future_b.result(timeout=20)

            statuses = sorted(
                [response_a.status_code, response_b.status_code]
            )
            assert statuses == [200, 409]

            final_response = client_a.get(f"/tasks/{task_id}")
            assert final_response.status_code == 200
            assert final_response.json()["version"] == 2

        finally:
            client_a.delete(f"/tasks/{task_id}")
