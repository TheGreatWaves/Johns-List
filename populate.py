
# App, db and tables
from init_schema import app, db, create, User, Group, group_member_table, Content, List

# For hashing
from werkzeug.security import generate_password_hash


users = []
groups = []
contents = []

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
    
    # Add
    for user in users:
        db.session.add(user)
        
    # =============== Flesh out the lore =============== #
    
    john    = User.query.filter_by(username='john').first()
    
    john.bio = "Hello my name is john, I like watching " \
                "anime. I made this website for other " \
                "people like me.\n I'm also in love with Bob."         
    john.profile_pic_url = "https://preview.redd.it/e57hd13fova51.jpg?width=640&crop=smart&auto=webp&s=14095bd6a0508c4f4e33f21932906562d3c892f7"
      
    bob     = User.query.filter_by(username='bob').first()
    bob.bio = "my idea of help from above is a sniper on the roof\n\n Copium got me double timing"
    bob.profile_pic_url = "https://i1.sndcdn.com/artworks-000161913473-5mwrx1-t500x500.jpg"
    
    jenny   = User.query.filter_by(username='jenny').first()
    jenny.bio = "Avid manga reader, threaten me and I will spoil any anime for you.\n\n" \
                "Bob has been a little fishy recently..."
    jenny.profile_pic_url = "https://ae01.alicdn.com/kf/Sb80c21b934154d12b869e3b01d9126der/Fate-Apocrypha-Astolfo-Black-Rider-3-8-5-Big-Peeker-Waifu-Kawaii.jpg_Q90.jpg_.webp"
    
     # ================================================= #
        

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
    
def add_contents():
    contents_to_add = \
    [
        Content("Shuumatsu Nani Shitemasu ka? Isogashii desu ka? Sukutte Moratte Ii desu ka?", "anime"),
        Content("Jujutsu Kaisen", "anime"),
        Content("Re:Zero − Starting Life in Another World", "manga")
    ]

    shuumatsu = contents_to_add[0]
    shuumatsu.poster = "https://cdn.myanimelist.net/images/about_me/ranking_items/3620541-41b9a6ad-673f-4792-a6d2-c02d64faac27.jpg?t=1664535682"
    shuumatsu.synopsis = "Putting his life on the line, Willem Kmetsch leaves his loved ones behind and sets out to battle a mysterious monster, and even" \
                        "though he is victorious, he is rendered frozen in ice. It is during his icy slumber that terrifying creatures known as 'Beasts' emerge" \
                        "on the Earth's surface and threaten humanity's existence. Willem awakens 500 years later, only to find himself the sole survivor of his" \
                        "race as mankind is wiped out. Together with the other surviving races, Willem takes refuge on the floating islands in the sky, living in" \
                        "fear of the Beasts below. He lives a life of loneliness and only does odd jobs to get by. One day, he is tasked with being a weapon "\
                        "storehouse caretaker. Thinking nothing of it, Willem accepts, but he soon realizes that these weapons are actually a group of young "\
                        "Leprechauns. Though they bear every resemblance to humans, they have no regard for their own lives, identifying themselves as mere weapons "\
                        "of war. Among them is Chtholly Nota Seniorious, who is more than willing to sacrifice herself if it means defeating the Beasts and ensuring peace." \
                        "Willem becomes something of a father figure for the young Leprechauns, watching over them fondly and supporting them in any way he can. He, who "\
                        "once fought so bravely on the frontlines, can now only hope that the ones being sent to battle return safely from the monsters that destroyed his kind."
    
    jujutsu_kaisen = contents_to_add[1]
    jujutsu_kaisen.poster = "https://m.media-amazon.com/images/M/MV5BNGY4MTg3NzgtMmFkZi00NTg5LWExMmEtMWI3YzI1ODdmMWQ1XkEyXkFqcGdeQXVyMjQwMDg0Ng@@._V1_.jpg"
    jujutsu_kaisen.synopsis = "A boy swallows a cursed talisman - the finger of a demon - and becomes cursed himself. He enters a shaman's school to be able to locate the " \
                            "demon's other body parts and thus exorcise himself."
                            
                            
    rezero = contents_to_add[2]
    rezero.poster = "https://upload.wikimedia.org/wikipedia/en/thumb/3/3c/Re-Zero_kara_Hajimeru_Isekai_Seikatsu_light_novel_volume_1_cover.jpg/220px-Re-Zero_kara_Hajimeru_Isekai_Seikatsu_light_novel_volume_1_cover.jpg"
    rezero.synopsis = "dude got sent into another world, but it's actually hell"
    
    for content in contents_to_add:
        db.session.add(content)
        
    
    

def populate():
    add_users()
    add_groups()
    add_contents()
    
    # Commit changes
    db.session.commit()

# Main program entry point
if __name__ == '__main__':  
    with app.app_context():
        create()
        populate()