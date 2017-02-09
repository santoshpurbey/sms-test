from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from smsservice.models import Message,MessageTable
from smsservice.forms import MessageForm, GroupSMSForm, MultipleSMS, CreateGroup
from smsservice.models import Group
from django.views.generic import View
from django.http import HttpResponse
from django.http import JsonResponse
from django_tables2 import RequestConfig
from django.http import HttpResponseRedirect
from django.contrib import messages
import time
import xlwt
# Create your views here.

@login_required
def dashboard(request):
	template_name = 'dashboard/dashboard_index.html'
	return render(request, template_name)

	
@login_required
def compose_message(request):
	if request.method=='POST':
		print(request.POST)
		form = MessageForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponse('Message sent!')
	else:
		template_name = 'messages/messages.html'
		form = MessageForm()
	context = {'form': form}

	return render(request, template_name, context)

class ContactGroupView(View):
	def get(self, request):
		form=CreateGroup()
		group_list = Group.objects.all()
		context={'form':form, 'group_list':group_list}
		return render(self.request, 'create-group/contents.html', context)

	def post(self, request):
		time.sleep(1) 
		form = CreateGroup(self.request.POST, self.request.FILES)
		if form.is_valid():
			messages.success(request, 'Group created successfully',fail_silently=True)
			group = form.save()
			data = {'is_valid': True, 'name': group.file.name, 'url': group.file.url}

		else:
			data = {'is_valid': False}
			return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/')) #redirect to same page after form submit


		return JsonResponse(data)

@login_required
def multiple_sms(request):
	''' send bulk sms with phone_numbers seperated by comma '''
	if request.method=='POST':
		form = MultipleSMS(request.POST)
		if form.is_valid():
			messages.success(request, 'Message successfully sent', fail_silently=True)

			phone_numbers = form.cleaned_data['phone_numbers']
			message = form.cleaned_data['message']
			phones = phone_numbers.split(',')
			for phone in phones:
				messageform = MessageForm({'phone':phone, 'text':message})
				if messageform.is_valid:
					messageform.save()
			return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/')) #redirect to same page after form submit


	else:
		form = MultipleSMS()
	context = {'form': form}
	return render(request,'messages/compose/single_message.html', context)

@login_required
def sent_messages(request):
	'''List of sent messages in table views'''
	queryset = Message.objects.all()
	table = MessageTable(queryset)
	RequestConfig(request).configure(table)
	return render(request, 'messages/sent.html', {'table': table})


#export sent-messages to excel
@login_required
def export_sent_xls(request):
	'''Export sent messages to excel sheet '''
	response = HttpResponse(content_type='application/ms-excel')
	response['Content-Disposition'] = 'attachment; filename="users.xls"'

	wb = xlwt.Workbook(encoding='utf-8')
	ws = wb.add_sheet('Message')

	# Sheet header, first row
	row_num = 0

	font_style = xlwt.XFStyle()
	font_style.font.bold = True

	columns = ['Direction', 'Status','Phone','Text','Sent Date']

	for col_num in range(len(columns)):
		ws.write(row_num, col_num, columns[col_num], font_style)

	# Sheet body, remaining rows
	font_style = xlwt.XFStyle()

	rows = Message.objects.all().values_list('direction', 'status','phone','text','sent_date')
	for row in rows:
		row_num += 1
		for col_num in range(len(row)):
			ws.write(row_num, col_num, row[col_num], font_style)

	wb.save(response)
	return response