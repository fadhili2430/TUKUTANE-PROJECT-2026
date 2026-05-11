from .models import Activity, CampusArea, db

def populate_initial_data():
    # Populate Activities
    activities = [
        {'name': 'Coding', 'description': 'Programming and software development'},
        {'name': 'Hiking', 'description': 'Outdoor hiking and nature walks'},
        {'name': 'Chess', 'description': 'Board game strategy and competition'},
        {'name': 'Bowling', 'description': 'Bowling alley games and social events'},
        {'name': 'Pool', 'description': 'Pool table games and billiards'},
        {'name': 'Gaming', 'description': 'Video games and gaming sessions'},
        {'name': 'Football', 'description': 'Football matches and training sessions'},
        {'name': 'Basketball', 'description': 'Basketball games and practice'},
        {'name': 'Study Group', 'description': 'Group study sessions and academic support'},
    ]

    for act in activities:
        if not Activity.query.filter_by(name=act['name']).first():
            db.session.add(Activity(name=act['name'], description=act['description']))

    # Campus Areas — MMU buildings + all major Kenyan university campuses
    areas = [
        # --- Multimedia University of Kenya (MMU) — Ongata Rongai, Nairobi ---
        {'name': 'MMU - Main Block',       'description': 'Multimedia University main academic building'},
        {'name': 'MMU - Sports Centre',    'description': 'MMU sports facilities and gymnasium'},
        {'name': 'MMU - Library',          'description': 'MMU library and study grounds'},
        {'name': 'MMU - Cafeteria',        'description': 'MMU dining and social area'},
        {'name': 'MMU - Computer Lab',     'description': 'MMU computing and IT facilities'},
        {'name': 'MMU - Student Centre',   'description': 'MMU student activities hub'},
        {'name': 'MMU - Lecture Block',    'description': 'MMU lecture halls and classrooms'},
        {'name': 'MMU - Hostels',          'description': 'MMU student residential area'},

        # --- Other Kenyan Universities ---
        {'name': 'University of Nairobi',              'description': 'Main campus, Nairobi CBD'},
        {'name': 'Kenyatta University',                'description': 'Main campus, Kahawa, Nairobi'},
        {'name': 'Strathmore University',              'description': 'Madaraka Estate, Nairobi'},
        {'name': 'JKUAT',                              'description': 'Jomo Kenyatta University, Juja'},
        {'name': 'Technical University of Kenya',      'description': 'Haile Selassie Avenue, Nairobi'},
        {'name': 'USIU-Africa',                        'description': 'United States International University, Nairobi'},
        {'name': 'Daystar University',                 'description': 'Athi River Campus, Machakos'},
        {'name': 'Catholic University (CUEA)',         'description': 'Lang\'ata, Nairobi'},
        {'name': 'Moi University',                     'description': 'Main campus, Eldoret'},
        {'name': 'Maseno University',                  'description': 'Maseno, Kisumu County'},
        {'name': 'Egerton University',                 'description': 'Njoro, Nakuru County'},
        {'name': 'Dedan Kimathi University',           'description': 'Nyeri, Central Kenya'},
        {'name': 'Mount Kenya University',             'description': 'Main campus, Thika'},
        {'name': 'Kisii University',                   'description': 'Kisii Town, Kisii County'},
        {'name': 'Laikipia University',                'description': 'Nyahururu, Laikipia County'},
        {'name': 'Machakos University',                'description': 'Machakos Town'},
        {'name': 'Chuka University',                   'description': 'Chuka, Tharaka Nithi County'},
        {'name': 'Kirinyaga University',               'description': 'Kutus, Kirinyaga County'},
        {'name': 'Pwani University',                   'description': 'Kilifi, Coast Region'},
        {'name': 'Jaramogi Oginga Odinga University', 'description': 'Bondo, Siaya County'},
    ]

    for area in areas:
        if not CampusArea.query.filter_by(name=area['name']).first():
            db.session.add(CampusArea(name=area['name'], description=area['description']))

    db.session.commit()
