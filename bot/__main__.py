import asyncio
import traceback

import asyncpg.exceptions
import loguru
import sqlalchemy.exc
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from bot.bot_helper import send
from bot.config import get_settings
from bot.creator import get_app


app = get_app()


@app.exception_handler(Exception)
async def exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:  # pragma: no cover
    response = JSONResponse(
        status_code=500,
        content={'message': 'Internal server error'},
    )
    settings = get_settings()
    message_list = [
        f'*Exception occurred on {settings.PROJECT_NAME}*:',
        'REQUEST:',
    ]
    for key, value in request.items():
        message_list.append(f'\t- {key}: {value}')
    message_list.extend(
        [
            '',
            f'EXCEPTION: {exc}',
        ]
    )
    if isinstance(
        exc,
        (
            asyncpg.exceptions.TooManyConnectionsError,
            sqlalchemy.exc.TimeoutError,
        ),
    ):
        response = JSONResponse(
            status_code=429,
            content={'message': 'Too many requests'},
        )
        # await send.send_traceback_message_safe(
        #     logger=loguru.logger,
        #     message='\n'.join(message_list),
        #     code='Without code'
        # )
    else:
        await send.send_traceback_message(
            '\n'.join(message_list), code=traceback.format_exc()
        )
    return response


if __name__ == '__main__':  # pragma: no cover
    settings = get_settings()

    asyncio.get_event_loop().run_until_complete(
        send.send_message_safe(
            logger=loguru.logger,
            message=f'Created application: ' f'debug={settings.DEBUG}',
            level='info',
        )
    )
