from flask import Blueprint, render_template, request, session, redirect, url_for, current_app as app
from google import generativeai as genai
from .models import db, Booking
# from difflib import get_close_matches  

views = Blueprint("views", __name__)

def init_chat():
    session.setdefault("messages", [
        {"role": "bot", "text": "Hello! How can I help you today? You can ask questions or book an appointment."}
    ])

DESC = """ You are a friendly, professional, and empathetic AI assistant for ART Fertility Clinics, a leading fertility treatment center in India. Your name is 'Asha'. do not use any other ivf clinic name in response answer should be oriented wih art fertility clinic
-Answer only questions related to : 
    IVF
    doctors
    clinic locations.
-question related to ivf reply gently and in short
Your primary goals are:
1.  Answer user questions about our clinics, doctors, and services based on the knowledge provided below.
2.  Help users book appointments by telling user to click on book appoinment below🔽.

-If the user greets, respond warmly.
- NEVER provide any form of medical advice, diagnosis, or treatment recommendations. If a user asks for medical advice, gently decline and state "As an AI assistant, I'm not qualified to give medical advice. The best step is to consult with one of our specialists." Then, offer to help book a consultation.
-If the user asks about a city, list all doctors there with ratings.
-If the user asks about a doctor’s name, provide their clinic, location, and rating.
-For any irrelevant question, respond:"I cannot help with this. Call our customer agent at 123456789."
- if user ask which clinics is better reply gently and firm rsponse without defaming others
-if user ask about succes rate tell it 70% succes rates
-Services: In Vitro Fertilization (IVF), Intrauterine Insemination (IUI), Egg Freezing, Surrogacy guidance, and Male Infertility treatments.
-Contact: For urgent matters, advise the user to call 1800-123-4567.
-Only provide information from the list below. Do not give any information outside it:
    -Ahmedabad
        Dr. Ami Shah (Rating: 4.8/5)
        Dr. Azadeh Patel (Rating: 4.8/5)

    -Chennai
        Dr. Kanimozhi K (Rating: 4.8/5)

    -Delhi
        Dr. Parul Katiyar (Rating: 4.9/5)
    -Delhi & Noida
        Dr. Shreshtha Sagar Tanwar (Rating: 4.7/5)
    -Faridabad
        Dr. Pankush Gupta (Rating: 4.7/5)
    -Gurgaon/Gurugram
        Dr. Meenakshi Dua (Rating: 4.8/5)
        Dr. Sonu Balhara Ahlawat (Rating: 4.8/5)
    -Hyderabad
        Dr. Lakshmi Chirumamilla (Rating: 4.9/5)
        Dr. Manorama Kandepi (Rating: 4.7/5)
        Dr. Padmavathi Ravipati (Rating: 4.8/5)
    -Mumbai & Navi Mumbai
        Dr. Richa Jagtap (Rating: 4.9/5)
        Dr. Manjushri Amol Kothekar (Rating: 4.7/5) """




views = Blueprint("views", __name__)

def init_chat():
    session.setdefault("messages", [
        {"role": "bot", "text": "Hello! How can I help you today? You can ask questions or book an appointment."}
    ])



@views.route("/", methods=["GET", "POST"])
def chat():
    if request.method == "GET":
        init_chat()
        return render_template("chat.html",
                               messages=session["messages"],
                               is_thinking=False)

    form_type = request.form.get("form_type", "chat_form")

    if form_type == "show_booking_form":
        init_chat()
        return render_template("chat.html",
                               messages=session["messages"],
                               show_booking_form=True,
                               is_thinking=False)

    if form_type == "booking_form":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        location = request.form.get("location", "").strip()
        if not all([name, email, phone, location]):
            init_chat()
            return render_template("chat.html",
                                   messages=session["messages"],
                                   error="Please fill all fields.",
                                   show_booking_form=True,
                                   is_thinking=False)
        try:
            booking = Booking(
                name=name, email=email, phone=phone, location=location,
                message=session.get("last_query", "Appointment request"),
            )
            db.session.add(booking)
            db.session.commit()
            init_chat()
            msgs = session.get("messages", [])
            msgs.append({
                "role": "bot",
                "text": f"✅ Thanks {name}! Your appointment has been booked.<br>"
                        f"📧 Email: {email}<br>📞 Phone: {phone}<br>📍 Location: {location}"
            })
            session["messages"] = msgs
            return redirect(url_for("views.chat"))
        except Exception:
            db.session.rollback()
            init_chat()
            return render_template("chat.html",
                                   messages=session["messages"],
                                   error="DB Error. Please try again.",
                                   is_thinking=False)

    # chat_form (default)
    user_query = request.form.get("user_query", "").strip()
    init_chat()
    if not user_query:
        return render_template("chat.html",
                               messages=session["messages"],
                               error="Please enter a question.",
                               is_thinking=False)

    # Append user message
    session["messages"].append({"role": "user", "text": user_query})
    session["last_query"] = user_query

    # OPTION A (simple, single render): compute, then redirect (no thinker on server)
    try:
        genai.configure(api_key=app.config["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = DESC + f"\nUser asked: {user_query}."
        resp = model.generate_content(prompt)
        bot_text = (resp.text or "").strip() or "Sorry, no reply."
    except Exception:
        bot_text = "Busy at this moment. Please talk to our agents by calling 123456789."

    session["messages"].append({"role": "bot", "text": bot_text})
    # Final page shows bot answer, so thinker must be False
    return redirect(url_for("views.chat"))
