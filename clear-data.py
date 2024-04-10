import sqlite3

if __name__ == '__main__':
    NAME_DB = "database.db"
    conn = sqlite3.connect(NAME_DB)
    conn.execute("DELETE FROM tbl_article")
    conn.commit()
    print("Data Berhasil di Hapus")
