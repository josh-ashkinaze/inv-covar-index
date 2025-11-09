* Stata do file to run swindex on all test datasets
ssc install swindex
clear all
set more off

* Load the data
import delimited "test_datasets.csv", clear

* Create a file to store results
file open results using "swindex_results.csv", write replace
file write results "dataset_id,index_value" _n

* foreach dataset, do the swindex...
quietly levelsof dataset_id, local(datasets)
foreach ds in `datasets' {

    preserve

    * Keep only this dataset
    keep if dataset_id == `ds'

    * Get list of variable columns (exclude dataset_id and obs_id)
    ds var*
    local varlist `r(varlist)'

    * Run swindex
    capture swindex `varlist', generate(anderson_index)

    if _rc == 0 {
        * Save the index values to results file
        forvalues i = 1/`=_N' {
            local idx_val = anderson_index[`i']
            file write results "`ds',`idx_val'" _n
        }
    }
    else {
        display "Error running swindex for dataset `ds'"
    }

    restore
}

file close results

display "Results saved to swindex_results.csv"
