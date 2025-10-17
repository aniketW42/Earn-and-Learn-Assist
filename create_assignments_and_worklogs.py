#!/usr/bin/env python
"""
Script to assign existing students to departments and create dummy worklogs
"""
import os
import sys
import django
from datetime import date, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ENL_Assist.settings')
django.setup()

from scheme.models import SchemeApplication, WorkLog, Department, StudentDepartmentAssignment
from users.models import User

def create_departments():
    """Create departments if they don't exist"""
    departments_data = [
        {
            'name': 'Computer Engineering',
            'code': 'COMP',
            'description': 'Computer Engineering Department with focus on software development and system design',
            'is_active': True
        },
        {
            'name': 'Information Technology',
            'code': 'IT',
            'description': 'Information Technology Department specializing in IT systems and infrastructure',
            'is_active': True
        },
        {
            'name': 'Electronics & Telecommunication',
            'code': 'ENTC',
            'description': 'Electronics & Telecommunication Department focusing on communication systems',
            'is_active': True
        },
        {
            'name': 'Mechanical Engineering',
            'code': 'MECH',
            'description': 'Mechanical Engineering Department with emphasis on design and manufacturing',
            'is_active': True
        },
        {
            'name': 'Civil Engineering',
            'code': 'CIVIL',
            'description': 'Civil Engineering Department focusing on construction and infrastructure',
            'is_active': True
        }
    ]
    
    created_departments = []
    for dept_data in departments_data:
        department, created = Department.objects.get_or_create(
            code=dept_data['code'],
            defaults=dept_data
        )
        created_departments.append(department)
        if created:
            print(f"✓ Created department: {department.name}")
        else:
            print(f"→ Department already exists: {department.name}")
    
    return created_departments

def assign_students_to_departments():
    """Assign approved students to departments based on their application department"""
    
    # Get all approved students
    approved_applications = SchemeApplication.objects.filter(status='Approved')
    departments = Department.objects.all()
    
    # Create a mapping of department names to Department objects
    dept_mapping = {}
    for dept in departments:
        # Try to match by department name or code
        dept_mapping[dept.name.lower()] = dept
        dept_mapping[dept.code.lower()] = dept
    
    # Add some common variations
    dept_mapping['computer engineering'] = departments.filter(code='COMP').first()
    dept_mapping['computer'] = departments.filter(code='COMP').first()
    dept_mapping['information technology'] = departments.filter(code='IT').first()
    dept_mapping['it'] = departments.filter(code='IT').first()
    dept_mapping['electronics'] = departments.filter(code='ENTC').first()
    dept_mapping['mechanical'] = departments.filter(code='MECH').first()
    dept_mapping['civil'] = departments.filter(code='CIVIL').first()
    
    assigned_count = 0
    
    for application in approved_applications:
        # Check if already assigned
        if StudentDepartmentAssignment.objects.filter(student=application.student).exists():
            print(f"→ {application.first_name} {application.last_name} already assigned")
            continue
        
        # Try to find matching department
        app_dept_lower = application.department.lower()
        assigned_dept = None
        
        # Try exact match first
        if app_dept_lower in dept_mapping:
            assigned_dept = dept_mapping[app_dept_lower]
        else:
            # Try partial matches
            for key, dept in dept_mapping.items():
                if key in app_dept_lower or app_dept_lower in key:
                    assigned_dept = dept
                    break
        
        # If no match found, assign to Computer Engineering as default
        if not assigned_dept:
            assigned_dept = departments.filter(code='COMP').first()
            print(f"⚠ No department match for '{application.department}' - assigning to {assigned_dept.name}")
        
        # Create assignment
        assignment = StudentDepartmentAssignment.objects.create(
            student=application.student,
            department=assigned_dept,
            is_active=True
        )
        
        print(f"✓ Assigned {application.first_name} {application.last_name} to {assigned_dept.name}")
        assigned_count += 1
    
    print(f"\n📊 Total students assigned: {assigned_count}")
    return assigned_count

def create_dummy_worklogs():
    """Create dummy worklogs for approved students"""
    
    # Get all approved students
    approved_applications = SchemeApplication.objects.filter(status='Approved')
    
    # Work descriptions for variety
    work_descriptions = [
        "Assisted in laboratory maintenance and equipment setup",
        "Helped with administrative tasks and file organization",
        "Supported faculty in research activities and data collection",
        "Maintained computer lab systems and software updates",
        "Assisted in library operations and book cataloging",
        "Helped with event organization and student activities",
        "Supported department in documentation and record keeping",
        "Assisted in academic material preparation and printing",
        "Helped with campus maintenance and cleanliness drives",
        "Supported IT department with network maintenance",
        "Assisted in examination duties and invigilation",
        "Helped with student registration and admission processes"
    ]
    
    total_worklogs_created = 0
    
    for application in approved_applications:
        student = application.student
        
        # Check existing worklogs count
        existing_count = WorkLog.objects.filter(student=student).count()
        
        # Create worklogs for the past 45 days
        start_date = date.today() - timedelta(days=45)
        end_date = date.today() - timedelta(days=1)  # Don't create for today
        
        current_date = start_date
        student_worklogs_created = 0
        
        while current_date <= end_date:
            # Randomly decide if student worked on this day (60% chance)
            if random.random() < 0.6:
                # Check if worklog already exists for this date
                if not WorkLog.objects.filter(student=student, date=current_date).exists():
                    try:
                        # Random hours between 2-8
                        hours = random.randint(2, 8)
                        
                        # Random description
                        description = random.choice(work_descriptions)
                        
                        # Create worklog and then update the date
                        worklog = WorkLog.objects.create(
                            student=student,
                            hours_worked=hours,
                            description=description,
                            is_verified=random.choice([True, True, False]),  # 66% chance of being verified
                            is_rejected=False
                        )
                        # Update the date field after creation to bypass auto_now_add
                        WorkLog.objects.filter(id=worklog.id).update(date=current_date)
                        
                        student_worklogs_created += 1
                        total_worklogs_created += 1
                    except Exception as e:
                        print(f"   ⚠ Skipped {current_date} for {student.username}: {str(e)}")
                        pass
            
            current_date += timedelta(days=1)
        
        print(f"✓ Created {student_worklogs_created} worklogs for {application.first_name} {application.last_name} (had {existing_count} existing)")
    
    print(f"\n📈 Total new worklogs created: {total_worklogs_created}")
    return total_worklogs_created

def main():
    print("🚀 Starting data setup...\n")
    
    # Check existing data
    print("📊 Current data status:")
    total_students = User.objects.filter(role='student').count()
    approved_applications = SchemeApplication.objects.filter(status='Approved').count()
    existing_departments = Department.objects.count()
    existing_assignments = StudentDepartmentAssignment.objects.count()
    existing_worklogs = WorkLog.objects.count()
    
    print(f"   Students: {total_students}")
    print(f"   Approved Applications: {approved_applications}")
    print(f"   Departments: {existing_departments}")
    print(f"   Department Assignments: {existing_assignments}")
    print(f"   Work Logs: {existing_worklogs}")
    print()
    
    # Step 1: Create departments
    print("1️⃣ Creating departments...")
    departments = create_departments()
    print()
    
    # Step 2: Assign students to departments
    print("2️⃣ Assigning students to departments...")
    assigned_count = assign_students_to_departments()
    print()
    
    # Step 3: Create dummy worklogs
    print("3️⃣ Creating dummy worklogs...")
    worklogs_created = create_dummy_worklogs()
    print()
    
    # Final summary
    print("✅ Setup completed!")
    print("📊 Final Summary:")
    print(f"   Departments: {Department.objects.count()}")
    print(f"   Student assignments: {StudentDepartmentAssignment.objects.count()}")
    print(f"   Total worklogs: {WorkLog.objects.count()}")
    print(f"   Verified worklogs: {WorkLog.objects.filter(is_verified=True).count()}")
    print()
    print("🎉 All done! Students are now assigned to departments with dummy worklogs.")

if __name__ == "__main__":
    main()
