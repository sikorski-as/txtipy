import requests
from html.parser import HTMLParser

class FormParser(HTMLParser):
	def __init__(self):
		super().__init__()
		self.inputs = {}
		self.getting_textarea = False
		self.textarea_name = None
		
	def handle_starttag(self, tag, attrs):
		attrs = dict(attrs)
		if tag == 'input':
			name = attrs['name']
			self.inputs[name] = attrs['value'] if 'value' in attrs else None
		elif tag == 'textarea':
			self.getting_textarea = True
			self.textarea_name = attrs['name']
			
	def handle_data(self, data):
		if self.getting_textarea:
			self.inputs[self.textarea_name] = data 
			self.getting_textarea = False
			self.textarea_name = None
	
	@staticmethod
	def parse(html_text):
		parser = FormParser()
		parser.feed(html_text)
		return parser.inputs

# todo: more exceptions
class PageDoesNotExist(Exception):
	def __init__(self, pagename):
		super().__init__(pagename + ' does not exist')
		self.pagename = pagename
		
class PageAlreadyExists(Exception):
	def __init__(self, pagename):
		super().__init__(pagename + ' already exists')
		self.pagename = pagename
			
class Page:
	def __init__(self, name, password):
		self.name = name # url
		self.password = password
		self._session = requests.Session()
		
	#
	# low-level methods
	#
		
	def get_form(self):
		if not self.exists():
			raise PageDoesNotExist(self.name)
			
		r = self._session.get(f'http://txti.es/{self.name}/edit')
		form = FormParser.parse(r.text)
		return form
		
	def post_form(self, form):
		form['edit_code'] = self.password
		
		r = self._session.post(f'http://txti.es', data=form)
		
		good_pass = 'The code you submitted didn\'t match our records.' not in r.text
		good_url = 'The URL you chose' not in r.text
		good_content = 'Content (Cannot be blank)' not in r.text
		good_response = r.status_code == requests.codes.ok
				
		return good_pass and good_url and good_content and good_response
		
	def set_field(self, fieldname, value):
		form = self.get_form()
		form[fieldname] = value
		return self.post_form(form)
		
	def get_field(self, fieldname):
		form = self.get_form()
		return form[fieldname]
		
	#
	# high-level methods
	#
	
	def exists(self):
		r = self._session.get(f'http://txti.es/{self.name}')
		return r.status_code == requests.codes.ok
		
	def push_as_new(self, content='<empty>'):
		if self.exists():
			raise PageAlreadyExists(self.name)
			
		form = {
			'custom_url': self.name,
			'custom_edit_code': self.password,
			'content': content,
			'submit': 'Save+and+done',
			'username': '',
			'form_level': '2'
		}
		return self.post_form(form)	
		
	def delete(self):
		if not self.exists():
			raise PageDoesNotExist(self.name)
			
		form = self.get_form()
		good_first = self.post_form(form)
		form = {
			'page_id': form['page_id'],
			'confirm_delete': 'Delete this txti forever'
		}
		good_second = self.post_form(form)
		return good_first and good_second	
		
	# url
	def set_url(self, new_url):
		status = self.set_field('custom_url', new_url)	
		if status:
			self.name = new_url
			
		return status
		
	def get_url(self):
		return self.name
		
	# password	
	def get_password(self):
		return self.password
		
	def set_password(self, new_password):
		status = self.set_field('custom_edit_code', new_password)
		if status:
			self.password = new_password
		return status
		
	# content	
	def get_content(self):
		return self.get_field('content')
	
	def set_content(self, new_content):
		return self.set_field('content', new_content)
	
	# title
	def get_title(self):
		return self.get_field('title')
		
	def set_title(self, new_title):
		return self.set_field('title', new_title)

	# description
	def get_description(self):
		return self.get_field('description')	
	
	def set_descritpion(self, new_description):
		return self.set_field('description', new_description)
