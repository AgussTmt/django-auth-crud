from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TaskForm
from .models import tasks
from django.utils import timezone
from django.contrib.auth.decorators import login_required
# Create your views here.


def home(home):
    return render(home, 'home.html', {})


def SignUp(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {'form': UserCreationForm})
    else:
        try:
            if request.POST['password1'] == request.POST['password2']:
                # register user
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
        except IntegrityError:
            return render(request, 'signup.html', {
                'form': UserCreationForm,
                'error': 'Username already exists'
            })
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': 'Password do not match'
        })

@login_required
def show_tasks(request):
    list_task = tasks.objects.filter(user=request.user, datecompleted=None)   
    return render(request, 'tasks.html', {
        'tasks': list_task
    })
    
@login_required    
def show_completed_tasks (request):
    list_task = tasks.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')   
    return render(request, 'tasks.html', {
        'tasks': list_task
    })

@login_required
def close_session(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password1'])
        if user is None:

            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Invalid username or password'
            })
        else:
            login(request, user)
            return redirect('/tasks')

@login_required

def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html', {
            'form': TaskForm
        })
    else:
        try:
            form = TaskForm(request.POST)
            newtask = form.save(commit=False)
            newtask.user = request.user
            newtask.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html', {
                'form': TaskForm,
                'error': 'please provide valid data'
            })



@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(tasks, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task,'form': form})
    else:
        try:
            task = get_object_or_404(tasks, id=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            task = get_object_or_404(tasks, pk=task_id, user=request.user)
            
            return render(request, 'task_detail.html', {'task': task,
                'form': TaskForm,
                'error': 'Error updating task'
            })


@login_required
def complete_task(request, task_id):
    
    task = get_object_or_404(tasks, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('/tasks')

@login_required    
def delete_task(request, task_id):
    
    task = get_object_or_404(tasks, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('/tasks')        
    
