from django.db import models

# Create your models here.
class Event(models.Model):
    event_id = models.CharField(max_length=200, primary_key=True)
    subject = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=200)
    attendees = models.TextField()  # This will store a JSON string
    description = models.TextField()
    is_cancelled = models.BooleanField(default=False)
    is_online_meeting = models.BooleanField(default=False)
    online_meeting_provider = models.CharField(max_length=200, null=True, blank=True)
    web_link = models.URLField(max_length=1000, null=True, blank=True)
    organizer = models.TextField() # This will store a JSON string