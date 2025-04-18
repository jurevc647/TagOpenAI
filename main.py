from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from openai import OpenAI
import ast
import os

# ✅ Inicializacija OpenAI klienta z API ključem iz okolja
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 📚 Vnaprej definirani tagi z opisi
TAGI_OPISI = {
    "srčno-žilni sistem": "Raziskave povezane s srcem, žilami in krvnim obtokom.",
    "matematični model": "Uporaba enačb in simulacij za opis bioloških sistemov.",
    "biomehanika": "Proučevanje mehanskega vedenja tkiv, organov in telesa.",
    "JVPnaprava": "Naprava za merjenje pritiska v jugularni veni.",
    "vesoljska medicina": "Fiziološke spremembe v breztežnosti.",
    "ultrazvok": "Uporaba ultrazvoka za slikanje tkiv.",
    "ni zadetka": "Opis ne ustreza nobeni kategoriji."
}
TAGI = list(TAGI_OPISI.keys())


@app.get("/", response_class=HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "tags": [(tag, TAGI_OPISI[tag]) for tag in TAGI],
        "vnos": "",
        "izbrani": []
    })


@app.post("/", response_class=HTMLResponse)
async def form_post(request: Request, raziskava: str = Form(...)):
    tagi_z_opisi = "\n".join([f"- {tag}: {opis}" for tag, opis in TAGI_OPISI.items()])

    prompt = f"""
Na podlagi spodnjega opisa izberi največ 3 najprimernejše tage izmed naslednjih.
Vsak tag ima priložen opis, ki ti pomaga razumeti, kaj pomeni.

Tagi:
{tagi_z_opisi}

Če noben tag ne ustreza, izberi 'ni zadetka'.
Vrni samo seznam izbranih tagov kot Python seznam (npr. ["tag1", "tag2"]).

Opis raziskave: "{raziskava}"
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # ali gpt-4 / gpt-4o, če imaš dostop
            messages=[
                {"role": "system", "content": "Ti si pomočnik za klasifikacijo znanstvenih raziskav."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=100
        )
        odgovor = response.choices[0].message.content.strip()
        selected_tags = ast.literal_eval(odgovor)
    except Exception as e:
        selected_tags = [f"Napaka: {str(e)}"]

    prikaz = [(tag, TAGI_OPISI[tag]) for tag in TAGI]
    izbrani = [tag for tag in selected_tags if tag in TAGI]

    return templates.TemplateResponse("index.html", {
        "request": request,
        "tags": prikaz,
        "vnos": raziskava,
        "izbrani": izbrani
    })
