#!/bin/env python3

class ABGGame:

	def __init__ (this):
		this.ids = set()

	def import (filename: str):

	def export (filename: str):

	def addItem (filename: str):

class ABGBorderStyle (enum):
	DOTTED

class ABGLabelPosition (enum):
	LEFT

class ABGColor:
	TRANSPARENT = ABGColor("transparent")

	def __init__ (this, asString: str):
		this.asString = asString

class ABGItem:

class ABGZone (ABGItem):
	def __init__ (this):
		this.width = 200,
		this.height = 200,
		this.borderColor = ABGColor("#cccccc33")
		this.borderStyle = ABGBorderStyle.DOTTED
		this.backgroundColor = ABGColor.TRANSPARENT
		this.labelPosition = ABGLabelPosition.LEFT
		this.label = ""
		this.holdItems = False
		this.setState = None
		this.onItem = None
		this.id = None

class ABGToken (ABGItem):
	def __init__ (this):
		this.size = 50
		this.color = ABGColor("#b3b3b3")
		this.flippedColor = ABGColor("#b3b3b3")
		this.flipped = False
		this.text = ""
		this.textColor = ABGColor("#000")
		this.fontSize = 24

class ABGScreen (ABGItem):
	def __init__ (this):
		this.width
		this.height
		this.borderColor
		this.borderStyle
		this.backgroundColor
		this.ownedBy
		this.setState

class ABGRound (ABGItem):
	def __init__ (this):
		this.size = 50
		this.color = ABGColor("#ccc")
		this.flippedColor = ABGColor("#ccc")
		this.flipped = False
		this.text = ""
		this.textColor = ABGColor("#000")
		this.fontSize = 16

class ABGRect (ABGItem):
	def __init__ (this):
		this.width = 50
		this.height = 50
		this.color = ABGColor("#ccc")
		this.flippedColor = ABGColor("#ccc")
		this.flipped = False
		this.text = ""
		this.textColor = ABGColor("#000")
		this.fontSize = 16

class ABGPawn (ABGItem):
	def __init__ (this):
		this.size = 50
		this.color = ABGColor("#b3b3b3")

class ABGNote (ABGItem):
	def __init__ (this):
		this.value = ""
		this.color = ABGColor("#FFEC27")
		this.label = ""
		this.textColor = ABGColor("#000")
		this.fontFamily = "Roboto"
		this.fontSize = 20
		this.width = 300
		this.height = 200
		this.setState

class ABGMeeple (ABGItem):
	def __init__ (this):
		this.size = 50
		this.color = ABGColor("#b3b3b3")

class ABGJewel (ABGItem):
	def __init__ (this):
		this.size = 50
		this.color = ABGColor("#b3b3b3")

class ABGPicture (ABGItem):
	def __init__ (this):
		this.width
		this.height
		this.content = "/default.png"
		this.backContent: rawBackContent
		this.flipped = False
		this.unflippedFor
		this.text
		this.backText
		this.overlay
		this.setState
		this.id

class ABGHexagon (ABGItem):
	def __init__ (this):
		this.size = 50
		this.color = "#ccc"
		this.flippedColor = "#ccc"
		this.flipped = False
		this.text = ""
		this.textColor = "#000"
		this.fontSize = "16"
		this.vertical = False

class ABGGenerator (ABGItem): # Not sure if truly an item.
	def __init__ (this):

class ABGDiceImage (ABGItem):
	def __init__ (this):
		this.id
		this.value = 0
		this.images
		this.width = 50
		this.height = 50
		this.rollOnDblClick = False
		#this.rollOnMove = !rollOnDblClick

class ABGDice (ABGItem):
	def __init__ (this):
		this.value = 0,
		this.color = "#CCC"
		this.label = ""
		this.textColor = "#fff"
		this.fontSize = 35
		this.id

class ABGCylinder (ABGItem):
	def __init__ (this):
		this.size = 50
		this.color = ABGColor("#b3b3b3")

class ABGCube (ABGItem):
	def __init__ (this):
		this.size = 50
		this.color = ABGColor("#b3b3b3")

class ABGCounter (ABGItem):
	def __init__ (this):
		this.value = 0
		this.color = ABGColor("#CCC")
		this.label = ""
		this.textColor = ABGColor("#000")
		this.fontSize = 22
		this.setState

class ABGCheckerBoard (ABGItem):
	def __init__ (this):
		this.width = 50,
		this.height = this.width,
		this.color = ABGColor("#CCC")
		this.alternateColor = ABGColor("#888")
		this.colCount = 3
		this.rowCount = 3
		this.setState
		this.id
