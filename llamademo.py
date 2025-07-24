"""Tkinter-pohjainen käyttöliittymä, joka kysyy LLaMA-mallilta vastauksia."""
import subprocess
import re
import tkinter as tk
from tkinter import scrolledtext
import threading


def kysy_llamalta():
    """Hakee käyttäjän kysymyksen ja käynnistää vastaushaun taustasäikeessä."""
    kysymys = kysymyskentta.get()

    if not kysymys.strip():
        päivitä_vastaus("Anna jokin kysymys.")
        return

    päivitä_vastaus("Odota hetki, haetaan vastausta...")

    säie = threading.Thread(
        target=hae_vastaus_taustalla,
        args=(kysymys,),
        daemon=True
    )
    säie.start()


def hae_vastaus_taustalla(kysymys):
    """Suorittaa LLaMA-mallin komentoriviltä ja palauttaa vastauksen."""
    try:
        process = subprocess.Popen(
            ["ollama", "run", "llama3"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        output, _ = process.communicate(
            input=kysymys.encode("utf-8"),
            timeout=60
        )

        vastaus = output.decode("utf-8", errors="ignore")
        puhdas_vastaus = re.sub(
            r"\x1B\[[0-9;?]*[a-zA-Z]",
            "",
            vastaus
        ).strip()

        vastauskentta.after(
            0,
            lambda: päivitä_vastaus(puhdas_vastaus)
        )

    except subprocess.TimeoutExpired:
        process.kill()
        vastauskentta.after(
            0,
            lambda: päivitä_vastaus(
                "Aikakatkaisu: LLaMA ei vastannut ajoissa."
            )
        )
    except Exception as virhe:
        virheviesti = f"Virhe: {str(virhe)}"
        vastauskentta.after(0, lambda: päivitä_vastaus(virheviesti))


def päivitä_vastaus(teksti):
    """Päivittää vastauskentän sisällön pääsäikeessä."""
    def update():
        vastauskentta.delete("1.0", tk.END)
        vastauskentta.insert(tk.END, teksti)

    vastauskentta.after(0, update)


# Tkinter-käyttöliittymä
ikkuna = tk.Tk()
ikkuna.title("Kysy Llamalta")
ikkuna.geometry("500x400")

tk.Label(ikkuna, text="Kysy jotain:").pack(pady=5)

kysymyskentta = tk.Entry(ikkuna, width=60)
kysymyskentta.pack(pady=5)
kysymyskentta.bind("<Return>", lambda event: kysy_llamalta())

tk.Button(ikkuna, text="Kysy", command=kysy_llamalta).pack(pady=10)

tk.Label(ikkuna, text="Vastaus:").pack(pady=5)

vastauskentta = scrolledtext.ScrolledText(
    ikkuna,
    height=10,
    wrap=tk.WORD
)
vastauskentta.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

ikkuna.mainloop()
