import streamlit as st
import sqlite3

# 上传用户信息
st.title("用户信息上传")
name = st.text_input("姓名")
student_id = st.text_input("学号")
photo = st.file_uploader("上传照片", type=["jpg", "jpeg", "png"])

if st.button("提交"):
    if name and student_id and photo:
        photo_bytes = photo.read()
        # 连接到数据库
        conn = sqlite3.connect('face_recognition.db')
        c = conn.cursor()
        # 插入用户信息
        c.execute('INSERT INTO users (name, student_id, photo) VALUES (?, ?, ?)', (name, student_id, photo_bytes))
        conn.commit()
        conn.close()
        st.success("用户信息上传成功")
    else:
        st.error("请填写姓名、学号并上传照片")

user_id = st.number_input("用户ID", min_value=1)
access_status = st.selectbox("通行状态", ["allowed", "denied"])

if st.button("更新通行状态"):
    conn = sqlite3.connect('face_recognition.db')
    c = conn.cursor()
    c.execute('INSERT INTO access_list (user_id, access_status) VALUES (?, ?)', (user_id, access_status))
    conn.commit()
    conn.close()
    st.success("通行状态更新成功")


