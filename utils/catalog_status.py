class Catalogstatus:
    def __init__(self,catalogname,index_build_status=False):
        self.catalogname = catalogname
        self.index_build_status=index_build_status


    def update_status(self,index):
        self.index_build_status=index