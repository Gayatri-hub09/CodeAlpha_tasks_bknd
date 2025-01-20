from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField()
    
    def __str__(self):
        return self.title
    
    def is_full(self):
        return self.registrations.count() >= self.capacity

class Registration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, related_name='registrations', on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} registered for {self.event.title}"

    INSTALLED_APPS = [
    # other apps
    'events',
]
    python manage.py makemigrations
python manage.py migrate

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Event, Registration

def event_list(request):
    events = Event.objects.all()
    return render(request, 'events/event_list.html', {'events': events})

def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'events/event_detail.html', {'event': event})

@login_required
def register_for_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    if event.is_full():
        return render(request, 'events/event_full.html', {'event': event})
    
    if Registration.objects.filter(user=request.user, event=event).exists():
        return redirect('events:event_detail', event_id=event.id)
    
    registration = Registration(user=request.user, event=event)
    registration.save()
    return redirect('events:event_detail', event_id=event.id)

@login_required
def manage_registration(request):
    registrations = Registration.objects.filter(user=request.user)
    return render(request, 'events/manage_registration.html', {'registrations': registrations})

from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('register/<int:event_id>/', views.register_for_event, name='register_for_event'),
    path('manage/', views.manage_registration, name='manage_registration'),
]
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('events/', include('events.urls')),
]
<!DOCTYPE html>
<html>
<head>
    <title>Event List</title>
</head>
<body>
    <h1>Events</h1>
    <ul>
        {% for event in events %}
            <li>
                <a href="{% url 'events:event_detail' event.id %}">{{ event.title }}</a> - 
                {{ event.date }} ({{ event.capacity }} spots)
            </li>
        {% endfor %}
    </ul>
</body>
</html>
<!DOCTYPE html>
<html>
<head>
    <title>{{ event.title }}</title>
</head>
<body>
    <h1>{{ event.title }}</h1>
    <p>{{ event.description }}</p>
    <p>Date: {{ event.date }}</p>
    <p>Location: {{ event.location }}</p>
    
    {% if event.is_full %}
        <p>This event is full!</p>
    {% else %}
        <a href="{% url 'events:register_for_event' event.id %}">Register for this event</a>
    {% endif %}
    
    <p><a href="{% url 'events:event_list' %}">Back to event list</a></p>
</body>
</html>
<!DOCTYPE html>
<html>
<head>
    <title>Manage Registrations</title>
</head>
<body>
    <h1>Your Event Registrations</h1>
    <ul>
        {% for registration in registrations %}
            <li>{{ registration.event.title }} - Registered on {{ registration.registered_at }}</li>
        {% empty %}
            <p>You have no registrations.</p>
        {% endfor %}
    </ul>
</body>
</html>

<!DOCTYPE html>
<html>
<head>
    <title>Event Full</title>
</head>
<body>
    <h1>{{ event.title }} is full!</h1>
    <p>Sorry, this event has reached its full capacity.</p>
    <p><a href="{% url 'events:event_list' %}">Back to event list</a></p>
</body>
</html>

from django.contrib import admin
from .models import Event, Registration

admin.site.register(Event)
admin.site.register(Registration)
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('events/', include('events.urls')),
]
# event_registration/settings.py

LOGIN_REDIRECT_URL = 'events:event_list'
LOGOUT_REDIRECT_URL = 'events:event_list'

python manage.py runserver
