#!/usr/bin/env python3
"""
Test script to validate the workflow components locally.
"""

import os
import sys
import subprocess

def run_test(name, command, expected_exit_code=0):
    """Run a test command and check the result."""
    print(f"\n🧪 Testing: {name}")
    print(f"   Command: {command}")

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode == expected_exit_code:
            print(f"   ✅ PASSED (exit code: {result.returncode})")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ FAILED (expected: {expected_exit_code}, got: {result.returncode})")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"   ❌ FAILED with exception: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 Awesome Ford Transit Workflow Component Tests")
    print("=" * 60)

    # Change to the repository root
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(repo_root)
    print(f"📁 Working directory: {os.getcwd()}")

    # Check that all required files exist
    required_files = [
        '.github/ISSUE_TEMPLATE/new-awesome-ford-transit-resource.md',
        '.github/workflows/process-new-resource.yml',
        '.github/workflows/create-resource-pr.yml',
        '.github/scripts/validate_url.py',
        '.github/scripts/check_duplicates.py',
        '.github/scripts/format_entry.py',
        'README.md'
    ]

    print("\n📋 Checking required files:")
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - NOT FOUND")
            all_exist = False

    if not all_exist:
        print("\n❌ Some required files are missing!")
        return 1

    # Test the Python scripts
    tests_passed = []

    # Test URL validation
    print("\n" + "=" * 40)
    print("📝 Testing URL Validation Script")
    print("=" * 40)

    # Test with a valid URL
    tests_passed.append(
        run_test(
            "Valid URL (Ford.com)",
            "python3 .github/scripts/validate_url.py https://www.ford.com",
            expected_exit_code=0
        )
    )

    # Test with an invalid URL
    tests_passed.append(
        run_test(
            "Invalid URL",
            "python3 .github/scripts/validate_url.py not-a-url",
            expected_exit_code=1
        )
    )

    # Test duplicate checking
    print("\n" + "=" * 40)
    print("📝 Testing Duplicate Check Script")
    print("=" * 40)

    # Test with a URL that's likely in the README
    tests_passed.append(
        run_test(
            "Check known duplicate",
            "python3 .github/scripts/check_duplicates.py https://www.ford.com/",
            expected_exit_code=1  # Should fail if duplicate
        )
    )

    # Test with a unique URL
    tests_passed.append(
        run_test(
            "Check unique URL",
            "python3 .github/scripts/check_duplicates.py https://example-unique-transit-site-2024.com",
            expected_exit_code=0
        )
    )

    # Test formatting
    print("\n" + "=" * 40)
    print("📝 Testing Format Entry Script")
    print("=" * 40)

    tests_passed.append(
        run_test(
            "Format an entry",
            'python3 .github/scripts/format_entry.py --url "https://example.com" --description "Test products for Transit vans" --category "Suppliers"',
            expected_exit_code=0
        )
    )

    # Validate YAML files
    print("\n" + "=" * 40)
    print("📝 Validating YAML Syntax")
    print("=" * 40)

    yaml_files = [
        '.github/workflows/process-new-resource.yml',
        '.github/workflows/create-resource-pr.yml'
    ]

    for yaml_file in yaml_files:
        tests_passed.append(
            run_test(
                f"Validate {yaml_file}",
                f"python3 -c \"import yaml; yaml.safe_load(open('{yaml_file}'))\"",
                expected_exit_code=0
            )
        )

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    total_tests = len(tests_passed)
    passed_tests = sum(tests_passed)

    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")

    if passed_tests == total_tests:
        print("\n✅ All tests passed! The workflow is ready to use.")
        print("\n📌 Next steps:")
        print("1. Commit these changes to a new branch")
        print("2. Push to GitHub")
        print("3. Create a test issue to verify the workflow")
        print("4. Monitor GitHub Actions for any issues")
        return 0
    else:
        print(f"\n❌ {total_tests - passed_tests} test(s) failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())