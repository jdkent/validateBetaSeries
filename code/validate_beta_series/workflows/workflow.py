"""
useful workflows for generating faux task bold
"""

from niworkflows.engine.workflows import LiterateWorkflow as Workflow
from nipype.pipeline import engine as pe
from nipype.interfaces import utility as niu
from ..interfaces.faux_bold import CombineRestBold

def init_faux_bold_wf(bids_layout, base_dir=None, name="faux_bold"):
    # create workflow
    wf = Workflow(name=name, base_dir=None)
    input_node = pe.Node(
        niu.IdentityInterface([
            'task_name',
            'num_discard',
            'num_interp']
        )
    )

    output_node = pe.Node(
        niu.IdentityInterface([
            'faux_bold_files'
        ])
    )

    combine_bold = pe.MapNode(CombineRestBold(),
                              iterfield=['base_bold',
                                         'second_bold'])

    