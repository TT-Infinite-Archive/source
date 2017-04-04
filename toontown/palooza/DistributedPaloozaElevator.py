'''
Created on Apr 4, 2017

@author: Drew
'''
from direct.distributed.DistributedObject import DistributedObject

class DistributedPaloozaElevator(DistributedObject):


    def __init__(self, cr):
        DistributedObject.__init__(self, cr)