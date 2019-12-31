"""
useful workflows for generating faux task bold
"""

from niworkflows.engine.workflows import LiterateWorkflow as Workflow
from nipype.pipeline import engine as pe
from nipype.interfaces import utility as niu
from ..interfaces.faux_bold import CombineRestBold


def init_faux_bold_wf(bids_layout, base_dir=None, name="faux_bold"):
    # create workflow
    wf = Workflow(name=name, base_dir=base_dir)
    input_node = pe.Node(
        niu.IdentityInterface([
            'base_bold_list',
            'second_bold_list',
            'task_name',
            'num_discard',
            'num_interp']),
        name='input_node',
    )

    output_node = pe.Node(
        niu.IdentityInterface([
            'faux_bold_files']),
        name='output_node')

    combine_bold = pe.MapNode(CombineRestBold(return_type="file"),
                              iterfield=['base_bold',
                                         'second_bold'],
                              name='combine_node')

    participants = bids_layout.get_subjects()

    base_bold_list = []
    second_bold_list = []
    for participant in participants:
        for run, lst in zip([1, 2], [base_bold_list, second_bold_list]):
            try:
                bold_file = bids_layout.get(
                    task="rest",
                    extension=".nii.gz",
                    run=run,
                    subject=participant,
                    return_type='file',
                )[0]
            except IndexError:
                raise IndexError(f"{participant} does not have rest run: {run}")

            lst.append(bold_file)

    input_node.inputs.base_bold_list = base_bold_list
    input_node.inputs.second_bold_list = second_bold_list

    wf.connect([
        (input_node, combine_bold,
            [('base_bold_list', 'base_bold'),
             ('second_bold_list', 'second_bold'),
             ('task_name', 'task_name'),
             ('num_discard', 'num_discard'),
             ('num_interp', 'num_interp')]),
        (combine_bold, output_node,
            [('faux_bold', 'faux_bold_files')])
    ])

    return wf
