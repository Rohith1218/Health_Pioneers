import streamlit as st
import google.generativeai as genai
from datetime import datetime
import json


genai.configure(api_key="YOUR_API_KEY")


model = genai.GenerativeModel("gemini-pro")



def get_gemini_response(question):
    chat = model.start_chat(history=[])
    response = chat.send_message(question)
    return response.text



if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_history' not in st.session_state:
    st.session_state.user_history = {}
if 'show_history' not in st.session_state:
    st.session_state.show_history = False
if 'view_more' not in st.session_state:
    st.session_state.view_more = {}
if 'bookings' not in st.session_state:
    st.session_state.bookings = {}


with open('doc.json', 'r') as f:
    doctors = json.load(f)


def match_specialization(symptoms):
    if "heart" in symptoms.lower() or "chest" in symptoms.lower():
        return "Cardiologist"
    elif "skin" in symptoms.lower() or "rash" in symptoms.lower():
        return "Dermatologist"
    elif "eye" in symptoms.lower() or "vision" in symptoms.lower():
        return "Ophthalmologist"
    elif "bone" in symptoms.lower() or "joint" in symptoms.lower():
        return "Orthopedic Surgeon"
    elif "pregnancy" in symptoms.lower() or "female" in symptoms.lower():
        return "Gynecologist"
    elif "ear" in symptoms.lower() or "nose" in symptoms.lower():
        return "ENT Specialist"
    elif "brain" in symptoms.lower() or "nervous" in symptoms.lower():
        return "Neurologist"
    elif "child" in symptoms.lower() or "baby" in symptoms.lower():
        return "Pediatrician"
    else:
        return "General Practitioner"



def main():
    st.set_page_config(page_title="Smart Care Connect", page_icon=":hospital:", layout="wide")

    if not st.session_state.authenticated:
        st.title("Smart Care Connect :hospital:")
        st.write(
            "This application provides remote diagnostics and health advice using AI, specifically designed for people in rural areas with limited access to healthcare.")
        st.image(
            'images/scc_logo.jpg',
            caption='Smart Care Connect', width=400)

        st.markdown("## Social Impact")
        st.write(
            "This system aims to improve health outcomes and access to healthcare in underserved rural areas. By providing timely diagnostics and health advice remotely, it helps in early detection and treatment of health issues.")

        st.sidebar.title("User Login")
        st.sidebar.image(
            'images/user_avatar.jpg',
            width=100)
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")

        if st.sidebar.button("Login"):
            if username == "Rohith" and password == "0571":
                st.session_state.authenticated = True
                st.session_state.username = username
                if username not in st.session_state.user_history:
                    st.session_state.user_history[username] = []
                if username not in st.session_state.bookings:
                    st.session_state.bookings[username] = []
            else:
                st.sidebar.error("Invalid username or password")
    else:
        st.sidebar.title(f"Welcome, {st.session_state.username} :wave:")
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.show_history = False
            st.session_state.view_more = {}

        if st.sidebar.button("View History"):
            st.session_state.show_history = not st.session_state.show_history

        st.header("User Input :writing_hand:")
        symptoms = st.text_area("Enter your symptoms")

        if st.button("Get Diagnosis"):
            if symptoms:
                response = get_gemini_response(symptoms)
                st.write("## Diagnosis and Advice :memo:")
                st.write(response)

                st.session_state.user_history[st.session_state.username].append({
                    "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "symptoms": symptoms,
                    "response": response
                })
            else:
                st.write("Please enter your symptoms.")

        if st.session_state.show_history:
            st.write("## Your Health History :file_folder:")
            history = st.session_state.user_history[st.session_state.username]
            if history:
                for i, entry in enumerate(history):
                    st.write(f"### {i + 1}. {entry['datetime']}")
                    st.write(f"**Symptoms:** {entry['symptoms']}")

                    if st.button(f"View More {i + 1}", key=f"view_more_{i}"):
                        st.session_state.view_more[i] = not st.session_state.view_more.get(i, False)

                    if st.session_state.view_more.get(i, False):
                        st.write(f"**Response:** {entry['response']}")
            else:
                st.write("No history available.")

        st.header("Book an Appointment :calendar:")
        user_location = st.text_input("Enter your location")

        if user_location and symptoms:
            specialization = match_specialization(symptoms)
            st.write(f"Suggested Specialization: **{specialization}**")

            available_doctors = [doc for doc in doctors if doc["specialization"] == specialization and doc[
                "location"].lower() == user_location.lower()]
            if available_doctors:
                for i, doc in enumerate(available_doctors):
                    st.write(f"### {i + 1}. {doc['name']} ({doc['location']})")
                    for time in doc["availability"]:
                        if st.button(f"Book Appointment with {doc['name']} at {time}", key=f"book_{i}_{time}"):
                            st.session_state.bookings[st.session_state.username].append({
                                "doctor": doc['name'],
                                "time": time,
                                "location": doc['location'],
                                "specialization": specialization
                            })
                            st.success(f"Appointment booked with {doc['name']} at {time} :white_check_mark:")

        if st.sidebar.button("View Bookings"):
            st.write("## Your Appointments :calendar:")
            bookings = st.session_state.bookings[st.session_state.username]
            if bookings:
                for i, booking in enumerate(bookings):
                    st.write(f"### {i + 1}. {booking['doctor']} ({booking['location']})")
                    st.write(f"**Time:** {booking['time']}")
                    st.write(f"**Specialization:** {booking['specialization']}")
            else:
                st.write("No bookings available.")


if __name__ == "__main__":
    main()
