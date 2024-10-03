import logging, os

from textwrap import dedent

from flask import Flask, Response

try:
    from dotenv import load_dotenv
    load_dotenv()
    _ = os.environ.get("OAI_API_KEY")
except Exception as e:
    logging.exception(f"Failed in loading environment variables!", exc_info=e)
    exit(1)

from models import Chat, Client

app = Flask(__name__)

@app.route('/')
def homepage():
    return dedent("""
    The server is running!
    These are the endpoints available:
    {endpoints}
    """.strip())

@app.route('/assets/<path:asset>')
def fetch_resource(asset):
    path = f"assets/{asset}"
    print(path)
    with open(path, 'rb') as f:
        content = f.read()

    extension = path.split('.')[-1]
    mimetype = {
        "js" : "text/javascript",
        "webp" : "image/webp",
        "svg" : "image/svg+xml"
    }.get(extension, None)

    return Response(content, mimetype=mimetype)


def main():
    Chat.create = app.route("/chat", methods=["POST"  ])(Chat.create)
    Chat.read   = app.route("/chat", methods=["GET"   ])(Chat.read)
    Chat.update = app.route("/chat", methods=["PUT"   ])(Chat.update)
    Chat.delete = app.route("/chat", methods=["DELETE"])(Chat.delete)

    Client.enumerate = app.route("/clients", methods=["GET"])(Client.enumerate)

    app.run(debug=True)

if __name__ == "__main__":
    main()
