
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)

# 数据库连接函数
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='yuki&yunai',  # 替换为你的 MySQL 密码
        database='book_management'
    )

# 首页: 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # 登录成功后，跳转到书籍管理页面，并传递用户信息
            return redirect(url_for('book_management', user_id=user['user_id'], nickname=user['nickname'], gender=user['gender']))
        else:
            return "Invalid username or password", 401

    return render_template('login.html')




# 书籍管理页面
@app.route('/book_management/<int:user_id>', methods=['GET', 'POST'])
def book_management(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 获取当前用户信息（nickname 和 gender）
    cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
    user = cursor.fetchone()

    # 获取查询条件（如果有）
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)  # 获取当前页码
    per_page = 20  # 每页显示20本书
    offset = (page - 1) * per_page

    # 查询书籍，支持搜索（书名和简介）
    if search_query:
        cursor.execute('''
            SELECT * FROM books 
            WHERE user_id = %s 
            AND (title LIKE %s OR description LIKE %s) 
            LIMIT %s OFFSET %s
        ''', (user_id, f'%{search_query}%', f'%{search_query}%', per_page, offset))
    else:
        cursor.execute('''
            SELECT * FROM books 
            WHERE user_id = %s 
            LIMIT %s OFFSET %s
        ''', (user_id, per_page, offset))
    
    books = cursor.fetchall()

    # 获取总书籍数量，用于分页计算
    cursor.execute('SELECT COUNT(*) AS total_books FROM books WHERE user_id = %s', (user_id,))
    total_books = cursor.fetchone()['total_books']
    
    conn.close()

    # 计算总页数
    total_pages = (total_books + per_page - 1) // per_page

    return render_template('book_management.html', books=books, user_id=user_id, nickname=user['nickname'], gender=user['gender'], page=page, total_pages=total_pages, search_query=search_query)




# 添加书籍页面
@app.route('/add_book/<int:user_id>', methods=['GET', 'POST'])
def add_book(user_id):
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        publisher = request.form['publisher']
        description = request.form['description']
        cover_image = request.form['cover_image']  # 在实际情况中可以处理文件上传
        
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO books (user_id, title, author, publisher, description, cover_image)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (user_id, title, author, publisher, description, cover_image))
        
        conn.commit()
        conn.close()

        flash('Book added successfully!', 'success')
        return redirect(url_for('book_management', user_id=user_id))

    return render_template('add_book.html', user_id=user_id)


# 删除书籍
@app.route('/delete_book/<int:user_id>/<int:book_id>', methods=['POST'])
def delete_book(user_id, book_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM books WHERE book_id = %s AND user_id = %s', (book_id, user_id))
    
    conn.commit()
    conn.close()

    flash('Book deleted successfully!', 'success')
    return redirect(url_for('book_management', user_id=user_id))


# 编辑书籍
@app.route('/edit_book/<int:user_id>/<int:book_id>', methods=['GET', 'POST'])
def edit_book(user_id, book_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT * FROM books WHERE book_id = %s AND user_id = %s', (book_id, user_id))
    book = cursor.fetchone()

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        publisher = request.form['publisher']
        description = request.form['description']
        cover_image = request.form['cover_image']  # 在实际情况中可以处理文件上传

        cursor.execute('''
            UPDATE books 
            SET title = %s, author = %s, publisher = %s, description = %s, cover_image = %s 
            WHERE book_id = %s AND user_id = %s
        ''', (title, author, publisher, description, cover_image, book_id, user_id))

        conn.commit()
        conn.close()

        flash('Book updated successfully!', 'success')
        return redirect(url_for('book_management', user_id=user_id))

    conn.close()
    return render_template('edit_book.html', book=book, user_id=user_id)



# 处理用户信息修改
@app.route('/edit_profile/<int:user_id>', methods=['GET', 'POST'])
def edit_profile(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        # 获取修改后的信息
        nickname = request.form['nickname']
        gender = request.form['gender']
        password = request.form['password']

        # 更新用户信息
        cursor.execute('UPDATE users SET nickname = %s, gender = %s, password = %s WHERE user_id = %s',
                       (nickname, gender, password, user_id))
        conn.commit()
        conn.close()

        # 修改成功后，跳转到书籍管理页面
        return redirect(url_for('book_management', user_id=user_id))

    # 获取用户信息
    cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
    user = cursor.fetchone()
    conn.close()

    return render_template('edit_profile.html', user=user)



if __name__ == '__main__':
    app.run(debug=True)
