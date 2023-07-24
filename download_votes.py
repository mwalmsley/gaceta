import os

import requests
from bs4 import BeautifulSoup


def download_votes_for_all_parliaments(overwrite):
    # 58 to 65 inclusive
    # LVIII Legislatura (2000-2003) to LXV Legislatura (2021-2024)
    for parliament_index in range(58, 66):
        parliament_url = f'http://gaceta.diputados.gob.mx/voto{parliament_index}'

        period_links = get_period_links_in_parliament(parliament_url)
        assert len(period_links) > 0

        for period_link in period_links:
            print(period_link)
            vote_links_in_period = get_vote_links_in_period(period_link)
            assert len(vote_links_in_period) > 0

            for vote_link in vote_links_in_period:
                download_vote_link(vote_link, overwrite=overwrite)
              

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
    assert period_urls
    return period_urls


def get_vote_links_in_period(period_url):
    # same pattern as above, downloading the text contents of a vote page
    period_page = requests.get(period_url)
    period_page.raise_for_status()
    period_soup = BeautifulSoup(period_page.content, "html.parser")

    # periods before voto60/ordi21 have the vote text files on that page
    # periods on or after voto60/ordi21/ have the vote files in subfolder /LosVotos/
    # so check if /LosVotos/ subfolder is present and if so, append
    votes_subfolder = period_soup.find(string='LosVotos/')
    if votes_subfolder:
        # search in that page (i.e. under LosVotos subfolder)
        url_to_search_for_text_files = os.path.join(period_url, 'LosVotos/')
        page = requests.get(url_to_search_for_text_files)
        # print(os.path.join(period_url, 'LosVotos/'))
        # exit()
        page.raise_for_status()
        soup = BeautifulSoup(page.content, "html.parser")
    else:
        # search on the parliament page
        soup = period_soup
        url_to_search_for_text_files = period_url

    # get every link with text which starts 'voto...'
    results = soup.find_all("a", string=lambda x: x.startswith('voto'))
    # these are relative links, make them absolute links
    urls_to_raw_vote_files = [os.path.join(url_to_search_for_text_files, r['href']) for r in results]
    # save the list of links to a file, for reference
    # with open('data/urls_of_raw_vote_files.txt', 'w') as f:
        # f.write('\n'.join(urls_to_raw_vote_files))
    assert urls_to_raw_vote_files
    return urls_to_raw_vote_files

    # download each link
    # for url in urls_to_raw_vote_files:


def download_vote_link(vote_text_link, overwrite=False):
    
    print(f'Downloading {vote_text_link}')
    # some periods have the votes under /LosVotos/ subfolder
    # never add /LosVotos/ to the save path, no need (and creates inconsistency)
    # always name like e.g. data/raw/voto58/ordi11/
    save_subdir = '/'.join(vote_text_link.replace('/LosVotos', '').split('/')[-3:-1])
    save_dir = os.path.join('data', 'raw', save_subdir)
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)
    
    save_loc = os.path.join(save_dir, os.path.basename(vote_text_link))
    if os.path.isfile(save_loc) and not overwrite:
        print(f'Skipping existing file (overwrite=False): {save_loc}')
    else:
        text_page = requests.get(vote_text_link)
        # use latin-1 encoding, not the default utf-8, because of the accent characters e.g. ó
        # yay modern colonialism
        text = text_page.content.decode('latin-1')

        # deal with this one edge case where there's some weird prefixed text
        # http://gaceta.diputados.gob.mx/voto60/ordi32/LosVotos/voto0312-8.txt
        if vote_text_link == 'http://gaceta.diputados.gob.mx/voto60/ordi32/LosVotos/voto0312-8.txt':
            # drop the first lines of weird prefix text
            text = '\n'.join(text.split('\n')[6:])

        # helpful to avoid when the server returns a page saying "error",
        # but technically with a 200 success code (silly server)
        assert text.startswith('VERSION'), ValueError(text)  
        with open(save_loc, 'w') as f:
            f.write(text)


if __name__ == '__main__':

    # overwrite=True to always download every file, even if already saved
    download_votes_for_all_parliaments(overwrite=False)

    # or to test the pieces

    # period_folder_url = 'http://gaceta.diputados.gob.mx/voto64/'
    # get_vote_links_in_period(period_folder_url)

    # vote_text_url = 'http://gaceta.diputados.gob.mx/voto58/ordi11/voto1031_2.txt'
    # download_vote_link(vote_text_url, overwrite=True)

    # edge case
    # vote_text_url = 'http://gaceta.diputados.gob.mx/voto60/ordi32/LosVotos/voto0312-8.txt'
    # download_vote_link(vote_text_url, overwrite=True)
