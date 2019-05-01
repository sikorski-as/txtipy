from txtipy import *

page = Page('txtipy-example', 'txtipy_example')

try:
	status = page.push_as_new(content='#txtipy example')
	print('created:', status)
except PageAlreadyExists as e:
	print(e)
	
input('press enter to continue')
	
try:
	status = page.set_content('#txtipy example with changed content')
	print('updated content:', status)
except PageDoesNotExist as e:
	print(e)
	
input('press enter to continue')	
	
try:
	status = page.set_title('txtipy example - with title')
	print('title updated:', status)
except PageDoesNotExist as e:
	print(e)

input('press enter to continue')	
	
try:
	status = page.delete()
	print('deleted:', status)
except PageDoesNotExist as e:
	print(e)
