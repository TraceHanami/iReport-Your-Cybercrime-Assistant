from app import create_app
from database.connection import db
from database.models import User, PoliceOfficer, Volunteer
from auth.auth_handler import Auth
from datetime import datetime
import random

def seed_initial_data():
    app = create_app()
    
    with app.app_context():
        # Create admin user if not exists
        if not User.query.filter_by(email='admin@ireport.com').first():
            admin_user = User(
                email='admin@ireport.com',
                password_hash=Auth.hash_password('admin123'),
                full_name='System Administrator',
                role='admin',
                is_verified=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Admin user created")
        
        # Indian states with major districts
        indian_locations = [
            # Northern Region
            {
                'state': 'Delhi', 
                'districts': ['Central Delhi', 'North Delhi', 'South Delhi', 'East Delhi', 'West Delhi', 'New Delhi']
            },
            {
                'state': 'Uttar Pradesh',
                'districts': ['Lucknow', 'Kanpur', 'Varanasi', 'Agra', 'Meerut', 'Allahabad', 'Ghaziabad', 'Noida']
            },
            {
                'state': 'Punjab',
                'districts': ['Amritsar', 'Ludhiana', 'Jalandhar', 'Patiala', 'Bathinda', 'Mohali']
            },
            {
                'state': 'Haryana',
                'districts': ['Gurugram', 'Faridabad', 'Chandigarh', 'Ambala', 'Panipat', 'Karnal']
            },
            {
                'state': 'Rajasthan',
                'districts': ['Jaipur', 'Jodhpur', 'Udaipur', 'Kota', 'Ajmer', 'Bikaner']
            },
            {
                'state': 'Himachal Pradesh',
                'districts': ['Shimla', 'Mandi', 'Solan', 'Kangra', 'Kullu', 'Dharamshala']
            },
            
            # Southern Region
            {
                'state': 'Karnataka',
                'districts': ['Bangalore', 'Mysore', 'Hubli', 'Mangalore', 'Belgaum', 'Gulbarga']
            },
            {
                'state': 'Tamil Nadu',
                'districts': ['Chennai', 'Coimbatore', 'Madurai', 'Trichy', 'Salem', 'Vellore']
            },
            {
                'state': 'Kerala',
                'districts': ['Thiruvananthapuram', 'Kochi', 'Kozhikode', 'Thrissur', 'Kannur', 'Kollam']
            },
            {
                'state': 'Andhra Pradesh',
                'districts': ['Visakhapatnam', 'Vijayawada', 'Guntur', 'Nellore', 'Kurnool', 'Tirupati']
            },
            {
                'state': 'Telangana',
                'districts': ['Hyderabad', 'Warangal', 'Nizamabad', 'Khammam', 'Karimnagar', 'Mahbubnagar']
            },
            
            # Western Region
            {
                'state': 'Maharashtra',
                'districts': ['Mumbai', 'Pune', 'Nagpur', 'Nashik', 'Thane', 'Aurangabad']
            },
            {
                'state': 'Gujarat',
                'districts': ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot', 'Bhavnagar', 'Gandhinagar']
            },
            {
                'state': 'Goa',
                'districts': ['North Goa', 'South Goa']
            },
            
            # Eastern Region
            {
                'state': 'West Bengal',
                'districts': ['Kolkata', 'Howrah', 'Durgapur', 'Asansol', 'Siliguri', 'Bardhaman']
            },
            {
                'state': 'Bihar',
                'districts': ['Patna', 'Gaya', 'Bhagalpur', 'Muzaffarpur', 'Darbhanga', 'Purnia']
            },
            {
                'state': 'Odisha',
                'districts': ['Bhubaneswar', 'Cuttack', 'Rourkela', 'Berhampur', 'Sambalpur', 'Puri']
            },
            {
                'state': 'Jharkhand',
                'districts': ['Ranchi', 'Jamshedpur', 'Dhanbad', 'Bokaro', 'Hazaribagh', 'Deoghar']
            },
            
            # North-Eastern Region
            {
                'state': 'Assam',
                'districts': ['Guwahati', 'Silchar', 'Dibrugarh', 'Jorhat', 'Nagaon', 'Tezpur']
            },
            {
                'state': 'Meghalaya',
                'districts': ['Shillong', 'Tura', 'Jowai', 'Nongpoh', 'Baghmara']
            },
            {
                'state': 'Nagaland',
                'districts': ['Kohima', 'Dimapur', 'Mokokchung', 'Wokha', 'Tuensang']
            }
        ]

        # Police ranks in hierarchical order
        police_ranks = [
            'Inspector General', 'Deputy Inspector General', 'Superintendent', 
            'Deputy Superintendent', 'Inspector', 'Sub-Inspector', 
            'Assistant Sub-Inspector', 'Head Constable', 'Constable'
        ]

        # Police officer names (Indian names)
        police_first_names = ['Rajesh', 'Priya', 'Amit', 'Sunil', 'Neha', 'Vikram', 'Anjali', 'Rahul', 
                             'Pooja', 'Sanjay', 'Kavita', 'Deepak', 'Meera', 'Arun', 'Sonia', 'Ravi']
        police_last_names = ['Sharma', 'Singh', 'Kumar', 'Patel', 'Reddy', 'Mehta', 'Verma', 'Yadav',
                            'Jain', 'Malhotra', 'Choudhary', 'Thakur', 'Mishra', 'Tiwari', 'Nair']

        # Create police officers (2-3 per state)
        police_count = 0
        for location in indian_locations:
            officers_per_state = random.randint(2, 3)
            for i in range(officers_per_state):
                first_name = random.choice(police_first_names)
                last_name = random.choice(police_last_names)
                full_name = f"{first_name} {last_name}"
                email = f"police_{location['state'].lower().replace(' ', '_')}_{i+1}@ireport.com"
                
                if not User.query.filter_by(email=email).first():
                    # Create user
                    police_user = User(
                        email=email,
                        password_hash=Auth.hash_password('police123'),
                        full_name=full_name,
                        role='police',
                        is_verified=True
                    )
                    db.session.add(police_user)
                    db.session.commit()
                    
                    # Create police officer record - MATCHING YOUR ACTUAL MODEL SCHEMA
                    district = random.choice(location['districts'])
                    rank_index = min(i, len(police_ranks) - 1)  # Higher ranks for first officers
                    
                    police_officer = PoliceOfficer(
                        user_id=police_user.id,
                        badge_number=f"POL{location['state'][:3].upper()}{i+1:03d}",
                        rank=police_ranks[rank_index],
                        department=random.choice(['Patrol Department', 'Investigation Department', 'Traffic Department', 'CID', 'Cyber Crime Unit']),
                        police_station=f"{district} Police Station",
                        station=f"{district} Police Station",
                        state=location['state'],
                        district=district,
                        contact_number=f"+91{random.randint(7000000000, 9999999999)}",
                        specialization=random.choice(['Patrol', 'Investigation', 'Traffic', 'CID', 'Cyber Crime']),
                        is_active=True,
                        current_case_load=random.randint(0, 10),  # Using current_case_load from your model
                        performance_score=round(random.uniform(3.0, 5.0), 1)  # Using performance_score from your model
                    )
                    db.session.add(police_officer)
                    db.session.commit()
                    police_count += 1
                    print(f"✅ Police officer created: {full_name} - {location['state']}")

        print(f"\n👮 Created {police_count} police officers across India")

        # Create volunteers (2-3 per state)
        volunteer_count = 0
        volunteer_first_names = ['Anjali', 'Rohit', 'Priya', 'Raj', 'Sunita', 'Mohan', 'Kavita', 'Suresh',
                               'Neha', 'Vikram', 'Pooja', 'Arun', 'Meera', 'Sanjay', 'Radha', 'Amit']
        volunteer_last_names = ['Patel', 'Verma', 'Sharma', 'Kumar', 'Singh', 'Reddy', 'Nair', 'Mehta',
                              'Jain', 'Yadav', 'Mishra', 'Tiwari', 'Choudhary', 'Malhotra']

        volunteer_skills = [
            'Community Outreach', 'Counseling', 'Legal Aid', 'Documentation', 
            'First Aid', 'Crisis Management', 'Social Work', 'Child Protection',
            'Women Safety', 'Elder Care', 'Disaster Management', 'Cyber Safety'
        ]
        
        volunteer_qualifications = [
            'BA in Social Work', 'MA in Psychology', 'LLB', 'MSW', 
            'Diploma in Counseling', 'BSc Nursing', 'MA Sociology',
            'Public Health Degree', 'Crisis Management Certificate'
        ]

        for location in indian_locations:
            volunteers_per_state = random.randint(2, 3)
            for i in range(volunteers_per_state):
                first_name = random.choice(volunteer_first_names)
                last_name = random.choice(volunteer_last_names)
                full_name = f"{first_name} {last_name}"
                email = f"volunteer_{location['state'].lower().replace(' ', '_')}_{i+1}@ireport.com"
                
                if not User.query.filter_by(email=email).first():
                    # Create user
                    volunteer_user = User(
                        email=email,
                        password_hash=Auth.hash_password('volunteer123'),
                        full_name=full_name,
                        role='volunteer',
                        is_verified=True
                    )
                    db.session.add(volunteer_user)
                    db.session.commit()
                    
                    # Create volunteer record
                    district = random.choice(location['districts'])
                    
                    volunteer = Volunteer(
                        user_id=volunteer_user.id,
                        skills=random.choice(volunteer_skills),
                        qualifications=random.choice(volunteer_qualifications),
                        experience=f"{random.randint(1, 10)} years",
                        state=location['state'],
                        district=district,
                        status='approved',
                        background_check=random.choice([True, True, True, False]),  # 75% pass rate
                        availability=random.choice(['Weekdays', 'Weekends', 'Flexible', '24/7']),
                        rating=round(random.uniform(3.5, 5.0), 1),
                        cases_handled=random.randint(0, 15)
                    )
                    db.session.add(volunteer)
                    db.session.commit()
                    volunteer_count += 1
                    print(f"✅ Volunteer created: {full_name} - {location['state']}")

        print(f"\n🤝 Created {volunteer_count} volunteers across India")

        # Create sample public users from different states
        public_users = [
            {'email': 'user@ireport.com', 'name': 'Rahul Kumar', 'state': 'Delhi'},
            {'email': 'user_mumbai@ireport.com', 'name': 'Priya Shah', 'state': 'Maharashtra'},
            {'email': 'user_bangalore@ireport.com', 'name': 'Arun Reddy', 'state': 'Karnataka'},
            {'email': 'user_kolkata@ireport.com', 'name': 'Sonia Chatterjee', 'state': 'West Bengal'},
            {'email': 'user_chennai@ireport.com', 'name': 'Rajesh Iyer', 'state': 'Tamil Nadu'}
        ]

        for user_data in public_users:
            if not User.query.filter_by(email=user_data['email']).first():
                public_user = User(
                    email=user_data['email'],
                    password_hash=Auth.hash_password('user123'),
                    full_name=user_data['name'],
                    role='public',
                    is_verified=True
                )
                db.session.add(public_user)
                db.session.commit()
                print(f"✅ Public user created: {user_data['name']} - {user_data['state']}")

        print("\n🎉 Initial data seeded successfully!")
        print(f"\n📊 Summary:")
        print(f"   👑 Admin users: 1")
        print(f"   👮 Police officers: {police_count} (across {len(indian_locations)} states)")
        print(f"   🤝 Volunteers: {volunteer_count} (across {len(indian_locations)} states)")
        print(f"   👤 Public users: {len(public_users)}")
        
        print("\n📋 Sample Login Credentials (Pattern):")
        print("👑 Admin: admin@ireport.com / admin123")
        print("👮 Police: police_[state]_[number]@ireport.com / police123")
        print("   Example: police_delhi_1@ireport.com / police123")
        print("🤝 Volunteers: volunteer_[state]_[number]@ireport.com / volunteer123")
        print("   Example: volunteer_maharashtra_1@ireport.com / volunteer123")
        print("👤 Public: user@ireport.com / user123")
        
        print("\n🌍 Coverage:")
        print(f"   - States covered: {len(indian_locations)}")
        print("   - Regions: Northern, Southern, Western, Eastern, North-Eastern India")
        print("   - All major districts included")

if __name__ == '__main__':
    seed_initial_data()