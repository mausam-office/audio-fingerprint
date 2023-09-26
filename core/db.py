import psycopg2
from .utils import debug_error_log


def db_connection():
    conn = psycopg2.connect("dbname=dejavu user=postgres password=root")
    return conn

def execute_query(query:str, values:tuple=(), insert:bool=False, req_response:bool=False, top_n_rows:int=-1):
    conn = None
    cur = None
    data = None
    
    try:
        conn = db_connection()
        cur = conn.cursor()
        if insert or values:
            if values:
                debug_error_log('Values not supplied for query')
                return
            cur.execute(query, values)
        else:
            if values:
                debug_error_log('Does your query requrires values? ')
                debug_error_log('Executing without using values')
            cur.execute(query)
        conn.commit()
        
        # call fucntion to extract response if response required
        
        if req_response:
            data = cur.fetchall() if top_n_rows <= 0 else \
                    cur.fetchone() if top_n_rows == 1 else cur.fetchmany(size=top_n_rows)
            # data = cur.fetchone()
            # print(f"{data = }")

    except (Exception, psycopg2.DatabaseError) as error:
        debug_error_log(f"Error \n{error}")
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()
    
    if req_response:
        return data
    return

def get_advertisement_id(advertisemnet_name):
    query_select_song_id = f"""
        SELECT song_id FROM songs
        WHERE song_name='{advertisemnet_name}'
    """
    data = execute_query(query_select_song_id, req_response=True, top_n_rows=1)
    
    song_id = data[0] if isinstance(data, tuple) else data
    # print(f"{song_id = }")
    return song_id
