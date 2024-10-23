from lib2to3.pytree import Base

from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/test'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

# Routes
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        id_type = int(request.form['id_type'])
        login = request.form['login']
        password = request.form['password']

        user = User.query.filter_by(id_type=id_type, login=login, password=password).first()

        if user:
            session['user_id'] = user.user_id  # Store user_id in session
            session['id_type'] = id_type  # Store id_type in session

            # Debug information
            print(f"Redirecting user_id: {user.user_id}, id_type: {id_type}")

            if id_type == 1:
                return redirect('/employee')
            elif id_type == 2:
                return redirect('/manager/dashboard')
            elif id_type == 3:
                return redirect('/bus_manager')
            elif id_type == 4:
                return redirect(f'/user/{user.user_id}')
        else:
            flash('Incorrect login details, please try again.')

    return render_template('index.html')


@app.route('/user/<int:user_id>')
def user_form(user_id):
    user = User.query.get(user_id)
    if user and user.id_type == 4:
        return render_template('user_form.html', user=user)
    flash('Access Denied.')
    return redirect('/')


@app.route('/employee', methods=['GET', 'POST'])
def employee_form():
    # Fetch all privileges to display
    privileges = Privilege.query.all()  # Fetch privileges before the request method check

    if request.method == 'POST':
        privilege_name = request.form['privilege_name']
        new_privilege = Privilege(privilege_name=privilege_name)
        db.session.add(new_privilege)
        db.session.commit()
        flash('Privilege request submitted.')

        # You may want to re-fetch privileges after adding a new one
        privileges = Privilege.query.all()  # Optionally re-fetch privileges after POST

    return render_template('employee_form.html', privileges=privileges)



@app.route('/manager/dashboard', methods=['GET', 'POST'])
def manager_dashboard():
    print(f"Session data at dashboard: {session}")

    if 'user_id' in session and session['id_type'] == 2:  # Check if the user is an IT Manager
        if request.method == 'POST':
            if 'register' in request.form:
                privilege_name = request.form['privilege_name']
                # Register a new privilege
                new_privilege = Privilege(privilege_name=privilege_name, status='Active')
                db.session.add(new_privilege)
                db.session.commit()
                flash('New privilege registered successfully.')

            elif 'update' in request.form:
                privilege_id = request.form['privilege_id']
                new_status = request.form['status']
                # Update privilege status
                privilege = Privilege.query.get(privilege_id)
                if privilege:
                    privilege.status = new_status
                    db.session.commit()
                    flash('Privilege status updated successfully.')

            elif 'delete' in request.form:
                privilege_id = request.form['privilege_id']
                # Delete privilege
                privilege = Privilege.query.get(privilege_id)
                if privilege:
                    db.session.delete(privilege)
                    db.session.commit()
                    flash('Privilege deleted successfully.')

            elif 'show' in request.form:
                privilege_id = request.form['privilege_id']
                # Get specific privilege details
                privilege = Privilege.query.get(privilege_id)
                return render_template('manager_dashboard.html', privilege=privilege)

        # Fetch all privileges and users
        privileges = Privilege.query.all()
        users = User.query.all()
        return render_template('manager_dashboard.html', privileges=privileges, users=users)

    return redirect(url_for('login'))


@app.route('/bus_manager', methods=['GET', 'POST'])
def bus_manager_form():
    # Handle form submissions
    if request.method == 'POST':
        if 'register' in request.form:  # Register new privilege
            privilege_name = request.form['privilege_name']
            new_privilege = Privilege(privilege_name=privilege_name)
            db.session.add(new_privilege)
            db.session.commit()
            flash('Privilege registered successfully.')

        elif 'update' in request.form:  # Update privilege status
            privilege_id = request.form['privilege_id']
            new_status = request.form['status']
            privilege = Privilege.query.get(privilege_id)
            if privilege:
                privilege.status = new_status  # Assuming status is a column in your Privilege model
                db.session.commit()
                flash('Privilege updated successfully.')
            else:
                flash('Privilege not found.')

        elif 'delete' in request.form:  # Delete privilege
            privilege_id = request.form['privilege_id']
            privilege = Privilege.query.get(privilege_id)
            if privilege:
                db.session.delete(privilege)
                db.session.commit()
                flash('Privilege deleted successfully.')
            else:
                flash('Privilege not found.')

        elif 'show' in request.form:  # Show specific privilege
            privilege_id = request.form['privilege_id']
            privilege = Privilege.query.get(privilege_id)
            if privilege:
                flash(
                    f'Privilege ID: {privilege.privilege_id}, Name: {privilege.privilege_name}, Status: {privilege.status}')
            else:
                flash('Privilege not found.')

    # Query all privileges to display on the dashboard
    privileges = Privilege.query.all()
    return render_template('bus_manager_form.html', privileges=privileges)


@app.route('/employee/request', methods=['GET', 'POST'])
def request_privilege():
    if 'user_id' in session and session['id_type'] == 1:  # Check if the user is an IT Employee
        if request.method == 'POST':
            privilege_name = request.form['privilege_name']
            requested_by = session['user_id']  # Get current user ID from session

            # Insert the requested privilege into the database using ORM
            new_privilege = Privilege(privilege_name=privilege_name, requested_by=requested_by)
            db.session.add(new_privilege)
            db.session.commit()

            flash('Privilege request submitted.')
            return redirect(url_for('request_privilege'))  # Redirect to the same page to show updated list

        # Fetch all privileges to display
        privileges = Privilege.query.all()
        return render_template('request_privilege.html', privileges=privileges)

    return redirect(url_for('login'))



@app.route('/manager/form', methods=['GET', 'POST'])
def manager_form():
    if request.method == 'POST':
        if 'register' in request.form:
            privilege_name = request.form['privilege_name']
            new_privilege = Privilege(privilege_name=privilege_name)
            db.session.add(new_privilege)
            db.session.commit()
            flash('Privilege registered successfully!')
        elif 'update' in request.form:
            privilege_id = request.form['privilege_id']
            new_status = request.form['status']
            privilege = Privilege.query.get(privilege_id)
            if privilege:
                privilege.status = new_status
                db.session.commit()
                flash('Privilege status updated successfully!')
            else:
                flash('Privilege not found.')
        elif 'delete' in request.form:
            privilege_id = request.form['privilege_id']
            privilege = Privilege.query.get(privilege_id)
            if privilege:
                db.session.delete(privilege)
                db.session.commit()
                flash('Privilege deleted successfully!')
            else:
                flash('Privilege not found.')
        elif 'show' in request.form:
            privilege_id = request.form['privilege_id']
            privilege = Privilege.query.get(privilege_id)
            return render_template('manager_form.html', privilege=privilege)

    privileges = Privilege.query.all()
    return render_template('manager_form.html', privileges=privileges)

@app.route('/manager/requests', methods=['GET', 'POST'])
def view_requests():
    if session['id_type'] == 2:  # Check if the user is an IT Manager
        if request.method == 'POST':
            privilege_id = request.form['privilege_id']
            action = request.form['action']  # 'accept' or 'decline'

            if action == 'accept':
                # Accept privilege request and assign it
                privilege = Privilege.query.get(privilege_id)
                if privilege:
                    privilege.approval_status = 'Accepted'
                    privilege.assigned_to = privilege.requested_by  # Assign to user who requested
                    db.session.commit()
                    flash('Privilege request accepted and assigned.')

            elif action == 'decline':
                # Decline privilege request
                privilege = Privilege.query.get(privilege_id)
                if privilege:
                    privilege.approval_status = 'Declined'
                    db.session.commit()
                    flash('Privilege request declined.')

        # Fetch pending requests
        pending_requests = Privilege.query.filter_by(approval_status='Pending').all()
        return render_template('manager_dashboard.html', requests=pending_requests)

    return redirect(url_for('login'))

@app.route('/manager/update_user_privilege', methods=['POST'])
def update_user_privilege():
    if 'user_id' in session and session['id_type'] == 2:  # Check if the user is an IT Manager
        user_id = request.form['user_id']
        privilege_id = request.form['privilege_id']

        # Update user privilege
        user = User.query.get(user_id)
        if user:
            user.privilege_id = privilege_id  # Update to the new privilege_id
            db.session.commit()
            flash('User privilege updated successfully.')

        return redirect(url_for('manager_dashboard'))

    return redirect(url_for('login'))

@app.route('/manager/approve', methods=['POST'])
def approve_privilege():
    if 'user_id' in session and session['id_type'] == 2:  # Check if the user is an IT Manager
        privilege_id = request.form['privilege_id']
        action = request.form['action']  # 'accept' or 'decline'

        # Get the privilege record
        privilege = Privilege.query.get(privilege_id)

        if action == 'accept':
            # Update the approval status and assign to the user
            privilege.approval_status = 'Accepted'
            privilege.assigned_to = privilege.requested_by  # Assign the privilege to the requester
        else:
            # If declined, just update the approval status
            privilege.approval_status = 'Declined'

        db.session.commit()  # Commit changes to the database
        flash(f'Privilege request has been {privilege.approval_status.lower()}.')
        return redirect(url_for('view_requests'))  # Redirect to view requests

    return redirect(url_for('login'))

@app.route('/manager/users', methods=['GET'])
def view_users():
    if 'user_id' in session and session['id_type'] == 2:  # Check if the user is an IT Manager
        users = User.query.all()  # Fetch all users
        return render_template('manager_users.html', users=users)
    return redirect(url_for('login'))



# Models
# Define the User model
# Define the User model
class User(db.Model):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    login = Column(String, unique=True, nullable=False)  # Adjusted to match your database
    password = Column(String, nullable=False)
    id_type = Column(Integer)  # Represents the user type
    privilege_id = Column(Integer, ForeignKey('privileges.privilege_id'))  # New privilege column
    requested_privileges = relationship('Privilege',
                                         foreign_keys='Privilege.requested_by',
                                         backref='requesting_user')
    assigned_privileges = relationship('Privilege',
                                        foreign_keys='Privilege.assigned_to',
                                        backref='assigning_user')
    privilege = relationship('Privilege', foreign_keys=[privilege_id], backref='users')  # Specify foreign key

    def __repr__(self):
        return f"<User(user_id={self.user_id}, login={self.login}, id_type={self.id_type}, privilege_id={self.privilege_id})>"


# Define the Privilege model
class Privilege(db.Model):
    __tablename__ = 'privileges'

    privilege_id = Column(Integer, primary_key=True)
    privilege_name = Column(String, nullable=False)
    status = Column(String, default='In Progress')
    requested_by = Column(Integer, ForeignKey('users.user_id'))  # ForeignKey to User
    assigned_to = Column(Integer, ForeignKey('users.user_id'))  # ForeignKey to User
    approval_status = Column(String, default='Pending')

    def __repr__(self):
        return f"<Privilege(privilege_id={self.privilege_id}, name={self.privilege_name}, status={self.status})>"


if __name__ == '__main__':
    app.run(debug=True)
