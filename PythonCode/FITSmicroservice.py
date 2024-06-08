from flask import Flask, request, jsonify
from astropy.io import fits
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration for the upload folder
UPLOAD_FOLDER = 'C:/CODE/Code/CODE ON GITHUB/laTeX-Database-documents/Assignments/SemesterAssignmentFITS/PythonCode/FITSDATA/'
UPLOAD_FILENAME = 'FITS.fits'  # Specify the filename for the uploaded FITS file
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/fits/open', methods=['POST'])
def open_fits_file():
    """
    Endpoint to open a FITS file and return its header information.
    """
    print(f"Received {request.method} request to /fits/open")
    file = request.files.get('file')

    # Save the uploaded file to the upload folder
    if file and file.filename.endswith('.fits'):
        try:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], UPLOAD_FILENAME))
            with fits.open(os.path.join(app.config['UPLOAD_FOLDER'], UPLOAD_FILENAME)) as hdul:
                header = hdul[0].header
                # Extract some common header information
                header_info = {
                'SIMPLE': header.get('SIMPLE', ''),
                'NAXIS': header.get('NAXIS', ''),
                'OBJECT': header.get('OBJECT', ''),
                'TELESCOP': header.get('TELESCOP', ''),
                'INSTRUME': header.get('INSTRUME', ''),
                'DATE-OBS': header.get('DATE-OBS', ''),
                'EXPTIME': header.get('EXPTIME', ''),
                'FILTER': header.get('FILTER', ''),
                'BSCALE': header.get('BSCALE', ''),
                'BZERO': header.get('BZERO', ''),
                'BUNIT': header.get('BUNIT', ''),
                'CTYPE1': header.get('CTYPE1', ''),
                'CTYPE2': header.get('CTYPE2', ''),
                'CRVAL1': header.get('CRVAL1', ''),
                'CRVAL2': header.get('CRVAL2', ''),
                'CRPIX1': header.get('CRPIX1', ''),
                'CRPIX2': header.get('CRPIX2', ''),
                    # Add more header keywords as needed
                }
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        return jsonify({'header': header_info}), 200
    else:
        return jsonify({'error': 'No FITS file uploaded or file upload failed'}), 400

def parse_input_data(input_string):
    """
    Parse the input string containing comma-separated values and convert them to floats.
    """
    try:
        data = [float(value.strip()) for value in input_string.split(',') if value.strip()]
        return data
    except ValueError:
        raise ValueError("Invalid input format. Please provide comma-separated numeric values.")

@app.route('/fits/write', methods=['POST'])
def write_fits_file():
    """
    Endpoint to write a FITS file with provided data.
    """
    print(f"Received {request.method} request to /fits/write")
    data = request.json.get('data')  # Use request.json to get JSON data

    if data:
        try:
            fits_data = parse_input_data(data)
            # Assuming UPLOAD_FILENAME is defined elsewhere
            # You might also want to handle file paths securely
            # Ensure the UPLOAD_FOLDER exists
            hdul = fits.HDUList([fits.PrimaryHDU(fits_data)])
            hdul.writeto(os.path.join(app.config['UPLOAD_FOLDER'], UPLOAD_FILENAME), overwrite=True)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        return jsonify({'message': 'FITS file successfully written'}), 200
    else:
        return jsonify({'error': 'No data provided to write FITS file'}), 400

def append_to_fits_file(existing_data, new_data):
    """
    Append new data to existing FITS data.
    """
    try:
        existing_data.extend(parse_input_data(new_data))
        return existing_data
    except ValueError as e:
        raise ValueError("Invalid input format. Please provide comma-separated numeric values.") from e

@app.route('/fits/append', methods=['POST'])
def append_fits_file():
    """
    Endpoint to append data to an existing FITS file.
    """
    print(f"Received {request.method} request to /fits/append")
    data = request.json.get('data')

    if data:
        try:
            # Load existing FITS data (if any)
            existing_fits_data = []
            if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], UPLOAD_FILENAME)):
                with fits.open(os.path.join(app.config['UPLOAD_FOLDER'], UPLOAD_FILENAME)) as hdul:
                    existing_fits_data = hdul[0].data.tolist() if hdul else []

            combined_data = append_to_fits_file(existing_fits_data, data)

            # Write combined data to the FITS file
            hdul = fits.HDUList([fits.PrimaryHDU(combined_data)])
            hdul.writeto(os.path.join(app.config['UPLOAD_FOLDER'], UPLOAD_FILENAME), overwrite=True)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        return jsonify({'message': 'Data successfully appended to FITS file'}), 200
    else:
        return jsonify({'error': 'No data provided to append to FITS file'}), 400

@app.route('/fits/read', methods=['GET'])
def read_fits_file():
    """
    Endpoint to read the contents of a FITS file and return it.
    """
    print(f"Received {request.method} request to /fits/read")
    try:
        with fits.open(os.path.join(app.config['UPLOAD_FOLDER'], UPLOAD_FILENAME)) as hdul:
            data = hdul[0].data
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'data': data.tolist()}), 200  # Return data as a list

@app.route('/fits/rename/<string:new_filename>', methods=['PUT'])
def rename_fits_file(new_filename):
    """
    Endpoint to rename the existing FITS file on the server.
    """
    global UPLOAD_FILENAME  # Declare UPLOAD_FILENAME as global

    print(f"Received {request.method} request to /fits/rename")
    try:
        # Ensure new filename ends with '.fits'
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
    """
    Endpoint to delete the existing FITS file from the server.
    """
    print(f"Received {request.method} request to /fits/delete")
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