import streamlit as st
import easyocr
from PIL import Image
from streamlit_lottie import st_lottie
import streamlit_pandas as sp
import requests
import numpy as np
import pandas as pd
import sqlite3
import re

st.set_page_config(page_title="pic to text",layout="wide")
st.title("  Extract the TEXT:abcd: from IMAGES:credit_card:")
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code!=200:
        return None
    return r.json()
lottie_s=load_lottieurl(r"https://assets6.lottiefiles.com/packages/lf20_kaelaowc.json")

with st.container():
    st.write("---")
    left_column,right_column=st.columns(2)
    with right_column:
        st_lottie(
                lottie_s,
                speed=1,
                reverse=False,
                loop=True,
                quality="low",
                height=300
                )
    
    with left_column:
        image=st.file_uploader(label = ":black_square_for_stop: Upload Image :black_square_for_stop:",type=['png','jpg','jpeg'])
        #@st.cache_data
        def image_txt():
            reader=easyocr.Reader(['en'])
            return reader
        reader=image_txt()
        if image is not None:
            input_image=Image.open(image)
            st.image(input_image)
            result=reader.readtext(np.array(input_image),paragraph=True)
            result_txt=[]
            for i in result:
                result_txt.append(i[1])
                #st.write(i[1])
            df = pd.DataFrame(result_txt, columns= ['Details'])
            blankIndex=[''] * len(df)
            df.index=blankIndex
            st.dataframe(df)                
            name_regex = r'^[A-Za-z ]+$'
            phone_regex = r'^\+?\d[\d -]*\d$'
            website_regex = r'^www\.[^\.]+\.([A-Za-z]{2,}|com)$'
            email_regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
            address_regex = r'^\d+ [A-Za-z ]+,[ A-Za-z]+; [A-Za-z]+ \d{6}$'
            name = ""
            phone = ""
            website = ""
            email = ""
            address = ""
            brand = ""
            for item in result_txt:
                if re.match(name_regex, item):
                    name = item.strip()
                elif re.match(phone_regex, item):
                    phone = item.strip()
                elif re.match(website_regex, item):
                    website = item.strip()
                elif re.match(email_regex, item):
                    email = item.strip()
                elif re.match(address_regex, item):
                    address = item.strip()
                else:
                    brand = item.strip()

            df_dict = {'Name': [website],
		   'Phone_Number': [phone],
		   'Website': [brand],
		   'Email': [email],
		   'Address': [address],
		   'Brand_Name': [name]}
            df1=pd.DataFrame(df_dict)


            edited_df=st.experimental_data_editor(df1)
            s=st.button("Click to upload the details in database")
            if s:
                
                conn=sqlite3.connect('pictotxt.db')

                create_sql="CREATE TABLE IF NOT EXISTS image_text1 (image blob,Name VARCHAR(255) NOT NULL,Phone_Number VARCHAR(255),Website VARCHAR(255),Email VARCHAR(255),Address VARCHAR(255),Brand_Name VARCHAR(255))"
                cursor=conn.cursor()
                cursor.execute(create_sql)
                for row in edited_df.itertuples():
                    insert_sql="INSERT INTO image_text1(image,Name,Phone_Number,Website,Email,Address,Brand_Name) values(?,?,?,?,?,?,?)"
                    input_image=Image.open(image)
                    image_data=input_image.tobytes()
                    cursor.execute(insert_sql, (image_data,) + row[1:])
                    conn.commit()
                conn.close()
            
        else:
            st.write(":black_square_for_stop: Upload Image:black_square_for_stop:")

s1=st.button("Click to view the table")
if "s1_state" not in st.session_state:
    st.session_state.s1_state=False
if (s1 or st.session_state.s1_state):
    st.session_state.s1_state=True
    conn = sqlite3.connect('pictotxt.db')
    df2 = pd.read_sql_query("SELECT * from image_text1", conn)
    st.write(df2)

    all_wid=sp.create_widgets(df2)
    res=sp.filter_df(df2,all_wid)
    st.write(res)
    #conn.close()
with st.container():
    st.write('---')
    st.subheader("Hope you enjoyed using this webpage!!!:thumbsup:")
    st.write("Please provide your valuable Feedback!!!:speech_balloon:")
    st.write("##")
    contact_form="""
    <form action="https://formsubmit.co/aswiniprabha22@gmail.com" method="POST">
        <input type="hidden" name="_captcha" value="false">      
        <input type="text" name="name" placeholder="Your name" required>
        <input type="email" name="email" placeholder="Your email" required>
        <textarea name="message" placeholder="Your message here" required></textarea>
        <button type="submit">Send</button>
    </form>
    """
    left_column,right_column=st.columns(2)
    with left_column:
        st.markdown(contact_form,unsafe_allow_html=True)
    with right_column:
        st.empty()
st.caption("Made with ❤️ by @aswinitheaspiringDS")

        
