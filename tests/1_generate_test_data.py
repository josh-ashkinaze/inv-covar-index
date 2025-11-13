"""
Author: Joshua Ashkinaze
Date: 2025-11-09
Description: Creates synthetic data to test icw_index against Stata's swindex.
"""

import numpy as np
import pandas as pd

np.random.seed(42)

all_data = []

for dataset_id in range(100):
    n_vars = 5
    n_obs = np.random.randint(500, 2000)

    # Ensure at least 100 in each group
    n_control = max(100, n_obs // 2)
    n_treat = n_obs - n_control

    data = np.random.randn(n_obs, n_vars)
    data = np.round(data, 2)
    df = pd.DataFrame(data, columns=[f'var{i + 1}' for i in range(n_vars)])
    df['dataset_id'] = dataset_id
    df['obs_id'] = range(n_obs)

    # Assign treatment status with guaranteed balance
    treat_status = np.concatenate([np.zeros(n_control), np.ones(n_treat)])
    np.random.shuffle(treat_status)
    df['treat_status'] = treat_status.astype(int)

    all_data.append(df)

combined_df = pd.concat(all_data, ignore_index=True)
combined_df.to_csv('test_datasets.csv', index=False)

do_file_content = """* Stata do file to run swindex on all test datasets
ssc install swindex
clear all
set more off

import delimited "test_datasets.csv", clear

gen control = (treat_status == 0)

file open results1 using "swindex_results.csv", write replace
file write results1 "dataset_id,obs_id,index_value" _n

file open results2 using "swindex_normby_results.csv", write replace
file write results2 "dataset_id,obs_id,index_value" _n

quietly levelsof dataset_id, local(datasets)
foreach ds in `datasets' {
    preserve
    keep if dataset_id == `ds'
    ds var*
    local varlist `r(varlist)'
    
    capture swindex `varlist', generate(anderson_index)
    if _rc == 0 {
        forvalues i = 1/`=_N' {
            local idx_val = anderson_index[`i']
            local obs = obs_id[`i']
            file write results1 "`ds',`obs',`idx_val'" _n
        }
    }
    
    capture swindex `varlist', generate(anderson_index_normby) normby(control)
    if _rc == 0 {
        forvalues i = 1/`=_N' {
            local idx_val = anderson_index_normby[`i']
            local obs = obs_id[`i']
            file write results2 "`ds',`obs',`idx_val'" _n
        }
    }
    
    restore
}

file close results1
file close results2
"""

with open('run_swindex.do', 'w') as f:
    f.write(do_file_content)

print("Created test_datasets.csv and run_swindex.do")