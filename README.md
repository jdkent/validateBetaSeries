# Overview

## Create Fake task data

1. combine the resting state runs to create fake task
    - cut the first 10 volumes off the second run
    - create an interpolation volume to switch between the the final volume of the first
      run   to the "first" volume of second run.
    - 240 volumes first run + 230 volumes second run + 1 interpolation volume = 471 volumes
    - 471 volumes is the number of taskswitch volumes

1. use fmriprep outputs in T1w space to create relevant task contrasts (trial_type relative to baseline)
1. use the output betas (`effect_size`) for each trial_type to create a predicted timecourse for the bold images using (`events.tsv`)
1. add the predicted timecourses to the t1w_bold image.
1. apply inverse xforms to change t1w motion-corrected bold (with betas added) to original space:
    - json file indicates location of transforms: `single_subject_GE120069_wf/func_preproc_ses_post_task_rest_run_1_wf/bold_t1_trans_wf/merge_xforms/_0x7acc6dfbc12966c86e8ef8a1d9673883.json`
    - pass invert_transform_flags to `MultiApplyTransforms`.
1. run fmriprep again on the faux task data.
1. run nibetaseries on the faux task data.
