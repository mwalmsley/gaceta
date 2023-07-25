import glob
import os

import pandas as pd


def remove_extra_spaces(x):
    return ' '.join(x.split())

def parse_vote_file(vote_file_loc):

    # skip these badly formatted text files
    # some could be fixable if really needed
    files_to_skip = [
        'data/raw/voto60/ordi11/voto1017-1.txt',  # weird table
        'data/raw/voto60/ordi21/voto0913-15.txt',  # includes "0" votes
        'data/raw/voto63/ordi12/voto0315-1.txt',  # includes trailing characters
        'data/raw/voto60/ordi21/voto0913-20.txt', # includes "0" votes
        'data/raw/voto63/ordi32/voto0410-1.txt',  # stray )
        'data/raw/voto63/ordi32/voto0410-2.txt' # stray )
    ]

    if vote_file_loc in files_to_skip:
        print(f'Skipping known exception, {vote_file_loc}')
        return None

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
        # Parsing data/raw/voto63/ordi32/voto0410-1.txt
        # edge case, extra text
        # if 'voto59' in vote_file_loc:
        #     # slightly different format
        #     metadata_end_line = 26
        #     metadata_options_key = 'option'
        # else:
            
        metadata_end_line = 16
        metadata_options_key = 'opcion'
        # print(lines[metadata_end_line])
        assert lines[metadata_end_line].startswith('VOTO5'), ValueError(lines[:20])

        metadata_raw = lines[:metadata_end_line]
        metadata_clean = [remove_extra_spaces(line).lower().replace('-', '') for line in metadata_raw]
        # text before the first ":" is the key, text after the first ":" is the value
        # (there is another : in the datetime, hence this fiddle)
        metadata_key_value_tuples = [(line.split(':')[0], ''.join(line.split(':')[1:])) for line in metadata_clean]
        metadata = pd.Series(data=dict(metadata_key_value_tuples))
        # construct the vote index decoding based on metadata 'opcion1', 'opcion2', etc
        metadata_options = metadata[[x for x in metadata.index if x.startswith(metadata_options_key)]]
        metadata_options.index = [int(x.replace(metadata_options_key, '')) for x in metadata_options.index]
        encoded_vote_to_text_mapping = dict(metadata_options)
        # e.g. (and I think, always) = {
        #     1: 'quorum',
        #     2: 'pro',
        #     3: 'abstencion',
        #     4: 'contra',
        #     5: 'total'
        # }

    # load the votes themselves
    df = pd.read_csv(vote_file_loc, header=metadata_end_line+1, names=names)

    # remove double spaces from names
    df['name'] = df['name_raw'].apply(remove_extra_spaces)

    df['vote_encoded'] = df['vote_encoded'].astype('int')
    df['vote'] = df['vote_encoded'].apply(lambda x: encoded_vote_to_text_mapping[x])

    # don't care about the indexes
    del df['index_increasing']
    del df['index_decreasing']

    # add metadata
    # only the date, the hour is always the same
    df['date'] = metadata['fecha del voto'].lstrip(' ').split(' ')[0]
    # .split(' ')[0]  
    df['proposal'] = metadata['propuesta']
    # add the filename, to help distinguish e.g. voto1221-1 from voto1221-2
    # the proposals are often very slightly different
    df['proposal_id'] = '/'.join(vote_file_loc.replace('.txt', '').split('/')[-3:])
    # print(df['proposal_id'][0])
    # exit()

    # add some extra timing metadata from the file path
    parent_folder = os.path.basename(os.path.dirname(vote_file_loc))
    # e.g. ordi11, extra11
    year_and_period = parent_folder.replace('ordi', '').replace('extra', '')
    df['parliament_year'] = int(year_and_period[0])
    df['parliament_period_of_year'] = int(year_and_period[1])
    grandparent_folder = os.path.basename(os.path.dirname(os.path.dirname(vote_file_loc)))
    # e.g. voto58
    df['parliament_mandate'] = int(grandparent_folder.replace('voto', ''))
    filename = os.path.basename(vote_file_loc)
    # e.g. voto1231_1.txt
    df['nth_vote_of_day'] = int(filename.split('-')[-1].replace('.txt', ''))

    # I don't know what the VOTO1 etc. metadata values are tbh
    # they don't match the vote totals

    save_loc = vote_file_loc.replace('data/raw/', 'data/parsed/')

    assert save_loc != vote_file_loc  # don't accidentally overwrite the raw data (oops)
    if not os.path.isdir(os.path.dirname(save_loc)):
        os.makedirs(os.path.dirname(save_loc))
    df.to_csv(save_loc, index=False)


if __name__ == '__main__':

    # e.g. data/raw/voto50/ordi11/voto1031_1.txt
    # print(glob.glob('data/raw/*/*/*.txt'))
    for vote_file_loc in glob.glob('data/raw/*/*/*.txt'):
        parse_vote_file(vote_file_loc)
 