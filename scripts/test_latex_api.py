import requests
import urllib.parse
from pathlib import Path

def test_latex_online():
    # 1. Code LaTeX minimal (Hello World)
    latex_code = r"""
\documentclass{article}
\begin{document}
\section*{Test LatexOnline}
Ceci est un test de compilation genere par reZume.
\begin{itemize}
    \item Fonctionnalite : OK
    \item Status : Succes
\end{itemize}
\end{document}
"""
    
    base_url = "https://latexonline.cc/compile"
    output_file = Path("test_latex_api.pdf")
    
    print(f"📡 Envoi de la requete a {base_url}...")
    
    try:
        # Encodage du texte pour l'URL (méthode GET)
        params = {'text': latex_code}
        query_string = urllib.parse.urlencode(params)
        full_url = f"{base_url}?{query_string}"
        
        response = requests.get(full_url, timeout=30)
        
        if response.status_code == 200:
            # On vérifie que le contenu ressemble à un PDF (%PDF-...)
            if response.content.startswith(b"%PDF"):
                with open(output_file, "wb") as f:
                    f.write(response.content)
                print(f"✅ SUCCÈS ! Le fichier '{output_file}' a été généré ({len(response.content)} octets).")
            else:
                print("❌ ERREUR : Le serveur a repondu 200 mais le contenu n'est pas un PDF.")
                print("Extrait de la reponse :", response.content[:100])
        else:
            print(f"❌ ÉCHEC : Code HTTP {response.status_code}")
            print("Message :", response.text)
            
    except Exception as e:
        print(f"❌ ERREUR de connexion : {e}")

if __name__ == "__main__":
    test_latex_online()
