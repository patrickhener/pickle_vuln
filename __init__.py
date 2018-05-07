## Vulnerable Flask App
import couchdb
import string
import random
import base64
import cPickle
from flask import Flask, render_template, request
from hashlib import md5

app = Flask(__name__)
app.config.update(
	DATABASE = "syss"
)
db = couchdb.Server("http://localhost:5984/")[app.config["DATABASE"]]

@app.errorhandler(404)
def page_not_found(e):
    if random.randrange(0, 2) > 0:
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(random.randrange(50, 250)))
    else:
	return render_template("index.html")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/comments")
def comments():
    comments = []
    for id in db:
        comments.append({"title": db[id]["name"], "text": db[id]["comment"]})
    return render_template('comments.html', entries=comments)

@app.route("/submit", methods=["GET", "POST"])
def submit():
    error = None
    success = None

    if request.method == "POST":
        try:
            name = request.form["name"]
            komm = request.form["komm"]
            if not name or not komm:
                error = True
            else:
                # TODO - Pickle ins Verzeichnis, `check` ist fertig implementiert; Irgendein Cronjob muss die pickle dann noch in die DB schreiben?!
                p_id = md5(name + komm).hexdigest()
                outfile = open("/pickle/" + p_id + ".p", "wb")
                outfile.write(name + "\n" + komm)
                outfile.close()
                success = True

        except Exception as ex:
            error = True

    return render_template("submit.html", error=error, success=success)

@app.route("/check", methods=["GET", "POST"])
def check():
    comment = None
    pickle = None
    error = None

    if request.method == "POST":
        try:
            path = "/pickle/" + request.form["id"] + ".p"
            data = open(path, "rb").read()
    
            if "p1" in data:
                item = cPickle.loads(data)
                pickle = True
            else:
                item = data
                comment = True

        except Exception as ex:
            error = True

    return render_template("check.html", error=error, pickle=pickle, comment=comment)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='8080')
