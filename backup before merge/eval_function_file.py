import numpy as np
import pandas as pd


response_path=r"C:\Users\joziv\Desktop\RDTeam\ABEC3\OMFE\Results\response.txt"

max_spl=145

'''
TODO: Add Max excursion check @2/3 AES power
TODO: Add Max air velocity check @2/3 AES power
'''

def compute_fitness(response_path,passband, tolerance):

    """
    Evaluate design

    Parameters:
    response_path (dataframe)   : Path to the frequency response,Order: Frequency [Hz], Magnitude [dB], Phase [Deg])
    passband (int)              : Frequencies to compute 
    tolerance (int)             : Phase rotation tolerance in [Deg]
    """

    df=response_path

    #Use Passband as reference for metric calculation
    band_df=df[(df['frequency']>=passband[0]) & (df['frequency']<=passband[1])].copy()
   
    #raise error if missing or corrupted data
    if band_df.empty:
        raise ValueError("No data in passband")
    
    #Compute metrics for evaluation step:

    #SPL metrics
    band_spl=band_df['spl'].values
    mean_spl=np.mean(band_spl)
    std_spl=np.std(band_spl)
    max_dev=np.max(np.abs(band_spl-mean_spl))
    cutoff=mean_spl-3
    cutoff_l=np.min(df[(df['spl']>cutoff)]['frequency'])
    cutoff_h=np.min(df[(df['spl']<cutoff) & (df['frequency']>60)]['frequency'])
    range=cutoff_h-cutoff_l

    #phase metrics
    # Convert phase to radians & unwrapp
    band_df["phase"]=np.unwrap(np.radians(band_df["phase"]))
    # Get ref_phase value at geometric center of BP
    phase_ref = band_df.loc[band_df["frequency"].sub(np.sqrt(passband[0]*passband[1])).abs().idxmin(), "phase"]
    tolerance=np.radians(tolerance/2)
    stable_phase_df = band_df[(band_df["phase"] >= phase_ref - tolerance) & 
                              (band_df["phase"] <= phase_ref + tolerance)]
    
    # Get min and max frequency bounds of the stable phase region
    f_min = stable_phase_df["frequency"].min()
    f_max = stable_phase_df["frequency"].max()

    band_df['gd']=-np.gradient(band_df['phase'],band_df['frequency'])
    gd_std=np.std(band_df['gd'])
    max_gd=band_df['gd'].max()

    #normalize & evaluate
    n_spl=mean_spl/max_spl          #Maximize sensitivity
    n_std= 1/(1+std_spl)            #Aim for a flat response  
    n_dev= 1/(1+max_dev)            #Avoid steep dips or hills
    n_range=np.min([1,range/200])   #Largest range possible

    stable_phase=f_max-f_min/range
    n_gstd= 1/(1+gd_std*10)         #minimize group delay
    n_maxgd=1/(1+max_gd*10)        #minimize group delay spikes

    return (n_spl, n_std,n_dev,n_range,stable_phase ,n_gstd , n_maxgd)
    #return (n_spl, n_spl,n_dev,n_range,stable_phase ,n_maxgd , n_maxgd)



