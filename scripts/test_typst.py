import typst
import os

def test_typst_compilation():
    temp_file = "test_input.typ"
    output_path = "outputs/test_typst.pdf"
    
    # Création d'un petit fichier de test
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write("= Hello reZume\nCeci est un test Typst depuis un fichier physique.")

    print(f"--- Début de la compilation de {temp_file} ---")
    try:
        # Compilation vers PDF
        pdf_bytes = typst.compile(temp_file)
        
        # Sauvegarde du résultat
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
            
        print(f"✅ Succès ! Le PDF a été généré ici : {output_path}")
    except Exception as e:
        print(f"❌ Erreur lors de la compilation : {e}")
    finally:
        # Nettoyage
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == "__main__":
    test_typst_compilation()
