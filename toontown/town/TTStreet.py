from toontown.town.Street import Street

class TTStreet(Street):
    
    def enableTimeEffects(self):
        Street.enableTimeEffects(self)
        return
        
        self.loader.hood.startSpookySky()
        render.setColorScale(0.55, 0.55, 0.65, 1)
    
    def disableTimeEffects(self):
        Street.disableTimeEffects(self)
        return
        
        render.setColorScale(1, 1, 1, 1)