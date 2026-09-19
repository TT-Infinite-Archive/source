from panda3d.core import Point2, Point3, Quat

from toontown.toontowngui.Clickable import Clickable


class Clickable3d(Clickable):
    def projectFrame(self, nodePath, left, right, bottom, top):
        # Discard the rotational components so that the frame points are
        # measured in a camera-facing plane:
        transform = base.cam.getNetTransform().getInverse().compose(
            nodePath.getNetTransform()).setQuat(Quat())
        mat = transform.getMat()

        camSpaceTopLeft = mat.xformPoint(Point3(left, 0, top))
        camSpaceBottomRight = mat.xformPoint(Point3(right, 0, bottom))

        near = base.camLens.getNear()
        if (camSpaceTopLeft[1] < near) or (camSpaceBottomRight[1] < near):
            return None

        screenSpaceTopLeft = Point2()
        screenSpaceBottomRight = Point2()
        base.camLens.project(camSpaceTopLeft, screenSpaceTopLeft)
        base.camLens.project(camSpaceBottomRight, screenSpaceBottomRight)

        return (screenSpaceTopLeft[0], screenSpaceBottomRight[0],
                screenSpaceBottomRight[1], screenSpaceTopLeft[1])

    def setRegionFrame(self, frame):
        if frame is not None:
            self.region.setFrame(*frame)
        self.region.setActive(frame is not None)

    def setClickRegionFrame(self, left, right, bottom, top):
        self.setRegionFrame(
            self.projectFrame(self.contents, left, right, bottom, top))
