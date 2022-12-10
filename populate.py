
# App, db and tables
from init_schema import *

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
    
    admin = users_to_add[0]
    admin.profile_pic_url = "https://play-lh.googleusercontent.com/l_7GFUsvpn8yW1VjRA_1mZuEETw-Aia5DilKGkyCVYmkPnrOyvCEyabxwD9x0AmUpiq_"
    admin.bio = "he loves Rem lol"
    
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

    # =================== Lore members =================== #
        
    john    = User.query.filter_by(username='john').first()
    bob     = User.query.filter_by(username='bob').first()
    jenny   = User.query.filter_by(username='jenny').first()

    # ==================================================== #
    
    groups_to_add = \
    [
        Group(name='Fun big group', owner=john),
        Group(name='lonely group', owner=bob),
        Group(name='lover group', owner=jenny),
        Group(name='secret friendship', owner=john),
    ]
    
    secret_friendship = groups_to_add[3]
    secret_friendship.img_url = "https://i.ytimg.com/vi/S6bQibFNs2E/maxresdefault.jpg"
    
    fun_big_group = groups_to_add[0]
    fun_big_group.img_url = "https://cdn.otakutale.com/wp-content/uploads/2020/10/Higurashi-no-Naku-Koro-ni-2020-Anime-to-Run-for-24-Episodes-Title-Officially-Revealed.jpg"
    fun_big_group.info = "We're a big community of extremely sane friends living in an extremely peaceful village."
    
    # =================== Big group =================== #

    big_group = groups_to_add[0]
    
    for user in users:
        if user.name != 'john':
            big_group.add_member(user)
        
    # ================== Lover group ================== #
    
    lover_group = groups_to_add[2]
    
    lover_group.add_member(bob)
    
    # ================== Plot twist ================== #
    
    secret_friendship = groups_to_add[3]
    
    secret_friendship.add_member(bob)
    
    for group in groups_to_add:
        groups.append(group)
    
    for group in groups:
        db.session.add(group)

def add_content( lst, name, type ):
    lst.append( Content( name, type ) )
    return lst[-1]

def add_contents():

    contents_to_add = []
    
    shuumatsu       = add_content(contents_to_add, "Shuumatsu Nani Shitemasu ka? Isogashii desu ka? Sukutte Moratte Ii desu ka?", "anime")
    jujutsu_kaisen  = add_content(contents_to_add, "Jujutsu Kaisen", "anime")
    rezero          = add_content(contents_to_add, "Re:Zero Starting Life in Another World", "anime")
    erased          = add_content(contents_to_add, "Erased", "anime")
    pancreas        = add_content(contents_to_add, "I want to eat your pancreas", "anime")
    dandadan        = add_content(contents_to_add, "Dandadan", "manga")
    asobi           = add_content(contents_to_add, "Asobi Asobase", "anime")
    steinsgate      = add_content(contents_to_add, "Steins;Gate", "anime")
    aot             = add_content(contents_to_add, "Attack On Titan", "anime")
    oyasumi         = add_content(contents_to_add, "Oyasumi Punpun", "manga")
    horimiya        = add_content(contents_to_add, "Horimiya", "manga")
    
    
    horimiya.poster = "https://nntheblog.b-cdn.net/wp-content/uploads/2022/05/Practicing-by-redrawing-Horimiya-Illustration.png.webp"
    horimiya.synopsis = "On the surface, the thought of Kyouko Hori and Izumi Miyamura getting along would be the last thing in people's minds. "\
    "After all, Hori has a perfect combination of beauty and brains, while Miyamura appears meek and distant to his fellow classmates. However,"\
    " a fateful meeting between the two lays both of their hidden selves bare. Even though she is popular at school, Hori has little time to socialize "\
    "with her friends due to housework. On the other hand, Miyamura lives under the noses of his peers, his body bearing secret tattoos and piercings "\
    "that make him look like a gentle delinquent."
    horimiya.set_genre(
        GENRE_ROMANCE,
        GENRE_SOL,
        GENRE_DRAMA
    )
    
    oyasumi.poster = "https://d28hgpri8am2if.cloudfront.net/book_images/onix/cvr9781421586205/goodnight-punpun-vol-1-9781421586205_hr.jpg"
    oyasumi.synopsis = "Punpun Onodera is a normal 11-year-old boy living in Japan. Hopelessly idealistic and romantic, Punpun begins to "\
        "see his life take a subtle—though nonetheless startling—turn to the adult when he meets the new girl in his class, Aiko Tanaka. It "\
        "is then that the quiet boy learns just how fickle maintaining a relationship can be, and the surmounting difficulties of transitioning "\
        "from a naïve boyhood to a convoluted adulthood. When his father assaults his mother one night, Punpun realizes another thing: those whom "\
        "he looked up to were not as impressive as he once thought."
    oyasumi.set_genre(
        GENRE_TRAGIC,
        GENRE_DRAMA,
        GENRE_PSYCHOLOGICAL,
        GENRE_ROMANCE
    )
    
    aot.poster = "https://m.media-amazon.com/images/M/MV5BNzc5MTczNDQtNDFjNi00ZDU5LWFkNzItOTE1NzQzMzdhNzMxXkEyXkFqcGdeQXVyNTgyNTA4MjM@._V1_.jpg"
    aot.synopsis = "When man-eating Titans first appeared 100 years ago, humans found safety behind massive walls that stopped the giants in their tracks. "\
        "But the safety they have had for so long is threatened when a colossal Titan smashes through the barriers, causing a flood of the giants into what "\
            "had been the humans' safe zone. During the carnage that follows, soldier Eren Jaeger sees one of the creatures devour his mother, which leads him "\
                "to vow that he will kill every Titan. He enlists some friends who survived to help him, and that group is humanity's last hope for avoiding "\
                    "extinction at the hands of the monsters."
    aot.set_genre(
        GENRE_ACTION,
        GENRE_ADVENTURE,
        GENRE_HORROR,
        GENRE_SUPERNATURAL,
        GENRE_PSYCHOLOGICAL,
        GENRE_MYSTERY,
        GENRE_THRILLER,
        GENRE_TRAGIC
    )
    
    
    steinsgate.poster = "https://m.media-amazon.com/images/M/MV5BMjUxMzE4ZDctODNjMS00MzIwLThjNDktODkwYjc5YWU0MDc0XkEyXkFqcGdeQXVyNjc3OTE4Nzk@._V1_.jpg"
    steinsgate.synopsis = "Eccentric scientist Rintarou Okabe has a never-ending thirst for scientific exploration. Together with his ditzy but well-meaning "\
        "friend Mayuri Shiina and his roommate Itaru Hashida, Rintarou founds the Future Gadget Laboratory in the hopes of creating technological innovations "\
        "that baffle the human psyche. Despite claims of grandeur, the only notable 'gadget' the trio have created is a microwave that has the mystifying power "\
        "to turn bananas into green goo."
    steinsgate.set_genre(
        GENRE_THRILLER,
        GENRE_MYSTERY,
        GENRE_SCI_FI,
        GENRE_SUPERNATURAL,
        GENRE_PSYCHOLOGICAL,
        GENRE_TRAGIC,
        GENRE_TIME_TRAVEL,
        GENRE_ROMANCE
    )
    
    asobi.poster = "https://m.media-amazon.com/images/I/81saK-pr9FL._AC_UF894,1000_QL80_.jpg"
    asobi.synopsis = "During recess, Olivia, a foreign transfer student who doesn't know English, plays a game of 'look-the-other-way' with Hanako Honda, "\
        "a loud-mouthed airhead. Their rowdy behavior spurs the ire of Kasumi Nomura, a deadpan loner constantly teased by her older sister for her tendency "\
        "to lose games. Not willing to compete, Kasumi declines Olivia's offer to join the fun, but eventually gets involved anyway and dispenses her own brand "\
        "of mischief. Soon, a strange friendship blossoms between the peculiar trio, and they decide to form the 'Pastime Club', where they are free to resume their daily hijinks."
    asobi.set_genre(
        GENRE_COMEDY,
        GENRE_SOL
    )
    
    dandadan.poster = "https://mangaplus.shueisha.co.jp/drm/title/100171/title_thumbnail_portrait_list/181732.jpg?key=bc1192d36fb8b5670168d83589723495&duration=86400"
    dandadan.synopsis = "Ghosts, monsters, aliens, teen romance, battles...and the kitchen sink! This series has it all! Takakura, an occult maniac who doesn't "\
        "believe in ghosts, and Ayase, a girl who doesn't believe in aliens, try to overcome their differences when they encounter the paranormal! This manga is out of this world!"
    dandadan.set_genre(
        GENRE_ACTION,
        GENRE_ADVENTURE,
        GENRE_COMEDY,
        GENRE_MAGIC,
        GENRE_ROMANCE,
        GENRE_SUPERNATURAL,
        GENRE_MAGIC
    )
    
    pancreas.poster = "https://musicart.xboxlive.com/7/d03b5100-0000-0000-0000-000000000002/504/image.jpg?w=1920&h=1080"
    pancreas.synopsis = "A high school student discovers one of his classmates, Sakura Yamauchi, is suffering from a terminal illness. This secret brings the two"\
                    "together, as she lives out her final moments."
    pancreas.set_genre(
        GENRE_DRAMA,
        GENRE_SOL,
        GENRE_ROMANCE
    )
    
    erased.poster = "https://m.media-amazon.com/images/M/MV5BYzJmZjZkMjQtZjJmZC00M2JkLTg5MzktN2FkOTllNTc5MmMzXkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_FMjpg_UX1000_.jpg"
    erased.synopsis = "29-year-old Satoru Fujinuma is sent back in time 18 years to prevent the events leading to his mother's death, which began with a series "\
                        "of kidnappings while he was in 5th grade."
    erased.set_genre(
        GENRE_MYSTERY,
        GENRE_ROMANCE,
        GENRE_PSYCHOLOGICAL,
        GENRE_THRILLER,
        GENRE_SUPERNATURAL,
        GENRE_TIME_TRAVEL
    )
    
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
    shuumatsu.set_genre(
        GENRE_MAGIC,
        GENRE_ACTION,
        GENRE_ADVENTURE,
        GENRE_FANTASY,
        GENRE_MAGIC,
        GENRE_PSYCHOLOGICAL,
        GENRE_ROMANCE,
        GENRE_TRAGIC
    )
    
    jujutsu_kaisen.poster = "https://m.media-amazon.com/images/M/MV5BNGY4MTg3NzgtMmFkZi00NTg5LWExMmEtMWI3YzI1ODdmMWQ1XkEyXkFqcGdeQXVyMjQwMDg0Ng@@._V1_.jpg"
    jujutsu_kaisen.synopsis = "A boy swallows a cursed talisman - the finger of a demon - and becomes cursed himself. He enters a shaman's school to be able to locate the " \
                            "demon's other body parts and thus exorcise himself."
    jujutsu_kaisen.set_genre(
        GENRE_MAGIC,
        GENRE_ACTION,
        GENRE_ADVENTURE,
        GENRE_SUPERNATURAL
        )
                            
    rezero.poster = "https://m.media-amazon.com/images/M/MV5BN2NlM2Y5Y2MtYjU5Mi00ZjZiLWFjNjMtZDNiYzJlMjhkOWZiXkEyXkFqcGdeQXVyNjc2NjA5MTU@._V1_FMjpg_UX1000_.jpg"
    rezero.synopsis = "dude got sent into another world, but it's actually hell"
    
    rezero.set_genre(
        GENRE_HORROR,
        GENRE_ISEKAI,
        GENRE_MAGIC,
        GENRE_FANTASY,
        GENRE_ROMANCE,
        GENRE_ADVENTURE,
        GENRE_ROMANCE,
        GENRE_ACTION,
        GENRE_TIME_TRAVEL
    )
    
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