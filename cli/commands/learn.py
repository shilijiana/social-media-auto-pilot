"""自学习管理 CLI 命令。"""

import typer

app = typer.Typer(name="learn", help="自学习管理")


@app.command("status")
def learning_status():
    """查看学习状态。"""
    typer.echo("自学习状态（待实现）")


@app.command("rules")
def list_rules(
    rule_type: str = typer.Option("", "--type", "-t", help="规则类型"),
):
    """列出偏好规则。"""
    typer.echo(f"偏好规则列表 (类型: {rule_type})")


@app.command("report")
def learning_report():
    """生成自学习报告。"""
    typer.echo("自学习报告（待实现）")


@app.command("import")
def import_preferences(
    template: str = typer.Argument(..., help="偏好模板文件路径"),
):
    """导入初始偏好模板。"""
    typer.echo(f"导入偏好模板: {template}")
