from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():

    so1 = 5
    so2 = 10
    phepTinh = "-"

    return render_template("math.html", so1=so1, so2=so2, phepTinh=phepTinh)

if __name__ == "__main__":
    app.run(debug=True)