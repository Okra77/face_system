import streamlit as st
import sqlite3

# 连接到数据库
def get_db_connection():
    conn = sqlite3.connect('face_recognition.db')
    conn.row_factory = sqlite3.Row  # 使查询结果以字典形式返回
    return conn

# 删除用户
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    cursor.execute('DELETE FROM access_list WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

# 显示用户信息和通行状态
def display_user_info():
    st.title("查看资料库内名单")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT u.id, u.name, u.student_id, a.access_status
    FROM users u
    LEFT JOIN access_list a ON u.id = a.user_id
    ''')
    
    rows = cursor.fetchall()
    
    if rows:
        for row in rows:
            st.write(f"ID: {row['id']}")
            st.write(f"姓名: {row['name']}")
            st.write(f"学号: {row['student_id']}")
            st.write(f"通行状态: {row['access_status'] if row['access_status'] else '未定义'}")
            
            # 创建删除按钮
            delete_button = st.button(f"删除用户 {row['name']}", key=f"delete_{row['id']}")

            # 确认删除逻辑
            if delete_button:
                st.session_state[f'confirm_{row["id"]}'] = True

            if st.session_state.get(f'confirm_{row["id"]}', False):
                st.write(f"确认要删除用户 {row['name']} 吗？此操作无法撤销。")
                confirm_button = st.button(f"确认删除 {row['name']}", key=f"confirm_button_{row['id']}")
                cancel_button = st.button("取消", key=f"cancel_button_{row['id']}")

                if confirm_button:
                    delete_user(row['id'])
                    st.success(f"用户 {row['name']} 已被删除。")
                    st.session_state[f'confirm_{row["id"]}'] = False
                    st.experimental_rerun()  # 重新运行以刷新页面

                if cancel_button:
                    st.session_state[f'confirm_{row["id"]}'] = False

            st.write("---")
    else:
        st.write("资料库内没有用户信息。")
    
    conn.close()

# Streamlit应用程序
if __name__ == '__main__':
    display_user_info()
