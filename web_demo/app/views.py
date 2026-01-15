"""
Django views for the web demo using the custom RDBMS.

This module demonstrates how to use the custom RDBMS instead of Django ORM.
It implements a simple todo management system with CRUD operations.
"""

import json
import sys
import os
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings

# Add the RDBMS path to Python path
sys.path.insert(0, settings.RDBMS_PATH)

from rdbms.engine.database import Database
from rdbms.engine.executor import ExecutionEngine
from rdbms.storage.memory_store import MemoryStore


# Global database instance (in production, this would be managed differently)
_database = None
_executor = None


def get_database():
    """Get or create the database instance."""
    global _database, _executor
    
    if _database is None:
        # Initialize database with persistence
        _database = Database("web_demo")
        _executor = ExecutionEngine(_database)
        
        # Create tables if they don't exist
        _initialize_tables()
    
    return _database, _executor


def _initialize_tables():
    """Initialize the database tables for the demo."""
    database, executor = get_database()
    
    # Create users table
    create_users_sql = """
    CREATE TABLE users (
        id INT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(255) UNIQUE,
        active BOOLEAN DEFAULT TRUE
    )
    """
    
    # Create todos table
    create_todos_sql = """
    CREATE TABLE todos (
        id INT PRIMARY KEY,
        user_id INT NOT NULL,
        title VARCHAR(200) NOT NULL,
        completed BOOLEAN DEFAULT FALSE,
        created_at VARCHAR(50)
    )
    """
    
    # Execute table creation (ignore if tables already exist)
    try:
        executor.execute_sql(create_users_sql)
    except:
        pass  # Table likely already exists
    
    try:
        executor.execute_sql(create_todos_sql)
    except:
        pass  # Table likely already exists
    
    # Add some sample data if tables are empty
    if database.select_all("users"):
        return  # Data already exists
    
    # Sample users
    sample_users = [
        {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "active": True},
        {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "active": True},
        {"id": 3, "name": "Carol Davis", "email": "carol@example.com", "active": False}
    ]
    
    for user in sample_users:
        database.insert("users", user)
    
    # Sample todos
    sample_todos = [
        {"id": 1, "user_id": 1, "title": "Learn custom RDBMS", "completed": True, "created_at": "2024-01-15"},
        {"id": 2, "user_id": 1, "title": "Build Django demo", "completed": False, "created_at": "2024-01-15"},
        {"id": 3, "user_id": 2, "title": "Write documentation", "completed": False, "created_at": "2024-01-16"},
        {"id": 4, "user_id": 2, "title": "Test all features", "completed": False, "created_at": "2024-01-16"},
        {"id": 5, "user_id": 3, "title": "Review code", "completed": True, "created_at": "2024-01-14"}
    ]
    
    for todo in sample_todos:
        database.insert("todos", todo)


def home(request):
    """
    Home page showing the demo interface.
    
    This view renders a simple HTML page that demonstrates the custom RDBMS
    functionality through a todo management interface.
    """
    return render(request, 'app/index.html')


@csrf_exempt
@require_http_methods(["GET"])
def api_users(request):
    """API endpoint to get all users."""
    try:
        database, _ = get_database()
        users = database.select_all("users")
        
        # Convert to JSON-serializable format
        user_data = [user.to_dict() for user in users]
        
        return JsonResponse({
            "success": True,
            "data": user_data,
            "count": len(user_data)
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_todos(request):
    """API endpoint to get all todos with optional filtering."""
    try:
        database, _ = get_database()
        
        # Get query parameters
        user_id = request.GET.get('user_id')
        completed = request.GET.get('completed')
        
        if user_id:
            todos = database.select_by_column("user_id", int(user_id))
        elif completed is not None:
            todos = database.select_by_column("completed", completed.lower() == 'true')
        else:
            todos = database.select_all("todos")
        
        # Convert to JSON-serializable format
        todo_data = [todo.to_dict() for todo in todos]
        
        return JsonResponse({
            "success": True,
            "data": todo_data,
            "count": len(todo_data)
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_create_user(request):
    """API endpoint to create a new user."""
    try:
        data = json.loads(request.body)
        database, _ = get_database()
        
        # Auto-generate ID
        existing_users = database.select_all("users")
        new_id = max([user.get("id", 0) for user in existing_users] + [0]) + 1
        
        user_data = {
            "id": new_id,
            "name": data.get("name"),
            "email": data.get("email"),
            "active": data.get("active", True)
        }
        
        user = database.insert("users", user_data)
        
        return JsonResponse({
            "success": True,
            "message": "User created successfully",
            "data": user.to_dict()
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_create_todo(request):
    """API endpoint to create a new todo."""
    try:
        data = json.loads(request.body)
        database, _ = get_database()
        
        # Auto-generate ID
        existing_todos = database.select_all("todos")
        new_id = max([todo.get("id", 0) for todo in existing_todos] + [0]) + 1
        
        todo_data = {
            "id": new_id,
            "user_id": data.get("user_id"),
            "title": data.get("title"),
            "completed": data.get("completed", False),
            "created_at": data.get("created_at", "2024-01-15")
        }
        
        todo = database.insert("todos", todo_data)
        
        return JsonResponse({
            "success": True,
            "message": "Todo created successfully",
            "data": todo.to_dict()
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def api_update_todo(request, todo_id):
    """API endpoint to update a todo."""
    try:
        data = json.loads(request.body)
        database, _ = get_database()
        
        # Update the todo
        updated_count = database.update_where(
            "todos",
            lambda row: row.get("id") == int(todo_id),
            data
        )
        
        if updated_count == 0:
            return JsonResponse({
                "success": False,
                "error": "Todo not found"
            }, status=404)
        
        return JsonResponse({
            "success": True,
            "message": "Todo updated successfully",
            "updated_count": updated_count
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def api_delete_todo(request, todo_id):
    """API endpoint to delete a todo."""
    try:
        database, _ = get_database()
        
        # Delete the todo
        deleted_count = database.delete_where(
            "todos",
            lambda row: row.get("id") == int(todo_id)
        )
        
        if deleted_count == 0:
            return JsonResponse({
                "success": False,
                "error": "Todo not found"
            }, status=404)
        
        return JsonResponse({
            "success": True,
            "message": "Todo deleted successfully",
            "deleted_count": deleted_count
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_join_demo(request):
    """API endpoint demonstrating JOIN functionality."""
    try:
        database, _ = get_database()
        
        # Perform inner join between users and todos
        joined_data = database.join_inner(
            "users",
            "todos", 
            "id",
            "user_id"
        )
        
        return JsonResponse({
            "success": True,
            "message": f"Joined {len(joined_data)} records",
            "data": joined_data,
            "count": len(joined_data)
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_stats(request):
    """API endpoint showing database statistics."""
    try:
        database, _ = get_database()
        
        stats = database.get_database_info()
        
        return JsonResponse({
            "success": True,
            "data": stats
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)
