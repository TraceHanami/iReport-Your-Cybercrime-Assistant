from flask import Blueprint, request, jsonify
from database.connection import db
from database.models import ChatbotSession, ChatbotMessage, User, Complaint
from auth.models import Auth
import uuid
from datetime import datetime
import re

chatbot_bp = Blueprint('chatbot', __name__)

def get_user_from_token():
    """Extract user from authorization token"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    user_id, role = Auth.decode_token(token)
    return User.query.get(user_id) if user_id else None

@chatbot_bp.route('/start-session', methods=['POST'])
def start_chat_session():
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({"error": "Authentication required"}), 401
        
        # Create new chat session
        session_id = str(uuid.uuid4())
        
        session = ChatbotSession(
            user_id=user.id,
            session_id=session_id,
            language=user.language or 'en'
        )
        
        db.session.add(session)
        db.session.commit()
        
        # Add welcome message
        welcome_message = ChatbotMessage(
            session_id=session.id,
            message_type='bot',
            content=get_welcome_message(user.language or 'en')
        )
        
        db.session.add(welcome_message)
        db.session.commit()
        
        return jsonify({
            "session_id": session_id,
            "welcome_message": welcome_message.content,
            "session_created": session.created_at.isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@chatbot_bp.route('/send-message', methods=['POST'])
def send_message():
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({"error": "Authentication required"}), 401
        
        data = request.get_json()
        
        if 'session_id' not in data or 'message' not in data:
            return jsonify({"error": "Session ID and message are required"}), 400
        
        # Validate message length
        if len(data['message'].strip()) == 0:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        if len(data['message']) > 1000:
            return jsonify({"error": "Message too long. Maximum 1000 characters allowed."}), 400
        
        # Find session
        session = ChatbotSession.query.filter_by(
            session_id=data['session_id'],
            user_id=user.id
        ).first()
        
        if not session:
            return jsonify({"error": "Session not found"}), 404
        
        # Save user message
        user_message = ChatbotMessage(
            session_id=session.id,
            message_type='user',
            content=data['message'].strip()
        )
        
        db.session.add(user_message)
        
        # Generate bot response with context
        bot_response = generate_bot_response(
            data['message'], 
            user.language or 'en',
            user,
            session.id
        )
        
        # Save bot response
        bot_message = ChatbotMessage(
            session_id=session.id,
            message_type='bot',
            content=bot_response
        )
        
        db.session.add(bot_message)
        
        # Update session timestamp
        session.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "response": bot_response,
            "timestamp": datetime.utcnow().isoformat(),
            "message_id": bot_message.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@chatbot_bp.route('/session-history/<session_id>', methods=['GET'])
def get_session_history(session_id):
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({"error": "Authentication required"}), 401
        
        session = ChatbotSession.query.filter_by(
            session_id=session_id,
            user_id=user.id
        ).first()
        
        if not session:
            return jsonify({"error": "Session not found"}), 404
        
        messages = ChatbotMessage.query.filter_by(
            session_id=session.id
        ).order_by(ChatbotMessage.timestamp.asc()).all()
        
        messages_data = []
        for message in messages:
            messages_data.append({
                "id": message.id,
                "type": message.message_type,
                "content": message.content,
                "timestamp": message.timestamp.isoformat() if message.timestamp else None
            })
        
        return jsonify({
            "session_id": session_id,
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "messages": messages_data,
            "total_messages": len(messages_data)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chatbot_bp.route('/user-sessions', methods=['GET'])
def get_user_sessions():
    """Get all chat sessions for the current user"""
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({"error": "Authentication required"}), 401
        
        sessions = ChatbotSession.query.filter_by(
            user_id=user.id
        ).order_by(ChatbotSession.updated_at.desc()).all()
        
        sessions_data = []
        for session in sessions:
            # Get last message for preview
            last_message = ChatbotMessage.query.filter_by(
                session_id=session.id
            ).order_by(ChatbotMessage.timestamp.desc()).first()
            
            sessions_data.append({
                "session_id": session.session_id,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "updated_at": session.updated_at.isoformat() if session.updated_at else None,
                "message_count": ChatbotMessage.query.filter_by(session_id=session.id).count(),
                "last_message": last_message.content if last_message else None,
                "language": session.language
            })
        
        return jsonify({
            "sessions": sessions_data,
            "total_sessions": len(sessions_data)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chatbot_bp.route('/delete-session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a chat session"""
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({"error": "Authentication required"}), 401
        
        session = ChatbotSession.query.filter_by(
            session_id=session_id,
            user_id=user.id
        ).first()
        
        if not session:
            return jsonify({"error": "Session not found"}), 404
        
        # Delete all messages in the session
        ChatbotMessage.query.filter_by(session_id=session.id).delete()
        
        # Delete the session
        db.session.delete(session)
        db.session.commit()
        
        return jsonify({
            "message": "Session deleted successfully",
            "session_id": session_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def get_welcome_message(language='en'):
    """Get welcome message in specified language"""
    welcome_messages = {
        'en': "Hello! I'm the iReport assistant. How can I help you today? You can ask about filing complaints, tracking cases, emergency contacts, or general information.",
        'hi': "नमस्ते! मैं iReport सहायक हूं। आज मैं आपकी कैसे मदद कर सकता हूं? आप शिकायत दर्ज करने, मामलों को ट्रैक करने, आपातकालीन संपर्क या सामान्य जानकारी के बारे में पूछ सकते हैं।",
        'ta': "வணக்கம்! நான் iReport உதவியாளன். இன்று நான் உங்களுக்கு எவ்வாறு உதவ முடியும்? புகார்களை தாக்கல் செய்வது, வழக்குகளை கண்காணிப்பது, அவசர தொடர்புகள் அல்லது பொதுவான தகவல்கள் பற்றி நீங்கள் கேட்கலாம்.",
        'te': "హలో! నేను iReport సహాయకుడిని. ఈరోజు నేను మీకు ఎలా సహాయం చేయగలను? మీరు ఫిర్యాదులు దాఖలు చేయడం, కేసులను ట్రాక్ చేయడం, అత్యవసర సంప్రదింపులు లేదా సాధారణ సమాచారం గురించి అడగవచ్చు.",
        'bn': "হ্যালো! আমি iReport সহায়ক। আজ আমি আপনাকে কীভাবে সাহায্য করতে পারি? আপনি অভিযোগ দায়ের, মামলা ট্র্যাক করা, জরুরি যোগাযোগ বা সাধারণ তথ্য সম্পর্কে জিজ্ঞাসা করতে পারেন।",
        'ml': "ഹലോ! ഞാൻ iReport അസിസ്റ്റന്റാണ്. ഇന്ന് ഞാൻ നിങ്ങളെ എങ്ങനെ സഹായിക്കാനാകും? പരാതികൾ ഫയൽ ചെയ്യുന്നതിനെക്കുറിച്ചോ, കേസുകൾ ട്രാക്കുചെയ്യുന്നതിനെക്കുറിച്ചോ, അടിയന്തര കോൺ‌ടാക്റ്റുകളെക്കുറിച്ചോ അല്ലെങ്കിൽ പൊതുവായ വിവരങ്ങളെക്കുറിച്ചോ നിങ്ങൾക്ക് ചോദിക്കാം."
    }
    
    return welcome_messages.get(language, welcome_messages['en'])

def generate_bot_response(user_message, language='en', user=None, session_id=None):
    """Generate bot response based on user message with context awareness"""
    user_message_lower = user_message.lower().strip()
    
    # Enhanced responses with more context
    responses = {
        'en': {
            'greeting': "Hello! How can I assist you with iReport today?",
            'complaint': "To file a complaint, go to the 'File Complaint' section and fill out the required details. You'll need information about the incident, location, date, and involved parties. You can also attach evidence if available.",
            'track': "You can track your complaint using the case ID provided when you filed it. Go to 'Track Case' and enter your case ID. I can also help you check status if you provide your case ID.",
            'status': "Case status can be checked in the 'Track Case' section. You'll see updates from the assigned officer there. Common statuses include: Pending, Assigned, In Progress, and Resolved.",
            'volunteer': "To become a volunteer, sign up with your details and qualifications. After verification, you can help with cases in your area. Volunteers assist with documentation, follow-ups, and community support.",
            'emergency': "For emergencies requiring immediate police assistance, please call 100. For fire services, call 101. For medical emergencies, call 102 or 108.",
            'help': "I can help you with: filing complaints, tracking cases, volunteer information, emergency contacts, and general guidance. What specific help do you need?",
            'case_id_query': "I found a case ID in your message. Let me check the status for you...",
            'no_case_found': "I couldn't find any active cases associated with your account. You can file a new complaint in the 'File Complaint' section.",
            'multiple_cases': "I found multiple cases in your account. Please specify which case you're asking about, or visit the 'My Cases' section for detailed information.",
            'default': "I understand you're asking about something related to '{}'. For more specific assistance, please provide more details or visit the relevant section in the app. You can also contact our support team for personalized help."
        },
        'hi': {
            'greeting': "नमस्ते! आज iReport के साथ मैं आपकी कैसे सहायता कर सकता हूं?",
            'complaint': "शिकायत दर्ज करने के लिए, 'शिकायत दर्ज करें' अनुभाग पर जाएं और आवश्यक विवरण भरें। आपको घटना, स्थान, तारीख और शामिल पक्षों के बारे में जानकारी की आवश्यकता होगी। यदि उपलब्ध हो तो आप सबूत भी संलग्न कर सकते हैं।",
            'track': "आप अपनी शिकायत को केस आईडी का उपयोग करके ट्रैक कर सकते हैं जो आपको दर्ज करते समय प्रदान की गई थी। 'केस ट्रैक करें' पर जाएं और अपनी केस आईडी दर्ज करें। यदि आप अपनी केस आईडी प्रदान करते हैं तो मैं आपको स्थिति जांचने में भी मदद कर सकता हूं।",
            'status': "केस की स्थिति 'केस ट्रैक करें' अनुभाग में जांची जा सकती है। आपको वहां नियुक्त अधिकारी से अपडेट दिखाई देंगे। सामान्य स्थितियों में शामिल हैं: लंबित, नियुक्त, प्रगति पर, और हल।",
            'volunteer': "स्वयंसेवक बनने के लिए, अपने विवरण और योग्यताओं के साथ साइन अप करें। सत्यापन के बाद, आप अपने क्षेत्र में मामलों में मदद कर सकते हैं। स्वयंसेवक दस्तावेज़ीकरण, फॉलो-अप और सामुदायिक समर्थन में सहायता करते हैं।",
            'emergency': "तत्काल पुलिस सहायता की आवश्यकता वाली आपात स्थितियों के लिए, कृपया 100 पर कॉल करें। अग्निशमन सेवाओं के लिए, 101 पर कॉल करें। चिकित्सा आपात स्थितियों के लिए, 102 या 108 पर कॉल करें।",
            'help': "मैं आपकी मदद कर सकता हूं: शिकायतें दर्ज करना, मामलों को ट्रैक करना, स्वयंसेवक जानकारी, आपातकालीन संपर्क, और सामान्य मार्गदर्शन। आपको किस विशिष्ट सहायता की आवश्यकता है?",
            'default': "मैं समझता हूं कि आप '{}' के बारे में पूछ रहे हैं। अधिक विशिष्ट सहायता के लिए, कृपया अधिक विवरण प्रदान करें या ऐप में संबंधित अनुभाग पर जाएं। व्यक्तिगत सहायता के लिए आप हमारी सहायता टीम से भी संपर्क कर सकते हैं।"
        }
    }
    
    # Add more language responses as needed
    lang_responses = responses.get(language, responses['en'])
    
    # Check for case ID in message
    case_id = extract_case_id(user_message)
    if case_id and user:
        case_status = get_case_status(case_id, user.id)
        if case_status:
            return case_status
    
    # Check user's cases if they're asking about status generally
    if any(word in user_message_lower for word in ['my case', 'my cases', 'my complaint', 'my complaints']) and user:
        user_cases = get_user_cases(user.id)
        if user_cases:
            return user_cases
        else:
            return lang_responses.get('no_case_found', "No cases found for your account.")
    
    # Keyword matching with enhanced patterns
    if any(word in user_message_lower for word in ['hello', 'hi', 'hey', 'namaste', 'hola']):
        return lang_responses['greeting']
    elif any(word in user_message_lower for word in ['complaint', 'file', 'report', 'fir', 'शिकायत', 'புகார்']):
        return lang_responses['complaint']
    elif any(word in user_message_lower for word in ['track', 'status', 'update', 'progress', 'स्थिति', 'நிலை']):
        return lang_responses['track']
    elif any(word in user_message_lower for word in ['volunteer', 'help others', 'support', 'स्वयंसेवक', 'தன்னார்வலர்']):
        return lang_responses['volunteer']
    elif any(word in user_message_lower for word in ['emergency', 'urgent', 'immediate', 'आपातकाल', 'அவசர']):
        return lang_responses['emergency']
    elif any(word in user_message_lower for word in ['help', 'support', 'guide', 'सहायता', 'உதவி']):
        return lang_responses['help']
    else:
        return lang_responses['default'].format(user_message)

def extract_case_id(message):
    """Extract case ID from message using regex patterns"""
    # Pattern for iReport case IDs (e.g., IR20231201ABC12345)
    patterns = [
        r'IR\d{8}[A-Z0-9]{6,8}',  # Standard format
        r'CASE[-_][A-Z0-9]{6,12}',  # Alternative formats
        r'\b[A-Z]{2}\d{10,12}\b'   # Generic case ID pattern
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, message.upper())
        if matches:
            return matches[0]
    
    return None

def get_case_status(case_id, user_id):
    """Get status of a specific case"""
    try:
        complaint = Complaint.query.filter_by(
            case_id=case_id,
            user_id=user_id
        ).first()
        
        if complaint:
            status_messages = {
                'en': f"Case {case_id} is currently '{complaint.status}'. " +
                     f"Priority: {complaint.priority}. " +
                     f"Last updated: {complaint.updated_at.strftime('%Y-%m-%d') if complaint.updated_at else 'N/A'}.",
                'hi': f"केस {case_id} वर्तमान में '{complaint.status}' स्थिति में है। " +
                     f"प्राथमिकता: {complaint.priority}. " +
                     f"अंतिम अद्यतन: {complaint.updated_at.strftime('%Y-%m-%d') if complaint.updated_at else 'N/A'}."
            }
            
            # Default to English if language-specific message not available
            return status_messages.get('en')
        else:
            return f"Case {case_id} not found or you don't have permission to view it."
            
    except Exception as e:
        return f"Error retrieving case status: {str(e)}"

def get_user_cases(user_id):
    """Get summary of user's cases"""
    try:
        cases = Complaint.query.filter_by(user_id=user_id).order_by(
            Complaint.created_at.desc()
        ).limit(5).all()
        
        if not cases:
            return None
        
        case_summary = "Your recent cases:\n"
        for case in cases:
            case_summary += f"- {case.case_id}: {case.status} ({case.created_at.strftime('%Y-%m-%d')})\n"
        
        case_summary += "\nVisit 'My Cases' for detailed information."
        return case_summary
        
    except Exception as e:
        return f"Error retrieving your cases: {str(e)}"