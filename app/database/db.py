import asyncpg
import os

class Database:
    def __init__(self):
        self.user = os.environ.get("POSTGRES_USER")
        self.password = os.environ.get("POSTGRES_PASSWORD")
        self.host = "localhost"
        self.port = "5432"
        self.database = os.environ.get("POSTGRES_DB")
        self._cursor = None

        self._connection_pool = None
        self.con = None

    async def connect(self):
        if not self._connection_pool:
            try:
                self._connection_pool = await asyncpg.create_pool(
                    min_size=1,
                    max_size=10,
                    command_timeout=60,
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                )

            except Exception as e:
                print("Database ERROR while connecting: ", e)
                raise e
    
    async def close(self):
        if self._connection_pool:
            await self._connection_pool.close()
            self._connection_pool = None

    async def fetch_rows(self, query: str, *args):
        if not self._connection_pool:
            await self.connect()
        else:
            self.con = await self._connection_pool.acquire()
            try:
                result = await self.con.fetch(query, *args)
                return result
            except Exception as e:
                print("Database ERROR while fetching rows: ", e)
                raise e
            finally:
                await self._connection_pool.release(self.con)

    async def fetch_row(self, query: str, *args):
        if not self._connection_pool:
            await self.connect()
        else:
            self.con = await self._connection_pool.acquire()
            try:
                result = await self.con.fetchrow(query, *args)
                return result
            except Exception as e:
                print("Database ERROR while fetching row: ", e)
                raise e
            finally:
                await self._connection_pool.release(self.con)
    
    async def fetch_val(self, query: str, *args):
        if not self._connection_pool:
            await self.connect()
        else:
            self.con = await self._connection_pool.acquire()
            try:
                result = await self.con.fetchval(query, *args)
                return result
            except Exception as e:
                print("Database ERROR while fetching val: ", e)
                raise e
            finally:
                await self._connection_pool.release(self.con)

    async def execute(self, query: str, *args):
        if not self._connection_pool:
            await self.connect()
        else:
            self.con = await self._connection_pool.acquire()
            try:
                result = await self.con.execute(query, *args)
                return result
            except Exception as e:
                print("Database ERROR while executing query: ", e)
                raise e
            finally:
                await self._connection_pool.release(self.con)


