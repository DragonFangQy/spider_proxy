from . import app

app.config['PROPAGATE_EXCEPTIONS'] = True  # 抛出捕获的异常
app.config['JSON_AS_ASCII'] = False
