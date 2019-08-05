'''
Test data_set

Created on Jul 31, 2019

@author: skwok
'''

import sys
import models.data_set as data_set
from  utils.DRPF_logger import getLogger
import config.framework_config as framework_config

def classify (df):
    """
    For KCWI, IMTYPE can be OBJECT, CONTBARS, TWIFLAT, BIAS, ARCLAMP, FLATLAMP, DOMEFLAT, nan
    """
    #target_groups = df.groupby(["TARGNAME", "IMTYPE"])
    target_groups = df.groupby(["STATEID", "GROUPID", "TARGNAME"])
    print(target_groups)
    
    for gid, gr in target_groups:
        for rid, row in gr.iterrows():
            df.at[rid, "DRP_IMTYPE"] = row.IMTYPE
    return target_groups

if __name__ == "__main__":

    dirname = sys.argv[1]
    
    config = framework_config.ConfigClass("config.cfg")
    logger = getLogger(config.logger_config_file)
         
    ds = data_set.Data_set(dirname, logger, config)
    
    for f in sys.argv[1:]:
        ds.append_item(f)
        
    df = ds.data_table
    groups = classify (df)

    for gid, gr in groups:
        nfiles = len(gr)
        print (f"ConfID= {gid[0]}, GroupID= {gid[1]}, nr files= {nfiles}")

        sgr = gr.sort_index()
        
        for rid, row in sgr.iterrows():            
            print (rid, row.TTIME, row.TARGNAME, row.IMTYPE)
    
