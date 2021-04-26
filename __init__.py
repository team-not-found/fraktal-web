from flask import Flask, redirect, url_for, render_template, request, Markup
import io, base64
import fraktal_py as fp
import matplotlib.pyplot as plt
import numpy as np

# generate encoded matplotlib image from fractal parameters
def generateEncodedFractalImage(fractal_type, fractal_stepsize, fractal_resolution):
	if fractal_type == "fern":
		fractal = fp.Fern()
		fractal.generateFractal(int(fractal_resolution.split("_")[0]), int(fractal_resolution.split("_")[1]), int(fractal_stepsize))
		# Preprocessing (?)
		mat = np.log(np.asarray(fractal.density_map) + 1.0)

		# Plotting
		fig, ax = plt.subplots(figsize=(15, 8))
		plt.matshow(mat)
		
		# Encoding
		img = io.BytesIO()
		plt.savefig(img, format="png")
		img.seek(0)
		plot_url = base64.b64encode(img.getvalue()).decode()
		
		# Close the image to delete from memory
		plt.close()
	else:
		plot_url = ""
	return plot_url

app = Flask(__name__)

plot_fractal = ""

@app.route("/update_fractal", methods=["POST"])
def updateFractal():
	# Generate encoded fractal data and html image
	fractal_type = "fern"
	fractal_stepsize = 100000
	fractal_resolution = "1920_1080"
	plot_url = generateEncodedFractalImage(fractal_type, fractal_stepsize, fractal_resolution)
	plot_fractal = Markup('<img src="data:image/png;base64, {}">'.format(plot_url))

# Render home page from external html file.
@app.route("/")
@app.route("/home")
def home():
	return render_template("index.html", plot_fractal = plot_fractal)

# Run the server.
if __name__ == "__main__":
	# add debug and doesn't need to rerun after every change
    app.run(debug=True)