# Code generated automatically.

from bot.schemas import scheduler as scheduler_schemas

from .db_dump import job as db_dump


list_of_jobs: list[scheduler_schemas.JobInfo] = [
    scheduler_schemas.JobInfo(
        **{'trigger': 'cron', 'hour': 3, 'config': {'send_logs': True}},
        func=db_dump,
        name='db_dump',
    ),
]


__all__ = [
    'list_of_jobs',
]
