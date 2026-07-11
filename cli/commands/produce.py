"""内容生产 CLI 命令。"""

import typer

app = typer.Typer(name="produce", help="内容生产")


@app.command("text")
def generate_text(
    topic_id: int = typer.Argument(..., help="选题 ID"),
):
    """生成文案。"""
    typer.echo(f"生成文案: 选题 #{topic_id}")


@app.command("cover")
def generate_cover(
    content_id: int = typer.Argument(..., help="内容 ID"),
):
    """生成封面图。"""
    typer.echo(f"生成封面: 内容 #{content_id}")


@app.command("video")
def edit_video(
    content_id: int = typer.Argument(..., help="内容 ID"),
):
    """视频初剪。"""
    typer.echo(f"视频初剪: 内容 #{content_id}")


@app.command("finalize")
def finalize_content(
    content_id: int = typer.Argument(..., help="内容 ID"),
):
    """精加工定稿。"""
    typer.echo(f"精加工定稿: 内容 #{content_id}")
