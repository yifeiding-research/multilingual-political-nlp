import pandas as pd

lux_df = pd.read_excel('./political_influencers_Luxembourg_NEW.xlsx')

luxembourg_channels = [
    'Alternativ Demokratesch Reformpartei',
    'SvenClementClips',
    'Clara Moraru',
    'Zentrum fir politesch Bildung',
    'Paperjam',
    'Ruche33',
    'Brend Kersai',
    'Communauté des Français du Luxembourg (CFL)'
]

lux_filtered = lux_df[lux_df['channel_name'].isin(luxembourg_channels)]

print(f"Original: {len(lux_df)} videos")
print(f"Filtered: {len(lux_filtered)} videos")
print(f"\nChannels kept: {lux_filtered['channel_name'].nunique()}")
print(lux_filtered['channel_name'].value_counts())

lux_filtered.to_excel('political_influencers_Luxembourg_FILTERED.xlsx', index=False)
print("\nSaved: political_influencers_Luxembourg_FILTERED.xlsx")