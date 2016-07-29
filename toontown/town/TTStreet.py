from toontown.town.Street import Street

class TTStreet(Street):
    
    def enableTimeEffects(self):
        if not base.cr.newsManager.isStormEnabled():
            Street.enableTimeEffects(self)
            return
        
        self.loader.hood.startSpookySky()
        render.setColorScale(0.55, 0.55, 0.65, 1)
    
    def disableTimeEffects(self):
        if not base.cr.newsManager.isStormEnabled():
            Street.disableTimeEffects(self)
            return
        
        render.setColorScale(1, 1, 1, 1)