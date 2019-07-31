"""

ServerTask, a task to handle HTTP requests.

Created on Jul 19, 2019
                
@author: skwok
"""

import json
import socket
from utils.easyHTTP import EasyHTTPHandler, EasyHTTPServer, EasyHTTPServerThreaded
from utils.try_wrapper import tryEx

from models.arguments import Arguments

import traceback


class DRPF_server_handler (EasyHTTPHandler):
    """
    Handles the HTTP requests.
    """
    
    jsonText = "application/json"
    DRPFramework = None
    
    def _getParameters (self, qstr):
        for k, v in qstr.items():
            val = v[0]
            try:
                val = int(v[0])                
            except:
                try:
                    val = float(v[0])
                except:
                    val = v[0].strip()
            self.__dict__['_http_' + k] = val
    
    
    def get_pending_events (self, req, qstr):
        self._getParameters(qstr)
        events, events_hi = self.DRPFramework.getPendingEvents()        
        out = [ str(e) for e in events ]
        out_hi = [ str(e) for e in events_hi ]        
        return json.dumps({'events':out, 'events_hi': out_hi}), self.jsonText
    
    def add_next_file_event (self, req, qstr):
        self._getParameters(qstr)
        args = Arguments (name=self._http_file_name)
        self.DRPFramework.append_event ("next_file", args)
        return json.dumps("OK"), self.jsonText
    
    def add_create_contact_sheet_event(self, req, qstr):
        self._getParameters(qstr)
        out_dir = self.DRPFramework.config.output_directory
        args = Arguments(dir_name=out_dir, pattern="*.png",
                         out_name="contact_sheet.html", cnt=-1)
        self.DRPFramework.append_event ("contact_sheet", args)
        return json.dumps("OK"), self.jsonText
    
    def echo (self):
        self._getParameters(qstr)
        return json.dumps(qstr), self.PlainTextType            


def start_http_server (fw, config, logger):
    port = config.http_server_port        
    DRPF_server_handler.DocRoot = config.doc_root
    DRPF_server_handler.DRPFramework = fw
    httpd = EasyHTTPServerThreaded (("", port), DRPF_server_handler)
    hostname = socket.gethostname()
    logger.info ("HTTPD started %s %d" % (socket.gethostbyaddr(socket.gethostbyname(hostname)), port))
    logger.info ("DocRoot is " +  DRPF_server_handler.DocRoot)
    
    try:
        httpd.serve_forever()
        httpd.shutdown()
    except Exception as e:
        traceback.print_exc()
        logger.info ("HTTPD terminated")
