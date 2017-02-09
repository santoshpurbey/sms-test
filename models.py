from __future__ import unicode_literals

from django.db import models

from django.utils.timezone import now
import django_tables2 as tables


# Create your models here.
from django.contrib.auth.models import User


DIRECTION_CHOICES = (
	('I', 'Incoming'),
	('O', 'Outgoing'),
	)

STATUS_CHOICES = (
	('Q', 'Queued'),
	('R', 'Received'),
	('P', 'Processing'),
	('S', 'Sent'),
	('D', 'Delivered'),
	('E', 'Errored'),
	)

class Message(models.Model):
	'''To create message with '''
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	direction = models.CharField(max_length=1, choices=DIRECTION_CHOICES, default='O')
	status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='Q')
	phone = models.CharField(max_length=15) #send to or received phone no.
	text = models.TextField(help_text="Please Write your message...")
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	sent_date = models.DateTimeField(null=True,blank=True)
	delivered_date = models.DateTimeField(null=True, blank=True)


	def  __str__(self):
		# return 'Phone: {} Direction: {} Status: {}'.format(self.phone, self.direction, self.status)
		return self.text[:30]


class MessageTable(tables.Table):
	''' To display message in table form using django-table2'''
    class Meta:
        model = Message


class ContactGroup(models.Model):
	''' To create group of contacts using csv or excel'''
	name = models.CharField(max_length=50)
	file = models.FileField(upload_to='Group/User/File')
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return 'Group Name: {}'.format(self.name)


class UserContactGroup(models.Model):
	''' To create multiple contacts group for a single user'''
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	group = models.ManyToManyField(Group)

	def __str__(self):
		return 'user {}'.format(self.user)



class Notification(models.Model):
	NOTIFICATION_TYPES = (
	('I', 'Incoming'),
	('O', 'Outgoing'),
	('Q', 'Queued'),
	('R', 'Received'),
	('S', 'Sent'),
	('D', 'Delivered'),
	('E', 'Errored'),
	)

	from_user = models.ForeignKey(User, related_name='+')
    to_user = models.ForeignKey(User, related_name='+')
    date = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=1,
                                         choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ('-date',)

     def __str__(self):
     	return self.notification_type

     	