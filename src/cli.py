"""CLI principal du pipeline de publication."""
import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import box

app = typer.Typer(help="Pipeline de publication sociale pour Code Freelance")
console = Console()

CONTENT_DIR = Path(__file__).parent.parent / "content"


@app.command("list")
def list_posts(
    status: str = typer.Option(None, "--status", "-s", help="Filtrer par statut: draft|ready|published"),
):
    """Liste tous les posts et leur statut."""
    from src.parser import load_posts

    posts = load_posts(CONTENT_DIR, status=status)
    if not posts:
        console.print("[yellow]Aucun post trouvé.[/yellow]")
        raise typer.Exit()

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("Fichier", style="dim")
    table.add_column("Statut")
    table.add_column("Date")
    table.add_column("Titre")

    status_colors = {"draft": "yellow", "ready": "green", "published": "blue"}

    for post in posts:
        color = status_colors.get(post.status, "white")
        date_str = post.date.strftime("%Y-%m-%d %H:%M") if post.date else "-"
        table.add_row(
            post.path.name,
            f"[{color}]{post.status}[/{color}]",
            date_str,
            post.title,
        )

    console.print(table)


@app.command("publish")
def publish_now(
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Simuler sans publier"),
):
    """Publie les posts dont la date est échue (status: ready)."""
    from src.parser import load_posts, mark_published
    from src.publishers.bluesky import publish_to_bluesky

    posts = load_posts(CONTENT_DIR, status="ready")
    due = [p for p in posts if p.is_due]

    if not due:
        console.print("[green]Aucun post à publier pour l'instant.[/green]")
        raise typer.Exit()

    for post in due:
        console.print(f"\n[bold]Publication :[/bold] {post.title}")
        console.print(f"[dim]{post.body[:80]}...[/dim]" if len(post.body) > 80 else f"[dim]{post.body}[/dim]")

        if dry_run:
            console.print("[yellow][DRY RUN] Serait publié sur BlueSky[/yellow]")
            continue

        try:
            publish_to_bluesky(post.body)
            console.print("[green]✓ Publié sur BlueSky[/green]")
            mark_published(post)
        except Exception as e:
            console.print(f"[red]✗ Erreur BlueSky: {e}[/red]")


@app.command("generate")
def generate_posts(
    count: int = typer.Option(5, "--count", "-c", help="Nombre de posts à générer"),
    theme: str = typer.Option("general", "--theme", "-t", help="Theme: esn|livre|formation|general"),
):
    """Génère des brouillons de posts via Claude API."""
    from src.generator.claude import generate_drafts

    console.print(f"[cyan]Génération de {count} posts sur le thème '{theme}'...[/cyan]")
    drafts = generate_drafts(count=count, theme=theme)

    for i, draft in enumerate(drafts, 1):
        out_path = CONTENT_DIR / "drafts" / f"generated-{theme}-{i:02d}.adoc"
        out_path.write_text(draft, encoding="utf-8")
        console.print(f"[green]✓[/green] {out_path.name}")

    console.print(f"\n[bold]{len(drafts)} brouillons créés dans content/drafts/[/bold]")
    console.print("Relis-les, modifie :status: draft → ready pour les activer.")


if __name__ == "__main__":
    app()
