from .models import Activity, CampusArea, db

def populate_initial_data():
    # Populate Activities
    activities = [
        {'name': 'Coding', 'description': 'Programming and software development activities'},
        {'name': 'Hiking', 'description': 'Outdoor hiking and nature walks'},
        {'name': 'Chess', 'description': 'Board game strategy and competition'},
        {'name': 'Bowling', 'description': 'Bowling alley games and social events'},
        {'name': 'Pool', 'description': 'Pool table games and billiards'},
        {'name': 'Gaming', 'description': 'Video games and gaming sessions'},
    ]
    
    for act in activities:
        if not Activity.query.filter_by(name=act['name']).first():
            activity = Activity(name=act['name'], description=act['description'])
            db.session.add(activity)
    
    # Populate Campus Areas
    areas = [
        {'name': 'Main Block', 'description': 'Main academic building'},
        {'name': 'Sports Centre', 'description': 'Sports facilities and gymnasium'},
        {'name': 'Library Grounds', 'description': 'Library and surrounding areas'},
        {'name': 'Cafeteria', 'description': 'Dining and social area'},
        {'name': 'Lecture Hall A', 'description': 'Large lecture auditorium'},
        {'name': 'Computer Lab', 'description': 'Computing and IT facilities'},
    ]
    
    for area in areas:
        if not CampusArea.query.filter_by(name=area['name']).first():
            campus_area = CampusArea(name=area['name'], description=area['description'])
            db.session.add(campus_area)
    
    db.session.commit()