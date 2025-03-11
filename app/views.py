import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from app.models import UserProfile
from app.forms import LoginForm, UploadForm

###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')

@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")

@app.route('/upload', methods=['POST', 'GET'])
@login_required  # Ensure only logged-in users can access this route
def upload():
    form = UploadForm()  # Instantiate the UploadForm

    if form.validate_on_submit():  # Validate the form on submission
        file = form.file.data  # Get the file data from the form
        filename = secure_filename(file.filename)  # Secure the filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Save the file to the upload folder
        flash('File uploaded successfully!', 'success')
        return redirect(url_for('files'))  # Redirect to the route that displays uploaded files

    return render_template('upload.html', form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    if form.validate_on_submit():  # Validate the entire form submission
        username = form.username.data
        password = form.password.data

        # Query the database for the user
        user = UserProfile.query.filter_by(username=username).first()

        # Check if the user exists and the password is correct
        if user and check_password_hash(user.password, password):
            login_user(user)  # Log in the user
            flash('Logged in successfully!', 'success')
            return redirect(url_for('upload'))  # Redirect to the upload page after login
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()  # Log out the user
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))  # Redirect to the home page after logout

@app.route('/files')
@login_required
def files():
    # Get the list of uploaded images
    images = get_uploaded_images()
    return render_template('files.html', images=images)

@app.route('/uploads/<filename>')
@login_required
def get_image(filename):
    # Serve the uploaded image
    return send_from_directory(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']), filename)

# Helper function to get uploaded images
def get_uploaded_images():
    upload_folder = app.config['UPLOAD_FOLDER']
    return [f for f in os.listdir(upload_folder) if os.path.isfile(os.path.join(upload_folder, f))]

# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404