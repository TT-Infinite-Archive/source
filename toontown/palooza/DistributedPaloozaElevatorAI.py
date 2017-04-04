'''
Created on Apr 4, 2017

@author: Drew
'''
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedPaloozaElevatorAI(DistributedObjectAI):


    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)