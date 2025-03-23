import asyncpg
from decouple import config


class Database:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.pool = None
        print(f'Db obj created{self}')

    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(dsn=config('DB_LOCAL')
                # host=self.host,
                # port=self.port,
                # user=self.user,
                # password=self.password,
                # database=self.database,
            )
            print("✅ Database connection established")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")

    async def close(self):
        if self.pool:
            await self.pool.close()
            print("Database pool closed")

    async def execute(self, query: str, *args):
        """Выполняет SQL-запрос без возврата данных (INSERT, UPDATE, DELETE)"""
        async with self.pool.acquire() as conn:
            await conn.execute(query, *args)

    async def fetch(self, query: str, *args):
        """Выполняет SELECT-запрос и возвращает данные"""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def update(self, telegram_id: int, column: str, answer: str, minisurvey=False):
        """Сохраняет ответ пользователя в таблице"""
        query = f"UPDATE {'public.mini_survey' if minisurvey else 'public.survey'} SET {column} = $1 WHERE telegram_id = $2"
        # try:
        await self.execute(query, answer, telegram_id)
        #     print('ALTERATION MADE')
        # except Exception as e:
        #     print(f'Alteration failed: {e}')

    async def add_user(self, telegram_id: int, table: str):
        """Добавляет telegram_id в таблицу survey, если его еще нет"""
        query = f'INSERT INTO {table} (telegram_id) VALUES ($1) ON CONFLICT (telegram_id) DO NOTHING'
        await self.execute(query, telegram_id)