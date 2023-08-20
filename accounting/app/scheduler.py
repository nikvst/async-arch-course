from rocketry import Rocketry
from rocketry.conditions.api import cron

from app.db import async_session
from app.use_cases.accounts import CloseCurrentDayUseCase

app = Rocketry()


@app.task(cron("0 0 * * *"))
async def do_daily():
    async with async_session.begin() as session:
        await CloseCurrentDayUseCase(session).execute()


if __name__ == "__main__":
    app.run()
