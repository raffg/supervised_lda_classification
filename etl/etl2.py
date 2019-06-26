import psycopg2 as pg
import yaml
import pandas as pd


def load_config() -> list:
    schema_path = '../misc/schemas.yaml'
    with open(schema_path) as schema_file:
        config = yaml.load(schema_file)
    return config


def create_tables(config: list, connection: pg.extensions.connection):
    cur = connection.cursor()
    for table in config:
        name = table.get('name')
        schema = table.get('schema')
        ddl = f"""CREATE TABLE IF NOT EXISTS {name} ({schema})"""
        cur.execute(ddl)

    connection.commit()


def transform_tables(config: list):

    data_path = '../data/'

    for table in config:
        table_name = table.get('name')
        table_source = data_path + f"{table_name}.csv"
        table_cols = [str.upper(i) for i in table.get('columns')]
        df = pd.read_csv(table_source)
        df_reorder = df[table_cols]  # rearrange column here
        df_reorder.to_csv(table_source, index=False)


def load_tables(config: list, connection: pg.extensions.connection):

    # iterate and load
    cur = connection.cursor()
    data_path = '../data/'

    for table in config:
        table_name = table.get('name')
        table_source = data_path + f"{table_name}.csv"
        with open(table_source, 'r') as f:
            next(f)
            cur.copy_expert(f"COPY {table_name} FROM STDIN CSV NULL AS ''", f)
        connection.commit()


def etl():
    connection = pg.connect(
        host='localhost',
        port=54320,
        dbname='ht_db',
        user='postgres'
    )

    config = load_config()
    create_tables(config=config, connection=connection)
    transform_tables(config=config)
    load_tables(config=config, connection=connection)


if __name__ == '__main__':
    etl()
