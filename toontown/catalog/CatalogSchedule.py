from .Catalog import WeeklyCatalog, SeasonalCatalog, YearlyCatalog, MetaItem
from datetime import datetime


from .CatalogAccessoryItem import CatalogAccessoryItem as Accessory
from .CatalogClothingItem import CatalogClothingItem as Clothing
from .CatalogFurnitureItem import CatalogFurnitureItem as Furniture
from .CatalogAnimatedFurnitureItem import CatalogAnimatedFurnitureItem as AnimatedFurniture
from .CatalogWallpaperItem import CatalogWallpaperItem as Wallpaper
from .CatalogChatItem import CatalogChatItem as ChatPhrase
from .CatalogNametagItem import CatalogNametagItem as Nametag
from .CatalogWainscotingItem import CatalogWainscotingItem as Wainscoting
from .CatalogMouldingItem import CatalogMouldingItem as Moulding
from .CatalogFlooringItem import CatalogFlooringItem as Flooring
from .CatalogGardenItem import CatalogGardenItem as GardenProp
from .CatalogGardenStarterItem import CatalogGardenStarterItem as GardenStarter
from .CatalogEmoteItem import CatalogEmoteItem as Emote
from .CatalogRentalItem import CatalogRentalItem as Rental
from .CatalogToonStatueItem import CatalogToonStatueItem as ToonStatue
from .CatalogWindowItem import CatalogWindowItem as Window


JANUARY = 1
FEBRUARY = 2
MARCH = 3
APRIL = 4
MAY = 5
JUNE = 6
JULY = 7
AUGUST = 8
SEPTEMBER = 9
OCTOBER = 10
NOVEMBER = 11
DECEMBER = 12

NO_YEAR = 2003

AllSeasonalCatalogs = (

    # Accessory Schedule #

    SeasonalCatalog(
        datetime(month=JANUARY, day=1, year=NO_YEAR), datetime(month=FEBRUARY, day=28, year=NO_YEAR),
        items=[Accessory(440), Accessory(425), Accessory(158),
               Accessory(431), Accessory(420), Accessory(155),
               Accessory(419), Accessory(436), Accessory(428),
               Accessory(304), Accessory(301), Accessory(416),
               Accessory(414), Accessory(164), Accessory(323),
               Accessory(108), Accessory(139), Accessory(316),
               Accessory(131), Accessory(170), Accessory(221),
               Accessory(225)]
    ),

    SeasonalCatalog(
        datetime(month=MARCH, day=1, year=NO_YEAR), datetime(month=APRIL, day=30, year=NO_YEAR),
        items=[Accessory(305), Accessory(303), Accessory(144),
               Accessory(120), Accessory(116), Accessory(217),
               Accessory(218), Accessory(219), Accessory(445),
               Accessory(418), Accessory(432), Accessory(427),
               Accessory(423), Accessory(137), Accessory(163),
               Accessory(165), Accessory(153), Accessory(319),
               Accessory(154), Accessory(159), Accessory(162),
               Accessory(315), Accessory(160), Accessory(102)]
    ),

    SeasonalCatalog(
        datetime(month=MAY, day=1, year=NO_YEAR), datetime(month=JUNE, day=30, year=NO_YEAR),
        items=[Accessory(119), Accessory(136), Accessory(169),
               Accessory(140), Accessory(168), Accessory(138),
               Accessory(220), Accessory(433), Accessory(442),
               Accessory(424), Accessory(404), Accessory(156),
               Accessory(142), Accessory(152), Accessory(133),
               Accessory(166), Accessory(211), Accessory(314),
               Accessory(320), Accessory(173), Accessory(328),
               Accessory(329)]
    ),

    SeasonalCatalog(
        datetime(month=JULY, day=1, year=NO_YEAR), datetime(month=AUGUST, day=31, year=NO_YEAR),
        items=[Accessory(101), Accessory(103), Accessory(112),
               Accessory(113), Accessory(114), Accessory(115),
               Accessory(117), Accessory(118), Accessory(123),
               Accessory(124), Accessory(125), Accessory(126),
               Accessory(127), Accessory(128), Accessory(129),
               Accessory(130), Accessory(202), Accessory(204),
               Accessory(205), Accessory(206), Accessory(208),
               Accessory(209), Accessory(210), Accessory(302),
               Accessory(308), Accessory(309), Accessory(310),
               Accessory(317), Accessory(402), Accessory(403),
               Accessory(405), Accessory(406), Accessory(407),
               Accessory(408), Accessory(409), Accessory(410),
               Accessory(411), Accessory(412), Accessory(413)]
    ),

    SeasonalCatalog(
        datetime(month=SEPTEMBER, day=1, year=NO_YEAR), datetime(month=OCTOBER, day=31, year=NO_YEAR),
        items=[Accessory(306), Accessory(318), Accessory(121),
               Accessory(212), Accessory(214), Accessory(312),
               Accessory(150), Accessory(151), Accessory(147),
               Accessory(422), Accessory(141), Accessory(146),
               Accessory(444), Accessory(122), Accessory(430),
               Accessory(145), Accessory(132), Accessory(161),
               Accessory(134), Accessory(149), Accessory(207),
               Accessory(215), Accessory(216), Accessory(417),
               Accessory(222), Accessory(321), Accessory(322),
               Accessory(307), Accessory(135), Accessory(174)]
    ),

    SeasonalCatalog(
        datetime(month=NOVEMBER, day=1, year=NO_YEAR), datetime(month=DECEMBER, day=31, year=NO_YEAR),
        items=[Accessory(434), Accessory(435), Accessory(441),
               Accessory(446), Accessory(429), Accessory(110),
               Accessory(148), Accessory(443), Accessory(426),
               Accessory(439), Accessory(143), Accessory(313),
               Accessory(311), Accessory(437), Accessory(415),
               Accessory(167), Accessory(157), Accessory(106),
               Accessory(109), Accessory(421), Accessory(401),
               Accessory(447), Accessory(213), Accessory(330)]
    ),

    # End of Accessory Schedule #


    # Halloween Items

    SeasonalCatalog(
        datetime(month=OCTOBER, day=3, year=NO_YEAR), datetime(month=NOVEMBER, day=2, year=NO_YEAR),
        metaItems=[MetaItem(2900, count=3)],
        items=[Clothing(1801, 0), Clothing(1001, 0), Clothing(1002, 0),
               Wallpaper(10100), Wallpaper(10200), Furniture(10000),
               Furniture(10010), Nametag(9), Clothing(1744, 0),
               Clothing(1745, 0), Clothing(1748, 0), Clothing(1771, 0),
               Clothing(1774, 0), Clothing(1775, 0), Clothing(1743, 0),
               Clothing(1746, 0), Clothing(1747, 0), Clothing(1112, 0),
               Clothing(1113, 0), Clothing(1114, 0), Clothing(1115, 0),
               Clothing(1116, 0), Clothing(1117, 0), Clothing(1118, 0),
               Clothing(1119, 0), Clothing(1120, 0), Clothing(1121, 0),
               Clothing(1122, 0), Clothing(1123, 0), Clothing(1124, 0),
               Clothing(1125, 0), Clothing(1126, 0), Clothing(1127, 0),
               Accessory(171), Accessory(172), Accessory(224),
               Accessory(324), Accessory(325), Accessory(326),
               Accessory(327), Accessory(448), Accessory(449),
               ChatPhrase(10003)]
    ),

    # Valentine's Day Items

    SeasonalCatalog(
        datetime(month=FEBRUARY, day=1, year=NO_YEAR), datetime(month=FEBRUARY, day=28, year=NO_YEAR),
        metaItems=[MetaItem(2920, count=3), MetaItem(2921, count=2)],
        items=[Clothing(1200, 0), Clothing(1201, 0), Clothing(1202, 0),
               Clothing(1203, 0), Clothing(1204, 0), Clothing(1205, 0),
               Wallpaper(12000), Wallpaper(12100), Wallpaper(12200),
               Wallpaper(12300), Wainscoting(1030, 0), Wainscoting(1030, 1),
               Moulding(1060, 0), Moulding(1060, 1), Clothing(1206, 0),
               Clothing(1207, 0), Clothing(1208, 0), Clothing(1209, 0),
               Clothing(1210, 0), Clothing(1211, 0), Clothing(1212, 0),
               Furniture(1670), Furniture(1680), Furniture(1450),
               Moulding(1100, 0), Moulding(1110, 0), Moulding(1120, 0)]
    ),

    # Saint Patrick's Day Items

    SeasonalCatalog(
        datetime(month=MARCH, day=1, year=NO_YEAR), datetime(month=MARCH, day=20, year=NO_YEAR),
        metaItems=[MetaItem(2930, count=3)],
        items=[Clothing(1300, 0), Clothing(1301, 0), Clothing(1302, 0),
               Clothing(1303, 0), Clothing(1304, 0), Clothing(1305, 0),
               Clothing(1306, 0), Wallpaper(13000), Wallpaper(13100),
               Wallpaper(13200), Wallpaper(13300), Flooring(11000),
               Flooring(11010)]
    ),

    # ???

    SeasonalCatalog(
        datetime(month=MAY, day=25, year=NO_YEAR), datetime(month=JUNE, day=25, year=NO_YEAR),
        items=[Clothing(1400, 0), Clothing(1401, 0), Clothing(1402, 0)],
    ),

    # ???

    SeasonalCatalog(
        datetime(month=AUGUST, day=1, year=NO_YEAR), datetime(month=AUGUST, day=31, year=NO_YEAR),
        items=[Clothing(1403, 0), Clothing(1404, 0), Clothing(1405, 0),
               Clothing(1406, 0)],
    ),

    # ???

    SeasonalCatalog(
        datetime(month=SEPTEMBER, day=24, year=NO_YEAR), datetime(month=OCTOBER, day=24, year=NO_YEAR),
        items=[AnimatedFurniture(460), AnimatedFurniture(270), AnimatedFurniture(990),
               Furniture(450)],
    ),

    # Estate/Doodle Party Phrases

    SeasonalCatalog(
        datetime(month=JUNE, day=15, year=2010), datetime(month=AUGUST, day=15, year=2010),
        metaItems=[MetaItem(2940, count=4)]
    ),

    # Flappy Cog Garden Prop

    SeasonalCatalog(
        datetime(month=SEPTEMBER, day=1, year=NO_YEAR), datetime(month=SEPTEMBER, day=30, year=NO_YEAR),
        items=[GardenProp(135, 1)],
    ),

    SeasonalCatalog(
        datetime(month=JANUARY, day=1, year=NO_YEAR), datetime(month=JANUARY, day=31, year=NO_YEAR),
        items=[GardenProp(135, 1)],
    ),

    SeasonalCatalog(
        datetime(month=APRIL, day=1, year=NO_YEAR), datetime(month=APRIL, day=30, year=NO_YEAR),
        items=[GardenProp(135, 1)],
    ),

    SeasonalCatalog(
        datetime(month=JUNE, day=1, year=NO_YEAR), datetime(month=JUNE, day=30, year=NO_YEAR),
        items=[GardenProp(135, 1)],
    ),

    # Fourth of July Items

    SeasonalCatalog(
        datetime(month=JUNE, day=26, year=NO_YEAR), datetime(month=JULY, day=16, year=NO_YEAR),
        items=[Clothing(1500, 0), Clothing(1501, 0), Clothing(1502, 0),
               Clothing(1503, 0)],
    ),

    # Summer Shirts

    SeasonalCatalog(
        datetime(month=JUNE, day=5, year=NO_YEAR), datetime(month=JULY, day=1, year=NO_YEAR),
        items=[Clothing(1768, 0), Clothing(1769, 0)],
    ),

    # Christmas Items

    SeasonalCatalog(
        datetime(month=DECEMBER, day=4, year=NO_YEAR), datetime(month=JANUARY, day=4, year=NO_YEAR),
        metaItems=[MetaItem(2910, count=3)],
        items=[Furniture(680), Furniture(681), GardenProp(130, 1),
               GardenProp(131, 1), AnimatedFurniture(10020), Furniture(10030, 0),
               Wallpaper(11000), Wallpaper(11100), Flooring(10010),
               Moulding(1090, 0), Clothing(1100, 0), Clothing(1101, 0),
               Clothing(1104, 0), Clothing(1105, 0), Clothing(1108, 0),
               Clothing(1109, 0), Clothing(1802, 0), Furniture(1040),
               Furniture(1050), Wallpaper(11200), Flooring(10000),
               Moulding(1080, 0), Moulding(1085, 0), Clothing(1102, 0),
               Clothing(1103, 0), Clothing(1106, 0), Clothing(1107, 0),
               Clothing(1110, 0), Clothing(1111, 0)]
    ),

)

PermenantCatalog = YearlyCatalog(items=[
    GardenProp(100, 1), GardenProp(101, 1), GardenProp(103, 1), GardenProp(104, 1),
    GardenStarter(),
    ToonStatue(105, endPoseIndex=108),
    # Rental(1, 2880, 1000),
    Nametag(100), Nametag(0),
    Clothing(1608, 0, 0), Clothing(1605, 0, 0), Clothing(1602, 0, 0),
    Clothing(1607, 0, 0), Clothing(1604, 0, 0), Clothing(1601, 0, 0),
    Clothing(1606, 0, 0), Clothing(1603, 0, 0), Clothing(1600, 0, 0),
    Emote(20, 0), Emote(21, 0), Emote(22, 0), Emote(23, 0), Emote(24, 0)]
)

AllWeeklyCatalogs = (
    WeeklyCatalog(
        series=1, number=1,
        metaItems=[MetaItem(100), MetaItem(2000, count=5), MetaItem(3000),
                   MetaItem(3500), MetaItem(4000), MetaItem(4500)],
        items=[Emote(5), Furniture(210, 0), Furniture(220, 0)]),

    WeeklyCatalog(
        series=1, number=2,
        metaItems=[MetaItem(100), MetaItem(2000, count=5), MetaItem(3000),
                   MetaItem(3500), MetaItem(4000), MetaItem(4500)],
        items=[Furniture(600), Furniture(610), Clothing(116, 0),
               Clothing(216, 0), Furniture(1400)]),

    WeeklyCatalog(
        series=1, number=3,
        metaItems=[MetaItem(300), MetaItem(2000, count=5), MetaItem(3000),
                   MetaItem(3500), MetaItem(4000), MetaItem(4500), MetaItem(5000)],
        items=[Furniture(1100), Furniture(1020), Furniture(1410), Clothing(408, 0)]),

    WeeklyCatalog(
        series=1, number=4, isSale=False,
        newRod=True, newCloset=True,
        metaItems=[MetaItem(100, count=1), MetaItem(2000, count=5), MetaItem(3000, count=1),
                   MetaItem(3500, count=1), MetaItem(4000, count=1), MetaItem(4500, count=1), ],
        items=[Window(40), Furniture(110), Furniture(100), ]
    ),

    WeeklyCatalog(
        series=1, number=5, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2000, count=5), MetaItem(3000, count=1),
                   MetaItem(3500, count=1), MetaItem(4000, count=1), MetaItem(4500, count=1), ],
        items=[Furniture(1420), Emote(9), Furniture(700), Furniture(710),
               ]
    ),

    WeeklyCatalog(
        series=1, number=6, isSale=False,
        newRod=False, newCloset=True,
        metaItems=[MetaItem(300, count=1), MetaItem(2000, count=5), MetaItem(3000, count=1),
                   MetaItem(3500, count=1), MetaItem(4000, count=1), MetaItem(4500, count=1), ],
        items=[Furniture(410), AnimatedFurniture(490), Furniture(1000), Clothing(117, 0),
               Clothing(217, 0), ]
    ),

    WeeklyCatalog(
        series=1, number=7, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2000, count=5), MetaItem(3000, count=1),
                   MetaItem(3500, count=1), MetaItem(4000, count=1), MetaItem(4500, count=1),
                   MetaItem(5000, count=1), ],
        items=[Furniture(1430), Furniture(1510), Furniture(1610), Nametag(1),
               ]
    ),

    WeeklyCatalog(
        series=1, number=8, isSale=False,
        newRod=True, newCloset=True,
        metaItems=[MetaItem(100, count=1), MetaItem(2000, count=5), MetaItem(3000, count=1),
                   MetaItem(3500, count=1), MetaItem(4000, count=1), MetaItem(4500, count=1), ],
        items=[Window(70), Furniture(1210), Clothing(409, 0), ]
    ),

    WeeklyCatalog(
        series=1, number=9, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(2000, count=5), MetaItem(3000, count=1),
                   MetaItem(3500, count=1), MetaItem(4000, count=1), MetaItem(4500, count=1), ],
        items=[Emote(13), Furniture(1200), Furniture(900), ]
    ),

    WeeklyCatalog(
        series=1, number=10, isSale=False,
        newRod=False, newCloset=True,
        metaItems=[MetaItem(100, count=1), MetaItem(2000, count=5), MetaItem(3000, count=1),
                   MetaItem(3500, count=1), MetaItem(4000, count=1), MetaItem(4500, count=1), ],
        items=[Furniture(910), Furniture(1600), Clothing(118, 0), Clothing(218, 0),
               ]
    ),

    WeeklyCatalog(
        series=1, number=11, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2000, count=5), MetaItem(3000, count=1),
                   MetaItem(3500, count=1), MetaItem(4000, count=1), MetaItem(4500, count=1),
                   MetaItem(5000, count=1), ],
        items=[Furniture(800), Furniture(1010), Clothing(410, 0), ]
    ),

    WeeklyCatalog(
        series=1, number=12, isSale=False,
        newRod=True, newCloset=True,
        metaItems=[MetaItem(300, count=1), MetaItem(2000, count=5), MetaItem(3000, count=1),
                   MetaItem(3500, count=1), MetaItem(4000, count=1), MetaItem(4500, count=1), ],
        items=[Furniture(620), ]
    ),

    WeeklyCatalog(
        series=1, number=13, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(2000, count=5), MetaItem(3000, count=1),
                   MetaItem(3500, count=1), MetaItem(4000, count=1), MetaItem(4500, count=1), ],
        items=[Clothing(119, 0), Clothing(219, 0), ]
    ),

    WeeklyCatalog(
        series=2, number=1, isSale=False,
        newRod=False, newCloset=True,
        metaItems=[MetaItem(100, count=1), MetaItem(2000, count=2), MetaItem(2010, count=3),
                   MetaItem(3010, count=1), MetaItem(3510, count=1), MetaItem(4010, count=1),
                   MetaItem(4510, count=1), ],
        items=[Furniture(1110), Furniture(630), Furniture(1630), Emote(11),
               Nametag(11), ]
    ),

    WeeklyCatalog(
        series=2, number=2, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2000, count=2), MetaItem(2010, count=3),
                   MetaItem(3010, count=1), MetaItem(3510, count=1), MetaItem(4010, count=1),
                   MetaItem(4510, count=1), ],
        items=[Furniture(230), Furniture(920), Furniture(1440), ]
    ),

    WeeklyCatalog(
        series=2, number=3, isSale=False,
        newRod=True, newCloset=True,
        metaItems=[MetaItem(300, count=1), MetaItem(2000, count=2), MetaItem(2010, count=3),
                   MetaItem(3010, count=1), MetaItem(3510, count=1), MetaItem(4010, count=1),
                   MetaItem(4510, count=1), MetaItem(5000, count=1), ],
        items=[Furniture(420), AnimatedFurniture(480), Furniture(120), Clothing(120, 0),
               Clothing(220, 0), ]
    ),

    WeeklyCatalog(
        series=2, number=4, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2000, count=2), MetaItem(2010, count=3),
                   MetaItem(3010, count=1), MetaItem(3510, count=1), MetaItem(4010, count=1),
                   MetaItem(4510, count=1), ],
        items=[Furniture(1700), Furniture(640), Window(50), ]
    ),

    WeeklyCatalog(
        series=2, number=5, isSale=False,
        newRod=False, newCloset=True,
        metaItems=[MetaItem(100, count=1), MetaItem(2000, count=2), MetaItem(2010, count=3),
                   MetaItem(3010, count=1), MetaItem(3510, count=1), MetaItem(4010, count=1),
                   MetaItem(4510, count=1), ],
        items=[Furniture(1120), Furniture(930), Furniture(1500), Emote(6),
               ]
    ),

    WeeklyCatalog(
        series=2, number=6, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(2000, count=2), MetaItem(2010, count=3),
                   MetaItem(3010, count=1), MetaItem(3510, count=1), MetaItem(4010, count=1),
                   MetaItem(4510, count=1), ],
        items=[Furniture(430), AnimatedFurniture(491), Furniture(1620), Furniture(1442),
               ]
    ),

    WeeklyCatalog(
        series=2, number=7, isSale=False,
        newRod=True, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2000, count=2), MetaItem(2010, count=3),
                   MetaItem(3010, count=1), MetaItem(3510, count=1), MetaItem(4010, count=1),
                   MetaItem(4510, count=1), MetaItem(5000, count=1), ],
        items=[Furniture(610), Furniture(940), Clothing(121, 0), Clothing(221, 0),
               ]
    ),

    WeeklyCatalog(
        series=2, number=8, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2000, count=2), MetaItem(2010, count=3),
                   MetaItem(3010, count=1), MetaItem(3510, count=1), MetaItem(4010, count=1),
                   MetaItem(4510, count=1), ],
        items=[Furniture(1710), Furniture(1030), Window(60), Nametag(7),
               ]
    ),

    WeeklyCatalog(
        series=2, number=9, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(2000, count=2), MetaItem(2010, count=3),
                   MetaItem(3010, count=1), MetaItem(3510, count=1), MetaItem(4010, count=1),
                   MetaItem(4510, count=1), ],
        items=[Furniture(1130), Furniture(130), Emote(8), ]
    ),

    WeeklyCatalog(
        series=2, number=10, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2000, count=2), MetaItem(2010, count=3),
                   MetaItem(3010, count=1), MetaItem(3510, count=1), MetaItem(4010, count=1),
                   MetaItem(4510, count=1), ],
        items=[Furniture(1530), Furniture(1640), Furniture(1441), ]
    ),

    WeeklyCatalog(
        series=2, number=11, isSale=False,
        newRod=True, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2000, count=2), MetaItem(2010, count=3),
                   MetaItem(3010, count=1), MetaItem(3510, count=1), MetaItem(4010, count=1),
                   MetaItem(4510, count=1), MetaItem(5000, count=1), ],
        items=[Furniture(300), Furniture(1220), ]
    ),

    WeeklyCatalog(
        series=2, number=12, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(2000, count=2), MetaItem(2010, count=3),
                   MetaItem(3010, count=1), MetaItem(3510, count=1), MetaItem(4010, count=1),
                   MetaItem(4510, count=1), ],
        items=[Furniture(810), Furniture(1230), Furniture(1443), ]
    ),

    WeeklyCatalog(
        series=2, number=13, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(2000, count=2), MetaItem(2010, count=3),
                   MetaItem(3010, count=1), MetaItem(3510, count=1), MetaItem(4010, count=1),
                   MetaItem(4510, count=1), ],
        items=[Furniture(310), Furniture(1520), Furniture(1650), Window(80),
               Clothing(222, 0), ]
    ),

    WeeklyCatalog(
        series=3, number=1, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2000, count=1), MetaItem(2010, count=2),
                   MetaItem(2020, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), ],
        items=[Furniture(1240), Furniture(1661), Emote(5), ]
    ),

    WeeklyCatalog(
        series=3, number=2, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2000, count=1), MetaItem(2010, count=2),
                   MetaItem(2020, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), ],
        items=[Furniture(1800), Furniture(240), Furniture(1200), Nametag(12),
               ]
    ),

    WeeklyCatalog(
        series=3, number=3, isSale=False,
        newRod=True, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(2000, count=1), MetaItem(2010, count=2),
                   MetaItem(2020, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), MetaItem(5000, count=1), ],
        items=[Furniture(145), Clothing(123, 0), Clothing(224, 0), ]
    ),

    WeeklyCatalog(
        series=3, number=4, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2000, count=1), MetaItem(2010, count=2),
                   MetaItem(2020, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), ],
        items=[Window(100), Furniture(1810), ]
    ),

    WeeklyCatalog(
        series=3, number=5, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2000, count=1), MetaItem(2010, count=2),
                   MetaItem(2020, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), ],
        items=[Furniture(650), Furniture(1900), ]
    ),

    WeeklyCatalog(
        series=3, number=6, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(2000, count=1), MetaItem(2010, count=2),
                   MetaItem(2020, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), ],
        items=[Furniture(1725), ]
    ),

    WeeklyCatalog(
        series=3, number=7, isSale=False,
        newRod=True, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2000, count=1), MetaItem(2010, count=2),
                   MetaItem(2020, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), ],
        items=[Window(90), Clothing(124, 0), Clothing(411, 0), ]
    ),

    WeeklyCatalog(
        series=3, number=8, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2000, count=1), MetaItem(2010, count=2),
                   MetaItem(2020, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), ],
        items=[Furniture(140), Furniture(1020), Emote(13), ]
    ),

    WeeklyCatalog(
        series=3, number=9, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(2000, count=1), MetaItem(2010, count=2),
                   MetaItem(2020, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), ],
        items=[Furniture(950), Furniture(1660), Clothing(310, 0), Nametag(2),
               ]
    ),

    WeeklyCatalog(
        series=3, number=10, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2000, count=1), MetaItem(2010, count=2),
                   MetaItem(2020, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), MetaItem(5000, count=1), ],
        items=[Furniture(400), AnimatedFurniture(470), Furniture(660), Furniture(1200),
               ]
    ),

    WeeklyCatalog(
        series=3, number=11, isSale=False,
        newRod=True, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2000, count=1), MetaItem(2010, count=2),
                   MetaItem(2020, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), ],
        items=[Furniture(1910), Furniture(1000), ]
    ),

    WeeklyCatalog(
        series=3, number=12, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(2000, count=1), MetaItem(2010, count=2),
                   MetaItem(2020, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), ],
        items=[Furniture(1720), Emote(9), ]
    ),

    WeeklyCatalog(
        series=3, number=13, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(2000, count=1), MetaItem(2010, count=2),
                   MetaItem(2020, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), ],
        items=[Window(110), Clothing(311, 0), ]
    ),

    WeeklyCatalog(
        series=4, number=1, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2010, count=1), MetaItem(2020, count=2),
                   MetaItem(2030, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), MetaItem(5000, count=1), ],
        items=[Window(120), Clothing(125, 0), ]
    ),

    WeeklyCatalog(
        series=4, number=2, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(2010, count=1), MetaItem(2020, count=2),
                   MetaItem(2030, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), ],
        items=[Clothing(412, 0), Clothing(312, 0), Furniture(1920), ]
    ),

    WeeklyCatalog(
        series=4, number=3, isSale=False,
        newRod=True, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2010, count=1), MetaItem(2020, count=2),
                   MetaItem(2030, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), ],
        items=[Wallpaper(3900), Furniture(980), Nametag(13), ]
    ),

    WeeklyCatalog(
        series=4, number=4, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(2010, count=1), MetaItem(2020, count=2),
                   MetaItem(2030, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), ],
        items=[Clothing(130, 0), Furniture(150), ]
    ),

    WeeklyCatalog(
        series=4, number=5, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2010, count=1), MetaItem(2020, count=2),
                   MetaItem(2030, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), ],
        items=[Clothing(128, 0), Wallpaper(3700), Furniture(160), ]
    ),

    WeeklyCatalog(
        series=4, number=6, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(2010, count=1), MetaItem(2020, count=2),
                   MetaItem(2030, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), ],
        items=[Clothing(313, 0), Clothing(413, 0), Furniture(960), Emote(7),
               ]
    ),

    WeeklyCatalog(
        series=4, number=7, isSale=False,
        newRod=True, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2010, count=1), MetaItem(2020, count=2),
                   MetaItem(2030, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), ],
        items=[Furniture(1930), Furniture(670), ]
    ),

    WeeklyCatalog(
        series=4, number=8, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(2010, count=1), MetaItem(2020, count=2),
                   MetaItem(2030, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), MetaItem(5000, count=1), ],
        items=[Clothing(126, 0), Furniture(1970), ]
    ),

    WeeklyCatalog(
        series=4, number=9, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2010, count=1), MetaItem(2020, count=2),
                   MetaItem(2030, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), ],
        items=[Furniture(720), Furniture(970), ]
    ),

    WeeklyCatalog(
        series=4, number=10, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(2010, count=1), MetaItem(2020, count=2),
                   MetaItem(2030, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), ],
        items=[Clothing(127, 0), Furniture(1950), Nametag(4), ]
    ),

    WeeklyCatalog(
        series=4, number=11, isSale=False,
        newRod=True, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2010, count=1), MetaItem(2020, count=2),
                   MetaItem(2030, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), ],
        items=[Furniture(1940), Window(130), ]
    ),

    WeeklyCatalog(
        series=4, number=12, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(2010, count=1), MetaItem(2020, count=2),
                   MetaItem(2030, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), ],
        items=[Wallpaper(3800), Clothing(129, 0), Emote(10), ]
    ),

    WeeklyCatalog(
        series=4, number=13, isSale=False,
        newRod=True, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2010, count=1), MetaItem(2020, count=2),
                   MetaItem(2030, count=3), MetaItem(3020, count=1), MetaItem(3530, count=1),
                   MetaItem(4020, count=1), MetaItem(4520, count=1), ],
        items=[Furniture(250), Furniture(1960), ]
    ),

    WeeklyCatalog(
        series=5, number=1, isSale=True,
        newRod=False, newCloset=False,
        metaItems=[],
        items=[Furniture(2100), Furniture(2200), Furniture(1100), Furniture(110),
               Furniture(100), Furniture(700), Furniture(710),
               Furniture(410), AnimatedFurniture(490), Furniture(1210),
               Furniture(1200), Furniture(800), Furniture(1110),
               Furniture(230), Furniture(420), AnimatedFurniture(480),
               Furniture(120), Furniture(1700), Furniture(1120),
               Furniture(430), AnimatedFurniture(491), Furniture(1130),
               Furniture(130), Furniture(300), Furniture(1220),
               Furniture(810), Furniture(1230), Furniture(310),
               Furniture(1240), Furniture(240), Furniture(145),
               Furniture(1725), Furniture(140), Furniture(950),
               Furniture(1720), ]
    ),

    # Series 5 only has 5 catalog issues.

    WeeklyCatalog(
        series=5, number=2, isSale=True,
        newRod=False, newCloset=False,
        metaItems=[],
        items=[Clothing(116, 0), Clothing(216, 0), Clothing(408, 0), Clothing(117, 0),
               Clothing(217, 0), Clothing(409, 0), Clothing(118, 0),
               Clothing(218, 0), Clothing(410, 0), Clothing(119, 0),
               Clothing(219, 0), Clothing(120, 0), Clothing(220, 0),
               Clothing(121, 0), Clothing(221, 0), Clothing(222, 0),
               Clothing(123, 0), Clothing(224, 0), Clothing(411, 0),
               Clothing(311, 0), Clothing(310, 0), ]
    ),

    WeeklyCatalog(
        series=5, number=3, isSale=True,
        newRod=False, newCloset=False,
        metaItems=[],
        items=[Window(40), Window(70), Window(50), Window(60),
               Window(80), Window(100), Window(90),
               Window(110), ]
    ),

    WeeklyCatalog(
        series=5, number=4, isSale=True,
        newRod=False, newCloset=False,
        metaItems=[],
        items=[Emote(5), Emote(9), Emote(13), Emote(11),
               Emote(6), Emote(8), Nametag(10),
               ]
    ),

    WeeklyCatalog(
        series=5, number=5, isSale=True,
        newRod=False, newCloset=False,
        metaItems=[],
        items=[Furniture(600), Furniture(610), Furniture(620), Furniture(630),
               Furniture(640), Furniture(650), Furniture(660),
               Furniture(900), Furniture(910), Furniture(920),
               Furniture(930), Furniture(940), Furniture(1000),
               Furniture(1010), Furniture(1020), Furniture(1030),
               Furniture(1400), Furniture(1410), Furniture(1420),
               Furniture(1430), Furniture(1440), Furniture(1441),
               Furniture(1442), Furniture(1443), Furniture(1500),
               Furniture(1510), Furniture(1520), Furniture(1530),
               Furniture(1600), Furniture(1610), Furniture(1620),
               Furniture(1630), Furniture(1640), Furniture(1650),
               Furniture(1660), Furniture(1661), Furniture(1710),
               Furniture(1800), Furniture(1810), Furniture(1900),
               Furniture(1910), ]
    ),

    # Series 6 only has 8 catalog issues.

    WeeklyCatalog(
        series=6, number=1, isSale=False,
        newRod=True, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(2020, count=1), MetaItem(2030, count=2),
                   MetaItem(2040, count=3), ],
        items=[Furniture(730), ]
    ),

    WeeklyCatalog(
        series=6, number=2, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2020, count=1), MetaItem(2030, count=2),
                   MetaItem(2040, count=3), ],
        items=[Furniture(260), ]
    ),

    WeeklyCatalog(
        series=6, number=3, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(2020, count=1), MetaItem(2030, count=2),
                   MetaItem(2040, count=3), MetaItem(5000, count=1), ],
        items=[Furniture(440), AnimatedFurniture(492), ]
    ),

    WeeklyCatalog(
        series=6, number=4, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2020, count=1), MetaItem(2030, count=2),
                   MetaItem(2040, count=3), ],
        items=[Furniture(170), Furniture(1250), ]
    ),

    WeeklyCatalog(
        series=6, number=5, isSale=False,
        newRod=True, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(2020, count=1), MetaItem(2030, count=2),
                   MetaItem(2040, count=3), ],
        items=[Furniture(1140), ]
    ),

    WeeklyCatalog(
        series=6, number=6, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2020, count=1), MetaItem(2030, count=2),
                   MetaItem(2040, count=3), ],
        items=[Furniture(2010), Nametag(8), ]
    ),

    WeeklyCatalog(
        series=6, number=7, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(2020, count=1), MetaItem(2030, count=2),
                   MetaItem(2040, count=3), MetaItem(5000, count=1), ],
        items=[Furniture(2000), ]
    ),

    WeeklyCatalog(
        series=6, number=8, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(100, count=1), MetaItem(2020, count=1), MetaItem(2030, count=2),
                   MetaItem(2040, count=3), ],
        items=[Furniture(3000), ]
    ),

    WeeklyCatalog(
        series=7, number=1, isSale=False,
        newRod=True, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(1, count=2030), MetaItem(2040, count=2),
                   MetaItem(2050, count=3), ],
        items=[Clothing(131, 0), Clothing(225, 0), ]
    ),

    WeeklyCatalog(
        series=7, number=2, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(1, count=2030), MetaItem(2040, count=2),
                   MetaItem(2050, count=3), ],
        items=[Furniture(105), ]
    ),

    WeeklyCatalog(
        series=7, number=3, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(1, count=2030), MetaItem(2040, count=2),
                   MetaItem(2050, count=3), ],
        items=[Furniture(205), ]
    ),

    WeeklyCatalog(
        series=7, number=4, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(1, count=2030), MetaItem(2040, count=2),
                   MetaItem(2050, count=3), ],
        items=[Furniture(625), ]
    ),

    WeeklyCatalog(
        series=7, number=5, isSale=False,
        newRod=True, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(1, count=2030), MetaItem(2040, count=2),
                   MetaItem(2050, count=3), ],
        items=[Emote(12), Nametag(5), ]
    ),

    WeeklyCatalog(
        series=7, number=6, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(1, count=2030), MetaItem(2040, count=2),
                   MetaItem(2050, count=3), ],
        items=[Clothing(314, 0), Clothing(414, 0), ]
    ),

    WeeklyCatalog(
        series=7, number=7, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(1, count=2030), MetaItem(2040, count=2),
                   MetaItem(2050, count=3), ],
        items=[Furniture(715), ]
    ),

    WeeklyCatalog(
        series=7, number=8, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(1, count=2030), MetaItem(2040, count=2),
                   MetaItem(2050, count=3), ],
        items=[Furniture(1015), Nametag(6), ]
    ),

    WeeklyCatalog(
        series=7, number=9, isSale=False,
        newRod=True, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(1, count=2030), MetaItem(2040, count=2),
                   MetaItem(2050, count=3), ],
        items=[Furniture(1215), ]
    ),

    WeeklyCatalog(
        series=7, number=10, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(1, count=2030), MetaItem(2040, count=2),
                   MetaItem(2050, count=3), ],
        items=[Emote(14), ]
    ),

    WeeklyCatalog(
        series=7, number=11, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(1, count=2030), MetaItem(2040, count=2),
                   MetaItem(2050, count=3), ],
        items=[Furniture(1260), ]
    ),

    WeeklyCatalog(
        series=7, number=12, isSale=False,
        newRod=False, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(1, count=2030), MetaItem(2040, count=2),
                   MetaItem(2050, count=3), ],
        items=[Furniture(705), Nametag(3), ]
    ),

    WeeklyCatalog(
        series=7, number=13, isSale=False,
        newRod=True, newCloset=False,
        metaItems=[MetaItem(300, count=1), MetaItem(1, count=2030), MetaItem(2040, count=2),
                   MetaItem(2050, count=3), ],
        items=[]
    ),



)