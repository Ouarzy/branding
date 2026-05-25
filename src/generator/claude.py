"""Génération de posts via Claude API."""
import os
import anthropic
from pathlib import Path
from datetime import datetime, timedelta

BOOK_SUMMARY = """
Code Freelance est un livre d'Emilien Pecoul qui guide les développeurs salariés
(notamment ceux en ESN) vers le freelance. Il aborde : comment trouver ses premières missions,
fixer son TJM, gérer l'administratif, construire son réseau, et trouver l'épanouissement
dans son travail. L'auteur partage son expérience personnelle de transition.
La formation associée : https://formation.hackyourjob.com/catalogue/devenir-freelance-tech.html
"""

THEMES = {
    "esn": "La vie en ESN : frustrations, plafond de verre, manque d'autonomie",
    "livre": "Le contenu du livre Code Freelance et ses enseignements",
    "formation": "La formation 'Devenir Freelance Tech' et ce qu'elle apporte",
    "general": "Le freelance tech en général : liberté, TJM, missions, clients",
}

SYSTEM_PROMPT = """Tu es un assistant qui aide Emilien Pecoul à créer du contenu pour les réseaux sociaux.
La cible : développeurs et développeuses salariés, souvent en ESN, qui ne se sentent pas épanouis.
Ton style : authentique, bienveillant, concret. Pas de marketing agressif. Pas de promesses miraculeuses.
Tu montres une vraie valeur, tu partages une expérience réelle, tu poses des questions qui font réfléchir.
Format de sortie : AsciiDoc selon le template fourni.
"""


def generate_drafts(count: int = 5, theme: str = "general") -> list[str]:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    theme_desc = THEMES.get(theme, THEMES["general"])

    user_prompt = f"""Génère {count} posts pour les réseaux sociaux (X et BlueSky) sur le thème : {theme_desc}

Contexte du livre :
{BOOK_SUMMARY}

Contraintes :
- Maximum 280 caractères par post (pour X)
- Ton authentique, pas de jargon marketing
- Chaque post doit apporter quelque chose (réflexion, conseil, anecdote)
- Varie les formats : question ouverte, partage d'expérience, conseil pratique
- Mentionne le livre ou la formation avec subtilité, pas systématiquement

Pour chaque post, utilise ce format AsciiDoc EXACT :

= [Titre court]
:date: [date YYYY-MM-DD HH:MM, en commençant demain, espacement 2-3 jours]
:networks: x,bluesky
:status: draft
:tags: [tags pertinents]

[Texte du post]

---

"""

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = response.content[0].text
    drafts = [block.strip() for block in raw.split("---") if block.strip()]
    return drafts[:count]
