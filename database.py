import sqlite3

# 连接到数据库（如果数据库不存在会自动创建）
conn = sqlite3.connect('face_recognition.db')
c = conn.cursor()

# 创建用户信息表
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    student_id TEXT NOT NULL,
    photo BLOB
)
''')

# 创建通行名单表
c.execute('''
CREATE TABLE IF NOT EXISTS access_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    access_status TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# 提交并关闭连接
conn.commit()
conn.close()
