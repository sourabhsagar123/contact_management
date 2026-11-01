"""
Seed Data Generator for Contact Management System
=================================================
Populates the database with realistic sample contacts and relationships
so the student can demonstrate autocomplete, AVL tree, Heap, and Graph
visualizations immediately upon launching!
"""

from database import (
    init_db,
    fetch_all_contacts,
    insert_contact_db,
    insert_relationship_db
)

SAMPLE_CONTACTS = [
    {"name": "Aaron Paul", "phone": "+91 98765 43210", "email": "aaron.p@gmail.com", "category": "Work", "company": "Google", "notes": "Senior Android Architect", "is_favorite": True, "call_count": 18},
    {"name": "Aarushi Sharma", "phone": "+91 98765 43211", "email": "aarushi.s@college.edu", "category": "College", "company": "IIT Bombay", "notes": "ADSA Lab Partner", "is_favorite": True, "call_count": 25},
    {"name": "Abhishek Verma", "phone": "+91 98765 43212", "email": "abhi.v@techcorp.in", "category": "Work", "company": "Microsoft", "notes": "Cloud DevOps Lead", "is_favorite": False, "call_count": 6},
    {"name": "Aditi Rao", "phone": "+91 98765 43213", "email": "aditi.rao@gmail.com", "category": "Friends", "company": "DesignCo", "notes": "UI/UX Mentor", "is_favorite": False, "call_count": 12},
    {"name": "Albert Einstein", "phone": "+91 98765 43214", "email": "einstein@princeton.edu", "category": "College", "company": "Princeton University", "notes": "Physics Guest Faculty", "is_favorite": True, "call_count": 42},
    {"name": "Alice Johnson", "phone": "+91 98765 43215", "email": "alice.j@apple.com", "category": "Work", "company": "Apple", "notes": "Swift & iOS Developer", "is_favorite": False, "call_count": 9},
    {"name": "Ananya Gupta", "phone": "+91 98765 43216", "email": "ananya.g@startup.io", "category": "Friends", "company": "FinTech Startup", "notes": "College hackathon teammate", "is_favorite": True, "call_count": 31},
    {"name": "Bob Dylan", "phone": "+91 98765 43217", "email": "bob.d@records.com", "category": "Family", "company": "Acoustics Ltd", "notes": "Uncle Bob - Guitarist", "is_favorite": False, "call_count": 4},
    {"name": "Bruce Wayne", "phone": "+91 98765 43218", "email": "bruce@wayneenterprises.com", "category": "Emergency", "company": "Wayne Enterprises", "notes": "Emergency Contact #1", "is_favorite": True, "call_count": 99},
    {"name": "Charlie Brown", "phone": "+91 98765 43219", "email": "charlie.b@peanuts.org", "category": "Friends", "company": "Freelance", "notes": "Childhood neighbor", "is_favorite": False, "call_count": 3},
    {"name": "Deepak Patel", "phone": "+91 98765 43220", "email": "deepak.p@tcs.com", "category": "Work", "company": "TCS Research", "notes": "Database Systems Consultant", "is_favorite": False, "call_count": 14},
    {"name": "Divya Nair", "phone": "+91 98765 43221", "email": "divya.nair@isro.gov.in", "category": "College", "company": "ISRO", "notes": "Satellite Communications Club Lead", "is_favorite": True, "call_count": 22},
    {"name": "Emily Watson", "phone": "+91 98765 43222", "email": "emily.w@meta.com", "category": "Work", "company": "Meta", "notes": "AI Infrastructure Engineer", "is_favorite": False, "call_count": 11},
    {"name": "Gaurav Sen", "phone": "+91 98765 43223", "email": "gaurav@systemdesign.in", "category": "College", "company": "EdTech", "notes": "System Design Mentor", "is_favorite": True, "call_count": 19},
    {"name": "Grace Hopper", "phone": "+91 98765 43224", "email": "grace.hopper@usnavy.mil", "category": "College", "company": "Yale University", "notes": "Compiler Construction Pioneer", "is_favorite": True, "call_count": 55},
    {"name": "Kavita Krishnan", "phone": "+91 98765 43225", "email": "kavita.k@hospital.org", "category": "Emergency", "company": "Apollo Hospitals", "notes": "Family Physician / Medical Emergency", "is_favorite": True, "call_count": 88},
    {"name": "Linus Torvalds", "phone": "+91 98765 43226", "email": "torvalds@kernel.org", "category": "Work", "company": "Linux Foundation", "notes": "Operating Systems Mentor", "is_favorite": True, "call_count": 75},
    {"name": "Manish Malhotra", "phone": "+91 98765 43227", "email": "manish@studio.com", "category": "Family", "company": "Apparel Co", "notes": "Cousin Manish", "is_favorite": False, "call_count": 2},
    {"name": "Neha Kulkarni", "phone": "+91 98765 43228", "email": "neha.k@infosys.com", "category": "Work", "company": "Infosys", "notes": "Algorithms Study Group Member", "is_favorite": False, "call_count": 8},
    {"name": "Peter Parker", "phone": "+91 98765 43229", "email": "peter.parker@dailybugle.com", "category": "Friends", "company": "Daily Bugle", "notes": "Freelance Photographer", "is_favorite": True, "call_count": 37},
    {"name": "Pooja Hegde", "phone": "+91 98765 43230", "email": "pooja.h@media.in", "category": "Friends", "company": "Cinema Productions", "notes": "College Drama Society", "is_favorite": False, "call_count": 7},
    {"name": "Rahul Dravid", "phone": "+91 98765 43231", "email": "rahul.d@bcci.tv", "category": "Emergency", "company": "National Cricket Academy", "notes": "Sports Coach & Mentor", "is_favorite": True, "call_count": 40},
    {"name": "Rohan Deshmukh", "phone": "+91 98765 43232", "email": "rohan.d@amazon.in", "category": "College", "company": "Amazon AWS", "notes": "Mini-project teammate", "is_favorite": False, "call_count": 15},
    {"name": "Siddharth Shukla", "phone": "+91 98765 43233", "email": "sid.s@finances.com", "category": "Family", "company": "HDFC Bank", "notes": "Brother Sid", "is_favorite": True, "call_count": 50},
    {"name": "Tanvi Joshi", "phone": "+91 98765 43234", "email": "tanvi.j@zomato.com", "category": "Friends", "company": "Zomato", "notes": "Foodie & roommate", "is_favorite": False, "call_count": 16},
    {"name": "Vikram Sarabhai", "phone": "+91 98765 43235", "email": "vikram.s@prl.res.in", "category": "College", "company": "Physical Research Lab", "notes": "Space Research Advisor", "is_favorite": True, "call_count": 65}
]

# Sample relationship edges (from index, to index, relation label)
SAMPLE_EDGES = [
    (0, 5, "Colleague"),       # Aaron & Alice
    (1, 22, "Project Partner"),# Aarushi & Rohan
    (1, 13, "Mentor-Student"), # Aarushi & Gaurav Sen
    (2, 10, "Colleague"),      # Abhishek & Deepak
    (3, 6, "Best Friend"),     # Aditi & Ananya
    (4, 14, "Research Peer"),  # Einstein & Grace Hopper
    (6, 19, "Classmate"),      # Ananya & Peter Parker
    (7, 17, "Relative"),       # Bob & Manish
    (8, 15, "Emergency Contact"), # Bruce & Kavita
    (10, 18, "Colleague"),     # Deepak & Neha
    (11, 25, "Research Advisor"), # Divya & Vikram
    (16, 22, "Open Source Mentor"), # Linus & Rohan
    (20, 24, "Roommate"),      # Pooja & Tanvi
    (21, 23, "Family Friend")  # Rahul & Siddharth
]


def seed_sample_data_if_empty() -> None:
    """Inserts sample contacts and edges only if database is fresh/empty."""
    init_db()
    existing = fetch_all_contacts()
    if len(existing) > 0:
        return  # Already has contacts

    id_map = {}
    for i, c in enumerate(SAMPLE_CONTACTS):
        cid = insert_contact_db(c)
        id_map[i] = cid

    for u_idx, v_idx, rel in SAMPLE_EDGES:
        if u_idx in id_map and v_idx in id_map:
            insert_relationship_db(id_map[u_idx], id_map[v_idx], rel)
