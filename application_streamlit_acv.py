import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Calculateur ACV - OneMW",
    page_icon="🌍",
    layout="centered"
)

# --- FACTEURS D'ÉMISSION (kgCO2e/unité) ---
# Valeurs issues de la littérature scientifique (2025-2026)
FE_PANNEAUX_CHINE = 456.7    # Moyenne des technologies (PERC, TOPCon, HJT) en kg CO2e / kWc
FE_PANNEAUX_EUROPE = 320.0   # Moyenne TOPCon/HJT Europe en kg CO2e / kWc
FE_ONDULEURS_KW = 35.0       # Onduleurs de chaîne en kg CO2e / kW
FE_STOCKAGE_KWH = 62.0       # Chimie LFP en kg CO2e / kWh
FE_STRUCTURE_KWC = 85.0      # Structure fixe en kg CO2e / kWc
FE_CABLAGE_M = 0.32          # Câble DC cuivre en kg CO2e / m
FE_PDL_KVA = 60.0            # Poste de livraison (enveloppe béton) en kg CO2e / kVA

# --- EN-TÊTE DE L'APPLICATION ---
st.title("🌍 Calculateur Bilan Carbone (ACV)")
st.markdown("**OneMW** - Outil interne d'estimation de l'impact carbone des centrales au sol.")
st.divider()

# --- BARRE LATÉRALE (FORMULAIRE) ---
with st.sidebar:
    st.header("⚙️ Paramètres de la centrale")
    
    with st.form("formulaire_acv"):
        w_panneaux = st.number_input("Modules PV (kWc)", min_value=0.0, value=2000.0, step=100.0)
        w_origine = st.selectbox("Origine des panneaux", options=["Chine", "Europe"])
        w_onduleurs = st.number_input("Onduleurs (kW/kVA)", min_value=0.0, value=2000.0, step=100.0)
        w_stockage = st.number_input("Stockage (kWh)", min_value=0.0, value=500.0, step=50.0)
        w_cablage = st.number_input("Câblage (m)", min_value=0, value=1500, step=100)
        w_pdl = st.number_input("Poste de livraison (unité)", min_value=0, value=1, step=1)
        
        submit = st.form_submit_button("📊 Lancer l'ACV", use_container_width=True)

# --- CALCULS ET AFFICHAGE ---
# Choix du facteur d'émission des panneaux
fe_panneaux_actuel = FE_PANNEAUX_CHINE if w_origine == "Chine" else FE_PANNEAUX_EUROPE

# Calculs des impacts
impact_panneaux = w_panneaux * fe_panneaux_actuel
impact_onduleurs = w_onduleurs * FE_ONDULEURS_KW
impact_stockage = w_stockage * FE_STOCKAGE_KWH
impact_structure = w_panneaux * FE_STRUCTURE_KWC  # Calculé par kWc pour simplifier
impact_cablage = w_cablage * FE_CABLAGE_M
# L'impact du PDL est calculé par kVA, on utilise la puissance des onduleurs comme référence
impact_pdl = w_pdl * (w_onduleurs * FE_PDL_KVA)

impact_total = sum([impact_panneaux, impact_onduleurs, impact_stockage, impact_structure, impact_cablage, impact_pdl])

# Affichage du Résultat Global (uniquement en tonnes)
st.subheader("Résultat Global")
st.metric(label="Impact Total (tonnes CO2e)", value=f"{impact_total / 1000:,.1f}".replace(',', ' '))

st.divider()

col_tableau, col_graphique = st.columns([1, 1.2])

categories = ['Modules PV', 'Onduleurs', 'Stockage', 'Structures', 'Câblage', 'Poste Livraison']
valeurs = [impact_panneaux, impact_onduleurs, impact_stockage, impact_structure, impact_cablage, impact_pdl]
couleurs = ['#2ca02c', '#1f77b4', '#ff7f0e', '#7f7f7f', '#9467bd', '#8c564b']

with col_tableau:
    st.subheader("Détail par poste")
    df_resultats = pd.DataFrame({
        "Poste": categories,
        "kgCO2e": valeurs
    })
    df_resultats["kgCO2e"] = df_resultats["kgCO2e"].apply(lambda x: f"{x:,.0f}".replace(',', ' '))
    
    # --- NOUVELLES LIGNES POUR LA COULEUR ---
    # 1. Création d'un dictionnaire liant chaque catégorie à sa couleur
    dict_couleurs = dict(zip(categories, couleurs))
    
    # 2. Fonction pour colorer le fond de la ligne et mettre le texte en blanc
    def coloriser_ligne(row):
        couleur = dict_couleurs.get(row['Poste'], '')
        return [f'background-color: {couleur}; color: white;' for _ in row]
        
    # 3. Application du style au tableau
    df_style = df_resultats.style.apply(coloriser_ligne, axis=1)
    
    # 4. Affichage du tableau stylisé au lieu du tableau classique
    st.dataframe(df_style, hide_index=True, use_container_width=True)
    # ----------------------------------------

with col_graphique:
    st.subheader("Répartition")
    
    labels_filtres = [l for l, v in zip(categories, valeurs) if v > 0]
    valeurs_filtres = [v for v in valeurs if v > 0]
    couleurs_filtrees = [c for c, v in zip(couleurs, valeurs) if v > 0]
    
    fig, ax = plt.subplots(figsize=(5, 5))
    fig.patch.set_alpha(0.0) 
    ax.pie(valeurs_filtres, labels=labels_filtres, autopct='%1.1f%%', startangle=140, colors=couleurs_filtrees, 
           textprops={'color': "white" if st.get_option("theme.base") == "dark" else "black"})
    
    st.pyplot(fig)
