#!/bin/env python3

from abgeditor import *

if __name__ == '__main__':
	import sys

	ABGAssert.ensure(len(sys.argv) == 2, "Call with a content.json file as argument to test.")
	testGame = ABGGame()
	print("Parsing: " + sys.argv[1] + "...")
	testGame.fromFile(sys.argv[1])
	print("Parsing completed. Editing...")
	centerJewel = testGame.findItemsMatching({ 'label': "center_jewel" })[0]
	targetMeeple = testGame.findItemsMatching({ 'label': "target_meeple" })[0]

	targetMeeple.setLocationRelativeTo(centerJewel, 10, 50)
	targetMeeple.setAttributeValue("color", "#FFFFFF")

	for i in range(0, 100):
		newMeeple = targetMeeple.clone()
		testGame.addItem(newMeeple)
		newMeeple.setAttributeValue("color", "rgb(255, 255, " + str(int(255.0 - 255.0 * i / 100.0)) + ")")
		newMeeple.setAttributeValue("id", "meeple_id_" + str(i))
		newMeeple.setLocationRelativeTo(targetMeeple, 50, 0)
		targetMeeple = newMeeple

	testGame.toFile(sys.argv[1] + ".out")
