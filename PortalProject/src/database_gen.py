import sqlite3 as sqlite

nc4h_database_con = sqlite.connect('nc4h.db')

tables_script = """

    DROP TABLE IF EXISTS "page";
    DROP TABLE IF EXISTS "medialinks";
    DROP TABLE IF EXISTS "otherlinks";


    CREATE TABLE "page" (
        pageid    INTEGER UNIQUE,
        nc4her    TEXT,
        pagename    TEXT,
        wtd    TEXT,
        textsource TEXT,
         notes,
        PRIMARY KEY(pageid)
    );

    CREATE TABLE "medialinks" (
        mediaid INTEGER UNIQUE PRIMARY KEY,
        link TEXT,
        pageid INTEGER
    );

    CREATE TABLE "otherlinks" (
        otherid INTEGER UNIQUE PRIMARY KEY,
        link TEXT,
        pageid INTEGER
    );
    """

try:
    cursor = nc4h_database_con.cursor()
    cursor.executescript(tables_script)
    nc4h_database_con.commit()
    print "Operation complete\n"                    
except Exception, e:
    print "Something went wrong:"
    print e
finally:    
    nc4h_database_con.close()
