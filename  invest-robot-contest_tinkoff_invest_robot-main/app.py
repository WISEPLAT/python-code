from flask import Flask, jsonify, render_template
from flask import request
from loguru import logger

from settings import settings

from src.algotrading import get_account, glossary
from src.algotrading import get_shares
from src.algotrading import _sandbox_accounts
from src.strategy.macd import macd_test, macd_sandbox_run

app = Flask(__name__)


@app.before_request
def before_first_request():
    try:
        get_account.test_connect()

    except Exception as err:
        if "unauthenticated" in err.code.value:
            err = """Проверте правильность ввода API токена<br>
                И перезапустите сервер"""

        logger.error(f"{err}")
        return render_template("error.html", error=err)


@app.route("/", methods=['GET'])
def show_index():
    user_info = get_account.main()

    return render_template("index.html", user_info=user_info)


@app.route("/instruments", methods=['GET'])
def show_instruments():
    shares = get_shares.main()

    return render_template("instruments.html", thead=glossary.thead, shares=shares)


############################# sandbox ##################################
@app.route("/sandbox", methods=['GET'])
def show_sandbox():
    sandbox_accounts = _sandbox_accounts.get()

    return render_template("sandbox.html", sandbox_accounts=sandbox_accounts)


@app.route("/sandbox/<uuid>", methods=['DELETE'])
def delete_sandbox_account(uuid):
    logger.info(f"Получен запрос на удаление account_id={uuid}")
    _sandbox_accounts.delete(uuid)

    return "ok", 201


@app.route("/sandbox/", methods=['POST'])
def open_sandbox_account():
    _sandbox_accounts.open()

    return "ok", 201


@app.route("/sandbox/payin", methods=['POST'])
def sandbox_payin():
    data = request.get_json()

    try:
        sandbox_id = data['sandbox_id']
        ammount = int(data['ammount'])
        cur = data['cur']

    except KeyError as err:
        logger.warning(f"sandbox_payin: {data=}, {err=}")
        return f'{{"error": "Необходимо передать {str(err)}"}}', 422

    except ValueError as err:
        logger.warning(f"sandbox_payin: {data=}, {err=}")
        return f'{{"error": "параметр ammount принимиет только целые положительные числа"}}', 422

    _sandbox_accounts.payin(sandbox_id, ammount, cur)

    return "ok", 200


############################# stratgy ##################################
@app.route("/stratgy", methods=['GET'])
def show_stratgy():
    sandbox_accounts = _sandbox_accounts.get()
    return render_template("stratgy.html", sandbox_accounts=sandbox_accounts,
                                           timeframe=glossary.timeframe)


@app.route("/stratgy/test", methods=['POST'])
def post_stratgy_test():
    data = request.get_json()
    data['window_slow'] = int(data['window_slow'])
    data['window_fast'] = int(data['window_fast'])
    data['window_sign'] = int(data['window_sign'])
    data['timeframe'] = int(data['timeframe'])

    result = macd_test(data)

    return result


@app.route("/stratgy/sandbox", methods=['POST'])
def post_stratgy_sandbox():
    data = request.get_json()
    data['window_slow'] = int(data['window_slow'])
    data['window_fast'] = int(data['window_fast'])
    data['window_sign'] = int(data['window_sign'])
    data['timeframe'] = int(data['timeframe'])

    result = macd_sandbox_run(data)

    return result


############################# info ##################################
@app.route("/info", methods=['GET'])
def show_info():
    return render_template("info.html")


@app.route("/test", methods=['GET'])
def show_test():
    return render_template("test.html")


if __name__ == '__main__':
    app.run(host=settings.flask_run_host, port=settings.flask_run_port, debug=True)
