"""
A minimal test API blueprint to verify blueprint registration.
"""
from flask import Blueprint, jsonify
import sys

print("\n=== Loading TEST API routes module ===", file=sys.stderr)

try:
    # Create a very simple blueprint
    test_bp = Blueprint('test_api', __name__)
    print(f"✓ Created TEST API blueprint: {test_bp}", file=sys.stderr)
    
    @test_bp.route('/ping')
    def ping():
        print("Ping route called", file=sys.stderr)
        return jsonify({
            'status': 'success',
            'message': 'pong',
            'blueprint': test_bp.name
        })
        
    print("✓ Added ping route to TEST API blueprint", file=sys.stderr)
    
except Exception as e:
    print(f"✗ Error in TEST API blueprint: {str(e)}", file=sys.stderr)
    raise
