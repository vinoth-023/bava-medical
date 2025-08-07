# bava_medical_app.py (Fully Updated and Fixed)

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os
import uuid
import time

# Firebase Init
firebase_config = dict(st.secrets["firebase"])
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)
db = firestore.client()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_image(uploaded_file):
    ext = uploaded_file.name.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return filepath

# -------------------------- Pages --------------------------
def home_page():
    st.markdown("""
        <style>
        .main::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-image: url('https://i.ibb.co/NZTVxB6/medical-bg.jpg');
            background-size: cover;
            background-repeat: no-repeat;
            background-position: center;
            opacity: 0.2;
            z-index: -1;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center; color:#007bff;'>🩺 Bava Medicals</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown("""
                <div style='padding: 30px; border-radius: 12px; background-color: #f9f9f9; box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>
                    <h3 style='text-align:center;'>Welcome!</h3>
            """, unsafe_allow_html=True)
            st.button("Login as User", on_click=lambda: st.session_state.update({"page": "user_login"}))
            st.button("Login as Admin", on_click=lambda: st.session_state.update({"page": "admin_login"}))
            st.markdown("</div>", unsafe_allow_html=True)

def user_login():
    st.subheader("User Login")
    email = st.text_input("Email").lower()
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        users = db.collection("users").where("email", "==", email).where("password", "==", password).get()
        if users:
            st.session_state.update({"user_email": email, "page": "user_dashboard"})
        else:
            st.error("Invalid credentials")
    st.info("New user?")
    if st.button("Register"):
        st.session_state.page = "user_register"
    if st.button("⬅️ Back"):
        st.session_state.page = "home"
def user_register():
    st.subheader("Register New User")

    name = st.text_input("Full Name")
    age = st.number_input("Age", min_value=0)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    phone = st.text_input("Phone Number")
    address = st.text_area("Address")
    email = st.text_input("Email").lower()
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        # Basic field validation
        if not name or not age or not phone or not address or not email or not password:
            st.warning("Please fill in all the fields.")
        else:
            # Check if user already exists
            existing_user = db.collection("users").where("email", "==", email).get()
            if existing_user:
                st.error("Email already registered. Try logging in.")
            else:
                db.collection("users").add({
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "phone": phone,
                    "address": address,
                    "email": email,
                    "password": password
                })
                st.success("Registration successful! Redirecting to dashboard...")
                time.sleep(1)
                st.session_state.update({"user_email": email, "page": "user_dashboard"})

    if st.button("⬅️ Back"):
        st.session_state.page = "user_login"

def user_dashboard():
    st.title("Welcome to Bava Medical Shop")
    st.caption(f"Logged in as: {st.session_state.user_email}")
    st.button("🔓 Logout", on_click=lambda: st.session_state.clear(), key="logout_user", type="primary")

    tab1, tab2, tab3 = st.tabs(["🆕 New Order", "📦 Track Order", "📜 Order History"])

    with tab1:
        st.subheader("Place a New Order")
        medicine = st.text_input("Medicine Name (optional)")
        image = st.file_uploader("Upload Medical Sheet (optional)", type=["png", "jpg", "jpeg"])
        age = st.number_input("Enter Age", min_value=0)
        gender = st.selectbox("Choose Gender", ["Male", "Female", "Other"])
        symptoms = st.multiselect("Select Symptoms", ["Headache", "Fever", "Cold", "Cough", "Shoulder Pain", "Leg Pain"])

        if st.button("Order"):
            if not age or not gender:
                st.warning("Please enter both Age and Gender before placing the order.")
            elif not medicine and image is None and not symptoms:
                st.warning("Please enter medicine name, upload prescription image, or enter symptoms.")
            else:
                image_url = save_image(image) if image else ""
                order = {
                    "email": st.session_state.user_email,
                    "medicine": medicine,
                    "image": image_url,
                    "entered_age": age,
                    "entered_gender": gender,
                    "symptoms": symptoms,
                    "status": "Order Placed",
                    "timestamp": datetime.now()
                }
                db.collection("orders").add(order)
                st.success("Order placed successfully!")
                st.rerun()

    with tab2:
        st.subheader("Track Your Orders")
        email = st.session_state.user_email.lower()
        orders = db.collection("orders") \
               .where("email", "==", email) \
               .where("status", "in", ["Order Placed", "Out for Delivery"]) \
               .get()
        
        if not orders:
            st.info("No active orders found.")
        for o in orders:
            data = o.to_dict()
            status = data['status']
            if status == "Order Placed":
                color = "🔴"
            elif status == "Out for Delivery":
                color = "🟡"
            else:
                color = "🟢"
                
            st.markdown(f"**Status:** {color} {status}")
            st.markdown(f"**Date:** {data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            if st.button("Delete", key="delete_" + o.id):
                db.collection("orders").document(o.id).delete()
                st.success("Order deleted.")
                st.rerun()


    with tab3:
        st.subheader("Order History")
        delivered_orders = db.collection("orders") \
                             .where("email", "==", st.session_state.user_email) \
                             .where("status", "==", "Delivered") \
                             .get()
        if not delivered_orders:
            st.info("No delivered orders yet.")
        for o in delivered_orders:
            data = o.to_dict()
            st.markdown(f"✅ Delivered: {data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} - {data.get('medicine', 'N/A')}")
            if st.button("Re-order", key="re_" + o.id):
                new_order = data.copy()
                new_order["timestamp"] = datetime.now()
                new_order["status"] = "Order Placed"
                db.collection("orders").add(new_order)
                st.success("Re-ordered successfully!")
                st.rerun()
            if st.button("Delete", key="delete_delivered_" + o.id):
                db.collection("orders").document(o.id).delete()
                st.success("Delivered order deleted.")
                st.rerun()

def admin_login():
    st.subheader("Admin Login")
    email = st.text_input("Admin Email").lower()
    password = st.text_input("Admin Password", type="password")
    if st.button("Login"):
        if email == "admin@gmail.com" and password == "admin@123":
            st.success("Admin login successful")
            st.session_state.page = "admin_dashboard"
        else:
            st.error("Invalid admin credentials")
    if st.button("⬅️ Back"):
        st.session_state.page = "home"

def admin_dashboard():
    st.title("🛒 Admin Dashboard")

    st.subheader("📦 Pending Orders")
    pending_orders = db.collection("orders").where("status", "==", "Order Placed").stream()

    pending_found = False
    for o in pending_orders:
        data = o.to_dict()
        pending_found = True
        with st.container():
            st.markdown("---")
            st.markdown(f"**📧 Email:** {data.get('email', '')}")
            st.markdown(f"**💊 Medicine:** {data.get('medicine', '-') or '-'}")
            st.markdown(f"**🎯 Age:** {data.get('entered_age', '-')}")
            st.markdown(f"**🧬 Gender:** {data.get('entered_gender', '-')}")
            st.markdown(f"**📝 Symptoms:** {data.get('symptoms', '-')}")
            st.markdown(f"**🕒 Time:** {data.get('timestamp', '').strftime('%Y-%m-%d %H:%M:%S') if data.get('timestamp') else '-'}")

            # Show image if exists
            if data.get("image"):
                st.markdown(
                    f"<a href='{data['image']}' target='_blank'><img src='{data['image']}' width='100'></a>",
                    unsafe_allow_html=True
                )

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("✅ Mark Delivered", key="deliver_" + o.id):
                    db.collection("orders").document(o.id).update({"status": "Delivered"})
                    st.success("✅ Order marked as delivered.")
                    time.sleep(1)
                    st.rerun()
            with col2:
                if st.button("🗑️ Delete", key="delete_pending_" + o.id):
                    db.collection("orders").document(o.id).delete()
                    st.success("🗑️ Order deleted.")
                    time.sleep(1)
                    st.rerun()

    if not pending_found:
        st.info("No pending orders found.")

    st.markdown("## ✅ Delivered Orders")
    delivered_orders = db.collection("orders").where("status", "==", "Delivered").stream()

    delivered_found = False
    for o in delivered_orders:
        data = o.to_dict()
        delivered_found = True
        with st.container():
            st.markdown("---")
            st.markdown(f"**📧 Email:** {data.get('email', '')}")
            st.markdown(f"**💊 Medicine:** {data.get('medicine', '-') or '-'}")
            st.markdown(f"**🎯 Age:** {data.get('entered_age', '-')}")
            st.markdown(f"**🧬 Gender:** {data.get('entered_gender', '-')}")
            st.markdown(f"**📝 Symptoms:** {data.get('symptoms', '-')}")
            st.markdown(f"**🕒 Time:** {data.get('timestamp', '').strftime('%Y-%m-%d %H:%M:%S') if data.get('timestamp') else '-'}")

            # Show image if exists
            if data.get("image"):
                st.markdown(
                    f"<a href='{data['image']}' target='_blank'><img src='{data['image']}' width='100'></a>",
                    unsafe_allow_html=True
                )

            if st.button("🗑️ Delete", key="delete_delivered_" + o.id):
                db.collection("orders").document(o.id).delete()
                st.success("🗑️ Delivered order deleted.")
                time.sleep(1)
                st.rerun()

    if not delivered_found:
        st.info("No delivered orders found.")


# -------------------------- Router --------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

page_router = {
    "home": home_page,
    "user_login": user_login,
    "user_register": user_register,
    "user_dashboard": user_dashboard,
    "admin_login": admin_login,
    "admin_dashboard": admin_dashboard,
}

page_router[st.session_state.page]()
