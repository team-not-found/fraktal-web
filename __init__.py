from flask import Flask, redirect, url_for, render_template, request, Markup, jsonify
import io, base64
import fraktal_py as fp
from matplotlib.figure import Figure
import numpy as np

# generate encoded matplotlib image from fractal parameters
def generateEncodedFractalImage(fractal_type, fractal_stepsize, fractal_resolution):
	if fractal_type == "fern":
		fractal = fp.Fern()
		fractal.generateFractal(int(fractal_resolution.split("_")[0]), int(fractal_resolution.split("_")[1]), int(fractal_stepsize))
		# Preprocessing (?)
		mat = np.log(np.asarray(fractal.density_map) + 1.0)

		# Plotting
		fig = Figure()
		ax = fig.subplots()
		#ax.matshow(np.random.random((2000, 1000)))
		ax.matshow(mat)

		# Encoding
		buf = io.BytesIO()
		fig.savefig(buf, format="png")
		buf.seek(0)
		plot_url = base64.b64encode(buf.getbuffer()).decode("ascii")
	else:
		plot_url = ""
	return plot_url

app = Flask(__name__)

plot_fractal = ""

@app.route("/update_fractal", methods=["POST"])
def updateFractal():
	# Generate encoded fractal data and html image
	fractal_type = "fern"
	fractal_stepsize = "100000"
	fractal_resolution = "1920_1080"
	plot_url = generateEncodedFractalImage(fractal_type, fractal_stepsize, fractal_resolution)
	plot_fractal = Markup('<img src="data:image/png;base64, {}">'.format(plot_url))
	return jsonify("", render_template("image.html", plot_fractal = plot_fractal))

# Render home page from external html file.
@app.route("/")
def home():
	return render_template("index.html", plot_fractal = plot_fractal)

# Run the server.
if __name__ == "__main__":
	# add debug and doesn't need to rerun after every change
    app.run(debug=True)