
# App, db and tables
from init_schema import app, db, create, User, Group, group_member_table, Content, List

# For hashing
from werkzeug.security import generate_password_hash


users = []
groups = []

def add_users():
    users_to_add = \
    [
        User(email="admin@gmail.com", username="admin", password=generate_password_hash('123')),
        User(email="john@gmail.com", username="john", password=generate_password_hash('123')),
        User(email="bob@gmail.com", username="bob", password=generate_password_hash('123')),
        User(email="jenny@gmail.com", username="jenny", password=generate_password_hash('123')),
    ]
    
    for user in users_to_add:
        users.append(user)
    
    # =============== Flesh out the lore =============== #
    
    john    = User.query.filter_by(username='john').first()
    
    
    
    bob     = User.query.filter_by(username='bob').first()
    jenny   = User.query.filter_by(username='jenny').first()
    
     # ================================================= #
    
    # Add
    for user in users:
        db.session.add(user)
        

def add_groups():
    
    groups_to_add = \
    [
        Group(name='Fun big group'),
        Group(name='another group'),
        Group(name='lover group'),
        Group(name='secret friendship'),
    ]
    
    for group in groups_to_add:
        groups.append(group)
    
    for group in groups:
        db.session.add(group)
        
        
    # =================== Lore members =================== #
        
    john    = User.query.filter_by(username='john').first()
    bob     = User.query.filter_by(username='bob').first()
    jenny   = User.query.filter_by(username='jenny').first()
        
    # =================== Big group =================== #

    big_group = Group.query.filter_by(name='Fun big group').first()
    
    for user in users:
        big_group.add_member(user)
        
    # ================ Some other group ================ #
    
    lonely_group = Group.query.filter_by(name='another group').first()
    
    lonely_group.add_member(bob)
    
    # ================== Lover group ================== #
    
    lover_group = Group.query.filter_by(name='lover group').first()
    
    lover_group.add_member(bob)
    lover_group.add_member(jenny)
    
    # ================== Plot twist ================== #
    
    secret_friendship = Group.query.filter_by(name='secret friendship').first()
    
    secret_friendship.add_member(bob)
    secret_friendship.add_member(john)

def populate():
    add_users()
    add_groups()
    
    # Commit changes
    db.session.commit()

# Main program entry point
if __name__ == '__main__':  
    with app.app_context():
        create()
        populate()