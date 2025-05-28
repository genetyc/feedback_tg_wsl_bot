import asyncpg
from openpyxl import load_workbook
from decouple import config
from aiogram.types import FSInputFile

class Database:
    admins = [int(admin_id) for admin_id in config('ADMINS').split(',')]
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.pool = None

    async def connect(self):
        try:
            # self.pool = await asyncpg.create_pool(dsn=self.database # TODO это вообще чтоооо
            #     # host=self.host,
            #     # port=self.port,
            #     # user=self.user,
            #     # password=self.password,
            #     # database=self.database,
            # )
            
            dsn = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
            self.pool = await asyncpg.create_pool(dsn=dsn)
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

    async def fetchval(self, query: str, *args):
        """Выполняет SELECT-запрос и возвращает значение"""
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    async def update(self, telegram_id: int, column: str, answer: str, minisurvey=False):
        """Сохраняет ответ пользователя в таблице"""
        query = f"UPDATE {'public.mini_survey' if minisurvey else 'public.survey'} SET {column} = $1 WHERE telegram_id = $2"
        await self.execute(query, answer, telegram_id)

    async def add_user(self, telegram_id: int, table: str):
        """Добавляет telegram_id в таблицу survey, если его еще нет"""
        query = f'INSERT INTO {table} (telegram_id) VALUES ($1) ON CONFLICT (telegram_id) DO NOTHING'
        await self.execute(query, telegram_id)

    async def del_user(self, telegram_id: int, minisurvey=False):
        query = f'DELETE FROM public.{'survey' if not minisurvey else 'mini_survey'} WHERE telegram_id = $1'
        await self.execute(query, telegram_id)

    async def count_users(self):
        query = 'SELECT COUNT(*) FROM public.mini_survey WHERE is_complete = TRUE'
        return await self.fetchval(query)

    async def get_average_edu_rating(self):
        """Средний рейтинг и количество рецендентов из небольшого опроса"""
        rating_query = f'SELECT AVG(edu_rating) FROM public.mini_survey WHERE edu_rating > 0'
        total_query = f'SELECT COUNT(edu_rating) FROM public.mini_survey WHERE edu_rating > 0'
        
        rating_result = await self.fetchval(rating_query)
        total_result = await self.fetchval(total_query)
        return [rating_result, total_result]

    async def get_rating_range(self):
        neg_rating = await self.fetchval('SELECT COUNT(*) FROM public.mini_survey WHERE edu_rating > 0 AND edu_rating < 5')
        neutral_rating = await self.fetchval('SELECT COUNT(*) FROM public.mini_survey WHERE edu_rating > 4 AND edu_rating < 8')
        pos_rating = await self.fetchval('SELECT COUNT(*) FROM public.mini_survey WHERE edu_rating > 7')
        return [neg_rating, neutral_rating, pos_rating]

    async def gather_opinion(self):
        """Количество недовольных людей"""
        disappointed_query = f'SELECT COUNT(*) FROM public.mini_survey WHERE is_disappointed = TRUE AND is_complete = TRUE'
        return await self.fetchval(disappointed_query)
    
    async def who_would_share(self):
        """Количество людей, готовых порекомендовать студию"""
        share_query = 'SELECT COUNT(*) FROM public.mini_survey WHERE NOT would_u_share = $1 AND is_complete = True'
        return await self.fetchval(share_query, 'Нет')
    
    async def clear_table(self, exceptions=admins, case=3): # case 1: clear Survey, case 2: clear MiniSurvey, case 3: clear both
        placeholders = ','.join(f"${i+1}" for i in range(len(exceptions)))
        query_survey = f"""
            DELETE FROM public.survey
            WHERE telegram_id NOT IN ({placeholders})
        """
        query_mini_survey = f"""
            DELETE FROM public.mini_survey
            WHERE telegram_id NOT IN ({placeholders})
        """
        if case==1:
            await self.execute(query_survey, *exceptions)
        elif case==2:
            await self.execute(query_mini_survey, *exceptions)
        else:
            await self.execute(query_survey, *exceptions)
            await self.execute(query_mini_survey, *exceptions)

    from aiogram import Bot
    async def export_to_excel_and_send(self, bot: Bot, chat_id: int):
        survey_query = "SELECT * FROM public.survey"
        minis_query = "SELECT * FROM public.mini_survey"
        survey_rows = await self.fetch(survey_query)
        minis_rows = await self.fetch(minis_query)
        wb = load_workbook("templ.xlsx")
        ws = wb['Большой опрос']
        mini_ws = wb['Качество обучения']
        
        async def survey_export(ws, rows):
            for idx, row in enumerate(rows, start=3):
                for index, x in enumerate(row, 65):
                    if index == 65 or index == 66:
                        cell = ws[f'{chr(index)}{idx}']
                        cell.value = x
                    elif 67 <= index <= 73:
                        cell = ws[f'{chr(index+1)}{idx}']
                        cell.value = x
                    elif index == 74 or index == 77:
                        temp=x.split(';')
                        cor = 2 if index == 77 else 0
                        for i in range(len(temp)):
                            cell = ws[f'{chr(index+1+i+cor)}{idx}']
                            cell.value = temp[i]
                    elif index == 75 or index == 76:
                        cell = ws[f'{chr(index+3)}{idx}']
                        cell.value = x
                    elif 77 < index < 84:
                        cell = ws[f'{chr(index+6)}{idx}']
                        cell.value = x
                    else:
                        cell = ws[f'C{idx}']
                        cell.value = x

        async def minisurvey_export(ws, rows):
            for idx, row in enumerate(rows, start=2):
                for index, x in enumerate(row, 65):
                    if index == 73 or index == 74:
                        cell = ws[f'{chr(index+1)}{idx}']
                        cell.value = x
                    elif index == 75:
                        cell = ws[f'{chr(index-2)}{idx}']
                        cell.value = x
                    else:
                        cell = ws[f'{chr(index)}{idx}']
                        cell.value = x
                    avg_rating, users_total = await self.get_average_edu_rating()
            neg_rating, neutral_rating, pos_rating = await self.get_rating_range()
            for index, value in enumerate([users_total, avg_rating, neg_rating, neutral_rating, pos_rating], start=1):
                cell = ws[f'P{index}']
                cell.value = value

        await survey_export(ws, survey_rows)
        await minisurvey_export(mini_ws, minis_rows)
        wb.save('poll.xlsx')
        file = FSInputFile('poll.xlsx')
        await bot.send_document(chat_id=chat_id, document=file, caption="📄 Данные опроса")
        import os
        os.remove('poll.xlsx')