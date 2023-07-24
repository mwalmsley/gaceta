import glob
import os

import pandas as pd


def join_parsed_votes():

    # e.g. data/raw/voto50/ordi11/voto1031_1.txt
    parsed_vote_file_locs = glob.glob('data/parsed/*/*/*.txt')
    df = pd.concat([pd.read_csv(loc) for loc in parsed_vote_file_locs])
    assert not any(df.duplicated(subset=['name', 'proposal']))
    print(df)

    save_loc = os.path.join('data', 'all_parsed_votes.csv')
    print(f'Saving all parsed votes to {save_loc}')
    df.to_csv(save_loc, index=False)


if __name__ == '__main__':

    join_parsed_votes()
