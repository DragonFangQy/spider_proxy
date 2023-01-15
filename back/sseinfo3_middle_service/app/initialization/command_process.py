import os

import click
from flask.cli import with_appcontext

from configs.sysconf import PROJECT_PATH
from . import app


@app.cli.command("init", help="init a project")
@click.pass_context
def init(ctx):
    """
    创建一个Flask项目~
    """
    if ".git" in os.listdir(PROJECT_PATH):
        click.echo("看上去你的项目已经初始化过了, 删除.git文件继续")
        return

    project_name = click.prompt('即将创建一个APP, 请输入名字(默认使用文件夹名称)', default="")
    if not project_name:
        project_name = PROJECT_PATH.split("/")[-1].lower()

    with open(os.path.join(PROJECT_PATH, "app/configs/base.py"), "w") as f:
        f.write(f"PROJECT_NAME ='{project_name}'")

    ctx.forward(gen_secret_key)

    # init git
    os.system(f"git init {PROJECT_PATH}")


# @app.cli.command('create_user', help="create a user")
@click.option('--username', '-u', help="username")
@click.password_option()
@click.option("--is_admin", help="is admin: True of False, default false ", type=bool, default=False)
def hello_command(username, password, is_admin):
    from blueprints.users.user_models import UserModel
    from .sqlalchemy_process import safe_commit

    user = UserModel
    with safe_commit():
        user.create(username=username, password=password, is_superuser=is_admin)
    click.echo(f'user {username} created')


@app.cli.command("gen_secret_key", help="gen a secret key for flask in base.py")
@click.option('--force', '-f', type=bool, default=False)
def gen_secret_key(force):
    with open(os.path.join(PROJECT_PATH, "app/configs/base.py"), "r+") as f:
        content = f.read()
        if "SECRET_KEY" in content:
            if not force:
                click.echo("SECRET_KEY is set, skipping...")
                return

        f.write(f"\nSECRET_KEY = {os.urandom(24)}\n")


@app.cli.command("app_name", help="print a app name so that you know it's name")
def print_app_name():
    click.echo(f"{app.name}")


@app.cli.command("create_db", help="create a database if not exists")
@click.option("--drop", help="是否需要删除当前数据库", type=bool, default=False)
def create_db(drop: bool):
    from pymysql import connect

    from configs.sysconf import (MYSQL_CHARSET, MYSQL_DATABASE, MYSQL_HOST, MYSQL_PASSWD, MYSQL_PORT,
                                            MYSQL_USER)
    with connect(user=MYSQL_USER, password=MYSQL_PASSWD, host=MYSQL_HOST, port=MYSQL_PORT,
                 charset=MYSQL_CHARSET) as conn:
        with conn.cursor() as cr:
            conn.begin()
            if drop:
                res = click.prompt(f"正在删除数据库{MYSQL_DATABASE}是否继续..., y确定", confirmation_prompt=True)
                if res.lower() != "y":
                    click.echo("ABORT!")
                    return
                click.echo(f"DROPPING DATABASE {MYSQL_DATABASE}")
                cr.execute(f"DROP DATABASE {MYSQL_DATABASE}")
                click.echo(f"{MYSQL_DATABASE} DROPPED")

            click.echo("CREATING DATABASE")
            cr.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE} CHAR SET {MYSQL_CHARSET}")
            conn.commit()
            click.echo("DATABASE CREATED!")


@app.cli.command("create_all", help="create tables if not exists")
@with_appcontext
def create_all():
    import entities
    from initialization.sqlalchemy_process import db
    db.create_all()


@app.cli.command("drop_all", help="drop all tables, very! dangerous!")
@with_appcontext
def drop_all():
    res = click.prompt("drop table is very dangerous continue?.. y to continue", confirmation_prompt=True)
    if res.upper() != "Y":
        click.echo("abort!")
        return
    from initialization.sqlalchemy_process import db
    click.echo("by you command!")
    db.drop_all()
    return
