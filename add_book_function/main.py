'''
Cloud Function to add a new book to Firestore.
'''
import functions_framework
import firebase_admin # Added import
from firebase_admin import credentials, firestore # Removed initialize_app from here

# Initialize Firebase Admin SDK
# It's recommended to initialize the app once per function instance.
# For local development, you might need to set GOOGLE_APPLICATION_CREDENTIALS.
if not firebase_admin._apps: # Corrected Firebase initialization check
    firebase_admin.initialize_app() # Corrected Firebase initialization call

db = firestore.client()

@functions_framework.http
def add_book_to_firestore(request):
    '''HTTP Cloud Function to add a book to Firestore.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values understandable by
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    '''
    if request.method != 'POST':
        return 'Only POST requests are accepted', 405

    try:
        request_json = request.get_json(silent=True)
        if not request_json:
            return 'Invalid JSON', 400

        # Basic validation (can be expanded)
        required_fields = ['title', 'author', 'isbn']
        for field in required_fields:
            if field not in request_json or not request_json[field]:
                return f'Missing required field: {field}', 400

        isbn = request_json['isbn']
        book_ref = db.collection('books').document(isbn)

        # Prepare data for Firestore, adding server timestamps
        book_data = {
            'title': request_json.get('title'),
            'author': request_json.get('author'),
            'isbn': isbn,
            'description': request_json.get('description', ''),
            'publishedDate': request_json.get('publishedDate', ''),
            'coverImageUrl': request_json.get('coverImageUrl', ''),
            'ebookFileUrl': request_json.get('ebookFileUrl', ''),
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }

        book_ref.set(book_data) # Use set() to create or overwrite

        return f'Book with ISBN {isbn} added successfully.', 201

    except Exception as e:
        print(f"Error adding book: {e}")
        return 'Error adding book to Firestore.', 500
