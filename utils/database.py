import time
import pytz
from datetime import datetime, timedelta

import asyncpg

from loader import asyncpg_pool

async def create_table_users(delete_table=False):
    async with asyncpg_pool.acquire() as conn:
        if delete_table:
            await conn.execute('DROP TABLE IF EXISTS Users')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS Users(
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                balance INTEGER DEFAULT 0,
                ban_status INTEGER DEFAULT 0,
                ban_reason TEXT
            )
        ''')

async def create_table_orders_history(delete_table=False):
    async with asyncpg_pool.acquire() as conn:
        if delete_table:
            await conn.execute('DROP TABLE IF EXISTS OrdersHistory')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS OrdersHistory(
                num SERIAL PRIMARY KEY,
                user_id BIGINT,
                amount INTEGER,
                comment TEXT,
                create_time BIGINT,
                admin_id BIGINT,
                cryptobot_check TEXT,
                status TEXT DEFAULT 'pending'
            )
        ''')

async def create_table_reports_history(delete_table=False):
    async with asyncpg_pool.acquire() as conn:
        if delete_table:
            await conn.execute('DROP TABLE IF EXISTS ReportsHistory')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS ReportsHistory(
                num SERIAL PRIMARY KEY,
                user_id BIGINT,
                data TEXT,
                file_id TEXT,
                create_time BIGINT,
                admin_id BIGINT,
                edited_status INTEGER DEFAULT 0
            )
        ''')


async def add_user(user_id, username):
    async with asyncpg_pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO Users(user_id, username)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO UPDATE
            SET username = EXCLUDED.username
        ''', user_id, username)

async def get_user_info(user_id, params):
    async with asyncpg_pool.acquire() as conn:
        row = await conn.fetchrow(f'SELECT {params} FROM Users WHERE user_id = $1', user_id)
        return row if ',' in params else row[0] if row else None

async def update_user_info(user_id, column, param):
    async with asyncpg_pool.acquire() as conn:
        await conn.execute(f'UPDATE Users SET {column} = $1 WHERE user_id = $2', param, user_id)

async def get_table_info(table, num, params, id_name='num'):
    async with asyncpg_pool.acquire() as conn:
        if isinstance(num, str) and num.isdigit(): num = int(num)
        row = await conn.fetchrow(f'SELECT {params} FROM {table} WHERE {id_name} = $1', num)
        return row if ',' in params else row[0] if row else None

async def update_table_info(table, num, column, param, id_name='num'):
    async with asyncpg_pool.acquire() as conn:
        if isinstance(num, str) and num.isdigit(): num = int(num)
        await conn.execute(f'UPDATE {table} SET {column} = $1 WHERE {id_name} = $2', param, num)

async def add_order(user_id, amount, comment, create_time, admin_id):
    async with asyncpg_pool.acquire() as conn:
        return await conn.fetchval('''
            INSERT INTO OrdersHistory(user_id, amount, comment, create_time, admin_id) VALUES($1, $2, $3, $4, $5) RETURNING num
        ''', user_id, amount, comment, create_time, admin_id)

async def add_report(user_id, data, file_id, create_time, admin_id):
    async with asyncpg_pool.acquire() as conn:
        return await conn.fetchval('''
            INSERT INTO ReportsHistory(user_id, data, file_id, create_time, admin_id) VALUES($1, $2, $3, $4, $5) RETURNING num
        ''', user_id, data, file_id, create_time, admin_id)

async def get_all_users_ids():
    async with asyncpg_pool.acquire() as conn:
        row = await conn.fetch('SELECT user_id FROM Users')
        return [user_id for (user_id,) in row]

async def get_all_user_buys_count(user_id):
    async with asyncpg_pool.acquire() as conn:
        row = await conn.fetchrow('SELECT COUNT(*) FROM OrdersHistory WHERE user_id = $1', user_id)
        return row[0]

async def update_user_balance(user_id, amount):
    async with asyncpg_pool.acquire() as conn:
        await conn.execute('UPDATE Users SET balance = balance + $1 WHERE user_id = $2', amount, user_id)

async def get_all_users():
    async with asyncpg_pool.acquire() as conn:
        row = await conn.fetch('SELECT user_id, username FROM Users')
        return row

async def get_all_admin_orders(admin_id):
    async with asyncpg_pool.acquire() as conn:
        row = await conn.fetch('SELECT num, amount, create_time, status FROM OrdersHistory WHERE admin_id = $1 ORDER BY create_time DESC', admin_id)
        return row

async def get_all_user_orders(user_id):
    async with asyncpg_pool.acquire() as conn:
        row = await conn.fetch('SELECT num, amount, create_time, status FROM OrdersHistory WHERE user_id = $1 ORDER BY create_time DESC', user_id)
        return row

async def get_all_reports():
    async with asyncpg_pool.acquire() as conn:
        row = await conn.fetch('SELECT num, create_time, edited_status FROM ReportsHistory ORDER BY create_time DESC')
        return row

async def get_all_admin_reports(admin_id):
    async with asyncpg_pool.acquire() as conn:
        row = await conn.fetch('SELECT num, create_time, edited_status FROM ReportsHistory WHERE admin_id = $1 ORDER BY create_time DESC', admin_id)
        return row

async def get_all_user_reports(user_id):
    async with asyncpg_pool.acquire() as conn:
        row = await conn.fetch('SELECT num, create_time, edited_status FROM ReportsHistory WHERE user_id = $1 ORDER BY create_time DESC', user_id)
        return row

async def get_top_users():
    async with asyncpg_pool.acquire() as conn:
        result = await conn.fetch('''
            SELECT u.username, SUM((r.data::jsonb->>'count')::int) as total_count
            FROM Users u
            JOIN ReportsHistory r ON u.user_id = r.user_id
            GROUP BY u.username
            ORDER BY total_count DESC
        ''')

        # Преобразование результатов в список словарей
        top_users = [(record["username"], record["total_count"]) for record in result]
        return top_users

async def get_top_users_with_date_range(start_date, end_date):
    async with asyncpg_pool.acquire() as conn:
        result = await conn.fetch('''
            SELECT u.username, SUM((r.data::jsonb->>'count')::int) as total_count
            FROM Users u
            JOIN ReportsHistory r ON u.user_id = r.user_id
            WHERE r.date BETWEEN $1 AND $2
            GROUP BY u.username
            ORDER BY total_count DESC
        ''', start_date, end_date)

        # Преобразование результатов в список словарей
        top_users = [(record["username"], record["total_count"]) for record in result]
        return top_users

async def get_reports_by_date(day, month, year):
    date_str = f"{day} {month} {year}"
    msk_tz = pytz.timezone('Europe/Moscow')
    naive_datetime = datetime.strptime(date_str, "%d %m %Y")
    local_datetime = msk_tz.localize(naive_datetime)
    start_of_day = int(local_datetime.timestamp())
    end_of_day = start_of_day + 86400
    
    async with asyncpg_pool.acquire() as conn:
        results = await conn.fetch('''
            SELECT U.username, R.data
            FROM Users U
            JOIN ReportsHistory R ON U.user_id = R.user_id
            WHERE R.create_time >= $1 AND R.create_time < $2
        ''', start_of_day, end_of_day)
        
        return [(record['username'], record['data']) for record in results]
