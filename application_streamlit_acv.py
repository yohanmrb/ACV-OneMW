import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# --- CONFIGURATION DE LA PAGE ---
# Doit toujours être la première commande Streamlit
st.set_page_config(
    page_title="Calculateur ACV - OneMW",
    page_icon="🌍",
    layout="centered"
)

# --- FACTEURS D'ÉMISSION PAR DÉFAUT (kgCO2e/unité) ---
FE_PANNEAUX_KWC = 600.0
FE_ONDULEURS_KW = 150.0
FE_STOCKAGE_KWH = 120.0
FE_STRUCTURE_TONNE = 2500.0
FE_CABLAGE_KM = 3000.0

# --- EN-TÊTE DE L'APPLICATION ---
st.title("🌍 Calculateur Bilan Carbone (ACV)")
st.markdown("**OneMW** - Outil interne d'estimation de l'impact carbone des centrales au sol.")
st.divider()

# --- BARRE LATÉRALE (FORMULAIRE) ---
with st.sidebar:
    st.header("⚙️ Paramètres de la centrale")
    
    # Création d'un formulaire pour ne recalculer que lorsqu'on clique sur le bouton
    with st.form("formulaire_acv"):
        w_panneaux = st.number_input("Modules PV (kWc)", min_value=0.0, value=2000.0, step=100.0)
        w_onduleurs = st.number_input("Onduleurs (kW)", min_value=0.0, value=2000.0, step=100.0)
        w_stockage = st.number_input("Stockage (kWh)", min_value=0.0, value=500.0, step=50.0)
        w_structure = st.number_input("Structures acier (tonnes)", min_value=0.0, value=60.0, step=5.0)
        w_cablage = st.number_input("Raccordement (km)", min_value=0.0, value=1.5, step=0.1)
        
        # Le bouton d'exécution
        submit = st.form_submit_button("📊 Lancer l'ACV", use_container_width=True)

# --- CALCULS ET AFFICHAGE (Exécuté au lancement ou au clic) ---
# Calculs
impact_panneaux = w_panneaux * FE_PANNEAUX_KWC
impact_onduleurs = w_onduleurs * FE_ONDULEURS_KW
impact_stockage = w_stockage * FE_STOCKAGE_KWH
impact_structure = w_structure * FE_STRUCTURE_TONNE
impact_cablage = w_cablage * FE_CABLAGE_KM

impact_total = sum([impact_panneaux, impact_onduleurs, impact_stockage, impact_structure, impact_cablage])

# Affichage des métriques principales en haut
st.subheader("Résultat Global")
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Impact Total (tonnes CO2e)", value=f"{impact_total / 1000:,.1f}".replace(',', ' '))
with col2:
    st.metric(label="Impact Total (kg CO2e)", value=f"{impact_total:,.0f}".replace(',', ' '))

st.divider()

# Affichage des détails sous forme de colonnes (Tableau et Graphique)
col_tableau, col_graphique = st.columns([1, 1.2])

# Préparation des données
categories = ['Modules PV', 'Onduleurs', 'Stockage', 'Structures', 'Câblage']
valeurs = [impact_panneaux, impact_onduleurs, impact_stockage, impact_structure, impact_cablage]
couleurs = ['#2ca02c', '#1f77b4', '#ff7f0e', '#7f7f7f', '#9467bd']

with col_tableau:
    st.subheader("Détail par poste")
    # Création d'un tableau propre
    df_resultats = pd.DataFrame({
        "Poste": categories,
        "kgCO2e": valeurs
    })
    # Formatage des nombres pour plus de lisibilité
    df_resultats["kgCO2e"] = df_resultats["kgCO2e"].apply(lambda x: f"{x:,.0f}".replace(',', ' '))
    st.dataframe(df_resultats, hide_index=True, use_container_width=True)

with col_graphique:
    st.subheader("Répartition")
    
    # Filtrer les valeurs à zéro pour le graphique
    labels_filtres = [l for l, v in zip(categories, valeurs) if v > 0]
    valeurs_filtres = [v for v in valeurs if v > 0]
    couleurs_filtrees = [c for c, v in zip(couleurs, valeurs) if v > 0]
    
    # Création du graphique camembert avec Matplotlib (fond transparent)
    fig, ax = plt.subplots(figsize=(5, 5))
    fig.patch.set_alpha(0.0) # Fond transparent pour s'adapter au thème clair/sombre de Streamlit
    ax.pie(valeurs_filtres, labels=labels_filtres, autopct='%1.1f%%', startangle=140, colors=couleurs_filtrees, 
           textprops={'color': "white" if st.get_option("theme.base") == "dark" else "black"})
    
    # Affichage du graphique dans Streamlit
    st.pyplot(fig)

# Note de bas de page
st.caption("⚠️️ Ces valeurs sont des estimations basées sur des facteurs d'émission par défaut. Elles devront être mises à jour avec les fiches PEP/ADEME spécifiques au projet.")