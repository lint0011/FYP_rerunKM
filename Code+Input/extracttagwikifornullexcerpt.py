import MySQLdb as mdb
import MySQLdb.cursors
import re

def extractTagWiki():
	con = mdb.connect('localhost','root','l56530304T','fyp',cursorclass = MySQLdb.cursors.SSCursor);
	cur = con.cursor()

	f = open('nulltagexcerpt.txt',encoding = 'utf8')
	lines = f.readlines()
	f.close()

	fw = open('exception_tagwiki.txt','w',encoding = 'utf8')
	for line in lines:
		tag = line.strip()
		select = 'select tag.TagName, post.Body\
					from tag join post on \
					tag.WikiPostId = post.Id\
					where tag.TagName = '+'\''+tag+'\' '
		cur.execute(select)
		for row in cur:
			if row[1] is not None:
				fw.write(row[0]+'\t'+row[1]+'\n')
	fw.close()

def cleanTagWiki():
	f = open('exception_tagwiki.txt',encoding = 'utf8')
	lines = f.readlines()
	f.close()

	fw = open('exception_tagwiki_cleaned.txt','w',encoding = 'utf8')
	for line in lines:
		items = line.strip().split('\t')
		#pattern = items[1]
		symbol_list = ['=', '*', '{', '}', '[', ']', '&', '$']
		pattern = re.sub("<code>(.*?)</code>",
		                 lambda m: "" if any(symbol in m.group(1) for symbol in symbol_list) else m.group(), items[1],
		                 flags=re.S)

		pattern = re.sub(r"</?[a-z][^>]*>", " ", pattern)
		pattern = re.sub(r"&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;|e\.g\.|i\.e\.", " ", pattern)
		pattern = re.sub(r"\*|~|`", " ", pattern)
		pattern = re.sub(r"&#xA", ". ", pattern)

		# pattern = re.sub(r"https?://.+?&#xA", "&#xA", pattern)
		pattern = re.sub(r"https?://\S+", " ", pattern)
		# pattern = re.sub(r"https?://.+?$", "", pattern)
		pattern = re.sub(r' . ;   ','',pattern)
		pattern = pattern.lower()

		fw.write(items[0]+'\t'+pattern+'\n')

	fw.close()

if __name__ == '__main__':

	try:
	
		cleanTagWiki()
		
	except Exception as e :
		print('There are exceptions')
		print(e)
		raise		




