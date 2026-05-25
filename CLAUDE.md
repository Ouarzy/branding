# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project context

Pipeline semi-automatisé de publication sur X et BlueSky pour promouvoir le livre **Code Freelance** d'Emilien Pecoul et la formation associée (https://formation.hackyourjob.com/catalogue/devenir-freelance-tech.html).

**Cible** : développeurs salariés (souvent en ESN) qui ne s'épanouissent pas. Ils n'aiment pas le marketing agressif — le ton doit être authentique, bienveillant, concret.

**Workflow utilisateur** :
1. Générer des brouillons via `branding generate`
2. Relire et valider les `.adoc` en changeant `:status: draft` → `:status: ready`
3. GitHub Actions publie automatiquement les posts dont la date est échue

## Commands

```bash
# Installation
pip install -e ".[dev]"

# Lister les posts
branding list
branding list --status ready

# Générer des brouillons (nécessite ANTHROPIC_API_KEY)
branding generate --count 5 --theme esn   # themes: esn|livre|formation|general

# Publier maintenant (posts status:ready dont la date est passée)
branding publish
branding publish --dry-run   # simuler sans publier

# Lint
ruff check src/
```

## Architecture

```
content/
  _template.adoc       # template avec toutes les métadonnées
  drafts/              # brouillons à relire (status: draft ou ready)
  published/           # archivage manuel optionnel

src/
  parser.py            # parse les .adoc, extrait métadonnées + body → Post dataclass
  cli.py               # CLI Typer : list | publish | generate
  publishers/
    x.py               # tweepy → X API v2
    bluesky.py         # atproto → AT Protocol BlueSky
  generator/
    claude.py          # Claude API (Opus) → génère des batches de posts en .adoc

.github/workflows/
  publish.yml          # cron toutes les heures 7h-20h UTC, publie + commit statuts
```

### Format AsciiDoc des posts

Chaque fichier `.adoc` dans `content/` contient :
```asciidoc
= Titre
:date: 2026-06-01 09:00
:networks: x,bluesky
:status: draft          # draft | ready | published
:tags: freelance,esn

Texte du post (≤280 car. pour X)
```

`parser.py` ignore les fichiers préfixés par `_` et les lignes commençant par `//`.

### Variables d'environnement requises

Voir `.env.example`. En production, stockées dans GitHub Actions Secrets :
- `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`
- `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD`
- `ANTHROPIC_API_KEY`

## Key decisions & constraints

- **Ton éditorial** : jamais de promesses miraculeuses, pas de "tu vas gagner 10x plus". Montrer la valeur réelle, partager des expériences concrètes.
- **Limite X** : 280 caractères max par post. Le parser ne tronque pas — c'est à l'utilisateur de respecter la limite lors de la rédaction.
- **GitHub Actions** publie puis committe le changement de statut (`published`) avec `[skip ci]` pour éviter les boucles.
- **Génération Claude** : utilise `claude-opus-4-7` pour la qualité éditoriale. Les drafts générés ne sont jamais publiés sans validation manuelle.
