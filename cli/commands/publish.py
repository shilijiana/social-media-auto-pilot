"""多平台发布 CLI 命令。"""

import typer

app = typer.Typer(name="publish", help="多平台发布")


@app.command("run")
def publish_content(
    content_id: int = typer.Argument(..., help="内容 ID"),
    platform: str = typer.Option("", "--platform", "-p", help="目标平台"),
    account: str = typer.Option("", "--account", "-a", help="账号名称"),
):
    """发布内容到指定平台。"""
    typer.echo(f"发布内容 #{content_id} 到 {platform} (账号: {account})")


@app.command("status")
def publish_status(
    publication_id: int = typer.Argument(..., help="发布记录 ID"),
):
    """查看发布状态。"""
    typer.echo(f"发布状态: #{publication_id}")
