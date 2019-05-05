

class BuildsFeed():
    import sys
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print 'This scrip require BeautifulSoup package (https://www.crummy.com/software/BeautifulSoup/bs4/doc/#).' \
            '\nInstall: pip install beautifulsoup4'
        sys.exit()
    name = 'builds'
    title = 'Houdini Daily Builds'
    #model = BuildModel
    hash_fields = ['build', 'is_production']
    sort_field = 'build'
    SIDEFX_URL = 'https://www.sidefx.com'

    no_url_preview = True

    def parse(self):
        SIDEFX_URL = 'https://www.sidefx.com'
        url = self.SIDEFX_URL + '/download/daily-builds/'
        print 'url', url
        # parse page
        content = self.get_page_content(url, use_session=True)
        builds_elem = content.find('div', {'id': 'dailyBuild'})
        if not builds_elem:
            self.log('Error parse page. No div "dailyBuild"')
            return []
        is_production_build = False
        all_builds = []
        for build in builds_elem.findChildren(recursive=False):
            if build.name == 'span':
                if build.text.strip().upper() == 'PRODUCTION BUILDS':
                    is_production_build = True
                elif build.text.strip().upper() == 'DAILY BUILDS':
                    is_production_build = False
            elif build.name == 'div':
                os_class = [x for x in build['class'] if re.match(r"category-(win|linux|mac)", x)]
                if not os_class:
                    continue
                platform = os_class[0].split('-')[-1]
                a = build.find('a')
                sbuild = re.match(r".*?(\d+\.\d+\.\d+).*", a.text)
                if not sbuild:
                    # _send_log_error('Error get build version "%s"' % a.text)
                    continue
                build_ver = sbuild.group(1)
                url = self.SIDEFX_URL + a.get('href').split('=')[-1] + 'get/'
                filename = a.text
                all_builds.append([
                    build_ver, platform, url, filename, is_production_build
                ])
        per_build = {x[0]: {'urls': {}, 'is_production_build': None} for x in all_builds}
        for i, (build_ver, platform, url, filename, is_production_build) in enumerate(
                sorted(all_builds, key=lambda x: x[0])):
            file = dict(
                url=url,
                filename=filename
            )
            if platform in per_build[build_ver]['urls']:
                per_build[build_ver]['urls'][platform].append(file)
            else:
                per_build[build_ver]['urls'][platform] = [file]
            per_build[build_ver]['is_production_build'] = is_production_build
        return [{'urls': v['urls'], 'build': k, 'is_production': v['is_production_build']} for k, v in per_build.items()]

output = BuildsFeed()
#print dir(output), output.title, output.name, output.parse()
print output.parse()