#!/usr/bin/env python
"""
Demo data script for ENL Assist Payment System
This script creates demo users, departments, work logs, and payment data for testing
"""

import os
import sys
import django
from datetime import datetime, date, timedelta
from decimal import Decimal

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ENL_Assist.settings')
django.setup()

from django.contrib.auth import get_user_model
from scheme.models import (
    Department, DepartmentIncharge, StudentDepartmentAssignment, 
    WorkLog, PaymentRate, PaymentRecord, SchemeApplication
)

User = get_user_model()

def create_demo_data():
    print("🚀 Creating demo data for ENL Assist Payment System...")
    
    # 1. Create/Update Payment Rate
    print("\n📊 Setting up payment rate...")
    PaymentRate.objects.all().delete()  # Clear existing rates
    
    # Create EL Coordinator if doesn't exist
    el_coordinator, created = User.objects.get_or_create(
        username='el_coordinator',
        defaults={
            'email': 'el.coordinator@college.edu',
            'first_name': 'Rahul',
            'last_name': 'Sharma',
            'role': 'el_coordinator',
            'is_staff': True
        }
    )
    if created:
        el_coordinator.set_password('admin123')
        el_coordinator.save()
        print(f"   ✅ Created EL Coordinator: {el_coordinator.username}")
    
    # Set payment rate
    payment_rate = PaymentRate.objects.create(
        rate_per_hour=Decimal('50.00'),
        set_by=el_coordinator,
        notes="Initial rate setup for academic year 2024-25"
    )
    print(f"   ✅ Set payment rate: ₹{payment_rate.rate_per_hour}/hour")
    
    # 2. Create Departments
    print("\n🏢 Creating departments...")
    departments_data = [
        {'name': 'Computer Science', 'code': 'CS'},
        {'name': 'Electronics', 'code': 'EXTC'},
        {'name': 'Mechanical', 'code': 'MECH'},
        {'name': 'Information Technology', 'code': 'IT'},
    ]
    
    departments = {}
    for dept_data in departments_data:
        # Try to get existing department first
        try:
            dept = Department.objects.get(code=dept_data['code'])
            print(f"   ✅ Found existing: {dept.name} ({dept.code})")
        except Department.DoesNotExist:
            try:
                dept = Department.objects.get(name=dept_data['name'])
                print(f"   ✅ Found existing: {dept.name} ({dept.code})")
            except Department.DoesNotExist:
                dept = Department.objects.create(
                    name=dept_data['name'],
                    code=dept_data['code']
                )
                print(f"   ✅ Created: {dept.name} ({dept.code})")
        
        departments[dept_data['code']] = dept
    
    # 3. Create Department Incharges
    print("\n👨‍💼 Creating department incharges...")
    incharge_data = [
        {'username': 'cs_incharge', 'first_name': 'Dr. Amit', 'last_name': 'Patel', 'dept': 'CS'},
        {'username': 'extc_incharge', 'first_name': 'Dr. Priya', 'last_name': 'Singh', 'dept': 'EXTC'},
        {'username': 'mech_incharge', 'first_name': 'Dr. Raj', 'last_name': 'Kumar', 'dept': 'MECH'},
        {'username': 'it_incharge', 'first_name': 'Dr. Sunita', 'last_name': 'Gupta', 'dept': 'IT'},
    ]
    
    for incharge_info in incharge_data:
        user, created = User.objects.get_or_create(
            username=incharge_info['username'],
            defaults={
                'email': f"{incharge_info['username']}@college.edu",
                'first_name': incharge_info['first_name'],
                'last_name': incharge_info['last_name'],
                'role': 'department_encharge',
                'is_staff': True
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
        
        dept_incharge, created = DepartmentIncharge.objects.get_or_create(
            user=user,
            department=departments[incharge_info['dept']]
        )
        status = "Created" if created else "Exists"
        print(f"   ✅ {status}: {user.first_name} {user.last_name} -> {departments[incharge_info['dept']].name}")
    
    # 4. Create Scheme Applications for students and approve some of them
    print("\n📋 Creating scheme applications...")
    
    approved_students = []
    scheme_applications_created = 0
    
    for student_username, student_user in students.items():
        # Create scheme application for each student
        from scheme.models import SchemeApplication
        
        app, created = SchemeApplication.objects.get_or_create(
            student=student_user,
            defaults={
                'first_name': student_user.first_name,
                'last_name': student_user.last_name,
                'address': f"123 Main Street, {student_user.first_name}'s City, State - 123456",
                'state': 'Maharashtra',
                'dob': '2000-01-01',
                'annual_income': 250000,
                'fathers_occupation': 'Service',
                'caste_category': 'General',
                'college_name': 'Government Engineering College',
                'department': student_user.studentdepartmentassignment_set.first().department.name if student_user.studentdepartmentassignment_set.exists() else 'Computer Science',
                'prn_number': f'2024{student_username.upper()}001',
                'status': 'Pending'
            }
        )
        
        if created:
            scheme_applications_created += 1
        
        # Approve applications for first 6 students (to test approved vs non-approved scenarios)
        if student_username in ['student1', 'student2', 'student3', 'student4', 'student5', 'student6']:
            app.status = 'Approved'
            app.save()
            approved_students.append(student_user)
            print(f"   ✅ Approved: {student_user.first_name} {student_user.last_name}")
        else:
            # Keep remaining students in different statuses for testing
            if student_username == 'student7':
                app.status = 'Pending'
            else:  # student8
                app.status = 'Correction Required'
            app.save()
            print(f"   📋 Created ({app.status}): {student_user.first_name} {student_user.last_name}")
    
    print(f"   ✅ Created {scheme_applications_created} scheme applications")
    print(f"   ✅ Approved {len(approved_students)} students for scheme benefits")
    
    # Update user registration status for approved students
    for student in approved_students:
        student.is_registered = True
        student.save()
    print("\n👨‍🎓 Creating students...")
    students_data = [
        {'username': 'student1', 'first_name': 'Aarav', 'last_name': 'Patel', 'dept': 'CS'},
        {'username': 'student2', 'first_name': 'Diya', 'last_name': 'Shah', 'dept': 'CS'},
        {'username': 'student3', 'first_name': 'Arjun', 'last_name': 'Kumar', 'dept': 'EXTC'},
        {'username': 'student4', 'first_name': 'Kavya', 'last_name': 'Sharma', 'dept': 'EXTC'},
        {'username': 'student5', 'first_name': 'Rohan', 'last_name': 'Singh', 'dept': 'MECH'},
        {'username': 'student6', 'first_name': 'Ananya', 'last_name': 'Gupta', 'dept': 'IT'},
        {'username': 'student7', 'first_name': 'Vikram', 'last_name': 'Joshi', 'dept': 'IT'},
        {'username': 'student8', 'first_name': 'Ishita', 'last_name': 'Desai', 'dept': 'CS'},
    ]
    
    students = {}
    for student_info in students_data:
        user, created = User.objects.get_or_create(
            username=student_info['username'],
            defaults={
                'email': f"{student_info['username']}@student.college.edu",
                'first_name': student_info['first_name'],
                'last_name': student_info['last_name'],
                'role': 'student'
            }
        )
        if created:
            user.set_password('student123')
            user.save()
        
        # Assign student to department
        assignment, created = StudentDepartmentAssignment.objects.get_or_create(
            student=user,
            department=departments[student_info['dept']]
        )
        
        students[student_info['username']] = user
        status = "Created" if created else "Exists"
        print(f"   ✅ {status}: {user.first_name} {user.last_name} -> {departments[student_info['dept']].name}")
    
    # 5. Create Work Logs (current date only due to model constraints)
    print("\n📝 Creating sample work logs...")
    
    # Clear existing work logs for demo
    print("   🧹 Clearing existing work logs...")
    WorkLog.objects.all().delete()
    
    work_descriptions = [
        "Library maintenance and organization",
        "Computer lab assistance", 
        "Student registration support",
        "Event setup and coordination",
        "Administrative data entry",
        "Campus cleaning and maintenance",
        "Teaching assistance",
        "Laboratory equipment maintenance"
    ]
    
    total_logs_created = 0
    
    # Create work logs only for approved students
    for student_user in approved_students:
        import random
        hours = random.choice([3, 4, 5, 6, 7, 8])
        description = random.choice(work_descriptions)
        
        work_log = WorkLog.objects.create(
            student=student_user,
            hours_worked=hours,
            description=description,
            is_verified=True
        )
        total_logs_created += 1
    
    print(f"   ✅ Created {total_logs_created} work logs for approved students only")
    
    print("   📝 Note: Only students with approved scheme applications can create work logs.")
    print("       Students without approved applications will see scheme approval required page.")
    
    # 6. Calculate Payment Records (only for approved students with work logs)
    print("\n💰 Calculating payment records...")
    
    payment_records_created = 0
    
    # Since all work logs are from today, we'll create payment records for current month
    today = date.today()
    current_year = today.year
    current_month = today.month
    
    for student_user in approved_students:
        try:
            payment_record = PaymentRecord.calculate_for_student_month(
                student_user, current_year, current_month
            )
            if payment_record:
                payment_records_created += 1
        except Exception as e:
            print(f"   ⚠️  Error calculating payment for {student_user.username}: {e}")
    
    print(f"   ✅ Created {payment_records_created} payment records for approved students")
    
    # 7. Create some approved and paid records
    print("\n✅ Updating payment statuses...")
    
    # Mark some payments as approved/paid
    recent_payments = PaymentRecord.objects.all()[:10]
    for i, payment in enumerate(recent_payments):
        if i < 5:
            payment.status = 'approved'
            payment.approved_by = el_coordinator
        elif i < 8:
            payment.status = 'paid'
            payment.approved_by = el_coordinator
            payment.payment_date = payment.payment_month + timedelta(days=25)
            payment.payment_reference = f"PAY{payment.id:04d}"
        payment.save()
    
    print(f"   ✅ Updated status for {len(recent_payments)} payment records")
    
    # 8. Display Summary
    print("\n" + "="*60)
    print("📊 DEMO DATA SUMMARY")
    print("="*60)
    print(f"💰 Payment Rate: ₹{PaymentRate.get_current_rate().rate_per_hour}/hour")
    print(f"🏢 Departments: {Department.objects.count()}")
    print(f"👨‍💼 Department Incharges: {DepartmentIncharge.objects.count()}")
    print(f"👨‍🎓 Students: {User.objects.filter(role='student').count()}")
    print(f"� Scheme Applications: {SchemeApplication.objects.count()}")
    print(f"   - Approved: {SchemeApplication.objects.filter(status='Approved').count()}")
    print(f"   - Pending: {SchemeApplication.objects.filter(status='Pending').count()}")
    print(f"   - Correction Required: {SchemeApplication.objects.filter(status='Correction Required').count()}")
    print(f"�📝 Work Logs: {WorkLog.objects.count()} (only for approved students)")
    print(f"💳 Payment Records: {PaymentRecord.objects.count()} (only for approved students)")
    
    # Payment status breakdown
    for status, label in PaymentRecord.PAYMENT_STATUS_CHOICES:
        count = PaymentRecord.objects.filter(status=status).count()
        if count > 0:
            print(f"   - {label}: {count}")
    
    print("\n🎯 TEST CREDENTIALS:")
    print("   EL Coordinator: el_coordinator / admin123")
    print("   Dept Incharge: cs_incharge / admin123 (also extc_incharge, mech_incharge, it_incharge)")
    print("   Approved Students: student1-6 / student123 (can access work logs & payments)")
    print("   Non-Approved Students: student7-8 / student123 (will see scheme approval required)")
    
    print("\n🔒 AUTHORIZATION TESTING:")
    print("   ✅ Students 1-6: Approved scheme applications - can create work logs and view payments")
    print("   ❌ Student 7: Pending application - will be redirected to scheme approval page")
    print("   ❌ Student 8: Correction required - will be redirected to scheme approval page")
    
    print("\n✅ Demo data creation completed successfully!")
    print("🌐 Start the server with: python manage.py runserver")
    print("🔗 Visit: http://127.0.0.1:8000/")

if __name__ == "__main__":
    create_demo_data()
