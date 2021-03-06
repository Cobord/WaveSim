import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import wav_to_hash_flask
import save_elastic_search2

UPLOAD_FOLDER='./uploads/'
ALLOWED_EXTENSIONS=set(['wav'])
FUTURE_EXTENSIONS=set(['3gp','aa','wma','mp3','mp4','flac','aiff','au','ape','wv','m4a'])

app = Flask(__name__)
app.secret_key='92840184'

def allowed_file(filename):
	dotin=('.' in filename)
	if (not dotin):
		flash('Filename please')
		return False
	extension=filename.rsplit('.', 1)[1].lower()
	if extension in ALLOWED_EXTENSIONS:
		return True
	elif extension in FUTURE_EXTENSIONS:
		flash('Not yet supported')
		return False
	flash('Sound File please')
	return False

@app.route('/', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		# check if the post request has the file part
		if 'file' not in request.files:
			return redirect(url_for('exampleFile'))
		file = request.files['file']
		# if user does not select file, browser also
		# submit an empty part without filename
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			extension=filename.rsplit('.', 1)[1].lower()
			save_loc=os.path.join(UPLOAD_FOLDER, 'temp.'+extension)
			file.save(save_loc)
			return redirect(url_for('uploadedFile',filename=filename))
		return redirect(request.url)
	return '''
	<!doctype html>
	<title>WaveSim</title>
	<h1 style="color:blue;font-size:300%;" class="centered logo-format">WaveSim</h1>
	<h1>Upload in wav format only</h1>
	<h1>If you just click upload without a file, will use the preset example</h1>
	<form method=post enctype=multipart/form-data>
	<input type=file name=file>
	<input type=submit value=Upload>
	</form>
	'''

@app.route('/uploadedFile/<filename>')
def uploadedFile(filename):
	#extension=filename.rsplit('.',1)[1].lower()
	extension='wav'
	save_loc=os.path.join(UPLOAD_FOLDER,'temp.'+extension)
	(my_hashes,my_spec)=wav_to_hash_flask.lsh_and_spectra_of_unknown(save_loc,'all_hp.npy')
	potentials=save_elastic_search2.get_any_matches(my_hashes[0],my_hashes[1],my_hashes[2],my_hashes[3],my_hashes[4])
	#potentials=save_elastic_search2.get_any_matches2(my_hashes)
	scored_cands=wav_to_hash_flask.score_false_positives(potentials,my_spec)
	scored_cands=scored_cands[:10]
	return render_template("wavesim.html",scored_matches=scored_cands,found_match=(len(scored_cands)>0),your_wav=os.path.abspath(save_loc) )

@app.route('/exampleFile')
def exampleFile():
        extension='wav'
        save_loc=os.path.join(UPLOAD_FOLDER,'example.'+extension)
        (my_hashes,my_spec)=wav_to_hash_flask.lsh_and_spectra_of_unknown(save_loc,'all_hp.npy')
        potentials=save_elastic_search2.get_any_matches(my_hashes[0],my_hashes[1],my_hashes[2],my_hashes[3],my_hashes[4])
        #potentials=save_elastic_search2.get_any_matches2(my_hashes)
        scored_cands=wav_to_hash_flask.score_false_positives(potentials,my_spec)
        scored_cands=scored_cands[:10]
        return render_template("wavesim.html",scored_matches=scored_cands,found_match=(len(scored_cands)>0),your_wav=os.path.abspath(save_loc) )
