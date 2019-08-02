"""
Basic DRP - CCD basic tasks

Created: 2019-07-30

@author: skwok
"""

import os
from pipelines.base_pipeline import Base_pipeline
from models.arguments import Arguments
from primitives.ccd_primitives import *

class ccd_basic_pipeline (Base_pipeline):
    """
    CCD basic tasks: bias, dark, flat        
    """

    #
    # Format for the entries
    # Event name : action, new state, next event
    #
    event_table = {
        "next_file": ("ingest_file", "file_ingested", "file_ingested"),
        "file_ingested": ("action_planner", None, None),
        "process_bias": ("process_bias", None, None),
        "process_arcs": ("process_arc", None, None),
        "process_flat": ("process_flat", None, None),
        "process_object": ("process_object", None, "save_png"),
        "save_png": ("save_png", None, None)        
    }

    def __init__(self):
        """
        Constructor
        """
        Base_pipeline.__init__(self)
    
    def ingest_file (self, action, context):
        context.data_set.append_item (action.args.name)
        try:
            v = context.data_set.getInfo (action.args.name, "IMTYPE")
        except:
            v = "Unknown"
            fname = os.path.basename(action.args.name)            
            self.logger.warn(f"Unknown IMTYPE {fname}")
        return Arguments (name=action.args.name, imtype=v)
    
    def action_planner (self, action, context):
        if action.args.imtype == "BIAS":
            bias_args = Arguments(name="bias_args",
                                  want_type="BIAS",
                                  new_type="MASTER_BIAS",
                                  min_files=context.config.instrument.bias_min_nframes,
                                  new_file_name="master_bias.fits")
            context.push_event("process_bias", bias_args)
        elif "FLAT" in action.args.imtype:
            context.push_event("process_flat", action.args)
        elif "ARC" in action.args.imtype:
            context.push_event("process_arc", action.args)
        elif "OBJECT" in action.args.imtype:
            context.push_event("process_object", action.args)
            
            
        return Arguments (name="new_action")

if __name__ == "__main__":
    """
    Standalone test
    """
    pass
