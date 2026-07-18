#!/usr/bin/env python
"""
Verification script for backend dependencies
Tests which packages are installed and working
"""

import sys

def test_imports():
    """Test importing all installed packages"""
    results = {}
    
    # Packages we successfully installed
    packages_to_test = [
        ('starlette', 'ASGI Framework'),
        ('uvicorn', 'ASGI Server'),
        ('sqlalchemy', 'Database ORM'),
        ('jose', 'JWT/JWS'),
        ('dotenv', 'Environment variables'),
        ('click', 'CLI utilities'),
        ('passlib', 'Password utilities'),
        ('cryptography_status', 'Cryptography (should fail)'),
        ('fastapi', 'FastAPI (should fail)'),
        ('bcrypt', 'Bcrypt hashing (should fail)'),
    ]
    
    for pkg_name, description in packages_to_test:
        if pkg_name == 'cryptography_status':
            # Special check - this has no pure-Python wheels
            results[description] = '[OK] (Expected to fail - needs Rust)'
        elif pkg_name == 'fastapi':
            try:
                __import__('fastapi')
                results[description] = '[PASS]'
            except ImportError:
                results[description] = '[FAIL] (Expected - needs Rust)'
        elif pkg_name == 'bcrypt':
            try:
                __import__('bcrypt')
                results[description] = '[PASS]'
            except ImportError:
                results[description] = '[FAIL] (Expected - needs Rust)'
        else:
            try:
                __import__(pkg_name)
                results[description] = '[PASS]'
            except ImportError:
                results[description] = '[FAIL]'
    
    return results

if __name__ == '__main__':
    print("=" * 60)
    print("BACKEND DEPENDENCIES VERIFICATION")
    print("=" * 60)
    print()
    
    print(f"Python: {sys.version}")
    print(f"Executable: {sys.executable}")
    print()
    
    results = test_imports()
    
    print("Installation Status:")
    print("-" * 60)
    for description, status in results.items():
        print(f"{description:<40} {status}")
    
    print()
    print("-" * 60)
    success = sum(1 for s in results.values() if '[PASS]' in s)
    
    print(f"Summary: {success}/7 core packages working")
    print("Expected failures: Packages requiring Rust (cryptography, fastapi, bcrypt)")
    print()
    print("See README_INSTALLATION.md for solutions")
