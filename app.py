import streamlit as st
import sqlite3
from datetime import date

# Config page
st.set_page_config(page_title="FIT_BADOU - CeDT G15", page_icon="🏋️️‍♂️")

# Base de données
def db():
    con = sqlite3.connect("fit_badou.db")
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    con.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT, prenom TEXT, telephone TEXT, date_naissance TEXT
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER, montant INTEGER, mois TEXT, date_paiement TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER, date_presence TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)
    con.commit()
    con.close()

init_db()

st.title("🏋️‍♂️ FIT_BADOU - CeDT G15")

# Navigation
menu = st.sidebar.selectbox("Menu", [
    "Inscription", 
    "Liste des étudiants", 
    "Présences", 
    "Paiements", 
    "Partager sur WhatsApp"
])

if menu == "Inscription":
    st.header("Inscription d'un étudiant")
    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    tel = st.text_input("Téléphone")
    dob = st.date_input("Date de naissance")
    if st.button("S'inscrire"):
        if nom and prenom and tel:
            con = db()
            con.execute("INSERT INTO students(nom,prenom,telephone,date_naissance) VALUES(?,?,?,?)",
                        (nom, prenom, tel, str(dob)))
            con.commit()
            con.close()
            st.success("Inscription réussie !")
        else:
            st.error("Veuillez remplir tous les champs.")

elif menu == "Liste des étudiants":
    st.header("Liste des étudiants")
    con = db()
    students = con.execute("SELECT * FROM students ORDER BY nom,prenom").fetchall()
    con.close()
    if students:
        for s in students:
            st.write(f"• **{s['prenom']} {s['nom']}** - Tel: {s['telephone']}")
    else:
        st.info("Aucun étudiant inscrit pour le moment.")

elif menu == "Présences":
    st.header("Gestion des présences")
    con = db()
    students = con.execute("SELECT * FROM students ORDER BY nom,prenom").fetchall()
    if students:
        labels = {f"{s['prenom']} {s['nom']} - {s['telephone']}": s["id"] for s in students}
        label = st.selectbox("Étudiant", list(labels))
        if st.button("Marquer présent"):
            con.execute("INSERT INTO attendance(student_id,date_presence) VALUES(?,?)",
                        (labels[label], str(date.today())))
            con.commit()
            con.close()
            st.success("Présence enregistrée.")
    else:
        st.info("Aucun étudiant inscrit.")

elif menu == "Paiements":
    st.header("Paiements")
    
    # --- PROTECTION MOT DE PASSE COACH ---
    pwd = st.text_input("Mot de passe Administrateur", type="password")
    if pwd != st.secrets.get("ADMIN_PASSWORD", "B@mba583"):
        st.warning("🔒 Accès restreint. Veuillez saisir le mot de passe valide.")
        st.stop()
    # -------------------------------------

    con = db()
    students = con.execute("SELECT * FROM students ORDER BY nom,prenom").fetchall()
    if students:
        labels = {f"{s['prenom']} {s['nom']} - {s['telephone']}": s["id"] for s in students}
        label = st.selectbox("Étudiant", list(labels))
        montant = st.number_input("Montant (FCFA)", min_value=0, value=5000, step=500)
        mois = st.text_input("Mois", value=date.today().strftime("%m/%Y"))
        if st.button("Enregistrer le paiement"):
            con = db()
            con.execute("INSERT INTO payments(student_id,montant,mois,date_paiement) VALUES(?,?,?,?)",
                        (labels[label], int(montant), mois, str(date.today())))
            con.commit()
            con.close()
            st.success("Paiement enregistré.")
    else:
        st.info("Aucun étudiant inscrit.")

elif menu == "Partager sur WhatsApp":
    st.header("Partager l'application")
    st.write("Voici le lien de l'application à partager aux étudiants :")
    st.code("https://fitbadoucedtg15-gqckyubpu9qfkudmtetypm.streamlit.app")

# --- BOUTON CONTACT COACH WHATSAPP EN BARRE LATÉRALE ---
MON_NUMERO_WHATSAPP = "221774261843"
message_accueil = "Bonjour Coach Badou ! Je viens de m'inscrire au club FIT_BADOU et je souhaite recevoir mon programme d'entraînement."
lien_whatsapp = f"https://wa.me/{MON_NUMERO_WHATSAPP}?text={message_accueil.replace(' ', '%20')}"

st.sidebar.markdown("---")
st.sidebar.markdown("### 💬 Besoins d'infos / Programme ?")
st.sidebar.link_button("📲 Écrire au Coach sur WhatsApp", lien_whatsapp)
