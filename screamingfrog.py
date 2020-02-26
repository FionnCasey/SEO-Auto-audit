import os
import re

TABS = ['All Inlinks']

def create_sf_report(url, config_file='sf_config_default.seospiderconfig'):
	directory_root = os.getcwd()

	for tab in TABS:
		tab_name = re.sub(r'\s', '_', tab)
		if os.path.exists('%s\\output\\%s.csv' % (directory_root, tab_name)):
			os.remove('%s\\output\\%s.csv' % (directory_root, tab_name))

	print('Starting site crawl -- this can take a very long time!')
	cmd = 'cmd /c "crawl.lnk %s --config \"%s\\%s\" --output-folder \"%s\\output\" --bulk-export \"%s\" --headless"' % (url, directory_root, config_file, directory_root, ','.join(TABS))
	os.system(cmd)
	print('CSV created successfully')