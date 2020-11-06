import psycopg2

# conn = psycopg2.connect(
#     host="localhost",
#     database="suppliers",
#     user="postgres",
#     password="root")
def connect_db():
    conn=None
    try:
        # # read connection parameters
        # params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        # conn = psycopg2.connect(**params)
        conn=psycopg2.connect("dbname=suppliers user=postgres password=root")
        # create a cursor
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return conn


if __name__ == '__main__':
    connect_db()