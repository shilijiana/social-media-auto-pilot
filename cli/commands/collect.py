"""素材采集 CLI 命令。"""

import typer

app = typer.Typer(name="collect", help="素材采集")


@app.command("run")
def run_collection(
    topic_id: int = typer.Argument(..., help="选题 ID"),
    keywords: str = typer.Option("", "--keywords", "-k", help="关键词，逗号分隔"),
):
    """执行素材采集流程。"""
    typer.echo(f"开始素材采集: 选题 #{topic_id}, 关键词: {keywords}")


@app.command("status")
def collection_status(
    topic_id: int = typer.Argument(..., help="选题 ID"),
):
    """查看采集状态。"""
    typer.echo(f"采集状态: 选题 #{topic_id}")
