import sqlite3
def init_db():
    conn=sqlite3.connect('model_feedback.db')
    cursor=conn.cursor()
    with open('Schema.sql') as f :
        cursor.executescript(f.read())
    conn.commit()
    conn.close()
    print("✅ Feedback DB initialized.")

if __name__=='__main__':
    init_db()