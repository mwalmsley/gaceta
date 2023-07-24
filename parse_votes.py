import glob
import os

import pandas as pd


def remove_extra_spaces(x):
    return ' '.join(x.split())

def parse_vote_file(vote_file_loc):

    print(f'Parsing {vote_file_loc}')

    names = [
        'index_increasing',
        'index_decreasing',
        'name_raw',
        'party_initials',
        'vote_encoded'
    ]

    # read metadata and check it matches expectations
    with open(vote_file_loc, 'r') as f:
        lines = f.readlines()
        # expect exactly 17 lines of metadata, 18th line first voter starting with 1
        assert lines[17].startswith('1')

        metadata_raw = lines[:17]
        metadata_clean = [remove_extra_spaces(line).lower().replace('-', '') for line in metadata_raw]
        # text before the first ":" is the key, text after the first ":" is the value
        # (there is another : in the datetime, hence this fiddle)
        metadata_key_value_tuples = [(line.split(':')[0], ''.join(line.split(':')[1:])) for line in metadata_clean]
        # print(metadata_key_value_tuples)
        # metadata = dict(metadata_key_value_tuples)
        metadata = pd.Series(data=dict(metadata_key_value_tuples))
        # print(metadata)

        # construct the vote index decoding based on metadata 'opcion1', 'opcion2', etc
        metadata_options = metadata[[x for x in metadata.index if x.startswith('opcion')]]
        metadata_options.index = [int(x.replace('opcion', '')) for x in metadata_options.index]
        encoded_vote_to_text_mapping = dict(metadata_options)
        # print(encoded_vote_to_text_mapping)
        # encoded_vote_to_text_mapping = {
        #     1: 'quorum',
        #     2: 'pro',
        #     3: 'abstencion',
        #     4: 'contra',
        #     5: 'total'
        # }

    # load the votes themselves
    df = pd.read_csv(vote_file_loc, header=17, names=names)

    # remove double spaces from names
    df['name'] = df['name_raw'].apply(remove_extra_spaces)

    df['vote_encoded'] = df['vote_encoded'].astype('int')
    df['vote'] = df['vote_encoded'].apply(lambda x: encoded_vote_to_text_mapping[x])

    # don't care about the indexes
    del df['index_increasing']
    del df['index_decreasing']
    # print(df.head())

    # add metadata
    # only the date, the hour is always the same
    df['date'] = metadata['fecha del voto'].lstrip(' ').split(' ')[0]
    # .split(' ')[0]  
    df['proposal'] = metadata['propuesta']
    # add the filename, to help distinguish e.g. voto1221-1 from voto1221-2
    # the proposals are often very slightly different
    df['proposal_id'] = os.path.basename(vote_file_loc).replace('.txt', '')

    # the VOTON metadata values are the same on every vote sheet, and don't match the vote totals
    # metadata_totals = metadata[[x for x in metadata.index if x.startswith('voto')]]
    # print(metadata_totals)
    # print(df['vote_encoded'].value_counts())

    save_loc = vote_file_loc.replace('/data/raw/', '/data/parsed/')
    df.to_csv(save_loc, index=False)

if __name__ == '__main__':

    # vote_file_loc = 'data/example.csv'
    # vote_file_loc = 'data/raw_vote_files/voto0116-1.txt'
    # parse_vote_file(vote_file_loc)

    # e.g. data/raw/voto50/ordi11/voto1031_1.txt
    for vote_file_loc in glob.glob('data/raw/*/*/*.txt'):
        parse_vote_file(vote_file_loc)
