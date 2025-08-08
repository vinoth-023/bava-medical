# bava_medical_app.py (Fully Updated and Fixed)

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os
import uuid
import time
from datetime import datetime
import pytz

# Get current time in IST (Asia/Kolkata)
ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)

order_time = now.strftime("%d-%m-%Y %H:%M:%S")

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
def apply_custom_styles():
    st.markdown("""
        <style>
        /* Background and fonts */
        body, .main, .block-container {
            background-color: #f0f4f8;
            font-family: 'Segoe UI', sans-serif;
            color: #333;
        }

        /* Headings */
        h1, h2, h3 {
            color: #007bff;
            text-align: center;
            margin-bottom: 0.5em;
            animation: fadeInDown 1s ease-in-out;
        }

        /* Card container */
        .card {
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
            padding: 30px;
            transition: transform 0.3s ease;
        }
        .card:hover {
            transform: scale(1.02);
        }

        /* Buttons */
        .stButton > button {
            background-color: #007bff;
            color: white;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: bold;
            border: none;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 123, 255, 0.2);
        }
        .stButton > button:hover {
            background-color: #0056b3;
            transform: scale(1.05);
            box-shadow: 0 6px 18px rgba(0, 86, 179, 0.3);
        }

        /* Input boxes: text, number, etc. */
        input[type="text"], input[type="number"], textarea {
            border: 1.5px solid #007bff !important;
            border-radius: 6px !important;
            padding: 8px 12px !important;
            box-shadow: 0 4px 10px rgba(0, 123, 255, 0.1) !important;
            transition: all 0.3s ease-in-out;
        }

        input[type="text"]:focus, input[type="number"]:focus, textarea:focus {
            border-color: #0056b3 !important;
            box-shadow: 0 6px 18px rgba(0, 86, 179, 0.2) !important;
        }

        /* Select, multiselect, file uploader (indirect styling via class) */
        .stSelectbox, .stMultiSelect, .stFileUploader, .stNumberInput {
            background-color: white;
            border: 1.5px solid #007bff;
            border-radius: 6px;
            padding: 6px;
            box-shadow: 0 4px 10px rgba(0, 123, 255, 0.1);
            transition: all 0.3s ease-in-out;
        }

        /* Image zoom */
        img:hover {
            transform: scale(1.05);
            transition: 0.3s ease-in-out;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        }

        /* Info boxes */
        .stAlert, .stMarkdown {
            transition: 0.3s ease-in-out;
        }

        /* Animation */
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        </style>
    """, unsafe_allow_html=True)

# -------------------------- Pages --------------------------
def home_page():
    apply_custom_styles()
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
    apply_custom_styles()
    st.subheader("User Login")

    email = st.text_input("Email").strip().lower()
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not email or not password:
            st.warning("Please enter both email and password.")
        else:
            users = db.collection("users").where("email", "==", email).where("password", "==", password).get()
            if users:
                st.success("Login successful!")
                st.session_state.update({"user_email": email, "page": "user_dashboard"})
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")

    st.info("New user?")
    if st.button("Register"):
        st.session_state.update({  "page": "user_register"})
        st.rerun()

    if st.button("⬅️ Back"):
        st.session_state.page = "home"
        st.rerun()

def user_register():
    apply_custom_styles()
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
                st.rerun()

    if st.button("⬅️ Back"):
        st.session_state.page = "user_login"
        st.rerun()


def user_dashboard():
    apply_custom_styles()
    st.title("Welcome to Bava Medical Shop")
    st.caption(f"Logged in as: {st.session_state.user_email}")
    st.button("🔓 Logout", on_click=lambda: st.session_state.clear(), key="logout_user", type="primary")

    tab1, tab2, tab3 = st.tabs(["🆕 New Order", "📦 Track Order", "📜 Order History"])

    with tab1:
        st.subheader("Place a New Order")
        
        # Inputs
        medicine = st.text_input("Medicine Name (optional)")
        image = st.file_uploader("Upload Medical Sheet (optional)", type=["png", "jpg", "jpeg"])
        age = st.number_input("Enter Age", min_value=0)
        gender = st.selectbox("Choose Gender", ["Male", "Female", "Other"])
        symptoms = st.multiselect("Select Symptoms", ["Headache", "Fever", "Cold", "Cough", "Shoulder Pain", "Leg Pain"])

        # Order button
        if st.button("🛒 Order"):
            if not age or not gender:
                st.warning("Please enter both Age and Gender before placing the order.")
            elif not medicine and image is None and not symptoms:
                st.warning("Please enter medicine name, upload prescription image, or enter symptoms.")
            else:
                # Open confirmation modal
                st.session_state.show_confirm_modal = True
                st.experimental_rerun()

        # Handle modal confirmation
        if st.session_state.get("show_confirm_modal", False):
            with st.modal("Confirm Order"):
                st.write("⚠️ Are you sure you want to place this order?")
                st.write("This action cannot be undone.")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Yes, Place Order"):
                        image_url = save_image(image) if image else ""
                        ist = pytz.timezone('Asia/Kolkata')
                        now = datetime.now(ist)
                        order_time = now.strftime("%d-%m-%Y %H:%M:%S")
                        order = {
                            "email": st.session_state.user_email,
                            "medicine": medicine,
                            "image": image_url,
                            "entered_age": age,
                            "entered_gender": gender,
                            "symptoms": symptoms,
                            "status": "Order Placed",
                            "timestamp": order_time
                        }
                        db.collection("orders").add(order)
                        st.success("✅ Order placed successfully!")
                        st.session_state.show_confirm_modal = False
                        st.session_state.user_tab = 2  # Switch to Track Order
                        st.rerun()

                with col2:
                    if st.button("❌ Cancel"):
                        st.session_state.show_confirm_modal = False
                        st.experimental_rerun()
                

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
            st.markdown(f"**Date:** {data['timestamp']}")  # ✅ FIXED: No .strftime() here
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
    apply_custom_styles()
    st.subheader("Admin Login")
    email = st.text_input("Admin Email").lower()
    password = st.text_input("Admin Password", type="password")
    if st.button("Login"):
        if email == "admin@gmail.com" and password == "admin@123":
            st.success("Admin login successful")
            st.session_state.page = "admin_dashboard"
            st.rerun()
        else:
            st.error("Invalid admin credentials")
    if st.button("⬅️ Back"):
        st.session_state.page = "home"
        st.rerun()


def admin_dashboard():
    apply_custom_styles()
    st.title("Admin Dashboard")
    st.button("🔓 Logout", on_click=lambda: st.session_state.clear(), key="logout_admin", type="primary")

    tab1, tab2 = st.tabs(["📦 Pending Orders", "✅ Delivered Orders"])

    with tab1:
        st.subheader("Pending Orders")
        pending_orders = db.collection("orders").where("status", "in", ["Order Placed", "Out for Delivery"]).stream()

        for order in pending_orders:
            data = order.to_dict()
            st.markdown(f"### 📬 {data.get('email')}")
            st.markdown(f"**Age:** {data.get('entered_age', 'N/A')}")
            st.markdown(f"**Gender:** {data.get('entered_gender', 'N/A')}")
            st.markdown(f"**Medicine:** {data.get('medicine', 'N/A')}")
            st.markdown(f"**Symptoms:** {', '.join(data.get('symptoms', [])) if data.get('symptoms') else 'N/A'}")
            st.markdown(f"**Date:** {data.get('timestamp').strftime('%Y-%m-%d %H:%M:%S')}")

            if data.get("image") and os.path.exists(data["image"]):
                st.image(data["image"], caption="Uploaded Image", use_column_width=True)

            current_status = data.get("status", "Order Placed")
            new_status = st.selectbox(
                "Update Status",
                ["Order Placed", "Out for Delivery", "Delivered"],
                index=["Order Placed", "Out for Delivery", "Delivered"].index(current_status),
                key=f"status_{order.id}"
            )

            if st.button("✅ Update Status", key=f"update_{order.id}"):
                db.collection("orders").document(order.id).update({"status": new_status})
                st.success(f"Status updated to '{new_status}'")
                st.rerun()

            if st.button("Delete", key="delete_pending_" + order.id):
                db.collection("orders").document(order.id).delete()
                st.warning("Order deleted.")
                st.rerun()

    with tab2:
        st.subheader("Delivered Orders")
        delivered_orders = db.collection("orders").where("status", "==", "Delivered").stream()

        for order in delivered_orders:
            data = order.to_dict()
            st.markdown(f"### 📬 {data.get('email')}")
            st.markdown(f"**Age:** {data.get('entered_age', 'N/A')}")
            st.markdown(f"**Gender:** {data.get('entered_gender', 'N/A')}")
            st.markdown(f"**Medicine:** {data.get('medicine', 'N/A')}")
            st.markdown(f"**Symptoms:** {', '.join(data.get('symptoms', [])) if data.get('symptoms') else 'N/A'}")
            st.markdown(f"**Delivered On:** {data.get('timestamp').strftime('%Y-%m-%d %H:%M:%S')}")

            if data.get("image") and os.path.exists(data["image"]):
                st.image(data["image"], caption="Uploaded Image", use_column_width=True)

            if st.button("🗑️ Delete Order", key=f"delete_{order.id}"):
                db.collection("orders").document(order.id).delete()
                st.success("Order deleted successfully!")
                st.rerun()


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
