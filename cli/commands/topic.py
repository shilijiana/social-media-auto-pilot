"""选题计划管理 CLI 命令。"""

import typer

app = typer.Typer(name="topic", help="选题计划管理")


@app.command("list")
def list_topics():
    """列出所有选题计划。"""
    typer.echo("选题计划列表（待实现）")


@app.command("create")
def create_topic(
    title: str = typer.Argument(..., help="选题标题"),
    platforms: str = typer.Option("", "--platforms", "-p", help="目标平台，逗号分隔"),
):
    """创建新的选题计划。"""
    typer.echo(f"创建选题: {title} (平台: {platforms})")


@app.command("approve")
def approve_topic(
    topic_id: int = typer.Argument(..., help="选题 ID"),
):
    """审批通过选题计划。"""
    typer.echo(f"审批选题 #{topic_id}")
