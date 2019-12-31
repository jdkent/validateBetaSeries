from ..faux_bold import CombineRestBold
import numpy as np
import nibabel as nib


def test_CombineRestBold():
    expected_out = 16
    base_img = nib.Nifti2Image(np.zeros((1, 1, 1, 10)), np.eye(4))
    second_img = nib.Nifti2Image(np.zeros((1, 1, 1, 10)), np.eye(4))

    num_discard = 5
    num_interp = 1
    combine_rest_bold = CombineRestBold(
        base_bold=base_img,
        second_bold=second_img,
        num_discard=num_discard,
        num_interp=num_interp,
        return_type='object')

    res = combine_rest_bold.run()

    assert res.outputs.faux_bold.shape[-1] == expected_out
