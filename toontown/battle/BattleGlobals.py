from panda3d.core import Point3

SuitPoints = (
    # One Cog
    ((Point3(0, 5, 0), 179),),
    # Two Cogs
    ((Point3(2, 5.3, 0), 170), (Point3(-2, 5.3, 0), 180)),
    # Three Cogs
    ((Point3(4, 5.2, 0), 170), (Point3(0, 6, 0), 179), (Point3(-4, 5.2, 0), 190)),
    # Four Cogs
    ((Point3(6, 4.4, 0), 160), (Point3(2, 6.3, 0), 170), (Point3(-2, 6.3, 0), 190),(Point3(-6, 4.4, 0), 200))
)
SuitPendingPoints = (
    # Point to wait, angle
    (Point3(-4, 8.2, 0), 190),
    (Point3(0, 9, 0), 179),
    (Point3(4, 8.2, 0), 170),
    (Point3(8, 3.2, 0), 160)
)
ToonPoints = (
    # One Toon
    ((Point3(0, -6, 0), 0),),
    # Two Toons
    ((Point3(1.5, -6.5, 0), 5), (Point3(-1.5, -6.5, 0), -5)),
    # Three Toons
    ((Point3(3, -6.75, 0), 5), (Point3(0, -7, 0), 0), (Point3(-3, -6.75, 0), -5)),
    # Four Toons
    ((Point3(4.5, -7, 0), 10), (Point3(1.5, -7.5, 0), 5), (Point3(-1.5, -7.5, 0), -5), (Point3(-4.5, -7, 0), -10))
)
ToonPendingPoints = (
    (Point3(-3, -8, 0), -5),
    (Point3(0, -9, 0), 0),
    (Point3(3, -8, 0), 5),
    (Point3(5.5, -5.5, 0), 20)
)

