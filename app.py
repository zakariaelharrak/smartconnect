from flask import Flask, render_template, request, redirect, abort, send_from_directory, url_for

import os
from werkzeug.utils import secure_filename

app = Flask(__name__)


# Directory to store generated HTML files
HTML_DIR = os.path.join(os.getcwd(), 'html_files')

# Directory to store contact files
CONTACTS_DIR = os.path.join(os.getcwd(), 'contacts')

# Directory to store uploaded images
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')


# Directory to store uploaded banner images
UPLOAD_FOLDER_BANNERS = os.path.join(os.getcwd(), 'banners')


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(HTML_DIR):
    os.makedirs(HTML_DIR)

if not os.path.exists(CONTACTS_DIR):
    os.makedirs(CONTACTS_DIR)

if not os.path.exists(UPLOAD_FOLDER_BANNERS):
    os.makedirs(UPLOAD_FOLDER_BANNERS)

# Allowed extensions for image upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# Index route
@app.route('/')
def index():
    return render_template('index.html')

# Generate route
@app.route('/generate', methods=['POST'])
def generate():
    project_name = request.form['project_name']
    project_description = request.form['project_description']
    role = request.form['role']
    background_color = request.form['background_color']
    
    # Check if an image file was uploaded
    if 'image' not in request.files:
        return redirect(request.url)

    image = request.files['image']

    # If the user does not select a file, the browser submits an empty file without a filename
    if image.filename == '':
        return redirect(request.url)

    # Check if the file is allowed
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(image_path)
    else:
        return abort(400, 'Invalid file format')

    # Check if a banner image file was uploaded
    if 'banner' in request.files:
        banner = request.files['banner']

        if banner and allowed_file(banner.filename):
            banner_filename = secure_filename(banner.filename)
            banner_path = os.path.join(UPLOAD_FOLDER_BANNERS, banner_filename)
            banner.save(banner_path)
        else:
            return abort(400, 'Invalid banner image format')
        
   
    

    link_pairs = [(request.form.get(f'name{i}'), request.form.get(f'url{i}'), request.form.get(f'icon{i}')) for i in range(1, 6) if request.form.get(f'name{i}') and request.form.get(f'url{i}')]

    map_url = request.form.get('map_url')
    # Pass project name, image path, banner path, link pairs, and background color to the page.html template
    rendered_template = render_template('page.html', 
                                         page_name=project_name, 
                                         project_description=project_description, 
                                         role=role, 
                                         image_path=os.path.basename(image_path),
                                         banner_path=os.path.basename(banner_path),
                                         links=link_pairs, 
                                         map_url=map_url,
                                         background_color=background_color
                                         )
  

    # Save the rendered template to an HTML file
    html_filename = os.path.join(HTML_DIR, f"{project_name}.html")
    with open(html_filename, 'w') as html_file:
        html_file.write(rendered_template)

    return redirect(url_for('show_page', page_name=project_name))





# Contacts route
@app.route('/contacts', methods=['POST'])
def upload_contact():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(CONTACTS_DIR, filename)
        file.save(file_path)
        return 'File uploaded successfully'
    else:
        return abort(400, 'Invalid file format')

# Show page route
@app.route('/pages/<string:page_name>')
def show_page(page_name):
    # Check if the HTML file exists
    filename = os.path.join(HTML_DIR, f"{page_name}.html")
    if os.path.exists(filename):
        return send_from_directory(HTML_DIR, f"{page_name}.html")
    else:
        abort(404)

# Uploaded image route
@app.route('/uploads/<path:filename>')
def get_uploaded_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Banner route
@app.route('/banners/<path:filename>')
def get_banner(filename):
    return send_from_directory(UPLOAD_FOLDER_BANNERS, filename)



# Contract generator route
@app.route('/contractgenerator')
def contract_generator():
    return render_template('contractgenerator.html', banners=os.listdir(UPLOAD_FOLDER_BANNERS))


if __name__ == '__main__':
    app.run(debug=True)
