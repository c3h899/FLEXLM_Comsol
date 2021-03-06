import argparse, datetime
import numpy, pandas, os, re, json
import pprint

def get_license_status(lic_file):
	lic_query = os.popen("lmutil lmstat -a -c " + lic_file).read()
	return lic_query
def read_license_data(log_file):
	f = open(log_file, "r")
	return f.read()
def strip_empty_lines(text):
	# Splits query into an array of lines; Empty lines
	lines = text.split("\n")
	return [line for line in lines if line.strip() != ""]
def print_lines(array):
	# Prints  array of lines
	for elm in array: print(elm)
def FLEX_user_of(array, line, array_len):
	# Regex Strings
	line01_entry = re.compile(r"^Users of (\w+):\s*\((.*)\)")
	line01a_Uncounted = re.compile(r"^Uncounted, node-locked")
	line01b_Total = re.compile(r"^Total of (\d+) licenses? issued;\s*Total of (\d+) licenses? in use")
	line02_Details = re.compile(r"^  \"(\w+)\" v([0-9\.]+), vendor: (\w+), expiry: (.*)")
	opt_vendor_str = re.compile(r"^\s*vendor_string:\s*(.*)")
	opt_uncounted = re.compile(r"^\s*uncounted(.*)")
	line03_lic = re.compile(r"^\s*(\w+).*") # TODO: Expand if Needed
	line04_user = re.compile(r"\s*(.*) ([\w\.-]+) ([\w\.-]+)\s*(?=\d+)? \(v([0-9\.]+)\) \(.*\), start (\w+ \d+/\d+ \d+\:\d+),?\s*(.*)$")
		# TODO: ANSYS reporting aliases the machine name into the user name.
		# Priority: LOW
	opt_licenses = re.compile(r"(\d+) licenses$")
		# Optional Non-Capture Group Added in Middle for ANSYS
		# Optional Capture Groud Added to end for ANSYS
	# Returned Object
	event = dict()
	# Entry Point
	m1 = re.match(line01_entry, array[line])
	feature = None
	if m1:
		line = line + 1
		feature = m1[1]
		m1a = re.match(line01a_Uncounted, m1[2])
		if m1a:
			event["Licenses_total"] = -1
			event["Licenses_used"] = -1
		else:
			m1b = re.match(line01b_Total, m1[2])
			if(m1b):
				event["Licenses_total"] = int(m1b[1])
				event["Licenses_used"] = int(m1b[2])
	# TODO: support for looping over multiple license groupings
	def safe_match(pattern):
		return None if (line >= array_len) else re.match(pattern, array[line])
	# (Optional) Details String
	m2 = safe_match(line02_Details)
	if m2:
		line = line + 1
		event["Expiry"] = m2[4]
		user_list = list()
		# (Optional) Vendor string
		m_vendor = safe_match(opt_vendor_str)
		if m_vendor:
			line = line + 1
			event["Vendor_String"] = m_vendor[1]
		# (Optional) uncounted nodelocked ...
		m_uncounted = safe_match(opt_uncounted)
		if m_uncounted:
			line = line + 1
			# Nothing is DONE with the result
		# License Type
		m3 = safe_match(line03_lic)
		if m3:
			line = line + 1
			event["License_type"] = m3[1]
		cont = True
		# User List
		while(cont):
			m4 = safe_match(line04_user)
			if m4:
				line = line + 1
				details = dict()
				details["User"] = m4[1].strip() # Strip operation should be redundant
				details["Machine"] = m4[2]
				details["Client"] = m4[3] # Distiction between m4[2] and m4[3] unclear
				date = datetime.datetime.strptime(m4[5], "%a %m/%d %H:%M")
				event["Date"] = date
				m4a = re.match(opt_licenses, m4[6])
				details["Num_License"] = 1 if not m4a else int(m4a[1])
				user_list.append(details)
			else:
				cont = False
		event["Users"] = user_list
	return ((feature, event, line)) 
def parse_log(array):
	## Log Headder
	line01_copyright = re.compile(r"^lmutil - Copyright \(c\) [\d]{4}-[\d]{4} Flexera. All Rights Reserved.")
	line02_date = re.compile(r"^Flexible License Manager status on ([a-zA-Z0-9/:\ ]+)")
	line03_detect = re.compile(r"^\[.*\]")
	line04_status = re.compile(r"^License server status: (\d+)@([\w\.]+)")
	line05_licfile = re.compile(r"^\s*License file\(s\) on ([\w\.]+): (.*):")
	line06_version = re.compile(r"^\s*([\w\.]+): license server ([a-zA-Z]+)\s*(\([a-zA-Z]+\))? v(.*)")
		# Optional Non-Capture Group Added for CST
	line07_vendor = re.compile(r"^Vendor daemon status \(on .*\):")
	line08_daemon = re.compile(r"^\s*(\w+): ([a-zA-Z]+) v(.*)")
	line09_description = re.compile(r"^Feature usage info:")
	cont = True
	ii = 0
	# Line 1
	if re.match(line01_copyright, array[ii]):
		ii = ii + 1
		cont |= True
	if cont:
		match = dict()
		# Line 2
		m2 = re.match(line02_date, array[ii])
		if m2:
			ii = ii + 1
			match["Date"] = datetime.datetime.strptime(m2[1], "%a %m/%d/%Y %H:%M")
		# Line 3
		m3 = re.match(line03_detect, array[ii])
		if m3: ii = ii + 1
		# Line 4
		m4 = re.match(line04_status, array[ii])
		if m4:
			ii = ii + 1
			match["Port"] = int(m4[1])
			match["Server"] = m4[2]
		# Line 5
		m5 = re.match(line05_licfile, array [ii])
		if m5:
			ii = ii + 1
			match["File"] = m5[2]
		# Line 6
		m6 = re.match(line06_version, array[ii])
		if m6:
			ii = ii + 1
			match["Server_Online"] = True if (m6[2] == "UP") else False
			match["Version"] = m6[3]
		# Line 7
		m7 = re.match(line07_vendor, array[ii])
		if m7: ii = ii + 1
		# Line 8
		m8 = re.match(line08_daemon, array[ii])
		if m8:
			ii = ii + 1
			match["Daemon"] = m8[1]
			match["Daemon_Online"] = True if (m8[2] == "UP") else False
		# Line 9
		m9 = re.match(line09_description, array[ii])
		if m9: ii = ii + 1
		## Features Loop
		array_len = len(array)
		features = dict()
		while( (ii < array_len) and (array[ii][0:5] == "Users") ):
			details = FLEX_user_of(array, ii, array_len)
			features[details[0]] = details[1]
			ii = details[2]
		# Add Features to Record
		match["Features"] = features
	## User Summary
	return match
def features_in_use(Records):
	dat = list()
	daemon = "Unknown" if not 'Daemon' in Records else Records['Daemon']
	if 'Features' in Records:
		for feature in Records['Features']:
			Feat = Records['Features'][feature]
			tot = Feat['Licenses_total']
			use = Feat['Licenses_used']
			rem = tot - use
			if (tot != -1) and (rem != tot) and ('Users' in Feat):
				for user in Feat['Users']:
					dat.append( ((daemon, feature, rem, use/tot, use, tot,
								user['User'], user['Machine'])) )
	return dat
def argument_parsing():
	# Definitions
	parser = argparse.ArgumentParser(description="COMSOL License Utilization Query Tool")
	parser.add_argument('--lic_file', '--names-list', default=[], nargs='+',
						help="License File/s.")
	parser.add_argument('--complete', action='store_true', help='Displays All Query Results')
	parser.add_argument('--brief', action='store_true', help='Displays Utilization Summary')
	parser.add_argument('--raw', action='store_true', help='Displays FLexLM RAW Output')
	parser.add_argument('--users', action='store_true', help='Displays Utilization with Users')
	parser.add_argument('--Xall', action='store_true', help='Export Full Query as JSON')
	parser.add_argument('--Xusers', action='store_true', help='Export Utilization with Users as CSV')
	
	# Evaluate User Input
	args = parser.parse_args()
	
	# Get Current Time
	dt = datetime.datetime.now()
	xusers_fname = dt.strftime("%Y-%m-%d T %H-%M-%S.csv")
	xall_fname = dt.strftime("%Y-%m-%d T %H-%M-%S.json")
	
	# Output Directory
	out_dir = "./Logs/"
	if not os.path.exists(out_dir): os.makedirs(out_dir)
	
	def df_from_list(in_use):
		df = pandas.DataFrame(in_use, columns = ['Daemon', 'Feature', 'Remaining',
			'Utilization', 'In-Use', 'Total', 'User', 'Machine'])
		df.sort_values(by=['Daemon', 'Utilization', 'In-Use', 'Feature', 'User', 'Machine'],
			ascending=[True, False, True, True, True, True,], inplace=True)	
		return df
	
	# Iteration
	in_use = []
	fname_pattern = re.compile(r"^(\w+).?(\w*)?")
	for lic in args.lic_file:
		# Resolve License File Name for use a prefix
		fname_prefix = re.match(fname_pattern, lic)[1]
		# Query FLEX Server
		status = get_license_status(lic)
		if args.raw: print(status)
		log = strip_empty_lines(get_license_status(lic))
		# Parse Results
		parsed = parse_log(log)
		# Basic Summary
		feat_list = features_in_use(parsed)
		in_use.extend(feat_list)
		# Argument Handling
		if args.complete: pprint.pprint(parsed)
		if args.Xall:
			with open(f"{out_dir}{fname_prefix} {xall_fname}", "w") as of: json.dump(parsed, of, default=str)
		
	# (Global) First Order Analytics
	df = df_from_list(in_use)
	if args.users:
		print("")
		print(df)
	if args.brief:
		pt = pandas.pivot_table(df, index=['Daemon', 'Feature'],
			values=['Remaining', 'Utilization', 'In-Use', 'Total'], aggfunc=numpy.mean)
		pt.sort_values(by=['Utilization', 'In-Use', 'Remaining'], ascending=[False, True, True], inplace=True)
		print("")
		print(pt)
	if args.Xusers:
		df.to_csv(f"{out_dir}{xusers_fname}", index=False)

## Main Body
argument_parsing()