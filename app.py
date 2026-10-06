import streamlit as st
import sqlite3
from datetime import date
from urllib.parse import quote

DB = "fit_badou.db"

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    con.execute("""CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        prenom TEXT NOT NULL,
        telephone TEXT UNIQUE NOT NULL,
        classe TEXT,
        date_inscription TEXT NOT NULL
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS payments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        montant INTEGER NOT NULL,
        mois TEXT NOT NULL,
        date_paiement TEXT NOT NULL,
        FOREIGN KEY(student_id) REFERENCES students(id)
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS attendance(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        date_presence TEXT NOT NULL,
        present INTEGER NOT NULL DEFAULT 1,
        UNIQUE(student_id,date_presence),
        FOREIGN KEY(student_id) REFERENCES students(id)
    )""")
    con.commit(); con.close()

init_db()
st.set_page_config(page_title="FIT_BADOU – CeDT G15", page_icon="🏋️", layout="wide")

st.markdown("""
<style>
.main .block-container{max-width:1100px;padding-top:2rem}
h1,h2,h3{font-weight:800}
.badge{padding:8px 12px;border-radius:20px;background:#f2b705;color:#1d2b36;font-weight:700}
</style>
""", unsafe_allow_html=True)

st.title("🏋️ FIT_BADOU – CeDT G15")
st.caption("Fitness & Renforcement Musculaire • Coach Badou")

menu = st.sidebar.radio("Menu", ["Inscription étudiant","Tableau de bord","Présences","Paiements","Partager sur WhatsApp"])

if menu == "Inscription étudiant":
    st.header("Inscription étudiant")
    with st.form("registration"):
        c1,c2 = st.columns(2)
        nom = c1.text_input("Nom")
        prenom = c2.text_input("Prénom")
        tel = st.text_input("Téléphone", placeholder="77 000 00 00")
        classe = st.text_input("Classe / filière", placeholder="GC2C, BTS...")
        ok = st.form_submit_button("S'inscrire")
    if ok:
        if not nom or not prenom or not tel:
            st.error("Remplissez le nom, le prénom et le téléphone.")
        else:
            try:
                con=db()
                con.execute("INSERT INTO students(nom,prenom,telephone,classe,date_inscription) VALUES(?,?,?,?,?)",
                            (nom.strip(),prenom.strip(),tel.replace(" ",""),classe.strip(),str(date.today())))
                con.commit(); con.close()
                st.success(f"Bienvenue {prenom} {nom} ! Inscription enregistrée.")
            except sqlite3.IntegrityError:
                st.error("Ce numéro de téléphone est déjà inscrit.")

elif menu == "Tableau de bord":
    st.header("Tableau de bord Coach")
    con=db()
    total=con.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    today=con.execute("SELECT COUNT(*) FROM attendance WHERE date_presence=? AND present=1",(str(date.today()),)).fetchone()[0]
    revenue=con.execute("SELECT COALESCE(SUM(montant),0) FROM payments").fetchone()[0]
    rows=con.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
    con.close()
    a,b,c=st.columns(3)
    a.metric("Étudiants", total); b.metric("Présents aujourd'hui",today); c.metric("Paiements (FCFA)", f"{revenue:,}".replace(",", " "))
    st.subheader("Dernières inscriptions")
    st.dataframe([dict(r) for r in rows], use_container_width=True) if rows else st.info("Aucun étudiant.")

elif menu == "Présences":
    st.header("Gestion des présences")
    con=db()
    students=con.execute("SELECT * FROM students ORDER BY nom,prenom").fetchall()
    con.close()
    if not students: st.info("Aucun étudiant inscrit.")
    else:
        d=st.date_input("Date", date.today())
        for s in students:
            key=f"p_{s['id']}_{d}"
            con=db()
            old=con.execute("SELECT present FROM attendance WHERE student_id=? AND date_presence=?",(s["id"],str(d))).fetchone()
            con.close()
            present=st.checkbox(f"{s['prenom']} {s['nom']} — {s['classe'] or ''}", value=bool(old and old["present"]), key=key)
            if st.button("Enregistrer", key="save_"+key):
                con=db()
                con.execute("""INSERT INTO attendance(student_id,date_presence,present) VALUES(?,?,?)
                               ON CONFLICT(student_id,date_presence) DO UPDATE SET present=excluded.present""",
                            (s["id"],str(d),int(present)))
                con.commit(); con.close()
                st.success("Présence enregistrée.")

elif menu == "Paiements":
        st.header("Paiements")
        
        # --- PROTECTION MOT DE PASSE COACH ---
        pwd = st.text_input("Mot de passe Administrateur", type="password")
        if pwd != st.secrets.get("ADMIN_PASSWORD", "B@mba583"):
            st.warning("🔒 Accès restreint. Veuillez saisir le mot de passe valide.")
            st.stop()
        # -------------------------------------

        con=db(); students=con.execute("SELECT * FROM students ORDER BY nom,prenom").fetchall()
        if students:
            labels={f"{s['prenom']} {s['nom']} - {s['telephone']}":s["id"] for s in students}
            label=st.selectbox("Étudiant", list(labels))
            montant=st.number_input("Montant (FCFA)", min_value=0, value=5000, step=500)
            mois=st.text_input("Mois", value=date.today().strftime("%m/%Y"))
            if st.button("Enregistrer le paiement"):
                con=db(); con.execute("INSERT INTO payments(student_id,montant,mois,date_paiement) VALUES(?,?,?,?)",
                                     (labels[label],int(montant),mois,str(date.today())))
                con.commit(); con.close(); st.success("Paiement enregistré.")
        else: st.info("Aucun étudiant inscrit.")
    else: st.info("Aucun étudiant inscrit.")

elif menu == "Partager sur WhatsApp":
    st.header("Partager l'application")
    st.write("Voici le lien de l'application à partager aux étudiants :")
    st.code("https://fitbadoucedtg15-gqckyubpu9qfkudmtetypm.streamlit.app")

# --- BOUTON DE CONTACT COACH WHATSAPP ---
MON_NUMERO_WHATSAPP = "221774261843"

message_accueil = "Bonjour Coach Badou ! Je viens de m'inscrire au club FIT_BADOU et je souhaite recevoir mon programme d'entraînement."
lien_whatsapp = f"https://wa.me/{MON_NUMERO_WHATSAPP}?text={message_accueil.replace(' ', '%20')}"

st.sidebar.markdown("---")
st.sidebar.markdown("### 💬 Besoins d'infos / Programme ?")
st.sidebar.link_button("📲 Écrire au Coach sur WhatsApp", lien_whatsapp)


