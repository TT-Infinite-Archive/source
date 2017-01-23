from toontown.data import Track
from toontown.data.Gag import Gag, PASS
from toontown.data.Effect import DamageEffect

DefaultGag = Gag(0, 'Nothing but a chuckle', None, 0, Track.TrackNone, Gag.RarityCommon, 0)
Gags = {
    0: DefaultGag,
    1: Gag(1, 'Cupcake', DamageEffect(0, 6), Gag.TargetSingleEnemy, Track.TrackThrow, Gag.RarityCommon, 1),
    2: Gag(2, 'Sliced Fruit Pie', DamageEffect(0, 12), Gag.TargetSingleEnemy, Track.TrackThrow, Gag.RarityCommon, 2),
    3: Gag(3, 'Golden Cupcake', DamageEffect(0, 999), Gag.TargetEnemies, Track.TrackThrow, Gag.RarityLegendary, 9),
    4: Gag(4, 'Red Cupcake', DamageEffect(0, 1), Gag.TargetEnemies, Track.TrackThrow, Gag.RarityRare, 1, chance=0.5),
    5: Gag(5, 'Sliced Cream Pie', DamageEffect(0, 16), Gag.TargetSingleEnemy, Track.TrackThrow, Gag.RarityCommon, 3),
    6: Gag(6, 'Fruit Pie', DamageEffect(0, 24), Gag.TargetSingleEnemy, Track.TrackThrow, Gag.RarityCommon, 4),
    7: Gag(7, 'Cream Pie', DamageEffect(0, 32), Gag.TargetSingleEnemy, Track.TrackThrow, Gag.RarityCommon, 5),
    8: Gag(8, 'Birthday Cake', DamageEffect(0, 80), Gag.TargetSingleEnemy, Track.TrackThrow, Gag.RarityCommon, 6),
    9: Gag(9, 'Cannon', DamageEffect(0, 80), Gag.TargetSingleEnemy, Track.TrackNone, Gag.RarityEpic, 6),
    PASS: Gag(99, 'Pass', None, 0, Track.TrackNone, Gag.RarityCommon, 0),
}







