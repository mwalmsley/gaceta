import glob
import os

import pandas as pd


def join_parsed_votes():

    # e.g. data/raw/voto50/ordi11/voto1031_1.txt
    for parliament_index in range(60, 66):
        save_loc = os.path.join('data', 'results', f'parliament_{parliament_index}_votes.csv')
        parsed_vote_file_locs = glob.glob(f'data/parsed/voto{parliament_index}/*/*.txt')
        print(f'Saving {len(parsed_vote_file_locs)} votes for parliament {parliament_index} to {save_loc}')
        # print([loc for loc in parsed_vote_file_locs if 'voto0306-1' in loc])
        # exit()
        assert parsed_vote_file_locs
        df = pd.concat([pd.read_csv(loc) for loc in parsed_vote_file_locs]).reset_index(drop=True)
        df = df.sort_values(['date', 'proposal_id', 'name'])
        is_duplicate = df.duplicated(subset=['name', 'proposal_id'])
        if any(is_duplicate):
            print('Duplicates found: {:.5f} percent of rows'.format(is_duplicate.mean()))
            print('Proposals with duplicates: \n{}'.format(df[is_duplicate]['proposal_id'].unique()))
            print('Taking first vote entry for those proposals')
            df = df.drop_duplicates(subset=['name', 'proposal_id'], keep='first')
        df.to_csv(save_loc, index=False)


if __name__ == '__main__':

    join_parsed_votes()
