import streamlit as st
import cv2
import numpy as np
import time
from datetime import datetime
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import smtplib
import sqlite3


recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('face3.yml')
cascade_path = "xml/haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(cascade_path)

DATABASE = 'face_recognition.db'

name = {
        '1': 'hsx',
        '2': 'hjy',
        '3': 'jzq',
    }


tab1, tab2 = st.tabs(["陌生访客留言", "新访客登入&旧访客识别"])



def detect_face(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=7,minSize=(100,100),flags=cv2.CASCADE_SCALE_IMAGE)
    return faces, gray

def new_user_registration(frame):
    with st.form(key='signup_form'):
        receiver = '3305364651@qq.com'
        to = [receiver]

        msg = MIMEMultipart()
            
        # 输入姓名和学号
        name = st.text_input("姓名")
        student_id = st.text_input("学号")
            
        # 上传照片
        st.image(frame, caption="上传照片", use_column_width=True)
        
        msg['Subject'] = "人脸识别注册信息"
        msg['From'] = msg_from

        # 添加姓名和学号到邮件内容
        body = f"姓名: {name}\n学号: {student_id}"
        msg.attach(MIMEText(body, 'plain', 'utf-8'))


        submit_signup_button = st.form_submit_button("提交注册信息")
        # 读取并附加图片
        if frame is not None:
            _, img_encoded = cv2.imencode('.jpg', frame)
            img_data = img_encoded.tobytes()
            image = MIMEImage(img_data, name='processed_image.jpg')
            msg.attach(image)

        
        # 检查所有输入是否已完成
        if submit_signup_button:
            try:
                s = smtplib.SMTP_SSL("smtp.qq.com", 465)
                s.starttls()
                s.login(msg_from, passwd)
                s.sendmail(msg_from, to, msg.as_string())
                s.quit()
                st.success("申请成功！")
            except Exception as e:
                st.error(f"发送邮件失败: {e}")



# 人脸识别
def display_camera():
    camera = cv2.VideoCapture(0)
    name = {
        '1': 'hsx',
        '2': 'hjy',
        '3': 'jzq',
    }
    
    video_placeholder = st.empty()
    image_placeholder = st.empty()
    text_placeholder1 = st.empty()
    text_placeholder2 = st.empty()

    
    if not camera.isOpened():
        st.error("无法打开摄像头，请确保摄像头已连接或没有被其他应用程序占用。")
        return
    
    while True:
        
        ret, frame = camera.read()
        if not ret:
            st.error("无法读取摄像头。")
            break

        
        face,gray = detect_face(frame)

        for (x, y, w, h) in face:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            id, conf = recognizer.predict(gray[y:y+h, x:x+w])
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute('SELECT name FROM users WHERE id = ?', (id,))
            user = c.fetchone()
            conn.close()
            
            if user and conf < 60:
                cv2.putText(frame, name[str(id)], (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            else:
                cv2.putText(frame, 'unknown', (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        if len(face) < 1:
            text_placeholder1.error("未检测到人脸，请保持正脸。")
        
        elif len(face) > 1:
            text_placeholder1.error("人数过多，请保持单人识别。")
    
        elif len(face) == 1 and conf < 30:
            if id == 1:
                text_placeholder1.error(f"禁止{name[str(id)]}通行，您位于黑名单中")
            else:
                text_placeholder1.success(f"识别成功，允许{name[str(id)]}通行")
        else:
            text_placeholder1.error("未登入访客，禁止进入")
        
        new_face = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)    
        video_placeholder.image(frame)

        if st.session_state.shot:
            new_user_registration(frame)
            if len(face) == 1 and conf > 60:
                video_placeholder = st.empty()
                output_dir = "data/new_visitors"
                new_face = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                #image_placeholder.image(new_face, caption="新访客照片", use_column_width=True)
            
                img_name = f'visitor_{datetime.now().strftime("%Y%m%d%H%M%S")}.jpg'
                cv2.imwrite(os.path.join(output_dir, img_name), new_face)
                st.success("照片已保存。")
                
                new_user_registration(new_face)
                
            elif len(face) == 1 and conf < 60:
                text_placeholder2.error("您已经在系统中，请勿重复录入。")
                st.session_state.shot = False
                continue
            elif len(face) == 0:
                text_placeholder2.error("未检测到人脸，请保持正脸。")
                st.session_state.shot = False
                continue
            else:
                text_placeholder2.error("人数过多，请保持单人识别。")
                st.session_state.shot = False
                continue




# 侧边栏
st.sidebar.title(":wrench:系统信息")
st.sidebar.markdown(":book:系统版本: v1.0")
st.sidebar.markdown(":girl:开发者: hjy")
st.sidebar.markdown(":man:教室负责人: 吴鹏程老师")
st.sidebar.markdown("如系统出现问题，请拨打:telephone_receiver::你打了我也不会接")

    
with tab1:
    msg_from = '319667558@qq.com'
    passwd = 'dtbxrcdyvbvecaae'


    st.title("陌生访客留言")
    st.markdown("如果您是未注册访客，请留下您的信息，我们会尽快联系您：")
    
    with st.form(key='my_form'):
        receiver = '3305364651@qq.com'
        to = [receiver]

        msg = MIMEMultipart()
        
        connect = st.text_area("留言内容")
        
        msg.attach(MIMEText(connect, 'plain', 'utf-8'))

        theme = st.text_input("留言者姓名及联络方式")
        msg['Subject'] = theme
        msg['From'] = msg_from

        submit_button = st.form_submit_button("留言")
        if submit_button:
            try:
                s = smtplib.SMTP_SSL("smtp.qq.com", 465)
                s.login(msg_from, passwd)
                s.sendmail(msg_from, to, msg.as_string())
                st.success("留言成功！")
            except Exception as e:
                st.error(f"发送邮件失败: {e}")

with tab2:
    st.markdown("# 新访客录入&旧访客识别:rocket:")
    st.markdown("请新访客将脸部对准摄像头并点击下面的按钮拍照：")
    st.markdown("旧访客无需做任何操作，系统会自动识别。")
    st.session_state.shot = st.button("拍照")
    display_camera()
    #image_placeholder = st.empty()
    
    if st.button("继续识别/重新拍照"):
        st.session_state.shot = False
        display_camera()













    




    





