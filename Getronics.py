import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.exceptions import RequestException
import re
import pandas as pd
import json


def abstract_cleaner(abstract):
    """Converts all the sup and sub script when passing the abstract block as html"""
    conversion_tags_sub = BeautifulSoup(str(abstract), 'html.parser').find_all('sub')
    conversion_tags_sup = BeautifulSoup(str(abstract), 'html.parser').find_all('sup')
    abstract_text = str(abstract).replace('<.', '< @@dot@@')
    for tag in conversion_tags_sub:
        original_tag = str(tag)
        key_list = [key for key in tag.attrs.keys()]
        for key in key_list:
            del tag[key]
        abstract_text = abstract_text.replace(original_tag, str(tag))
    for tag in conversion_tags_sup:
        original_tag = str(tag)
        key_list = [key for key in tag.attrs.keys()]
        for key in key_list:
            del tag[key]
        abstract_text = abstract_text.replace(original_tag, str(tag))
    abstract_text = sup_sub_encode(abstract_text)
    abstract_text = BeautifulSoup(abstract_text, 'html.parser').text
    abstract_text = sup_sub_decode(abstract_text)
    abstract_text = re.sub('\\s+', ' ', abstract_text)
    text = re.sub('([A-Za-z])(\\s+)?(:|\\,|\\.)', r'\1\3', abstract_text)
    text = re.sub('(:|\\,|\\.)([A-Za-z])', r'\1 \2', text)
    text = re.sub('(<su(p|b)>)(\\s+)(\\w+)(</su(p|b)>)', r'\3\1\4\5', text)
    text = re.sub('(<su(p|b)>)(\\w+)(\\s+)(</su(p|b)>)', r'\1\3\5\4', text)
    text = re.sub('(<su(p|b)>)(\\s+)(\\w+)(\\s+)(</su(p|b)>)', r'\3\1\4\6\5', text)
    abstract_text = re.sub('\\s+', ' ', text)
    abstract_text = abstract_text.replace('< @@dot@@', '<.')
    return abstract_text.strip()

def sup_sub_encode(html):
    """Encodes superscript and subscript tags"""
    encoded_html = html.replace('<sup>', 's#p').replace('</sup>', 'p#s').replace('<sub>', 's#b').replace('</sub>',
                                                                                                         'b#s') \
        .replace('<Sup>', 's#p').replace('</Sup>', 'p#s').replace('<Sub>', 's#b').replace('</Sub>', 'b#s')
    return encoded_html


def sup_sub_decode(html):
    """Decodes superscript and subscript tags"""
    decoded_html = html.replace('s#p', '<sup>').replace('p#s', '</sup>').replace('s#b', '<sub>').replace('b#s',
                                                                                                         '</sub>')
    return decoded_html

if __name__ == '__main__':
    all_data = []
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Cookie': 'OptanonAlertBoxClosed=2024-07-08T07:28:13.198Z; _ga=GA1.1.510729508.1720423694; _zitok=f81ade1beb701fb3158a1720423694; visitor_id506311=938844432; visitor_id506311-hash=3a09cc7f6d22237f9468ae2b4cd19b267261003b84f32f8c10167e663747f4d92fb1d689df77a629237c544dbb09a08298c1f5ce; OptanonConsent=isGpcEnabled=0&datestamp=Tue+Jul+09+2024+17%3A05%3A35+GMT%2B0530+(India+Standard+Time)&version=202306.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=f954453a-e179-45a1-8765-6821ed0b45a7&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&geolocation=%3B&AwaitingReconsent=false; _ga_EW1ZXMKEJD=GS1.1.1720524925.4.1.1720524942.0.0.0',
        'Priority': 'u=0, i',
        'Referer': 'https://www.getronics.com/insights/',
        'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }

    url = 'https://www.getronics.com/category/case-studies/'
    response = requests.get(url, headers=header)
    soup = BeautifulSoup(response.text, 'html.parser')
    data = soup.find('div', class_='elementor-posts-container elementor-posts elementor-posts--skin-classic elementor-grid')
    content = data.find_all('a', class_='elementor-post__read-more')
    for contents in content:
        link = contents.get('href')
        link_response = requests.get(link, headers=header)
        link_soup = BeautifulSoup(link_response.text, 'html.parser')
        title = link_soup.find('h1', class_='elementor-heading-title elementor-size-default')
        titles = abstract_cleaner(title)
        case_studies = link_soup.find('div', class_='elementor-element elementor-element-61bd35c8 elementor-widget-tablet__width-inherit elementor-widget-mobile__width-inherit elementor-widget elementor-widget-theme-post-content')
        Case_studies = abstract_cleaner(case_studies)
        all_dict = {'TITLE': titles, 'URL': link, 'Success_Abstract': Case_studies}
        all_data.append(all_dict)
        df = pd.DataFrame(all_data)
        df.to_csv('Getronics_output.csv', index=False)
        print(Case_studies)
        print(Case_studies)