import numpy as np

# minimal weighted average variance
def WAV(L_A, L_B, n):
    WAV = (len(L_A)/n) * np.var(L_A) + (len(L_B)/n) * np.var(L_B)
    return WAV

def binary_partition(L, Vthresh):
    n = len(L)
    # Find the optimal split index.
    delta_V = 0
    split_inx = None
    
    for inx in range(1, n):
        L_A = L.iloc[:inx]
        L_B = L.iloc[inx:]
        delta = np.var(L) - WAV(L_A, L_B, n)
        if delta > delta_V:
            delta_V = delta
            split_inx = inx
            
    if (split_inx is None) or (delta_V < Vthresh):
        return [L]
    else:
        L_A = L.iloc[:split_inx]
        L_B = L.iloc[split_inx:]
        return binary_partition(L_A, Vthresh) + binary_partition(L_B, Vthresh)
    
def V_clustering(L, Vthresh):
    v_cluster = binary_partition(L, Vthresh)
    # labels mapping
    labels = []
    for inx, cluster in enumerate(v_cluster):
        labels.extend([inx] * len(cluster))
    return labels