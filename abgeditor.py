#!/bin/env python3

import json

################################################################################
#### ABG ATTRIBUTE VALUE CLASSES ###############################################
################################################################################

class ABGBorderStyle:
	COLLECTION = set()

	def define (key):
		assert isinstance(key, str)
		assert (key not in ABGBorderStyle.COLLECTION)

		ABGBorderStyle.COLLECTION.add(key)

		return key

	def validate (value):
		assert value in ABGBorderStyle.COLLECTION

class ABGLabelPosition:
	COLLECTION = set()

	def define (key):
		assert isinstance(key, str)
		assert (key not in ABGLabelPosition.COLLECTION)

		ABGLabelPosition.COLLECTION.add(key)

		return key

	def validate (value):
		assert value in ABGLabelPosition.COLLECTION

class ABGColor:
	def validate (value):
		assert isinstance(value, str)

		# TODO

		return value

ABGColor.TRANSPARENT = ABGColor.validate("transparent")

################################################################################
#### ABG ATTRIBUTE CLASSES #####################################################
################################################################################
class ABGAttribute:
	COLLECTION = dict()

	def define (key, assertedClass, specialCheck, fromJson = None, toJson = None):
		assert isinstance(key, str)
		assert (key not in ABGAttribute.COLLECTION)

		result = ABGAttribute(key, assertedClass, specialCheck, fromJson, toJson)

		ABGAttribute.COLLECTION[key] = result

		return  result

	def __init__ (this, key, assertedClass, specialCheck, fromJson, toJson):
		this.key = key
		this.assertedClass = assertedClass
		this.specialCheck = specialCheck
		this.fromJson = fromJson
		this.toJson = toJson

	def validate (this, value):
		#print("Is this a valid " + this.key + "? " + str(value))

		assert isinstance(value, this.assertedClass)

		if this.specialCheck is not None:
			this.specialCheck(value)

		return this

	def getKey (this):
		return this.key

class ABGAttributesHaver:
	def __init__ (this, attributes, attributesHijacking = dict()):
		this.attributesHijacking = attributesHijacking

		for (key, value) in attributes.items():
			attribute = this.getAttributeFromKey(key)
			attribute.validate(value)

		this.attributes = attributes

	def getAttributeFromKey (this, key):
		if key in this.attributesHijacking:
			return this.attributesHijacking[key]
		else:
			return ABGAttribute.COLLECTION[key]

	def setAttributeValue (this, attribute, value):
		key = None

		if isinstance(attribute, str):
			key = attribute
			attribute = this.getAttributeFromKey(key)
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
			attribute = this.getAttributeFromKey(key)
		else:
			key = attribute.getKey()

		assert key in this.attributes

		return this.attributes[key]

	def pullAttributesFromJson (this, attributes: dict):
		for (key, value) in attributes.items():
			attribute = this.getAttributeFromKey(key)

			if (isinstance(value, list)):
				l = []

				for i in value:
					if (isinstance(i, dict)):
						assert attribute.fromJson is not None

						v = None

						if (attribute.fromJson == ABGItem):
							assert "type" in i
							v = ABGItem.createInstanceOf(i["type"])
						else:
							v = attribute.fromJson()
						v.pullAttributesFromJson(i)

						l.append(v)
					else:
						l.append(i)

				this.setAttributeValue(key, l)
			elif (isinstance(value, dict)):
				assert attribute.fromJson is not None
				v = attribute.fromJson()
				v.pullAttributesFromJson(value)

				this.setAttributeValue(key, v)
			else:
				this.setAttributeValue(key, value)

		return this

	def pushAttributesToJson (this, attributes: dict):
		for (key, value) in this.attributes.items():
			attribute = this.getAttributeFromKey(key)
			if (isinstance(value, list)):
				l = []
				for i in value:
					if (isinstance(i, ABGAttributeHaver)):
						d = dict()
						if (attribute.toJson):
							attribute.toJson(i, d)
						value.pushAttributesToJson(d)
						l.append(d)
					else:
						l.append(i)
			elif (isinstance(value, ABGAttributeHaver)):
				d = dict()
				value.pushAttributesToJson(d)
				attributes[key] = d
			else:
				attributes[key] = value

		return this

	def asDict (this):
		return this.attributes

	def validate (this):
		for (key, value) in this.attributes.items():
			attribute = this.getAttributeFromKey(key)
			attribute.validate(value)

		# TODO: we're currently not checking which attributes are there or not.

		return this

################################################################################
#### ABG ITEM CLASSES ##########################################################
################################################################################
class ABGItem (ABGAttributesHaver):
	INSTANCE_DEFAULT_ATTRIBUTES = {
		'x': 0,
		'y': 0,
		'layer': 0,
		'locked': False,
		'id': ""
	}

	SUBCLASSES = dict()
	def createInstanceOf (type_name: str):
		assert type_name in ABGItem.SUBCLASSES

		return ABGItem.SUBCLASSES[type_name]()

	def registerSubclass (type_name: str, c):
		assert type_name not in ABGItem.SUBCLASSES

		ABGItem.SUBCLASSES[type_name] = c

	def __init__ (this, type_name: str, attributes):
		attributes['type'] = type_name

		for (key, value) in ABGItem.INSTANCE_DEFAULT_ATTRIBUTES.items():
			if key not in attributes:
				attributes[key] = value

		ABGAttributesHaver.__init__(this, attributes)

	def pushNonInstanceAttributesTo (this, attributes: dict):
		for (key, value) in this.attributes.items():
			if key not in ABGItem.INSTANCE_DEFAULT_ATTRIBUTES:
				if (isinstance(value, ABGAttributeHaver)):
					d = dict()
					value.pushAttributesTo(d)
					attributes[key] = d
				else:
					attributes[key] = value

		return this

	def validateList (l):
		for i in l:
			assert isinstance(i, ABGItem)
			i.validate()

class ABGZone (ABGItem):
	KEY = "zone"

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGZone.KEY,
			{
				'width': 200,
				'height': 200,
				'borderColor': ABGColor.validate("#cccccc33"),
				'borderStyle': ABGBorderStyle.DOTTED,
				'backgroundColor': ABGColor.TRANSPARENT,
				'labelPosition': ABGLabelPosition.LEFT,
				'label': "",
				'holdItems': False,
				#'setState': None,
				#'onItem': None,
			}
		)

class ABGToken (ABGItem):
	KEY = "token"

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGToken.KEY,
			{
				'size': 50,
				'color': ABGColor.validate("#b3b3b3"),
				'flippedColor': ABGColor.validate("#b3b3b3"),
				'flipped': False,
				'text': "",
				'textColor': ABGColor.validate("#000"),
				'fontSize': 24,
			}
		)

class ABGScreen (ABGItem):
	KEY = "screen"

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGScreen.KEY,
			{
				'width': 1,
				'height': 1,
				'borderColor': ABGColor.TRANSPARENT,
				'borderStyle': ABGBorderStyle.DOTTED,
				'backgroundColor': ABGColor.TRANSPARENT,
				#'ownedBy': None,
				#'setState': None,
			}
		)

class ABGRound (ABGItem):
	KEY = "round"

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGRound.KEY,
			{
				'size': 50,
				'color': ABGColor.validate("#ccc"),
				'flippedColor': ABGColor.validate("#ccc"),
				'flipped': False,
				'text': "",
				'textColor': ABGColor.validate("#000"),
				'fontSize': 16,
			}
		)

class ABGRect (ABGItem):
	KEY = "rect"

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGRect.KEY,
			{
				'width': 50,
				'height': 50,
				'color': ABGColor.validate("#ccc"),
				'flippedColor': ABGColor.validate("#ccc"),
				'flipped': False,
				'text': "",
				'textColor': ABGColor.validate("#000"),
				'fontSize': 16,
			}
		)

class ABGPawn (ABGItem):
	KEY = "pawn"

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGPawn.KEY,
			{
				'size': 50,
				'color': ABGColor.validate("#b3b3b3"),
			}
		)

class ABGNote (ABGItem):
	KEY = "note"

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGNote.KEY,
			{
				'value': "",
				'color': ABGColor.validate("#FFEC27"),
				'label': "",
				'textColor': ABGColor.validate("#000"),
				'fontFamily': "Roboto",
				'fontSize': 20,
				'width': 300,
				'height': 200,
				#'setState': None,
			}
		)

class ABGMeeple (ABGItem):
	KEY = "meeple"

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGMeeple.KEY,
			{
				'size': 50,
				'color': ABGColor.validate("#b3b3b3"),
			}
		)

class ABGJewel (ABGItem):
	KEY = "jewel" # TODO: Check. It might be token

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGJewel.KEY,
			{
				'size': 50,
				'color': ABGColor.validate("#b3b3b3"),
			}
		)

class ABGPicture (ABGItem):
	KEY = "picture"

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGPicture.KEY,
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
				#'setState': None,
			}
		)

class ABGHexagon (ABGItem):
	KEY = "hexagon"

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGHexagon.KEY,
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
	KEY = "generator"

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGGenerator.KEY,
			{
			}
		)

class ABGDiceImage (ABGItem):
	KEY = "dieImage" # TODO: check.

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGDiceImage.KEY,
			{
				'value': 0,
				'images': None,
				'width': 50,
				'height': 50,
				'rollOnDblClick': False,
		#		'rollOnMove': !rollOnDblClick,
			}
		)

class ABGDice (ABGItem):
	KEY = "dice" # TODO: check.

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGDice.KEY,
			{
				'value': 0,
				'color': ABGColor.validate("#CCC"),
				'label': "",
				'textColor': ABGColor.validate("#fff"),
				'fontSize': 35,
			}
		)

class ABGCylinder (ABGItem):
	KEY = "cylinder"

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGCylinder.KEY,
			{
				'size': 50,
				'color': ABGColor.validate("#b3b3b3"),
			}
		)

class ABGCube (ABGItem):
	KEY = "cube"

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGCube.KEY,
			{
				'size': 50,
				'color': ABGColor.validate("#b3b3b3"),
			}
		)

class ABGCounter (ABGItem):
	KEY = "counter"

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGCounter.KEY,
			{
				'value': 0,
				'color': ABGColor.validate("#CCC"),
				'label': "",
				'textColor': ABGColor.validate("#000"),
				'fontSize': 22,
				#'setState': None,
			}
		)

class ABGCheckerBoard (ABGItem):
	KEY = "checkerBoard" # TODO: check

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGCheckerBoard.KEY,
			{
				'width': 50,
				'height': 50,
				'color': ABGColor.validate("#CCC"),
				'alternateColor': ABGColor.validate("#888"),
				'colCount': 3,
				'rowCount': 3,
				#'setState': None
			}
		)

################################################################################
#### ABG LANGUAGE CLASSES ######################################################
################################################################################
class ABGLanguage:
	COLLECTION = set()

	def define (key):
		assert isinstance(key, str)
		assert (key not in ABGLanguage.COLLECTION)

		ABGLanguage.COLLECTION.add(key)

		return key

	def validate (value):
		assert value in ABGLanguage.COLLECTION

class ABGMaterialLanguage:
	COLLECTION = set()

	def define (key):
		assert isinstance(key, str)
		assert (key not in ABGMaterialLanguage.COLLECTION)

		ABGMaterialLanguage.COLLECTION.add(key)

		return key

	def validate (value):
		assert value in ABGMaterialLanguage.COLLECTION

class ABGTranslation (ABGAttributesHaver):
	def __init__ (this):
		ABGAttributesHaver.__init__(
			this,
			{
				'language': "en",
				'name': "",
				'baseline': "",
				'description': ""
			}
		)

	def validateList (l):
		for i in l:
			assert isinstance(i, ABGTranslation)
			i.validate()

class ABGContent (ABGAttributesHaver):
	# Content objects have "content" that are strings...
	CONTENT_ATTRIBUTE = ABGAttribute("content", str, None, None, None)

	def __init__ (this):
		ABGAttributesHaver.__init__(
			this,
			{
				'type': "external",
				'content': ""
			},
			hijackedAttributes = {'content': ABGContent.CONTENT_ATTRIBUTE}
		)

class ABGAction (ABGAttributesHaver):

	def __init__ (this):
		ABGAttributesHaver.__init__(
			this,
			{
				'name': ""
			}
		)

################################################################################
#### ABG GAME CLASSES ##########################################################
################################################################################
class ABGDuration:
	def validate (value):
		assert isinstance(value, list)
	#	assert len(value) == 2
	#	assert isinstance(value[0], int)
	#	assert isinstance(value[1], int)
	#	assert value[0] >= 0
	#	assert value[1] <= 90
	#	assert value[0] <= value[1]

class ABGPlayerCount:
	def validate (value):
		assert isinstance(value, list)
		assert len(value) == 2
		assert isinstance(value[0], int)
		assert isinstance(value[1], int)
		assert value[0] >= 1
		assert value[1] <= 9
		assert value[0] <= value[1]

class ABGBoardPosition (ABGAttributesHaver):
	def __init__ (this):
		ABGAttributesHaver.__init__(
			this,
			{
				'top': 2000,
				'left': 2000,
				'width': 2000,
				'height': 2000,
			}
		)

class ABGBoard (ABGAttributesHaver):
	def __init__ (this):
		ABGAttributesHaver.__init__(
			this,
			{
				'size': 2000,
				'scale': 1,
				'defaultName': "",
				'bgType': "default",
				'playerCount': [1, 9],
				'duration': [],
				'gridSize': 1,
				'imageUrl': "/game_assets/default.png",
				'keepTitle': True,
				'initialBoardPosition': ABGBoardPosition(),
				'defaultLanguage': "en",
				'materialLanguage': "Multi-lang",
				'defaultBaseline': "",
				'defaultDescription': "",
				'translations': [],
				'published': False
			}
		)

class ABGGame (ABGAttributesHaver):
	def __init__ (this):
		ABGAttributesHaver.__init__(
			this,
			{
				'items': [],
				'board': ABGBoard(),
				'availableItems': [],
				'messages': [],
				'timestamp': 0,
				'gameId': ""
			}
		)
		this.ids = set()

	def fromFile (this, filename: str):
		file = open(filename)
		asDict = json.load(file)

		this.pullAttributesFromJson(asDict)

		return this

	def toFile (this, filename: str):
		asDict = dict()
		this.pushAttributesToJson(asDict)

		output = json.dump(asDict, ident=4);

		print(output)

		return this

################################################################################
#### ENUM CREATION #############################################################
################################################################################

ABGItem.registerSubclass(ABGZone.KEY, ABGZone)
ABGItem.registerSubclass(ABGToken.KEY, ABGToken)
ABGItem.registerSubclass(ABGScreen.KEY, ABGScreen)
ABGItem.registerSubclass(ABGRound.KEY, ABGRound)
ABGItem.registerSubclass(ABGRect.KEY, ABGRect)
ABGItem.registerSubclass(ABGPawn.KEY, ABGPawn)
ABGItem.registerSubclass(ABGNote.KEY, ABGNote)
ABGItem.registerSubclass(ABGMeeple.KEY, ABGMeeple)
ABGItem.registerSubclass(ABGJewel.KEY, ABGJewel)
ABGItem.registerSubclass(ABGPicture.KEY, ABGPicture)
ABGItem.registerSubclass(ABGHexagon.KEY, ABGHexagon)
ABGItem.registerSubclass(ABGGenerator.KEY, ABGGenerator)
ABGItem.registerSubclass(ABGDiceImage.KEY, ABGDiceImage)
ABGItem.registerSubclass(ABGDice.KEY, ABGDice)
ABGItem.registerSubclass(ABGCylinder.KEY, ABGCylinder)
ABGItem.registerSubclass(ABGCube.KEY, ABGCube)
ABGItem.registerSubclass(ABGCounter.KEY, ABGCounter)
ABGItem.registerSubclass(ABGCheckerBoard.KEY, ABGCheckerBoard)

ABGLabelPosition.LEFT = ABGLabelPosition.define("LEFT")

ABGBorderStyle.DOTTED = ABGBorderStyle.define("DOTTED")

ABGLanguage.EN = ABGLanguage.define("en")
ABGLanguage.FR = ABGLanguage.define("fr")

ABGMaterialLanguage.MULTI_LANG = ABGMaterialLanguage.define("Multi-lang")

ABGAttribute.ACTIONS = ABGAttribute.define("actions", list, ABGAction.validate, fromJson = ABGAction)
ABGAttribute.ALTERNATE_COLOR = ABGAttribute.define("alternateColor", str, ABGColor.validate)
ABGAttribute.AVAILABLE_ITEMS = ABGAttribute.define("availableItems", list, None, fromJson = ABGItem)
ABGAttribute.BACKGROUND_COLOR = ABGAttribute.define("backgroundColor", str, ABGColor.validate)
ABGAttribute.BACK_CONTENT = ABGAttribute.define("backContent", ABGContent, ABGContent.validate, fromJson = ABGContent)
ABGAttribute.BACK_TEXT = ABGAttribute.define("backText", str, None)
ABGAttribute.BG_TYPE = ABGAttribute.define("bgType", str, None)
ABGAttribute.BOARD = ABGAttribute.define("board", ABGBoard, None)
ABGAttribute.BORDER_COLOR = ABGAttribute.define("borderColor", str, ABGColor.validate)
ABGAttribute.BORDER_STYLE = ABGAttribute.define("borderStyle", str, ABGBorderStyle.validate)
ABGAttribute.COLOR = ABGAttribute.define("color", str, ABGColor.validate)
ABGAttribute.COL_COUNT = ABGAttribute.define("colCount", int, lambda x : (x > 0))
ABGAttribute.CONTENT = ABGAttribute.define("content", ABGContent, ABGContent.validate, fromJson = ABGContent)
ABGAttribute.DEFAULT_BASELINE = ABGAttribute.define("defaultBaseline", str, None)
ABGAttribute.DEFAULT_DESCRIPTION = ABGAttribute.define("defaultDescription", str, None)
ABGAttribute.DEFAULT_LANGUAGE = ABGAttribute.define("defaultLanguage", str, ABGLanguage.validate)
ABGAttribute.DEFAULT_NAME = ABGAttribute.define("defaultName", str, None)
ABGAttribute.BASELINE = ABGAttribute.define("baseline", str, None)
ABGAttribute.DESCRIPTION = ABGAttribute.define("description", str, None)
ABGAttribute.LANGUAGE = ABGAttribute.define("language", str, ABGLanguage.validate)
ABGAttribute.NAME = ABGAttribute.define("name", str, None)
ABGAttribute.DURATION = ABGAttribute.define("duration", list, ABGDuration.validate)
ABGAttribute.FLIPPED = ABGAttribute.define("flipped", bool, None)
ABGAttribute.FLIPPED_COLOR = ABGAttribute.define("flippedColor", str, ABGColor.validate)
ABGAttribute.FONT_SIZE = ABGAttribute.define("fontSize", int, lambda x : (x >= 0))
ABGAttribute.FONT_FAMILY = ABGAttribute.define("fontFamily", str, None)
ABGAttribute.GAME_ID = ABGAttribute.define("gameId", str, None)
ABGAttribute.GRID_SIZE = ABGAttribute.define("gridSize", int, lambda x : (x > 0))
ABGAttribute.HEIGHT = ABGAttribute.define("height", int, lambda x : (x > 0))
ABGAttribute.HOLD_ITEMS = ABGAttribute.define("holdItems", bool, None)
ABGAttribute.ID = ABGAttribute.define("id", str, None) # Don't know yet.
ABGAttribute.IMAGE_URL = ABGAttribute.define("imageUrl", str, None)
ABGAttribute.INITIAL_BOARD_POSITION = ABGAttribute.define("initialBoardPosition", ABGBoardPosition, ABGBoardPosition.validate, fromJson = ABGBoardPosition)
ABGAttribute.ITEMS = ABGAttribute.define("items", list, ABGItem.validateList, fromJson = ABGItem)
ABGAttribute.KEEP_TITLE = ABGAttribute.define("keepTitle", bool, None)
ABGAttribute.LABEL = ABGAttribute.define("label", str, None)
ABGAttribute.LABEL_POSITION = ABGAttribute.define("labelPosition", str, ABGLabelPosition.validate)
ABGAttribute.LAYER = ABGAttribute.define("layer", int, None)
ABGAttribute.LEFT = ABGAttribute.define("left", int, None)
ABGAttribute.LOCKED = ABGAttribute.define("locked", bool, None)
ABGAttribute.MATERIAL_LANGUAGE = ABGAttribute.define("materialLanguage", str, ABGMaterialLanguage.validate)
ABGAttribute.MESSAGES = ABGAttribute.define("messages", list, None)
ABGAttribute.ON_ITEM = ABGAttribute.define("onItem", int, None) # Don't know yet.
ABGAttribute.OVERLAY = ABGAttribute.define("overlay", str, None) # Don't know yet
ABGAttribute.OWNED_BY = ABGAttribute.define("ownedBy", int, None) # Don't know yet.
ABGAttribute.PLAYER_COUNT = ABGAttribute.define("playerCount", list, ABGPlayerCount.validate, fromJson = ABGPlayerCount)
ABGAttribute.PUBLISHED = ABGAttribute.define("published", bool, None)
ABGAttribute.ROLL_ON_DBL_CLICK = ABGAttribute.define("rollOnDblClick", bool, None)
ABGAttribute.ROW_COUNT = ABGAttribute.define("rowCount", int, lambda x : (x > 0))
ABGAttribute.SCALE = ABGAttribute.define("scale", int, lambda x : (x > 0))
ABGAttribute.SET_STATE = ABGAttribute.define("setState", int, None) # Don't know yet.
ABGAttribute.SIZE = ABGAttribute.define("size", int, lambda x : (x > 0))
ABGAttribute.TEXT = ABGAttribute.define("text", str, None)
ABGAttribute.TEXT_COLOR = ABGAttribute.define("textColor", str, ABGColor.validate)
ABGAttribute.TIMESTAMP = ABGAttribute.define("timestamp", int, lambda x : (x >= 0))
ABGAttribute.TOP = ABGAttribute.define("top", int, None)
ABGAttribute.TRANSLATIONS = ABGAttribute.define("translations", list, ABGTranslation.validateList, fromJson = ABGTranslation)
ABGAttribute.TYPE = ABGAttribute.define("type", str, None)
ABGAttribute.UNFLIPPED_FOR = ABGAttribute.define("unflippedFor", str, None) # Don't know yet
ABGAttribute.VERTICAL = ABGAttribute.define("vertical", bool, None)
ABGAttribute.VALUE = ABGAttribute.define("value", str, None)
ABGAttribute.WIDTH = ABGAttribute.define("width", int, lambda x : (x > 0))
ABGAttribute.X = ABGAttribute.define("x", int, None)
ABGAttribute.Y = ABGAttribute.define("y", int, None)


test = ABGHexagon()
