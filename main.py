from fastapi import Form
from typing import List

@app.post("/", response_class=HTMLResponse)
async def form_post(request: Request, raziskava: str = Form(...), izbrani: List[str] = Form([])):
    tagi_z_opisi = "\n".join([f"- {tag}: {opis}" for tag, opis in TAGI_OPISI.items()])
    prompt = f"""
Na podlagi spodnjega opisa izberi največ 3 najprimernejše tage izmed naslednjih.

Tagi:
{tagi_z_opisi}

Če noben tag ne ustreza, izberi 'ni zadetka'.
Vrni samo seznam izbranih tagov kot Python seznam (npr. ["tag1", "tag2"]).

Opis raziskave: "{raziskava}"
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ti si pomočnik za klasifikacijo znanstvenih raziskav."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=100
        )
        odgovor = response.choices[0].message.content.strip()
        predlagani_tagi = ast.literal_eval(odgovor)

        # Če uporabnik ni ročno označil ničesar, uporabi predloge modela
        if not izbrani:
            izbrani = [tag for tag in predlagani_tagi if tag in TAGI]

    except Exception as e:
        izbrani = [f"Napaka: {str(e)}"]

    prikaz = [(tag, TAGI_OPISI[tag]) for tag in TAGI]
    return templates.TemplateResponse("index.html", {
        "request": request,
        "tags": prikaz,
        "vnos": raziskava,
        "izbrani": izbrani
    })
