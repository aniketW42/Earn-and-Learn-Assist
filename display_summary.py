#!/usr/bin/env python
"""
Simple script to display student assignments and worklog summary
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ENL_Assist.settings')
django.setup()

from scheme.models import SchemeApplication, WorkLog, Department, StudentDepartmentAssignment
from django.db.models import Sum

def display_summary():
    print("🎯 ENL ASSIST - STUDENT ASSIGNMENTS & WORKLOG SUMMARY")
    print("=" * 60)
    
    # Department Overview
    print("\n📚 DEPARTMENTS:")
    for dept in Department.objects.filter(is_active=True).order_by('name'):
        assigned_count = StudentDepartmentAssignment.objects.filter(department=dept).count()
        print(f"   • {dept.name} ({dept.code}) - {assigned_count} students assigned")
    
    print(f"\n👥 STUDENT ASSIGNMENTS ({StudentDepartmentAssignment.objects.count()} total):")
    print("-" * 60)
    
    for assignment in StudentDepartmentAssignment.objects.select_related('student', 'department').order_by('department__name'):
        student = assignment.student
        
        # Get student's application for name
        try:
            app = SchemeApplication.objects.get(student=student)
            student_name = f"{app.first_name} {app.last_name}"
        except:
            student_name = student.username
        
        # Calculate worklog statistics
        total_logs = WorkLog.objects.filter(student=student).count()
        total_hours = WorkLog.objects.filter(student=student).aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0
        verified_hours = WorkLog.objects.filter(student=student, is_verified=True).aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0
        pending_hours = total_hours - verified_hours
        
        print(f"🎓 {student_name}")
        print(f"   └─ Department: {assignment.department.name}")
        print(f"   └─ Work Logs: {total_logs} entries | {total_hours}h total | {verified_hours}h verified | {pending_hours}h pending")
        print()
    
    # Overall Statistics
    total_hours_all = WorkLog.objects.aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0
    verified_hours_all = WorkLog.objects.filter(is_verified=True).aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0
    
    print("📊 OVERALL STATISTICS:")
    print(f"   • Total Work Logs: {WorkLog.objects.count()}")
    print(f"   • Total Hours Logged: {total_hours_all}")
    print(f"   • Verified Hours: {verified_hours_all}")
    print(f"   • Pending Verification: {total_hours_all - verified_hours_all} hours")
    print(f"   • Verification Rate: {(verified_hours_all/total_hours_all*100):.1f}%" if total_hours_all > 0 else "   • Verification Rate: 0%")

if __name__ == "__main__":
    display_summary()
