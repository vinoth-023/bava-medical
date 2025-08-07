import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os
import uuid
import time

# -------------------------- Firebase Init --------------------------
firebase_config = dict(st.secrets["firebase"])
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)
db = firestore.client()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------- Style --------------------------
st.markdown("""
    <style>
        .stButton>button {
            background-color: #4d94ff !important;  /* Medium blue for primary actions */
            color: white;
        }
        .stButton>.red-btn>button {
            background-color: #ff6666 !important;  /* Medium red */
            color: white;
        }
        .stButton>.green-btn>button {
            background-color: #28a745 !important;  /* Medium green */
            color: white;
        }
    </style>
""", unsafe_allow_html=True)


def save_image(uploaded_file):
    ext = uploaded_file.name.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return filepath


# -------------------------- Pages --------------------------
from datetime import datetime

def home_page():
    # Background styling
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

    # Centered Title & Welcome
    st.markdown("""
        <div style='text-align: center; margin-top: 30px;'>
            <h1 style='color:#007bff;'>🩺 Bava Medicals</h1>
            <h4 style='margin-top: -10px;'>Welcome to Bava Medicals - Your health, our priority!</h4>
            <p style='color: gray;'>Today's Date: <b>{}</b></p>
        </div>
    """.format(datetime.now().strftime("%A, %d %B %Y")), unsafe_allow_html=True)

    # Centered Buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown("""
                <div style='padding: 30px; border-radius: 12px; background-color: #f9f9f9; box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>
            """, unsafe_allow_html=True)

            st.button("Login as User", on_click=lambda: st.session_state.update({"page": "user_login"}))
            st.button("Login as Admin", on_click=lambda: st.session_state.update({"page": "admin_login"}))

            st.markdown("</div>", unsafe_allow_html=True)


def user_login():
    st.subheader("User Login")
    email = st.text_input("Email").strip().lower()
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = db.collection("users").where("email", "==", email).get()
        if users:
            user = users[0].to_dict()
            if user["password"] == password:
                st.session_state.update({"user_email": email, "page": "user_dashboard"})
            else:
                st.error("Incorrect password")
        else:
            st.error("User not found")

    st.info("New user?")
    st.button("Register", on_click=lambda: st.session_state.update({"page": "user_register"}), key="go_register")
    st.button("⬅️ Back", on_click=lambda: st.session_state.update({"page": "home"}), key="back_user_login", type="secondary")


def user_register():
    st.subheader("Register New User")
    name = st.text_input("Full Name")
    age = st.number_input("Age", min_value=0)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    phone = st.text_input("Phone Number")
    address = st.text_area("Address")
    email = st.text_input("Email").strip().lower()
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        db.collection("users").add({
            "name": name, "age": age, "gender": gender, "phone": phone,
            "address": address, "email": email, "password": password
        })
        st.success("Registration successful! Redirecting to dashboard...")
        time.sleep(1)
        st.session_state.update({"user_email": email, "page": "user_dashboard"})

    st.button("⬅️ Back", on_click=lambda: st.session_state.update({"page": "user_login"}), key="back_register", type="secondary")


def user_dashboard():
    st.title("Welcome to Bava Medical Shop")
    st.button("🔓 Logout", on_click=lambda: st.session_state.clear(), key="logout_user", type="primary")

    tab1, tab2, tab3 = st.tabs(["🆕 New Order", "📦 Track Order", "📜 Order History"])

    with tab1:
        st.subheader("Place a New Order")

        medicine = st.text_input("Medicine Name (optional)")
        image = st.file_uploader("Upload Medical Sheet (optional)", type=["png", "jpg", "jpeg"])
        age = st.number_input("Enter Age", min_value=0, step=1)
        gender = st.selectbox("Choose Gender", ["", "Male", "Female", "Other"])
        symptoms = st.multiselect("Select Symptoms", ["Headache", "Fever", "Cold", "Cough", "Shoulder Pain", "Leg Pain"])

        if st.button("Order"):
            # Validation
            if age == 0 or gender == "":
                st.warning("Please enter both Age and Gender before placing the order.")
            elif not medicine.strip() and image is None and not symptoms:
                st.warning("Please enter medicine name, upload prescription image, or select symptoms.")
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
                st.success("✅ Order placed successfully!")
                st.rerun()

    with tab2:
        st.subheader("Track Your Orders")
        orders = db.collection("orders").where("email", "==", st.session_state.user_email).where("status", "in", ["Order Placed", "Out for Delivery"]).get()
        for o in orders:
            data = o.to_dict()
            st.markdown(f"**Status:** 🟢 {data['status']}")
            st.markdown(f"**Date:** {data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            if st.button("Delete", key="delete_" + o.id):
                db.collection("orders").document(o.id).delete()
                st.success("Order deleted.")
                st.experimental_rerun()

    with tab3:
        st.subheader("Order History")
        delivered_orders = db.collection("orders").where("email", "==", st.session_state.user_email).where("status", "==", "Delivered").get()
        for o in delivered_orders:
            data = o.to_dict()
            st.markdown(f"✅ Delivered: {data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} - {data.get('medicine', 'N/A')}")
            if st.button("Re-order", key="re_" + o.id):
                new_order = data.copy()
                new_order["timestamp"] = datetime.now()
                new_order["status"] = "Order Placed"
                db.collection("orders").add(new_order)
                st.success("Re-ordered successfully!")
                st.experimental_rerun()


def admin_login():
    st.subheader("Admin Login")
    email = st.text_input("Admin Email").strip().lower()
    password = st.text_input("Admin Password", type="password")

    if st.button("Login"):
        if email == "admin@gmail.com" and password == "admin@123":
            st.success("Admin login successful")
            st.session_state.page = "admin_dashboard"
        else:
            st.error("Invalid admin credentials")

    st.button("⬅️ Back", on_click=lambda: st.session_state.update({"page": "home"}), key="back_admin_login", type="secondary")

def admin_dashboard():
    st.title("📢 Masha Allah - Today's Orders")
    st.markdown(f"### 🗓️ {datetime.now().strftime('%A, %d %B %Y')} | ⏰ {datetime.now().strftime('%H:%M:%S')}")
    st.button("🔓 Logout", on_click=lambda: st.session_state.clear(), key="logout_admin", type="primary")

    tab1, tab2 = st.tabs(["🕓 Pending Orders", "✅ Delivered Orders"])

    with tab1:
        st.subheader("Pending Orders")
        orders = db.collection("orders").where("status", "in", ["Order Placed", "Out for Delivery"]).get()
        for o in orders:
            data = o.to_dict()
            user_docs = db.collection("users").where("email", "==", data.get("email")).get()
            user_data = user_docs[0].to_dict() if user_docs else {}

            st.markdown(f"**User:** {user_data.get('name')} | 📞 {user_data.get('phone')}")
            st.markdown(f"**Address:** {user_data.get('address')}")
            st.markdown(f"**Medicine:** {data.get('medicine')} | Age: {data.get('entered_age')} | Gender: {data.get('entered_gender')}")
            st.markdown(f"**Symptoms:** {', '.join(data.get('symptoms', [])) if data.get('symptoms') else 'None'}")
            if data.get("image"):
                st.image(data["image"], width=250)
            st.markdown(f"**Current Status:** {data.get('status')}")

            new_status = st.selectbox("Update Status", ["Out for Delivery", "Delivered"], key="status_" + o.id)
            if st.button("Update", key="update_" + o.id):
                db.collection("orders").document(o.id).update({"status": new_status})
                st.success("Status updated.")
                st.experimental_rerun()
            if st.button("Delete", key="delete_pending_" + o.id):
                db.collection("orders").document(o.id).delete()
                st.warning("Order deleted.")
                st.experimental_rerun()
            st.markdown("---")

    with tab2:
        st.subheader("Delivered Orders")
        delivered = db.collection("orders").where("status", "==", "Delivered").get()
        for o in delivered:
            data = o.to_dict()
            st.markdown(f"**User:** {data.get('email')} | **Delivered:** {data.get('timestamp').strftime('%Y-%m-%d %H:%M:%S')}")
            st.markdown(f"**Medicine:** {data.get('medicine')}")
            if st.button("Delete", key="delete_delivered_" + o.id):
                db.collection("orders").document(o.id).delete()
                st.warning("Delivered order deleted.")
                st.experimental_rerun()
            st.markdown("---")


# -------------------------- Router --------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

pages = {
    "home": home_page,
    "user_login": user_login,
    "user_register": user_register,
    "user_dashboard": user_dashboard,
    "admin_login": admin_login,
    "admin_dashboard": admin_dashboard,
}

pages[st.session_state.page]()
