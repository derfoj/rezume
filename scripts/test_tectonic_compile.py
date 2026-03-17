
import os
import sys
import subprocess
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_tectonic_installation():
    print("=== TEST DE L'INSTALLATION TECTONIC ===")
    try:
        result = subprocess.run(["tectonic", "--version"], capture_output=True, text=True, check=True)
        print(f"✅ Tectonic est présent : {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Tectonic n'est pas trouvé dans le PATH ou ne fonctionne pas.")
        return False

def test_compilation():
    print("\n=== TEST DE COMPILATION ===")
    
    # Création d'un répertoire de test
    test_dir = Path("outputs/tectonic_test")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    tex_path = test_dir / "test_document.tex"
    pdf_path = test_dir / "test_document.pdf"
    
    # Suppression du PDF existant pour être sûr
    if pdf_path.exists():
        pdf_path.unlink()

    # Code LaTeX minimal
    latex_content = r"""
\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\begin{document}
\title{Test de Compilation Tectonic}
\author{reZume Engine}
\date{\today}
\maketitle

\section{Introduction}
Ceci est un document de test généré automatiquement pour vérifier que le moteur \textbf{Tectonic} fonctionne correctement sur cette machine.

\section{Vérification Unicode}
Test des caractères accentués : é, à, è, ô, î, ù.
Test de symboles : €, $\bullet$, $\rightarrow$.

\section{Conclusion}
Si vous lisez ceci dans un PDF, alors la compilation a réussi !
\end{document}
"""

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_content)
    
    print(f"📝 Fichier LaTeX créé : {tex_path}")
    print("🚀 Lancement de la compilation (cela peut prendre du temps la première fois)...")
    
    try:
        # Commande : tectonic -o <output_dir> <input_file>
        cmd = ["tectonic", "-o", str(test_dir), str(tex_path)]
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if process.returncode == 0:
            if pdf_path.exists():
                print(f"✅ SUCCÈS ! PDF généré à : {pdf_path}")
                print(f"📂 Taille du fichier : {pdf_path.stat().st_size} octets")
            else:
                print("❌ ERREUR : Le processus s'est terminé sans erreur mais le PDF est absent.")
        else:
            print("❌ ÉCHEC DE COMPILATION")
            print("--- STDOUT ---")
            print(process.stdout)
            print("--- STDERR ---")
            print(process.stderr)
            
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT : La compilation a mis plus de 2 minutes.")
    except Exception as e:
        print(f"❌ ERREUR INATTENDUE : {str(e)}")

if __name__ == "__main__":
    if test_tectonic_installation():
        test_compilation()
    else:
        print("\n💡 CONSEIL : Si vous avez installé Tectonic récemment, fermez et rouvrez votre terminal.")
        print("💡 CONSEIL : Vérifiez que 'tectonic.exe' est bien dans un dossier listé dans votre PATH (ex: C:\\Windows).")
