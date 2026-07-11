"""工作流管理 CLI 命令。"""

import typer

app = typer.Typer(name="workflow", help="工作流管理")


@app.command("run")
def run_workflow(
    pipeline_id: str = typer.Argument("p0_full", help="管线 ID"),
    topic_id: int = typer.Option(0, "--topic-id", "-t", help="选题 ID"),
):
    """运行完整工作流。"""
    typer.echo(f"启动工作流: {pipeline_id} (选题 #{topic_id})")


@app.command("list")
def list_instances():
    """列出工作流实例。"""
    typer.echo("工作流实例列表（待实现）")


@app.command("status")
def instance_status(
    instance_id: int = typer.Argument(..., help="工作流实例 ID"),
):
    """查看工作流实例状态。"""
    typer.echo(f"工作流实例 #{instance_id} 状态（待实现）")


@app.command("pause")
def pause_instance(
    instance_id: int = typer.Argument(..., help="工作流实例 ID"),
):
    """暂停工作流。"""
    typer.echo(f"暂停工作流 #{instance_id}")


@app.command("resume")
def resume_instance(
    instance_id: int = typer.Argument(..., help="工作流实例 ID"),
):
    """恢复工作流。"""
    typer.echo(f"恢复工作流 #{instance_id}")


@app.command("cancel")
def cancel_instance(
    instance_id: int = typer.Argument(..., help="工作流实例 ID"),
):
    """取消工作流。"""
    typer.echo(f"取消工作流 #{instance_id}")
