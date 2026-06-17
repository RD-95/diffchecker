from flask import Flask, render_template, request, jsonify
import difflib

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/compare", methods=["POST"])
def compare():
    data = request.get_json()
    text1 = data.get("text1", "")
    text2 = data.get("text2", "")

    lines1 = text1.splitlines(keepends=True)
    lines2 = text2.splitlines(keepends=True)

    d = difflib.HtmlDiff(wrapcolumn=80)
    table = d.make_table(
        lines1,
        lines2,
        fromdesc="Text 1 (Original)",
        todesc="Text 2 (Modified)",
        context=True,
        numlines=3,
    )
    return jsonify({"diff": table})


if __name__ == "__main__":
    app.run(debug=True)
