# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

"""
variables information for each time step is stored here:
"""


class SatBlock:
    def __str__(self):
        return (
            "Time Step: "
            + str(self.tstep)
            + "\n  mapping vertical (logical) vars: "
            + str(self.mlvars)
            + "\n  mapping horizontal (physical) vars: "
            + str(self.mpvars)
            + "\n  logic qubit pair vars: "
            + str(self.lq_pairs)
            + "\n  physical qubit pair vars: "
            + str(self.pq_pair_vars)
            + "\n  logic qubit pair dict: "
            + str(self.lq_pair_dict)
            + "\n  cnot vars: "
            + str(self.cnot_vars)
            + "\n  dict mapped cnot vars from cnots: "
            + str(self.cnot_var_dict)
            + "\n  predecessor cnot vars: "
            + str(self.pred_cnot_vars)
            + "\n  predecessor dict mapped cnot vars from cnots: "
            + str(self.pred_cnot_var_dict)
            + "\n  successor cnot vars: "
            + str(self.succ_cnot_vars)
            + "\n  successor dict mapped cnot vars from cnots: "
            + str(self.succ_cnot_var_dict)
            + "\n  swap distance logical qubit pair vars: "
            + str(self.sdistance_lqpairs)
            + "\n  zero distance logical qubit pair dict: "
            + str(self.zerod_lqpair_dict)
            + "\n  bridge logic qubit pair vars: "
            + str(self.bridge_lq_pairs)
            + "\n  bridge physical qubit pair vars: "
            + str(self.bridge_pq_pair_vars)
            + "\n  bridge logic qubit pair dict: "
            + str(self.bridge_lq_pair_dict)
            + "\n  bridge cnot vars: "
            + str(self.bridge_cnots)
            + "\n  bridge indicator variable (for choosing): "
            + str(self.bridge_ivar)
            + "\n  swap indication variable (for choosing): "
            + str(self.swap_ivar)
            + "\n  swap connection vars: "
            + str(self.swaps)
            + "\n  swap p vars: "
            + str(self.swaps_p)
            + "\n  witness logic qubit pair vars: "
            + str(self.witness_lpair_vars)
            + "\n  witness cnot vars: "
            + str(self.witness_cnot_vars)
            + "\n  witness logic qubit pair dict: "
            + str(self.witness_lq_pair_dict)
            + "\n  mapped p vars: "
            + str(self.mapped_pvars)
            + "\n  current cnot block var to indicate ALO true: "
            + str(self.cur_cnot_var)
            + "\n  cnot assumption ALO indicator var (for all previous blocks): "
            + str(self.cnot_ass_var)
            + "\n"
        )

    def __init__(self):
        self.tstep = -1
        self.mlvars = []
        self.mpvars = []
        self.lq_pairs = []
        self.pq_pair_vars = []
        self.lq_pair_dict = {}
        self.cnot_vars = []
        self.cnot_var_dict = {}
        # two way sat vars:
        self.pred_cnot_vars = []
        self.pred_cnot_var_dict = {}
        self.succ_cnot_vars = []
        self.succ_cnot_var_dict = {}
        # swap distance lq pair vars:
        self.sdistance_lqpairs = []
        self.zerod_lqpair_dict = {}
        # bridge vars:
        self.bridge_lq_pairs = []
        self.bridge_pq_pair_vars = []
        self.bridge_lq_pair_dict = {}
        self.bridge_cnots = []
        self.bridge_ivar = -1
        # swap vars:
        self.swap_ivar = -1
        self.swaps = []
        self.swaps_p = []
        # witness vars:
        self.witness_lpair_vars = []
        self.witness_cnot_vars = []
        self.witness_lq_pair_dict = {}
        # aux vars:
        self.mapped_pvars = []
        self.cur_cnot_var = -1
        self.cnot_ass_var = -1
