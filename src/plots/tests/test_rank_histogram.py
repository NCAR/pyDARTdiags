import pandas as pd
import numpy as np

# Example DataFrame setup
data = {
    'observation': [2.5, 3.0, 4.5],  # Actual observation values
    'obs_err_var': [0.1, 0.2, 0.3],  # Variance of the observation error
    'prior_ensemble_member1': [2.3, 3.1, 4.6],
    'prior_ensemble_member2': [2.4, 2.9, 4.4],
    'prior_ensemble_member3': [2.5, 3.2, 4.5]
}
df = pd.DataFrame(data)

# Call the function
rank, ens_size, _ = calculate_rank(df)

print("Rank:", rank)
print("Ensemble Size:", ens_size)
