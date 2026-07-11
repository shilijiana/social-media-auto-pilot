"""审阅管理 CLI 命令。"""

import typer

app = typer.Typer(name="review", help="审阅管理")


@app.command("pending")
def list_pending():
    """列出待审阅内容。"""
    typer.echo("待审阅列表（待实现）")


@app.command("approve")
def approve_content(
    content_id: int = typer.Argument(..., help="内容 ID"),
):
    """通过审阅。"""
    typer.echo(f"审阅通过: 内容 #{content_id}")


@app.command("reject")
def reject_content(
    content_id: int = typer.Argument(..., help="内容 ID"),
    reason: str = typer.Option("", "--reason", "-r", help="驳回原因"),
):
    """驳回审阅。"""
    typer.echo(f"审阅驳回: 内容 #{content_id}, 原因: {reason}")


@app.command("status")
def review_status():
    """查看当前审阅模式状态。"""
    typer.echo("审阅模式状态（待实现）")
