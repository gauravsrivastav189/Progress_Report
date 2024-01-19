from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import Trainee, ProgressReport
from .forms import ProgressReportForm  # Import the ProgressReportForm

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('progress_tracker:student_list')
    else:
        form = AuthenticationForm()
    return render(request, 'progress_tracker/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('progress_tracker:login')

# progress_tracker/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import ProgressReport
from .forms import ProgressReportForm

@login_required
def student_list(request):
    progress_reports = ProgressReport.objects.select_related('trainee').all()
    return render(request, 'progress_tracker/student_list.html', {'progress_reports': progress_reports})

@login_required
def update_progress_report(request):
    if request.method == 'POST':
        form = ProgressReportForm(request.POST)
        if form.is_valid():
            progress_report_id = form.cleaned_data['progress_report_id']
            marks = form.cleaned_data['marks']
            comments = form.cleaned_data['comments']

            # Get the progress report object
            progress_report = get_object_or_404(ProgressReport, id=progress_report_id)

            # Update the progress report
            progress_report.marks = marks
            progress_report.comments = comments
            progress_report.save()

            return redirect('progress_tracker:student_list')
    else:
        # Handle GET requests or invalid form submissions
        form = ProgressReportForm()

    return render(request, 'progress_tracker/update_progress_report.html', {'form': form})






@login_required
def progress_graph(request):
    all_trainees = Trainee.objects.all()
    attendance_data = {}
    for trainee in all_trainees:
        progress_reports = ProgressReport.objects.filter(trainee=trainee)
        percentages = [report.attendance / 100.0 for report in progress_reports]
        attendance_data[trainee.username] = percentages

    return render(request, 'progress_tracker/progress_graph.html', {'attendance_data': attendance_data})


@login_required
def progress_graph(request):
    all_trainees = Trainee.objects.all()
    attendance_data = {}
    for trainee in all_trainees:
        progress_reports = ProgressReport.objects.filter(trainee=trainee)
        percentages = [report.attendance / 100.0 for report in progress_reports]
        attendance_data[trainee.username] = percentages

    return render(request, 'progress_tracker/progress_graph.html', {'attendance_data': attendance_data})


@login_required
def marksheet(request):
    all_trainees = Trainee.objects.all()
    mark_data = {}
    for trainee in all_trainees:
        progress_reports = ProgressReport.objects.filter(trainee=trainee)
        marks = [report.marks /100.0 for report in progress_reports]
        mark_data[trainee.username] = marks

    return render(request, 'progress_tracker/marksheet.html', {'mark_data': mark_data})

@login_required
def assignmnet_report(request):
    all_trainees = Trainee.objects.all()
    assignment_data = {}
    for trainee in all_trainees:
        progress_reports = ProgressReport.objects.filter(trainee=trainee)
        assignments = [report.assignment /100.0 for report in progress_reports]
        assignment_data[trainee.username] = assignments

    return render(request, 'progress_tracker/assignmnet_report.html', {'assignment_data': assignment_data})

from django.db.models import Avg

@login_required
def overall_progress(request):
    all_trainees = Trainee.objects.all()
    overall_data = {}

    for trainee in all_trainees:
        progress_reports = ProgressReport.objects.filter(trainee=trainee)

        # Group progress reports by week number
        reports_by_week = {}
        for report in progress_reports:
            if report.week_number not in reports_by_week:
                reports_by_week[report.week_number] = {
                    'attendance': [],
                    'marks': [],
                    'assignment': [],
                }
            reports_by_week[report.week_number]['attendance'].append(report.attendance)
            reports_by_week[report.week_number]['marks'].append(report.marks)
            reports_by_week[report.week_number]['assignment'].append(report.assignment)

        # Calculate average percentage for each week
        weekly_data = {}
        for week, data in reports_by_week.items():
            weekly_data[week] = {
                'attendance': sum(data['attendance']) / len(data['attendance']),
                'marks': sum(data['marks']) / len(data['marks']),
                'assignment': sum(data['assignment']) / len(data['assignment']),
            }

        overall_data[trainee.username] = weekly_data

    return render(request, 'progress_tracker/overall_progress.html', {'overall_data': overall_data})
