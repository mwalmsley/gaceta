import os

import requests
from bs4 import BeautifulSoup


def download_votes_for_all_parliaments():
    # 58 to 65 inclusive
    # LVIII Legislatura (2000-2003) to LXV Legislatura (2021-2024)
    for parliament_index in range(58, 66):
        parliament_url = f'http://gaceta.diputados.gob.mx/voto{parliament_index}'

        period_links = get_period_links_in_parliament(parliament_url)
        assert len(period_links) > 0

        for period_link in period_links:
            vote_links_in_period = get_vote_links_in_period(period_link)
            assert len(vote_links_in_period) > 0

            for vote_link in vote_links_in_period:
                download_vote_link(vote_link)
              

def get_period_links_in_parliament(parliament_url):
    # search through
    page = requests.get(parliament_url)
    page.raise_for_status()
    soup = BeautifulSoup(page.content, "html.parser")
    # get every link with text starting 'ordi' or 'extra'
    ordinary_periods = soup.find_all("a", string=lambda x: x.startswith('ordi'))
    extra_periods = soup.find_all("a", string=lambda x: x.startswith('extra'))
    periods = ordinary_periods + extra_periods
    period_urls = [os.path.join(parliament_url, r['href']) for r in periods]
    return period_urls


def get_vote_links_in_period(period_url):
    # same pattern as above, downloading the text contents of a vote page
    page = requests.get(period_url)
    page.raise_for_status()
    soup = BeautifulSoup(page.content, "html.parser")
    # get every link with text which starts 'voto...'
    results = soup.find_all("a", string=lambda x: x.startswith('voto'))
    # these are relative links, make them absolute links
    urls_to_raw_vote_files = [os.path.join(period_url, r['href']) for r in results]
    # save the list of links to a file, for reference
    # with open('data/urls_of_raw_vote_files.txt', 'w') as f:
        # f.write('\n'.join(urls_to_raw_vote_files))
    return urls_to_raw_vote_files

    # download each link
    # for url in urls_to_raw_vote_files:


def download_vote_link(vote_text_link, overwrite=False):
    
    print(f'Downloading {vote_text_link}')
    save_subdir = '/'.join(vote_text_link.split('/')[-3:-1])
    # e.g. data/raw/voto58/ordi11/
    save_dir = os.path.join('data', 'raw', save_subdir)
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)
    save_loc = os.path.join(save_dir, os.path.basename(vote_text_link))
    if os.path.isfile(save_loc) and not overwrite:
        print(f'Skipping existing file (overwrite=False): {save_loc}')
    else:
        text_page = requests.get(vote_text_link)
        with open(save_loc, 'w') as f:
            # use latin-1 encoding, not the default utf-8, because of the accent characters e.g. ó
            # yay modern colonialism
            f.write(text_page.content.decode('latin-1'))
        exit()


if __name__ == '__main__':

    download_votes_for_all_parliaments()



# if __name__ == '__main__':



#     period_folder_url = 'http://gaceta.diputados.gob.mx/voto64/'
#     download_all_sessions(period_folder_url)

    # vote_text_link = 'http://gaceta.diputados.gob.mx/voto64/ordi11/LosVotos/'
    # download_all_votes(vote_text_link)
