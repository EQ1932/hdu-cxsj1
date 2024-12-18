import mysql.connector

# 连接数据库
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yuki&yunai",
    database="book_management"
)

cursor = conn.cursor()

# 向每个用户插入100本书籍
for user_id in range(1, 6):  # 假设用户ID从1到5
    for i in range(1, 101):  # 每个用户插入100本书
        title = f"Book {i} by User {user_id}"
        author = f"Author {user_id}"
        publisher = f"Publisher {user_id}"
        description = f"This is the description of Book {i}."
        cover_image = f"cover{user_id}.jpg"
        
        # 插入书籍数据
        cursor.execute("""
            INSERT INTO books (user_id, title, author, publisher, description, cover_image)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, title, author, publisher, description, cover_image))
    
    conn.commit()

cursor.close()
conn.close()

print("模拟数据插入完成！")
