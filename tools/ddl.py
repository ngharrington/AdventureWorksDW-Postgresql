import pyodbc
import jinja2
import decimal
import datetime


class Table:
    
    def __init__(self, name, columns):
        self.name = name
        self.columns = columns

    @property
    def public_columns(self):
        return [c for c in self.columns if c[1] != bytearray]

    def generate_postgres_ddl(self):
        postgres_types = [pyodbc_to_postgres_type(c) for c in self.public_columns]
        zipped = zip(self.public_columns, postgres_types)
        template = """
CREATE TABLE {{ table_name }} ({% for desc in descriptions %}
    {{ desc[0][0] }} {{ desc[1] }}{% if not loop.last %},{% endif %}{% endfor %}
)
"""
        env = jinja2.Environment()
        template = env.from_string(template)
        return template.render(table_name=self.name, descriptions=zipped)


def get_connection(conn_type: str):
    if conn_type == "MSSQL":
        return pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=sqlserver;UID=sa;PWD=ThisIsAReallyCoolPassword123;Database=AdventureWorksDW2019')
    else:
        raise ValueError("Only MSSQL is currently supported")


def get_source_tables(conn: pyodbc.Connection):
    tables = []
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name
        FROM INFORMATION_SCHEMA.TABLES
        WHERE table_type = 'BASE TABLE'
    """)
    rows = cursor.fetchall()
    for r in rows:
        tables.append(r[0])
    cursor.close()
    return tables


def get_column_descriptions(conn: pyodbc.Connection, sql_server_source_table: str):
    cursor = conn.cursor()
    cursor.execute("SELECT TOP 0 * FROM {}".format(sql_server_source_table))
    description = cursor.description
    cursor.close()
    return description


def generate_ddl(table_name, column_descriptions):
    template = """
CREATE TABLE {{ table_name }} ({% for desc in descriptions %}
    {{ desc[0] }}{% if not loop.last %},{% endif %}{% endfor %}
)
"""
    env = jinja2.Environment()
    template = env.from_string(template)
    return template.render(table_name=table_name, descriptions=column_descriptions)


# {<class 'decimal.Decimal'>, <class 'datetime.datetime'>, <class 'str'>, <class 'bool'>, <class 'float'>, <class 'datetime.date'>, <class 'int'>, <class 'bytearray'>}
def pyodbc_to_postgres_type(column_description):
    if column_description[1] == str:
        size = column_description[3]
        type = "VARCHAR({})".format(size)
    elif column_description[1] == int:
        type = "INT"
    elif column_description[1] == decimal.Decimal:
        precision = column_description[4]
        scale = column_description[5]
        type = "NUMERIC({}, {})".format(precision, scale)
    elif column_description[1] == datetime.datetime:
        type = "TIMESTAMP"
    elif column_description[1] == bool:
        type = "BOOLEAN"
    elif column_description[1] == float:
        precision = column_description[4]
        scale = column_description[5]
        type = "NUMERIC({}, {})".format(precision, scale)
    elif column_description[1] == datetime.date:
        type = "DATE"
    else:
        raise ValueError("Unhandled data type")
    return type

        


if __name__ == "__main__":
    found_types = set()
    with get_connection("MSSQL") as conn:
        for t in get_source_tables(conn):
            desc = get_column_descriptions(conn, t)
            table = Table(t, desc)
            ddl = table.generate_postgres_ddl()
            print(ddl)