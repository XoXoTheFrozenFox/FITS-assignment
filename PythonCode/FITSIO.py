from flask import Flask, request, jsonify
import os
import fitsio
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'C:/CODE/Code/CODE ON GITHUB/laTeX-Database-documents/Assignments/SemesterAssignmentFITS/PythonCode/FITSDATA/'
UPLOAD_FILENAME = 'FITS.fits'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/fits/open', methods=['POST'])
def open_fits_file():
    file = request.files.get('file')
    if file and file.filename.endswith('.fits'):
        try:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], UPLOAD_FILENAME))
            header_info = {}
            with fitsio.FITS(os.path.join(app.config['UPLOAD_FOLDER'], UPLOAD_FILENAME)) as fits:
                header = fits[0].read_header()
                header_info = {
                    'SIMPLE': header.get('SIMPLE', ''),
                    'NAXIS': header.get('NAXIS', ''),
                    'OBJECT': header.get('OBJECT', ''),
                }
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        return jsonify({'header': header_info}), 200
    else:
        return jsonify({'error': 'No FITS file uploaded or file upload failed'}), 400

def parse_input_data(input_string):
    try:
        data = [float(value.strip()) for value in input_string.split(',') if value.strip()]
        return data
    except ValueError:
        raise ValueError("Invalid input format. Please provide comma-separated numeric values.")

@app.route('/fits/write', methods=['POST'])
def write_fits_file():
    data = request.json.get('data')
    if data:
        try:
            fits_data = parse_input_data(data)
            fitsio.write(os.path.join(app.config['UPLOAD_FOLDER'], UPLOAD_FILENAME), fits_data, clobber=True)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        return jsonify({'message': 'FITS file successfully written'}), 200
    else:
        return jsonify({'error': 'No data provided to write FITS file'}), 400

def append_to_fits_file(existing_data, new_data):
    try:
        existing_data.extend(parse_input_data(new_data))
        return existing_data
    except ValueError as e:
        raise ValueError("Invalid input format. Please provide comma-separated numeric values.") from e

@app.route('/fits/append', methods=['POST'])
def append_fits_file():
    data = request.json.get('data')
    if data:
        try:
            existing_fits_data = []
            if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], UPLOAD_FILENAME)):
                existing_fits_data = fitsio.read(os.path.join(app.config['UPLOAD_FOLDER'], UPLOAD_FILENAME)).tolist()
            combined_data = append_to_fits_file(existing_fits_data, data)
            fitsio.write(os.path.join(app.config['UPLOAD_FOLDER'], UPLOAD_FILENAME), combined_data, clobber=True)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        return jsonify({'message': 'Data successfully appended to FITS file'}), 200
    else:
        return jsonify({'error': 'No data provided to append to FITS file'}), 400

@app.route('/fits/read', methods=['GET'])
def read_fits_file():
    try:
        data = fitsio.read(os.path.join(app.config['UPLOAD_FOLDER'], UPLOAD_FILENAME)).tolist()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({'data': data}), 200

@app.route('/fits/rename/<string:new_filename>', methods=['PUT'])
def rename_fits_file(new_filename):
    global UPLOAD_FILENAME
    try:
        if not new_filename.endswith('.fits'):
            new_filename += '.fits'
        old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], UPLOAD_FILENAME)
        new_file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        if os.path.exists(old_file_path):
            os.rename(old_file_path, new_file_path)
            UPLOAD_FILENAME = new_filename
            return jsonify({'message': 'FITS file successfully renamed'}), 200
        else:
            return jsonify({'error': 'FITS file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/fits/delete', methods=['DELETE'])
def delete_fits_file():
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], UPLOAD_FILENAME)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'message': 'FITS file successfully deleted'}), 200
        else:
            return jsonify({'error': 'FITS file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)