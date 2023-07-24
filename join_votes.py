import glob

import pandas as pd


def join_parsed_votes():

    parsed_vote_file_locs = glob.glob('data/parsed_vote_files/*.txt')
    df = pd.concat([pd.read_csv(loc) for loc in parsed_vote_file_locs])
    assert not any(df.duplicated(subset=['name', 'proposal']))
    print(df)
    df.to_csv('all_parsed_vote_files.csv', index=False)

if __name__ == '__main__':

    join_parsed_votes()