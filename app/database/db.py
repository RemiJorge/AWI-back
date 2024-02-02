import asyncpg
import os

class Database:

    # Initialize the database 
    def __init__(self):
        self.user = os.environ.get("POSTGRES_USER")
        self.password = os.environ.get("POSTGRES_PASSWORD")
        self.host = os.environ.get("POSTGRES_HOST")
        self.port = os.environ.get("POSTGRES_PORT")
        self.database = os.environ.get("POSTGRES_DB")
        self._cursor = None

        self._connection_pool = None

    # Function to connect to the database
    # Create a connection pool
    async def connect(self):
        if not self._connection_pool:
            try:
                self._connection_pool = await asyncpg.create_pool(
                    min_size=10,
                    max_size=30,
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
    
    # Function to close the connection pool
    async def close(self):
        if self._connection_pool:
            await self._connection_pool.close()
            self._connection_pool = None

    # All of the functions below will first try and
    # get a connection from the connection pool
    # and then after executing the query, release the connection

    # Function to fetch multiple rows
    async def fetch_rows(self, query: str, *args):
        if not self._connection_pool:
            await self.connect()
        else:
            con = await self._connection_pool.acquire()
            try:
                result = await con.fetch(query, *args)
                return result
            except Exception as e:
                print("Database ERROR while fetching rows: ", e)
                raise e
            finally:
                await self._connection_pool.release(con)

    # Function to fetch a single row
    async def fetch_row(self, query: str, *args):
        if not self._connection_pool:
            await self.connect()
        else:
            con = await self._connection_pool.acquire()
            try:
                result = await con.fetchrow(query, *args)
                return result
            except Exception as e:
                print("Database ERROR while fetching row: ", e)
                raise e
            finally:
                await self._connection_pool.release(con)
    
    # Function to execute a query that returns a single value
    # Example: INSERT INTO users (username, email, password) VALUES ($1, $2, $3) RETURNING user_id;
    async def fetch_val(self, query: str, *args):
        if not self._connection_pool:
            await self.connect()
        else:
            con = await self._connection_pool.acquire()
            try:
                result = await con.fetchval(query, *args)
                return result
            except Exception as e:
                print("Database ERROR while fetching val: ", e)
                raise e
            finally:
                await self._connection_pool.release(con)

    # Function to execute any query
    async def execute(self, query: str, *args):
        if not self._connection_pool:
            await self.connect()
        else:
            con = await self._connection_pool.acquire()
            try:
                result = await con.execute(query, *args)
                return result
            except Exception as e:
                print("Database ERROR while executing query: ", e)
                raise e
            finally:
                await self._connection_pool.release(con)
                
    # Function to insert multiple rows
    async def insert_many(self, table_name: str, data: list, columns: list):
        if not self._connection_pool:
            await self.connect()
        else:
            con = await self._connection_pool.acquire()
            try:
                # Use copy_records_to_table for efficient bulk inserts
                result = await con.copy_records_to_table(
                    table_name=table_name,
                    records=data,
                    columns=columns,
                )
                return result
            except Exception as e:
                print("Database ERROR while inserting many: ", e)
                raise e
            finally:
                await self._connection_pool.release(con)
    
    # Function to execute the same query multiple times with different arguments
    async def execute_many(self, query: str, args: list):
        if not self._connection_pool:
            await self.connect()
        else:
            con = await self._connection_pool.acquire()
            try:
                await con.executemany(query, args)
            except Exception as e:
                print("Database ERROR while executing many: ", e)
                raise e
            finally:
                await self._connection_pool.release(con)


