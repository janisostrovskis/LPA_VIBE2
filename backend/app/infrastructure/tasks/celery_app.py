"""Celery application instance for the LPA backend worker.

Soft rollback path: set CELERY_TASK_ALWAYS_EAGER=1 (plus
EMAIL_QUEUE_BACKEND=celery) to run tasks inline in the caller's thread
without a live Redis broker. Eager mode opens its own worker DB session
via build_worker_sessionmaker(), so it is equivalent to a real worker
for correctness purposes.
"""

from __future__ import annotations

import os

from celery import Celery

broker_url: str = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")

app = Celery(
    "lpa",
    broker=broker_url,
    include=["app.infrastructure.tasks.email_tasks"],
)

app.conf.task_always_eager = os.environ.get("CELERY_TASK_ALWAYS_EAGER", "").lower() in (
    "1",
    "true",
    "yes",
)
# Eager mode re-raises task exceptions in the caller — required for
# test correctness and to surface worker bugs during local dev.
app.conf.task_eager_propagates = True
