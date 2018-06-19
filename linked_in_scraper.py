import time
import json
import csv
import os
import requests
from bs4 import BeautifulSoup
from jinja2 import Template
import headers

# these represent different job functions
FUNCTION_FACETS = [17, 18, 14, 2, 4, 20, 5, 13, 12, 26] #FA
SENIORITY_FACETS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] #SE
LOCATION_FACETS = [ #G
    'us:8-2-0-1-2',
    'us:97',
    'us:va',
    'us:dc',
    'us:tx',
    'us:ca',
    'us:md',
    'us:70',
    'us:31',
    'us:ny',
    'us:8-8-0-8-1',
    'us:8-8-0-3-1',
    'us:ga',
    'us:52',
    'us:7',
    'us:8-8-0-95-11',
    'us:nj',
    'us:3-2-0-31-1',
]

FACETS = [
    ('FA', FUNCTION_FACETS),
    ('SE', SENIORITY_FACETS),
    ('G', LOCATION_FACETS)
]

def download_file(url, local_filename=None):
    '''Downloads a file with requests
    from: https://stackoverflow.com/a/16696317
    '''

    if local_filename is None:
        local_filename = url.split('/')[-1]

    print('saving to', local_filename)
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    return local_filename


def get_page(company_id, facet=None, facet_id=None, start=0, count=50):
    '''Gets a single page of results from linkedin for a particular job function at a company'''

    params = {
        'facet': ['CC'],
        'facet.CC': company_id,
        'count': count,
        'start': start,
    }

    if facet is not None and facet_id is not None:
        params['facet'] = ['CC', facet]
        params['facet.' + facet] = facet_id

    response = requests.get('https://www.linkedin.com/sales/search/results', headers=headers.headers, params=params)
    return response.json()


def get_company(company_id, outname):
    '''Gets all employees from a company using particular job functions'''
    people = []

    for facet, facet_ids in FACETS:
        for facet_id in facet_ids:
            print('getting facet', facet, facet_id, 'for company', company_id)
            count = 50
            start = 0
            results = get_page(company_id, facet, facet_id)
            total = results['pagination']['total']
            people += results['searchResults']
            start += count
            while start < total:
                print('getting', start, 'of', total)
                time.sleep(1)
                results = get_page(company_id, facet, facet_id, start)
                people += results['searchResults']
                start += count

                with open(outname, 'w') as outfile:
                    json.dump(people, outfile, indent=2)

    return outname


def get_images(datafile):
    '''Downloads profile images'''

    with open(datafile, 'r') as infile:
        people = json.load(infile)

    people = [p['member'] for p in people]

    for p in people:
        if 'vectorImage' not in p:
            continue

        pid = p['memberId']
        outname = 'images/{}.jpg'.format(pid)

        if os.path.exists(outname):
            print('skipping')
            continue

        url = p['vectorImage']['rootUrl']
        url += sorted(p['vectorImage']['artifacts'], key=lambda x: x['width'])[-1]['fileIdentifyingUrlPathSegment']

        print(url)

        download_file(url, outname)

        time.sleep(1)


def get_profile(pid):
    '''Downloads individual profiles'''

    outname = 'profiles/{}.json'.format(pid)
    if os.path.exists(outname):
        return outname

    out = {}
    url = 'https://www.linkedin.com/sales/people/{},NAME_SEARCH'.format(pid)
    print(url)
    response = requests.get(url, headers=headers.headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    codes = soup.select('code')
    for c in codes:
        try:
            d = json.loads(c.text)
            if 'contactInfo' in d:
                out = d
                break
        except Exception as e:
            continue

    with open(outname, 'w') as outfile:
        json.dump(out, outfile)

    time.sleep(1)
    return outname


def get_profiles(datafile):
    '''Gets all profiles'''

    with open(datafile, 'r') as infile:
        data = json.load(infile)

    for d in data:
        pid = d['member']['profileId']
        get_profile(pid)


def clean_and_parse(datafile, outname):
    '''Outputs csv, json and html from employee listings'''

    out = []
    mids = []
    with open(datafile, 'r') as infile:
        data = json.load(infile)

    for d in data:
        mid = d['member']['memberId']
        pid = d['member']['profileId']

        imgpath = 'images/{}.jpg'.format(mid)
        if not os.path.exists(imgpath):
            imgpath = None

        item = {
            'name': d['member'].get('formattedName', ''),
            'title': d['member'].get('title', ''),
            'img': imgpath,
            'company': d['company'].get('companyName', ''),
            'location': d['member'].get('location', ''),
            'id': d['member']['memberId'],
            'linkedin': 'https://linkedin.com/in/' + pid,
        }

        if mid not in mids:
            out.append(item)
            mids.append(mid)

    with open(outname + '.json', 'w') as jsonfile:
        json.dump(out, jsonfile, indent=2)

    with open(outname + '.csv', 'w') as csvfile:
        fieldnames = list(out[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in out:
            writer.writerow(row)

    with open('template.html', 'r') as templatefile:
        template = Template(templatefile.read())
    html = template.render(people=out)
    with open('index.html', 'w') as htmlout:
        htmlout.write(html)


if __name__ == '__main__':
    ICE = '533534'
    datafile = 'ice_raw.json'
    get_company(ICE, datafile)
    get_profiles(datafile)
    get_images(datafile)
    clean_and_parse(datafile, 'ice')
