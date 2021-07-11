import dfin

while True:
	text = input('DfIn > ')
	token, error = dfin.run('<stdin>',text)
	if error:
		print(error.as_string())
	else:
		print(token)