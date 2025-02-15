import argparse
import sqlite3


def create_db_and_table(db_name, table_name, dimensionality):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    columns = ', '.join([f'component{i} float' for i in range(1, dimensionality+1)])
    cursor.execute(f"CREATE TABLE {table_name} (term text primary key, {columns})")
    return conn, cursor

def insert_data(conn, cursor, table_name, embeddings_file, commit_after):
    with open(embeddings_file, 'r') as f:
        for i, line in enumerate(f):
            data = line.strip().split()
            term = data[0]
            components = data[1:]
            cursor.execute(f"INSERT INTO {table_name} VALUES (?, {', '.join(['?']*len(components))})", [term] + components)
            if (i+1) % commit_after == 0:
                conn.commit()
        conn.commit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--embeddings-file")
    parser.add_argument("--sqlite-database")
    parser.add_argument("--table")
    parser.add_argument("--dimensionality", type=int)
    parser.add_argument("--commit-after", type=int, default=1000)
    args = parser.parse_args()

    conn, cursor = create_db_and_table(args.sqlite_database, args.table, args.dimensionality)
    insert_data(conn, cursor, args.table, args.embeddings_file, args.commit_after)
