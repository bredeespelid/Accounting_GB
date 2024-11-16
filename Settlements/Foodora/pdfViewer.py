import tkinter as tk
from tkinter import filedialog, messagebox
from langchain_community.document_loaders import PyPDFLoader

def read_pdf(file_path):
    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()  # Leser alle sider i PDF-en
    content = "\n".join(page.page_content for page in pages)
    return content

def main():
    root = tk.Tk()
    root.withdraw()  # Skjul hovedvinduet

    # Åpne dialog for å velge PDF-filer
    file_paths = filedialog.askopenfilenames(
        title="Velg PDF-filer",
        filetypes=[("PDF files", "*.pdf")]
    )

    if not file_paths:
        messagebox.showinfo("Informasjon", "Ingen filer valgt. Programmet avsluttes.")
        return

    # Gå gjennom hver valgt fil og vis innholdet i konsollen
    for file_path in file_paths:
        try:
            content = read_pdf(file_path)
            print(f"Innhold fra {file_path}:\n{content}\n")
        except Exception as e:
            messagebox.showerror("Feil", f"Feil ved lesing av {file_path}: {str(e)}")

    messagebox.showinfo("Fullført", "Prosessering av PDF-filer er ferdig.")

if __name__ == "__main__":
    main()
