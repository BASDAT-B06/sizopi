from django.db import connection

def dictfetchall(cursor):
    """Helper untuk ambil hasil cursor sebagai list of dict"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_user_context(request):
    """Helper untuk mendapatkan context user dari session"""
    user = request.session.get("user", {})
    is_authenticated = request.session.get("is_authenticated", False)
    
    return {
        "is_logged_in": is_authenticated,
        "user_role": user.get("role", ""),
        "is_adopter": user.get("is_adopter", False),
        "username": user.get("username", ""),
    }
