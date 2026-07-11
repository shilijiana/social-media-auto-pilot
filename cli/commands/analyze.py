"""数据分析 CLI 命令。"""

import typer

app = typer.Typer(name="analyze", help="数据分析")


@app.command("run")
def run_analysis(
    publication_id: int = typer.Argument(..., help="发布记录 ID"),
):
    """执行数据分析。"""
    typer.echo(f"分析数据: 发布 #{publication_id}")


@app.command("report")
def show_report(
    topic_id: int = typer.Argument(..., help="选题 ID"),
):
    """查看分析报告。"""
    typer.echo(f"分析报告: 选题 #{topic_id}")
