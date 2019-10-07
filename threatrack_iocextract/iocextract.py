import os
import re

patterns = {}
defangs = []
hostname_whitelist = []

def load_patterns(path=os.path.join(os.path.abspath(os.path.dirname(__file__)),"patterns/")):
	def read_patterns(relpath):
		f = open(os.path.join(path,relpath),'r')
		text = f.read().split('\n')
		f.close()
		text = [t for t in text if not t.startswith('#') and not t == '']
		return '\n'.join(text)

	def expand(pattern, patterns):
		for m in re.findall(r'(?P<replace>%%file:(?P<file>[A-Za-z0-9\.]+)%%)', pattern):
			lines = read_patterns(m[1]).split('\n')
			sp = '(?:' + '|'.join(lines) + ')'
			pattern = pattern.replace(m[0], sp)
		for m in re.findall(r'(?P<replace>%%pattern:(?P<pattern>[A-Za-z0-9\.]+)%%)', pattern):
			pattern = pattern.replace(m[0], '(?:' + patterns[m[1]].pattern + ')')
		return pattern

	pattern_conf = read_patterns('patterns.csv').split('\n')
	global patterns
	patterns = {}
	for pattern in pattern_conf:
		name,p,opt = pattern.split('\t')
		p = expand(p, patterns)
		patterns.update({
			name :
			re.compile(p, re.I if 'i' in opt else 0 | re.S if 's' in opt else 0)
		})

	defang_conf = read_patterns('defangs.csv').split('\n')
	global defangs
	defangs = []
	for defang in defang_conf:
		defangs.append(defang.split('\t'))

	global hostname_whitelist
	hostname_whitelist = read_patterns('hostname_whitelist.csv').lower().split('\n')


def refang(text):
	for d,r in defangs:
		text = re.sub(re.compile(d, re.I), r, text)
	return text


def extract(text):
	iocs = {}
	for name, pattern in patterns.items():
		if name.startswith('.'):
			continue
		iocs[name] =  list(set(re.findall(pattern, text)))

	return iocs


def extract_all(text):
	return extract(refang(text))


def whitelist(iocs):
	hostnames = [h.lower() for h in iocs['hostname']]
	urls = []
	for url in iocs['url']:
		whitelisted = False
		for w in hostname_whitelist:
			# if a whitelisted hostname is early in the url remove it
			# this avoids matching https://evil.com/http://accounts.google.com/
			pos = url.lower().find("://"+w+"/")
			end = url.lower().endswith("://"+w)
			if pos >= 2 or end:
				whitelisted = True
				break
		if not whitelisted:
			urls.append(url)

	iocs['url'] = urls
	iocs['hostname'] = list(set(hostnames) - set(hostname_whitelist))

	return iocs


#def extract_smart(text_de):
#	text_re = refang(text_de)
#	iocs = extract(text_re)
#	#TODO: implement
#	return iocs


# init patterns
load_patterns()


# a small test application
# usage: python3 iocextract.py ../tests/01.txt <yara|snort|ipv4|...>
if __name__=="__main__":
	import sys

	iocs = extract( open(sys.argv[1],'r').read() )
	iocs = whitelist(iocs)

	print("\n".join(iocs[sys.argv[2]]))

