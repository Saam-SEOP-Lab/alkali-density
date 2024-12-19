def validate_is_float(text):
	try:
		float(text)
		isFloat=True
	except ValueError:
		isFloat=False
	return isFloat

def validate_text_exists(text):
    l = len(text)
    entryExists = False
    if (l > 0):
        entryExists=True
    return entryExists

def entry_exists_is_number(text):
	exists = validate_text_exists(text)
	isNum = validate_is_float(text)
	acceptableNumerical = False
	if (exists and isNum):
		acceptableNumerical = True
	return acceptableNumerical


