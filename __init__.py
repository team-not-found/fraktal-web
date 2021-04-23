from flask import Flask, redirect, url_for, render_template, request
import fraktal_py as fp
from pylab import *

app = Flask(__name__)

# Render home page from external html file.
@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():
	if request.method == "POST":
		# Get the type, stepsize and resolution of fractal from form by 'name' attribute 
		fractal_type = request.form["type"]
		fractal_stepsize = request.form["stepsize"]
		fractal_resolution = request.form["resolution"]
		if fractal_type == "fern":
			fractal = fp.Fern()
			fractal.generateFractal(int(fractal_resolution.split("_")[0]), int(fractal_resolution.split("_")[1]), int(fractal_stepsize))
			mat = log(asarray(fractal.density_map) + 1.0)
			matshow(mat)
			savefig("static/"+fractal_type+".png", dpi=300)
		return redirect(url_for("fractal", fractal_type=fractal_type))
	else:
		return render_template("index.html")

# Add another page.
@app.route("/<fractal_type>")
def fractal(fractal_type):
	# Pass arguments to page 
	return render_template("fractal.html", fractal_type=fractal_type)

# Run the server.
if __name__ == "__main__":
	# add debug and doesn't need to rerun after every change
    app.run(debug=True)
    print(akarmi)