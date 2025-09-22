import streamlit as st
import json
import requests
import traceback

# Configuration de l'API Gemini
# Vous devez insérer votre propre clé d'API ici.
# Obtenez-la sur https://aistudio.google.com/app/apikey
API_KEY = "AIzaSyCi4hp7QaEnaksgmuHBMGqY_hEjwn8UVSk"
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"

# --- Fonction pour envoyer une requête à l'API Gemini ---
def generate_text_with_api(prompt):
    """
    Envoie une requête à l'API de génération de contenu de Google et renvoie le texte généré.
    """
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }
    
    # Vérification de la clé d'API avant d'envoyer la requête
    if API_KEY == "VOTRE_CLE_API_ICI" or not API_KEY:
        st.error("La clé d'API est manquante ou invalide. Veuillez l'ajouter dans le code.")
        return None

    try:
        st.info("Envoi de la requête à l'API...")
        full_api_url = f"{API_URL}?key={API_KEY}"
        response = requests.post(full_api_url, headers=headers, json=payload)
        response.raise_for_status()
        st.success("Requête réussie ! Traitement de la réponse...")
        
        result = response.json()
        
        # Vérifie si la réponse contient du texte généré
        if result and result.get("candidates") and result["candidates"][0].get("content"):
            generated_text = result["candidates"][0]["content"]["parts"][0]["text"]
            return generated_text
        else:
            st.error("L'API n'a pas renvoyé de texte généré.")
            st.json(result)
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Une erreur s'est produite lors de la connexion à l'API : {e}")
        st.warning("Veuillez vérifier votre connexion Internet.")
        return None
    except Exception as e:
        st.error(f"Une erreur inattendue s'est produite : {e}")
        st.error(f"Détails de l'erreur : \n{traceback.format_exc()}")
        return None

def detect_language(code_snippet):
    """
    Détecte le langage de programmation d'un extrait de code en utilisant l'API Gemini.
    """
    prompt = f"Détectez le langage de programmation de ce code. Répondez uniquement avec le nom du langage, sans autre texte ni ponctuation. Par exemple: Python, JavaScript, Java, etc.\n\n{code_snippet}"
    detected_lang = generate_text_with_api(prompt)
    if detected_lang:
        # Nettoyer la réponse pour ne garder que le nom du langage
        return detected_lang.strip()
    return None

# --- Interface utilisateur Streamlit ---
def main():
    """
    Fonction principale de l'application Streamlit.
    """
    st.set_page_config(
        page_title="Convertisseur de code IA",
        page_icon="💻",
        layout="wide"
    )

    st.title("Mini-Projet IA : Convertisseur de code 🤖")
    st.markdown("Convertisseur du code d'un langage à un autre")

    # Liste des langages de programmation pris en charge.
    languages = [
        "Python", "JavaScript", "C++", "C", "Java", "Go", "Ruby", "PHP", "Rust", "Swift", "Kotlin"
    ]

    # Sélecteurs pour les langages source et cible.
    col1, col2 = st.columns(2)
    with col1:
        source_lang = st.selectbox("Langage source :", languages, index=0)
    with col2:
        target_lang = st.selectbox("Langage cible :", languages, index=1)

    # Zone de texte pour le code source.
    source_code = st.text_area(
        "Collez votre code ici :",
        height=300,
        placeholder=f"Collez votre code {source_lang} ici..."
    )

    # Boutons pour les actions.
    col_convert, col_explain = st.columns(2)

    with col_convert:
        convert_button = st.button("Convertir le code", type="primary")

    with col_explain:
        explain_button = st.button("Expliquer le code")

    # Logique du bouton de conversion
    if convert_button:
        if not source_code:
            st.warning("Veuillez coller du code à convertir.")
        elif source_lang == target_lang:
            st.warning("Veuillez sélectionner des langages source et cible différents.")
        else:
            # Détection du langage du code entré
            with st.spinner("Détection du langage en cours..."):
                detected_lang = detect_language(source_code)
            
            if detected_lang and detected_lang.lower() != source_lang.lower():
                st.warning(f"Le langage du code détecté est **{detected_lang}**, mais vous avez sélectionné **{source_lang}**. Veuillez corriger votre choix de langage source pour une meilleure conversion.")
            else:
                with st.spinner("Conversion en cours..."):
                    # Construction du prompt pour le modèle.
                    prompt = (
                        f"Translate the following {source_lang} code to {target_lang}. "
                        "Only provide the code, no explanations or extra text."
                        f"\n\n{source_code}"
                    )
                    
                    # Appel de la nouvelle fonction d'API.
                    output = generate_text_with_api(prompt)
                    
                    if output:
                        st.markdown("---")
                        st.subheader(f"Code converti en {target_lang} :")
                        # Utilisation de st.code pour une mise en forme correcte.
                        st.code(output, language=target_lang.lower())
    
    # Logique du bouton d'explication
    if explain_button:
        if not source_code:
            st.warning("Veuillez coller du code à expliquer.")
        else:
            with st.spinner("Génération de l'explication..."):
                # Construction du prompt pour le modèle
                prompt_explanation = f"Expliquez en un court paragraphe le script suivant en français:\n\n{source_code}"

                # Appel de la fonction d'API pour l'explication
                explanation_output = generate_text_with_api(prompt_explanation)

                if explanation_output:
                    st.markdown("---")
                    st.subheader("Explication du script :")
                    st.markdown(explanation_output)

    st.markdown("---")
    st.markdown("<sub>Ce projet est alimenté par l'API de Google et un modèle de langage (LLM).</sub>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
