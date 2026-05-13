from app import create_app
from models import db, User
import traceback

app = create_app()
app.config['TESTING'] = True

with app.test_client() as client:
    with app.app_context():
        user = User.query.first()
        if not user:
            print("No users found")
            exit()
            
    # Mock login by setting the user ID in session
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        
    try:
        response = client.get('/insights/index')
        if response.status_code == 200:
            print("Successfully requested /insights/index!")
        else:
            print(f"Failed with status code: {response.status_code}")
    except Exception as e:
        print("EXCEPTION CAUGHT:")
        traceback.print_exc()
