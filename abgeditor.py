#!/bin/env python3

class ABGGame:
	def __init__ (this):
		this.ids = set()

	def importJSONFile (filename: str):
		return None

	def exportJSONFile (filename: str):
		return None

	def addItem (filename: str):
		return None

class ABGBorderStyle:
	COLLECTION = set()

	def define (key):
		assert isinstance(key, str)
		assert (key not in ABGBorderStyle.COLLECTION)

		ABGBorderStyle.COLLECTION.add(key)

	def validate (value):
		assert value in ABGBorderStyle.COLLECTION

ABGBorderStyle.DOTTED = ABGBorderStyle.define("DOTTED")

class ABGLabelPosition:
	COLLECTION = set()

	def define (key):
		assert isinstance(key, str)
		assert (key not in ABGLabelPosition.COLLECTION)

		ABGLabelPosition.COLLECTION.add(key)

	def validate (value):
		assert value in ABGLabelPosition.COLLECTION

ABGLabelPosition.LEFT = ABGLabelPosition.define("LEFT")

class ABGColor:
	def validate (value):
		assert isinstance(value, str)

		# TODO

		return value

ABGColor.TRANSPARENT = ABGColor.validate("transparent")

class ABGAttribute:
	COLLECTION = dict()

	def define (key, assertedClass, specialCheck):
		assert isinstance(key, str)
		assert (key not in ABGAttribute.COLLECTION)

		result = ABGAttribute(key, assertedClass, specialCheck)

		ABGAttribute.COLLECTION[key] = result

		return  result

	def __init__ (this, key, assertedClass, specialCheck):
		this.key = key
		this.assertedClass = assertedClass
		this.specialCheck = specialCheck

	def validate (this, value):
		assert isinstance(value, this.assertedClass)

		if this.specialCheck is not None:
			assert this.specialCheck(value)

		return this

	def getKey (this):
		return this.key

ABGAttribute.ALTERNATE_COLOR = ABGAttribute.define("alternateColor", str, ABGColor.validate)
ABGAttribute.BACK_CONTENT = ABGAttribute.define("backContent", str, None)
ABGAttribute.BACKGROUND_COLOR = ABGAttribute.define("backgroundColor", str, ABGColor.validate)
ABGAttribute.BACK_TEXT = ABGAttribute.define("backText", str, None)
ABGAttribute.BORDER_COLOR = ABGAttribute.define("borderColor", str, ABGColor.validate)
ABGAttribute.BORDER_STYLE = ABGAttribute.define("borderStyle", str, ABGBorderStyle.validate)
ABGAttribute.COL_COUNT = ABGAttribute.define("colCount", int, lambda x : (x > 0))
ABGAttribute.COLOR = ABGAttribute.define("color", str, ABGColor.validate)
ABGAttribute.CONTENT = ABGAttribute.define("content", str, None)
ABGAttribute.FLIPPED = ABGAttribute.define("flipped", bool, None)
ABGAttribute.FLIPPED_COLOR = ABGAttribute.define("flippedColor", str, ABGColor.validate)
ABGAttribute.FONT_SIZE = ABGAttribute.define("fontSize", int, lambda x : (x >= 0))
ABGAttribute.HEIGHT = ABGAttribute.define("height", int, lambda x : (x > 0))
ABGAttribute.HOLD_ITEMS = ABGAttribute.define("holdItems", bool, None)
ABGAttribute.ID = ABGAttribute.define("id", str, None) # Don't know yet.
ABGAttribute.LABEL = ABGAttribute.define("label", str, None)
ABGAttribute.LABEL_POSITION = ABGAttribute.define("labelPosition", str, ABGLabelPosition.validate)
ABGAttribute.ON_ITEM = ABGAttribute.define("onItem", int, None) # Don't know yet.
ABGAttribute.OVERLAY = ABGAttribute.define("overlay", str, None) # Don't know yet
ABGAttribute.OWNED_BY = ABGAttribute.define("ownedBy", int, None) # Don't know yet.
ABGAttribute.ROLL_ON_DBL_CLICK = ABGAttribute.define("rollOnDblClick", bool, None)
ABGAttribute.ROW_COUNT = ABGAttribute.define("rowCount", int, lambda x : (x > 0))
ABGAttribute.SET_STATE = ABGAttribute.define("setState", int, None) # Don't know yet.
ABGAttribute.SIZE = ABGAttribute.define("size", int, lambda x : (x > 0))
ABGAttribute.TEXT = ABGAttribute.define("text", str, None)
ABGAttribute.TEXT_COLOR = ABGAttribute.define("textColor", str, ABGColor.validate)
ABGAttribute.UNFLIPPED_FOR = ABGAttribute.define("unflippedFor", str, None) # Don't know yet
ABGAttribute.VERTICAL = ABGAttribute.define("vertical", bool, None)
ABGAttribute.WIDTH = ABGAttribute.define("width", int, lambda x : (x > 0))

class ABGItem:
	def __init__ (this, attributes):
		for (key, value) in attributes.items():
			attribute = ABGAttribute.COLLECTION[key]
			attribute.validate(value)

		this.attributes = attributes

	def setAttributeValue (this, attribute, value):
		key = None

		if isinstance(attribute, str):
			key = attribute
			attribute = ABGAttribute.COLLECTION[key]
		else:
			key = attribute.getKey()

		assert key in this.attributes

		attribute.validate(value)

		this.attributes[key] = value

		return this

	def getAttributeValue (this, attribute):
		key = None

		if isinstance(attribute, str):
			key = attribute
			attribute = ABGAttribute.COLLECTION[key]
		else:
			key = attribute.getKey()

		assert key in this.attributes

		return this.attributes[key]

	def pullAttributesFrom (this, attributes: dict):
		for (key, value) in attributes.items():
			this.setAttribute(key, value)

		return this

	def pushAttributesTo (this, attributes: dict):
		for (key, value) in this.items():
			attributes[key] = value

		return this

class ABGZone (ABGItem):
	def __init__ (this):
		ABGItem.__init__(
			this,
			{
				'width': 200,
				'height': 200,
				'borderColor': ABGColor("#cccccc33"),
				'borderStyle': ABGBorderStyle.DOTTED,
				'backgroundColor': ABGColor.TRANSPARENT,
				'labelPosition': ABGLabelPosition.LEFT,
				'label': "",
				'holdItems': False,
				'setState': None,
				'onItem': None,
				'id': None
			}
		)

class ABGToken (ABGItem):
	def __init__ (this):
		ABGItem.__init__(
			this,
			{
				'size': 50,
				'color': ABGColor("#b3b3b3"),
				'flippedColor': ABGColor("#b3b3b3"),
				'flipped': False,
				'text': "",
				'textColor': ABGColor("#000"),
				'fontSize': 24,
			}
		)

class ABGScreen (ABGItem):
	def __init__ (this):
		ABGItem.__init__(
			this,
			{
				'width': 1,
				'height': 1,
				'borderColor': ABGColor.TRANSPARENT,
				'borderStyle': ABGBorderStyle.NONE,
				'backgroundColor': ABGColor.TRANSPARENT,
				'ownedBy': None,
				'setState': None,
			}
		)

class ABGRound (ABGItem):
	def __init__ (this):
		ABGItem.__init__(
			this,
			{
				'size': 50,
				'color': ABGColor("#ccc"),
				'flippedColor': ABGColor("#ccc"),
				'flipped': False,
				'text': "",
				'textColor': ABGColor("#000"),
				'fontSize': 16,
			}
		)

class ABGRect (ABGItem):
	def __init__ (this):
		ABGItem.__init__(
			this,
			{
				'width': 50,
				'height': 50,
				'color': ABGColor("#ccc"),
				'flippedColor': ABGColor("#ccc"),
				'flipped': False,
				'text': "",
				'textColor': ABGColor("#000"),
				'fontSize': 16,
			}
		)

class ABGPawn (ABGItem):
	def __init__ (this):
		ABGItem.__init__(
			this,
			{
				'size': 50,
				'color': ABGColor("#b3b3b3"),
			}
		)

class ABGNote (ABGItem):
	def __init__ (this):
		ABGItem.__init__(
			this,
			{
				'value': "",
				'color': ABGColor("#FFEC27"),
				'label': "",
				'textColor': ABGColor("#000"),
				'fontFamily': "Roboto",
				'fontSize': 20,
				'width': 300,
				'height': 200,
				'setState': None,
			}
		)

class ABGMeeple (ABGItem):
	def __init__ (this):
		ABGItem.__init__(
			this,
			{
				'size': 50,
				'color': ABGColor("#b3b3b3"),
			}
		)

class ABGJewel (ABGItem):
	def __init__ (this):
		ABGItem.__init__(
			this,
			{
				'size': 50,
				'color': ABGColor("#b3b3b3"),
			}
		)

class ABGPicture (ABGItem):
	def __init__ (this):
		ABGItem.__init__(
			this,
			{
				'width': 1,
				'height': 1,
				'content': "/default.png",
				'backContent': None,
				'flipped': False,
				'unflippedFor': None,
				'text': "",
				'backText': "",
				'overlay': None,
				'setState': None,
				'id': None,
			}
		)

class ABGHexagon (ABGItem):
	def __init__ (this):
		ABGItem.__init__(
			this,
			{
				'size': 50,
				'color': "#ccc",
				'flippedColor': "#ccc",
				'flipped': False,
				'text': "",
				'textColor': "#000",
				'fontSize': 16,
				'vertical': False,
			}
		)

class ABGGenerator (ABGItem): # Not sure if truly an item.
	def __init__ (this):
		ABGItem.__init__(
			this,
			{
			}
		)

class ABGDiceImage (ABGItem):
	def __init__ (this):
		ABGItem.__init__(
			this,
			{
				'id': None,
				'value': 0,
				'images': None,
				'width': 50,
				'height': 50,
				'rollOnDblClick': False,
		#		'rollOnMove': !rollOnDblClick,
			}
		)

class ABGDice (ABGItem):
	def __init__ (this):
		ABGItem.__init__(
			this,
			{
				'value': 0,
				'color': ABGColor("#CCC"),
				'label': "",
				'textColor': ABGColor("#fff"),
				'fontSize': 35,
				'id': None,
			}
		)

class ABGCylinder (ABGItem):
	def __init__ (this):
		ABGItem.__init__(
			this,
			{
				'size': 50,
				'color': ABGColor("#b3b3b3"),
			}
		)

class ABGCube (ABGItem):
	def __init__ (this):
		ABGItem.__init__(
			this,
			{
				'size': 50,
				'color': ABGColor("#b3b3b3"),
			}
		)

class ABGCounter (ABGItem):
	def __init__ (this):
		ABGItem.__init__(
			this,
			{
				'value': 0,
				'color': ABGColor("#CCC"),
				'label': "",
				'textColor': ABGColor("#000"),
				'fontSize': 22,
				'setState': None,
			}
		)

class ABGCheckerBoard (ABGItem):
	def __init__ (this):
		ABGItem.__init__(
			this,
			{
				'width': 50,
				'height': 50,
				'color': ABGColor("#CCC"),
				'alternateColor': ABGColor("#888"),
				'colCount': 3,
				'rowCount': 3,
				'setState': None,
				'id': None,
			}
		)
