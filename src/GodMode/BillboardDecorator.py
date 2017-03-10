from UM.Scene.SceneNodeDecorator import SceneNodeDecorator

import UM.Application

from .BillboardNode import BillboardNode

class BillboardDecorator(SceneNodeDecorator):
    def __init__(self):
        super().__init__()
        self._billboard = None

    def setNode(self, node):
        super().setNode(node)
        # Create a new billboard node.
        self._billboard = BillboardNode(self._node, parent = UM.Application.Application.getInstance().getController().getScene().getRoot())

    def clear(self):
        if self._billboard:
            self._billboard.setParent(None)
        self._billboard = None

    def getBillboard(self):
        return self._billboard