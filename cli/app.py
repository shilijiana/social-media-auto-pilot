"""AutoSoc CLI 主入口 — 基于 typer。"""

import typer

from autosoc import __version__


def _version_callback(version: bool):
    if version:
        print(f"AutoSoc v{__version__}")
        raise typer.Exit(code=0)


app = typer.Typer(
    name="autosoc",
    help="AutoSoc — 社交媒体自动化运营系统",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# 注册子命令组
from autosoc.cli.commands import topic, collect, produce, review, publish, analyze, learn, workflow  # noqa: E402, F401

app.add_typer(topic.app, name="topic", help="选题计划管理")
app.add_typer(collect.app, name="collect", help="素材采集")
app.add_typer(produce.app, name="produce", help="内容生产")
app.add_typer(review.app, name="review", help="审阅管理")
app.add_typer(publish.app, name="publish", help="多平台发布")
app.add_typer(analyze.app, name="analyze", help="数据分析")
app.add_typer(learn.app, name="learn", help="自学习管理")
app.add_typer(workflow.app, name="workflow", help="工作流管理")


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="显示版本信息",
        is_eager=True,
        callback=_version_callback,
    ),
):
    """AutoSoc — 社交媒体自动化运营系统"""
    pass


def entry():
    """应用入口点。"""
    from autosoc.core.logging import setup_logging
    setup_logging()
    app()
