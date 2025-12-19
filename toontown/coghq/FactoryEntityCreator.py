from otp.level import EntityCreator
from . import FactoryLevelMgr
from . import PlatformEntity
from . import ConveyorBelt
from . import GearEntity
from . import PaintMixer
from . import GoonClipPlane
from . import MintProduct
from . import MintProductPallet
from . import MintShelf
from . import PathMasterEntity
from . import RenderingEntity

class FactoryEntityCreator(EntityCreator.EntityCreator):

    def __init__(self, level):
        EntityCreator.EntityCreator.__init__(self, level)
        notlocal = EntityCreator.notlocal
        self.privRegisterTypes({'activeCell': notlocal,
         'crusherCell': notlocal,
         'battleBlocker': notlocal,
         'beanBarrel': notlocal,
         'button': notlocal,
         'conveyorBelt': ConveyorBelt.ConveyorBelt,
         'crate': notlocal,
         'door': notlocal,
         'directionalCell': notlocal,
         'gagBarrel': notlocal,
         'gear': GearEntity.GearEntity,
         'goon': notlocal,
         'gridGoon': notlocal,
         'golfGreenGame': notlocal,
         'goonClipPlane': GoonClipPlane.GoonClipPlane,
         'grid': notlocal,
         'healBarrel': notlocal,
         'levelMgr': FactoryLevelMgr.FactoryLevelMgr,
         'lift': notlocal,
         'mintProduct': MintProduct.MintProduct,
         'mintProductPallet': MintProductPallet.MintProductPallet,
         'mintShelf': MintShelf.MintShelf,
         'mover': notlocal,
         'paintMixer': PaintMixer.PaintMixer,
         'pathMaster': PathMasterEntity.PathMasterEntity,
         'rendering': RenderingEntity.RenderingEntity,
         'platform': PlatformEntity.PlatformEntity,
         'sinkingPlatform': notlocal,
         'stomper': notlocal,
         'stomperPair': notlocal,
         'laserField': notlocal,
         'securityCamera': notlocal,
         'elevatorMarker': notlocal,
         'trigger': notlocal,
         'moleField': notlocal,
         'maze': notlocal})
