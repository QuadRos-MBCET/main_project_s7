import codecs
import re

with codecs.open("frontend/pages/user_workspace.py", "r", "utf-8") as f:
    text = f.read()

new1 = '''    if "user_auth_mode" not in st.session_state:
        st.session_state["user_auth_mode"] = "login"
        
    if "user_db" not in st.session_state:
        st.session_state["user_db"] = {
            "demo": {"password": "demo", "category": "18 to 24", "norm": "AGE_18_PLUS"}
        }

    if st.session_state["verified_age_category"] is None:
        if st.session_state["user_auth_mode"] == "login":
            st.markdown("### 🔐 User Login")
            st.write("Welcome back! Please enter your credentials to access Instakill.")
            
            l_user = st.text_input("Username")
            l_pass = st.text_input("Password", type="password")
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("Login", type="primary", use_container_width=True):
                    db = st.session_state["user_db"]
                    if l_user in db and db[l_user]["password"] == l_pass:
                        st.session_state["verified_age_category"] = db[l_user]["category"]
                        st.session_state["verified_age_norm"] = db[l_user]["norm"]
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
            with c_btn2:
                if st.button("New User? Sign In", use_container_width=True):
                    st.session_state["user_auth_mode"] = "register"
                    st.rerun()
                    
        elif st.session_state["user_auth_mode"] == "register":
            st.markdown("### 📝 New User Registration")
            st.write("Please create your account and verify your age to continue.")
            
            r_user = st.text_input("Choose Username", key="reg_usr")
            r_pass = st.text_input("Choose Password", type="password", key="reg_pwd")
            
            if st.button("Already have an account? Login here"):
                st.session_state["user_auth_mode"] = "login"
                st.rerun()
                
            st.markdown("---")
            st.markdown("###'''

text = re.sub(r'    if st\.session_state\["verified_age_category"\] is None:\r?\n        st\.markdown\("###', new1, text, count=1)

new2 = '''                    st.markdown("### Complete Registration")
                    if st.button("Create Account & Enter Instakill", type="primary", use_container_width=True):
                        ru = st.session_state.get("reg_usr", "")
                        rp = st.session_state.get("reg_pwd", "")
                        
                        if not ru or not rp:
                            st.error("Please enter a username and password at the top of the form.")
                        elif ru in st.session_state["user_db"]:
                            st.error("Username already taken. Please choose another one.")
                        else:
                            st.session_state["user_db"][ru] = {
                                "password": rp,
                                "category": category,
                                "norm": norm_group
                            }
                            st.session_state["verified_age_category"] = category
                            st.session_state["verified_age_norm"] = norm_group
                            st.success("Account created successfully!")
                            st.rerun()'''

text = re.sub(r'                    st\.session_state\["verified_age_category"\] = category\r?\n                    st\.session_state\["verified_age_norm"\] = norm_group\r?\n\s+if st\.button\("Continue to Age-Aware Feed", use_container_width=True\):\r?\n                        st\.rerun\(\)', new2, text, count=1)

new3 = '''            if st.button("Log Out"):
                st.session_state["verified_age_category"] = None
                st.session_state["user_auth_mode"] = "login"
                st.rerun()'''

text = re.sub(r'            if st\.button\("Log Out"\):\r?\n                st\.session_state\["verified_age_category"\] = None\r?\n                st\.rerun\(\)', new3, text, count=1)

with codecs.open("frontend/pages/user_workspace.py", "w", "utf-8") as f:
    f.write(text)
