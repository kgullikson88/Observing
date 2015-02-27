import pandas as pd


def create_worklist(df):
    """
    Create a worklist from a pandas dataframe with the columns:
     - Target (string)
     - RA  (in hex)
     - DEC (in hex)
     - mag (Apparent magnitude of the target. optional. float, if given)
     - spt (spectral type of the target. optional. string, if given)
     - epoch (optional. Assumes J2000 if not given)
    """

    if 'spt' not in df.keys():
        df['spt'] = [''] * len(df)
    if 'epoch' not in df.keys():
        df['epoch'] = ['2000.0'] * len(df)

    for i, row in df.iterrows():
        print i
        print row['mag']
        print row['epoch']
        if 'mag' in row.keys():
            outline = '{0:d}  "{1:.2f} {2:s} {3:s}  "   {4:s}  {5:s}  {6:s}  0.0  0.0'.format(i + 1, row['mag'],
                                                                                              row['spt'], row['Target'],
                                                                                              row['RA'], row['DEC'],
                                                                                              row['epoch'])
        else:
            outline = '{0:d}  "{2:s} {3:s}  "   {4:s}  {5:s}  {6:s}  0.0  0.0'.format(i + 1, row['spt'], row['Target'],
                                                                                      row['RA'], row['DEC'],
                                                                                      row['epoch'])
        print(outline)


def Split_RA_DEC(string, divider=" "):
    """
    Split an RA/DEC string
    """
    if "+" in string:
        ra, dec = string.split("+")
        lat = "+"
    elif "-" in string:
        ra, dec = string.split("-")
        lat = "-"
    else:
        # Something weird happened and there was no divider. Just return -1 for error purposes
        return -1, -1

    ra_hours = ra.split()[0]
    ra_mins = ra.split()[1]
    ra_sec = ra.split()[2]

    dec_deg = dec.split()[0]
    dec_mins = dec.split()[1]
    dec_sec = dec.split()[2]

    ra = ra_hours + divider + ra_mins + divider + ra_sec
    dec = lat + dec_deg + divider + dec_mins + divider + dec_sec

    return ra, dec


def get_unobserved():
    """
    Go through my sample spreadsheet, and find the targets which are not yet observed
    """
    import os

    # Read in my target list
    filename = '{}/Dropbox/School/Research/AstarStuff/TargetLists/Final_Sample.xls'.format(os.environ['HOME'])
    sample = pd.read_excel(filename, sheetname=3, header=8, na_values=['     ~'])[1:]

    # Keep only the un-observed targets
    good = sample.dropna(subset=['Observed?'])
    good = good.loc[good['Observed?'].astype(str).str.contains('0')]

    # Split the ra/dec field into ra and dec fields
    radec = good['RA/DEC (J2000)'].map(Split_RA_DEC)
    good['RA'] = radec.map(lambda l: l[0])
    good['DEC'] = radec.map(lambda l: l[1])

    # Rename some columns
    good.rename(columns={'Mag K': 'mag', 'identifier': 'Target', '  spec. type': 'spt'}, inplace=True)

    return good


def get_followup():
    import os
    import StarData

    # Read in the observed target list
    filename = '{}/Dropbox/School/Research/AstarStuff/TargetLists/Observed_Targets3.xls'.format(os.environ['HOME'])
    sample = pd.read_excel(filename, sheetname=0, na_values=['     ~'])[1:]
    sample['Mag K'] = sample.apply(lambda row: row['Mag K'] if pd.notnull(row['Mag K']) else row['Mag V'], axis=1)


    # Get the targets with a detection
    detections = sample.loc[sample['Detections'].notnull()]

    # Get the detections without follow-up
    followup = detections.groupby('identifier').filter(lambda df: df.shape[0] == 1)
    followup.reset_index(inplace=True, drop=True)

    # Split RA/DEC field
    radec = followup['RA/DEC (J2000)'].map(Split_RA_DEC)
    followup['RA'] = radec.map(lambda l: l[0])
    followup['DEC'] = radec.map(lambda l: l[1])

    # Rename columns
    followup.rename(columns={'Mag K': 'mag', 'identifier': 'Target'}, inplace=True)

    # Add the spectral type from simbad (not in the table for some silly reason)
    followup['spectype'] = followup['Target'].map(lambda star: StarData.GetData(star).spectype)
    followup['spt'] = followup.apply(lambda row: '{} + {}'.format(row['spectype'], row['Detections']), axis=1)

    return followup


if __name__ == '__main__':
    import sys

    if '--new' in sys.argv[1:]:
        df = get_unobserved()

    elif '--follow-up' in sys.argv[1:]:
        df = get_followup()

    else:
        print 'Must give one of the following command line arguments:'
        print '  - "--new": for a worklist of un-observed targets'
        print '  - "--follow-up": for a worklist of follow-up targets'

    # Print out the worklist
    create_worklist(df[['Target', 'RA', 'DEC', 'mag', 'spt']])