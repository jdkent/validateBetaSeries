import bids
from validate_beta_series.workflows.workflow import init_faux_bold_wf

layout = bids.layout.BIDSLayout('data/bids')

faux_bold_wf = init_faux_bold_wf(layout)

faux_bold_wf.inputs.input_node.num_interp = 1

faux_bold_wf.inputs.input_node.num_discard = 10

faux_bold_wf.inputs.input_node.task_name = 'fauxbold'

faux_bold_wf.run()
