"""
Interfaces to generate baseline contrasts
"""
from nipype.interfaces.base import (
    BaseInterfaceInputSpec, TraitedSpec, SimpleInterface,
    InputMultiPath, OutputMultiPath, File, Directory,
    traits, isdefined
    )


class GenTrialTypeBetaInputSpec(BaseInterfaceInputSpec):
    bold_file = File(exists=True, mandatory=True,
                     desc="The bold run")
    bold_metadata = traits.Dict(desc='Dictionary containing useful information about'
                                ' the bold_file')
    mask_file = File(exists=True, mandatory=True,
                     desc="Binarized nifti file indicating the brain")
    events_file = File(exists=True, mandatory=True,
                       desc="File that contains all events from the bold run")
    confounds_file = traits.Either(None, File(exists=True),
                                   desc="File that contains all usable confounds")
    selected_confounds = traits.Either(None, traits.List(),
                                       desc="Column names of the regressors to include")
    hrf_model = traits.String(desc="hemodynamic response model")
    smoothing_kernel = traits.Either(None, traits.Float(),
                                     desc="full wide half max smoothing kernel")
    high_pass = traits.Float(0.0078125, desc="the high pass filter (Hz)")


class GenTrialTypeBetaOutputSpec(TraitedSpec):
    predicted_bold = File(desc="predicted responses")


class GenTrialTypeBeta(SimpleInterface):
    input_spec = GenTrialTypeBetaInputSpec
    output_spec = GenTrialTypeBetaOutputSpec

    def _run_interface(self, runtime):
        from nistats import first_level_model
        import nibabel as nib
        import pandas as pd
        import numpy as np

        # get t_r from bold_metadata
        t_r = self.inputs.bold_metadata['RepetitionTime']

        # get the confounds:
        if self.inputs.confounds_file and self.inputs.selected_confounds:
            confounds = _select_confounds(self.inputs.confounds_file,
                                          self.inputs.selected_confounds)
        else:
            confounds = None

        # high_pass, switch from Hz to Period
        high_pass_period = int(1 / self.inputs.high_pass)

        # setup the model
        model = first_level_model.FirstLevelModel(
            t_r=t_r,
            slice_time_ref=0,
            hrf_model=self.inputs.hrf_model,
            mask=self.inputs.mask_file,
            smoothing_fwhm=self.inputs.smoothing_kernel,
            standardize=False,
            signal_scaling=0,
            period_cut=high_pass_period,
            drift_model='cosine',
            verbose=1,
        )

        events_df = pd.read_csv(self.inputs.events_file, sep="\t")
        trial_types = events_df['trial_types'].unique()

        model.fit(self.inputs.bold_file,
                  events=events_df,
                  confounds=confounds)

        design_matrix = model.design_matrices_[0]
        bold_img = nib.load(self.inputs.bold_file)
        predicted_out = np.zeros(bold_img.shape)
        for trial_type in trial_types:
            beta_map = model.compute_contrast(trial_type, output_type='effect_size')
            beta_map_ex = np.expand_dims(beta_map, axis=3)

            design_series = design_matrix[trial_type]
            brain_map = np.tile(design_series, bold_img.shape)

            predicted_out += beta_map_ex * brain_map

        fname = "predicted_task_bold.nii.gz"
        bold_img.__class__(predicted_out, bold_img.affine, bold_img.header).to_filename(fname)

        self._results['predicted_bold'] = fname

        return runtime


def _select_confounds(confounds_file, selected_confounds):
    """Process and return selected confounds from the confounds file
    Parameters
    ----------
    confounds_file : str
        File that contains all usable confounds
    selected_confounds : list
        List containing all desired confounds
    Returns
    -------
    desired_confounds : DataFrame
        contains all desired (processed) confounds.
    """
    import pandas as pd
    import numpy as np
    confounds_df = pd.read_csv(confounds_file, sep='\t', na_values='n/a')

    # fill the first value of FramewiseDisplacement with the mean.
    if 'FramewiseDisplacement' in selected_confounds:
        confounds_df['FramewiseDisplacement'] = confounds_df['FramewiseDisplacement'].fillna(
                                np.mean(confounds_df['FramewiseDisplacement']))

    desired_confounds = confounds_df[selected_confounds]
    return desired_confounds
