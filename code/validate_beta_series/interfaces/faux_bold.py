"""
generate faux task bold images from rest data.
"""

from nipype.interfaces.base import (
    BaseInterfaceInputSpec, TraitedSpec, SimpleInterface,
    InputMultiPath, OutputMultiPath, File, Directory,
    traits, isdefined
    )


class CombineRestBoldInputSpec(BaseInterfaceInputSpec):
    base_bold = traits.File(exists=True, desc="initial bold image")
    second_bold = traits.File(exists=True, desc="second bold image")
    task_name = traits.Str(default_value="fauxtask", desc="task name for the output file")
    num_discard = traits.Int(desc="number of volumes to discard from second_bold")
    num_interp = traits.Int(desc="number of interpolation steps")


class CombineRestBoldOutputSpec(TraitedSpec):
    faux_bold = traits.File(desc="output bids file for fake task")


class CombineRestBold(SimpleInterface):
    input_spec = CombineRestBoldInputSpec
    output_spec = CombineRestBoldOutputSpec

    def _run_interface(self, runtime):
        import nibabel as nib
        import numpy as np
        import re

        base_img = nib.load(self.inputs.base_bold)
        second_img = nib.load(self.inputs.second_bold)

        base_data = base_img.get_fdata()
        base_data_ref = base_data[:, :, :, -1]
        second_data = second_img.get_fdata()[:, :, :, self.inputs.num_discard:]
        second_data_ref = second_data[:, :, :, 0]

        interpolated_volumes = np.linspace(
            base_data_ref, second_data_ref,
            num=self.inputs.num_interp, axis=-1,
            endpoint=False)[:, :, :, 1:]

        new_data = np.concatenate(
            (base_data, interpolated_volumes, second_data),
            axis=3)

        new_task_name = self.inputs.task_name
        pattern = "(.*task-)[A-Za-z0-9]+(.*)run-[0-9]+_(.*)"
        fname = re.sub(pattern, fr"\g<1>{new_task_name}\g<2>\g<3>", self.inputs.base_bold)
        base_img.__class__(new_data, base_img.affine, base_img.header).to_filename(fname)

        self._results['faux_bold'] = fname

        return runtime


class AddBoldResponseInputSpec(BaseInterfaceInputSpec):
    faux_bold = File(exists=True, desc="the generated faux bold")
    predicted_bold = File(exists=True, desc="the predicted bold from the task")


class AddBoldResponseOutputSpec(TraitedSpec):
    faux_task_bold = File(desc="not useful")


class AddBoldResponse(SimpleInterface):
    pass
