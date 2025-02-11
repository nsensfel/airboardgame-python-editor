#!/bin/env python3

import json

################################################################################
#### ABG ATTRIBUTE VALUE CLASSES ###############################################
################################################################################
class ABGAssert:
	def ensure (cond: bool, message: str):
		if not cond:
			raise Exception(message)

class ABGBorderStyle:
	COLLECTION = set()

	def define (key):
		ABGAssert.ensure(
			isinstance(key, str),
			"ABGBorderStyle keys must be strings. " + str(key) + " is not."
		)

		key = key.lower()

		ABGAssert.ensure(
			(key not in ABGBorderStyle.COLLECTION),
			"Duplicate definition of Border Style " + key + "."
		)

		ABGBorderStyle.COLLECTION.add(key)

		return key

	def validate (value):
		ABGAssert.ensure(
			isinstance(value, str),
			"Border Style must be strings. " + str(value) + " is not."
		)
		ABGAssert.ensure(
			value in ABGBorderStyle.COLLECTION,
			"Unknown Border Style: " + value + "."
		)

class ABGLabelPosition:
	COLLECTION = set()

	def define (key):
		ABGAssert.ensure(
			isinstance(key, str),
			"ABGLabelPosition keys must be strings. " + str(key) + " is not."
		)

		key = key.lower()

		ABGAssert.ensure(
			(key not in ABGLabelPosition.COLLECTION),
			"Duplicate definition of Label Position " + key + "."
		)

		ABGLabelPosition.COLLECTION.add(key)

		return key

	def validate (value):
		ABGAssert.ensure(
			isinstance(value, str),
			"Label Position must be strings. " + str(value) + " is not."
		)
		ABGAssert.ensure(
			value in ABGLabelPosition.COLLECTION,
			"Unknown Label Position: " + value + "."
		)

class ABGColor:
	def validate (value):
		ABGAssert.ensure(
			isinstance(value, str),
			"Colors must be strings. " + str(value) + " is not."
		)

		# TODO

		return value

ABGColor.TRANSPARENT = ABGColor.validate("transparent")

################################################################################
#### ABG ATTRIBUTE CLASSES #####################################################
################################################################################
class ABGAttribute:
	COLLECTION = dict()

	def define (key, assertedClass, specialCheck, fromJson = None, toJson = None):
		ABGAssert.ensure(
			isinstance(key, str),
			"ABGAttribute keys must be strings. " + str(key) + " is not."
		)
		ABGAssert.ensure(
			(key not in ABGAttribute.COLLECTION),
			"Duplicate definition of Attribute " + key + "."
		)

		result = ABGAttribute(key, assertedClass, specialCheck, fromJson, toJson)

		ABGAttribute.COLLECTION[key] = result

		return  result

	def ensureNumeral (value):
		if isinstance(value, int) or isinstance(value, float):
			return value

		try:
			return int(value)
		except:
			pass

		return float(value)

	def __init__ (this, key, assertedClass, specialCheck, fromJson, toJson):
		this.key = key
		this.assertedClass = assertedClass
		this.specialCheck = specialCheck
		this.fromJson = fromJson
		this.toJson = toJson

	def validate (this, value):
		if isinstance(this.assertedClass, list):
			matched = False

			for i in this.assertedClass:
				if i is None and value is None:
					matched = True
					break

				if isinstance(value, i):
					matched = True
					break

			ABGAssert.ensure(
				matched,
				(
					"The "
					+ this.key
					+ " attribute accepts values of the following types: "
					+ ", ".join([str(e) for e in this.assertedClass])
					+ ". The value "
					+ str(value)
					+ " is not compatible."
				)
			)

		elif this.assertedClass is not None:
			ABGAssert.ensure(
				isinstance(value, this.assertedClass),
				(
					"The "
					+ this.key
					+ " attribute accepts values of the type: "
					+ str(this.assertedClass)
					+ ". The value "
					+ str(value)
					+ " is not compatible."
				)
			)

		else:
			ABGAssert.ensure(
				(value is None),
				(
					"The "
					+ this.key
					+ " attribute accepts no values other than None."
					+ ". The value "
					+ str(value)
					+ " is not compatible."
				)
			)

		if this.specialCheck is not None:
			this.specialCheck(value)

		return this

	def getKey (this):
		return this.key

class ABGAttributesHaver:
	def __init__ (this, attributes, hijackedAttributes = dict()):
		this.hijackedAttributes = hijackedAttributes

		for (key, value) in attributes.items():
			attribute = this.getAttributeFromKey(key)
			attribute.validate(value)

		this.attributes = attributes

	def getAttributeFromKey (this, key):
		if key in this.hijackedAttributes:
			return this.hijackedAttributes[key]
		else:
			return ABGAttribute.COLLECTION[key]

	def setAttributeValue (this, attribute, value):
		key = None

		if isinstance(attribute, str):
			key = attribute
			attribute = this.getAttributeFromKey(key)
		else:
			key = attribute.getKey()

		ABGAssert.ensure(
			key in this.attributes,
			"There is no " + key + " attribute for this."
		)

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

		ABGAssert.ensure(
			key in this.attributes,
			"There is no " + key + " attribute for this."
		)

		return this.attributes[key]

	def pullAttributesFromJson (this, attributes: dict):
		for (key, value) in attributes.items():
			attribute = this.getAttributeFromKey(key)

			if (isinstance(value, list)):
				l = []

				for i in value:
					if (isinstance(i, dict)):
						ABGAssert.ensure(
							(attribute.fromJson is not None),
							"Missing Python class to parse: " + str(i) + "."
						)

						v = None

						if (attribute.fromJson == ABGItem):
							ABGAssert.ensure(
								("type" in i),
								"This Item entry has no \"type\" attribute."
							)

							v = ABGItem.createInstanceOf(i["type"])
						else:
							v = attribute.fromJson()

						v.pullAttributesFromJson(i)

						l.append(v)
					else:
						l.append(i)

				this.setAttributeValue(key, l)

			elif (isinstance(value, dict)):
				ABGAssert.ensure(
					(attribute.fromJson is not None),
					"Missing Python class to parse: " + str(value) + "."
				)

				v = attribute.fromJson()
				v.pullAttributesFromJson(value)

				this.setAttributeValue(key, v)
			else:
				if attribute.fromJson is not None:
					this.setAttributeValue(key, attribute.fromJson(value))
				else:
					this.setAttributeValue(key, value)

		return this

	def pushAttributesToJson (this, attributes: dict):
		for (key, value) in this.attributes.items():
			attribute = this.getAttributeFromKey(key)
			if (isinstance(value, list)):
				l = []
				for i in value:
					if (isinstance(i, ABGAttributesHaver)):
						d = dict()
						if (attribute.toJson):
							attribute.toJson(i, d)
						i.pushAttributesToJson(d)
						l.append(d)
					else:
						l.append(i)
				attributes[key] = l
			elif (isinstance(value, ABGAttributesHaver)):
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
		'moving': False,
		'id': "",
		'groupId': "",
		'actions': [],
		'grid': None
	}

	SUBCLASSES = dict()

	def createInstanceOf (type_name: str):
		ABGAssert.ensure(
			(type_name in ABGItem.SUBCLASSES),
			"Unknown type of Item: " + type_name + "."
		)

		return ABGItem.SUBCLASSES[type_name]()

	def registerSubclass (type_name: str, c):
		ABGAssert.ensure(
			(type_name not in ABGItem.SUBCLASSES),
			"Duplicate Item subclass for type: " + type_name + "."
		)

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
			ABGAssert.ensure(
				isinstance(i, ABGItem),
				"This is not an Item: " + str(i) + "."
			)
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
				'name': "",
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

class ABGImage (ABGItem):
	KEY = "image"

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGImage.KEY,
			{
				'width': 1,
				'height': 1,
				'content': ABGContent(),
				'backContent': ABGContent(),
				'flipped': False,
				'unflippedFor': [],
				'text': "",
				'label': "",
				'holdItems': False,
				'backText': "",
				'overlay': None,
				'rotation': 0
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
		ABGAssert.ensure(
			isinstance(key, str),
			"Languages must be strings. " + str(key) + " is not."
		)
		ABGAssert.ensure(
			(key not in ABGLanguage.COLLECTION),
			"Duplicate language definition: " + key + "."
		)

		ABGLanguage.COLLECTION.add(key)

		return key

	def validate (value):
		ABGAssert.ensure(
			value in ABGLanguage.COLLECTION,
			"Unknown language: " + value + "."
		)

class ABGMaterialLanguage:
	COLLECTION = set()

	def define (key):
		ABGAssert.ensure(
			isinstance(key, str),
			"Material languages must be strings. " + str(key) + " is not."
		)
		ABGAssert.ensure(
			(key not in ABGMaterialLanguage.COLLECTION),
			"Duplicate material language definition: " + key + "."
		)

		ABGMaterialLanguage.COLLECTION.add(key)

		return key

	def validate (value):
		ABGAssert.ensure(
			value in ABGMaterialLanguage.COLLECTION,
			"Unknown material language: " + value + "."
		)

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
			ABGAssert.ensure(
				isinstance(i, ABGTranslation),
				"This is not a translation: " + str(i) + "."
			)
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

	def validateList (l):
		for i in l:
			ABGAssert.ensure(
				isinstance(i, ABGAction),
				"This is not an action: " + str(i) + "."
			)
			i.validate()

################################################################################
#### ABG GAME CLASSES ##########################################################
################################################################################
class ABGDuration:
	def validate (value):
		ABGAssert.ensure(
			isinstance(value, list),
			"Duration should be a list. " + str(value) + " is not."
		)

class ABGPlayerCount:
	def validate (value):
		ABGAssert.ensure(
			isinstance(value, list),
			"Player count should be a list. " + str(value) + " is not."
		)
		ABGAssert.ensure(
			len(value) == 2,
			"Player count should have two values. " + str(value) + " does not."
		)
		ABGAssert.ensure(
			(isinstance(value[0], int) and isinstance(value[1], int)),
			"Player count should be two integers. " + str(value) + " is not."
		)
		ABGAssert.ensure(
			value[0] >= 1,
			"Minimal player count should be 1 or more. " + str(value) + " is illegal."
		)
		ABGAssert.ensure(
			value[1] <= 9,
			"Maximal player count should be 9 or less. " + str(value) + " is illegal."
		)
		ABGAssert.ensure(
			value[0] <= value[1],
			"Maximal player count should be less or equal to minimum player count. " + str(value) + " is illegal."
		)

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

class ABGLocation (ABGAttributesHaver):
	def __init__ (this):
		ABGAttributesHaver.__init__(
			this,
			{
				'x': 0,
				'y': 0,
			}
		)

class ABGGrid (ABGAttributesHaver):
	def __init__ (this):
		ABGAttributesHaver.__init__(
			this,
			{
				'type': "grid",
				'size': 0,
				'offset': ABGLocation()
			}
		)

	def validate (this):
		if this is not None:
			ABGAttributesHaver.validate(this)

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
				'neverSaved': True,
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

		json.dump(asDict, open(filename, 'w'), indent=4);

		return this

################################################################################
#### ENUM CREATION #############################################################
################################################################################

ABGItem.registerSubclass(ABGCheckerBoard.KEY, ABGCheckerBoard)
ABGItem.registerSubclass(ABGCounter.KEY, ABGCounter)
ABGItem.registerSubclass(ABGCube.KEY, ABGCube)
ABGItem.registerSubclass(ABGCylinder.KEY, ABGCylinder)
ABGItem.registerSubclass(ABGDice.KEY, ABGDice)
ABGItem.registerSubclass(ABGDiceImage.KEY, ABGDiceImage)
ABGItem.registerSubclass(ABGGenerator.KEY, ABGGenerator)
ABGItem.registerSubclass(ABGHexagon.KEY, ABGHexagon)
ABGItem.registerSubclass(ABGImage.KEY, ABGImage)
ABGItem.registerSubclass(ABGJewel.KEY, ABGJewel)
ABGItem.registerSubclass(ABGMeeple.KEY, ABGMeeple)
ABGItem.registerSubclass(ABGNote.KEY, ABGNote)
ABGItem.registerSubclass(ABGPawn.KEY, ABGPawn)
ABGItem.registerSubclass(ABGRect.KEY, ABGRect)
ABGItem.registerSubclass(ABGRound.KEY, ABGRound)
ABGItem.registerSubclass(ABGScreen.KEY, ABGScreen)
ABGItem.registerSubclass(ABGToken.KEY, ABGToken)
ABGItem.registerSubclass(ABGZone.KEY, ABGZone)

ABGLabelPosition.LEFT = ABGLabelPosition.define("left")
ABGLabelPosition.TOP = ABGLabelPosition.define("top")

ABGBorderStyle.DOTTED = ABGBorderStyle.define("DOTTED")
ABGBorderStyle.SOLID = ABGBorderStyle.define("SOLID")
ABGBorderStyle.DASHED = ABGBorderStyle.define("DASHED")

ABGLanguage.EN = ABGLanguage.define("en")
ABGLanguage.FR = ABGLanguage.define("fr")

ABGMaterialLanguage.MULTI_LANG = ABGMaterialLanguage.define("Multi-lang")
ABGMaterialLanguage.EN = ABGMaterialLanguage.define("en")
ABGMaterialLanguage.FR = ABGMaterialLanguage.define("fr")

ABGAttribute.ACTIONS = ABGAttribute.define("actions", list, ABGAction.validateList, fromJson = ABGAction)
ABGAttribute.ALTERNATE_COLOR = ABGAttribute.define("alternateColor", str, ABGColor.validate)
ABGAttribute.AVAILABLE_ITEMS = ABGAttribute.define("availableItems", list, None, fromJson = ABGItem)
ABGAttribute.BACKGROUND_COLOR = ABGAttribute.define("backgroundColor", str, ABGColor.validate)
ABGAttribute.BACK_CONTENT = ABGAttribute.define("backContent", ABGContent, ABGContent.validate, fromJson = ABGContent)
ABGAttribute.BACK_TEXT = ABGAttribute.define("backText", str, None)
ABGAttribute.BASELINE = ABGAttribute.define("baseline", str, None)
ABGAttribute.BG_TYPE = ABGAttribute.define("bgType", str, None)
ABGAttribute.BOARD = ABGAttribute.define("board", ABGBoard, None, fromJson = ABGBoard)
ABGAttribute.BORDER_COLOR = ABGAttribute.define("borderColor", str, ABGColor.validate)
ABGAttribute.BORDER_STYLE = ABGAttribute.define("borderStyle", str, ABGBorderStyle.validate)
ABGAttribute.COLOR = ABGAttribute.define("color", str, ABGColor.validate)
ABGAttribute.COL_COUNT = ABGAttribute.define("colCount", int, lambda x : (x > 0), fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.CONTENT = ABGAttribute.define("content", ABGContent, ABGContent.validate, fromJson = ABGContent)
ABGAttribute.DEFAULT_BASELINE = ABGAttribute.define("defaultBaseline", str, None)
ABGAttribute.DEFAULT_DESCRIPTION = ABGAttribute.define("defaultDescription", str, None)
ABGAttribute.DEFAULT_LANGUAGE = ABGAttribute.define("defaultLanguage", str, ABGLanguage.validate)
ABGAttribute.DEFAULT_NAME = ABGAttribute.define("defaultName", str, None)
ABGAttribute.DESCRIPTION = ABGAttribute.define("description", str, None)
ABGAttribute.DURATION = ABGAttribute.define("duration", list, ABGDuration.validate)
ABGAttribute.FILE = ABGAttribute.define("file", str, None)
ABGAttribute.FLIPPED = ABGAttribute.define("flipped", bool, None)
ABGAttribute.FLIPPED_COLOR = ABGAttribute.define("flippedColor", str, ABGColor.validate)
ABGAttribute.FONT_FAMILY = ABGAttribute.define("fontFamily", str, None)
ABGAttribute.FONT_SIZE = ABGAttribute.define("fontSize", [int, float], lambda x : (x >= 0), fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.GAME_ID = ABGAttribute.define("gameId", str, None)
ABGAttribute.GRID = ABGAttribute.define("grid", [ABGGrid, None], ABGGrid.validate, fromJson = ABGGrid)
ABGAttribute.GRID_SIZE = ABGAttribute.define("gridSize", int, lambda x : (x > 0), fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.GROUP_ID = ABGAttribute.define("groupId", str, None)
ABGAttribute.HEIGHT = ABGAttribute.define("height", [int, float], lambda x : (x > 0), fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.HOLD_ITEMS = ABGAttribute.define("holdItems", bool, None)
ABGAttribute.ID = ABGAttribute.define("id", str, None) # Don't know yet.
ABGAttribute.IMAGE_URL = ABGAttribute.define("imageUrl", str, None)
ABGAttribute.INITIAL_BOARD_POSITION = ABGAttribute.define("initialBoardPosition", ABGBoardPosition, ABGBoardPosition.validate, fromJson = ABGBoardPosition)
ABGAttribute.ITEMS = ABGAttribute.define("items", list, ABGItem.validateList, fromJson = ABGItem)
ABGAttribute.KEEP_TITLE = ABGAttribute.define("keepTitle", bool, None)
ABGAttribute.LABEL = ABGAttribute.define("label", str, None)
ABGAttribute.LABEL_POSITION = ABGAttribute.define("labelPosition", str, ABGLabelPosition.validate)
ABGAttribute.LANGUAGE = ABGAttribute.define("language", str, ABGLanguage.validate)
ABGAttribute.LAYER = ABGAttribute.define("layer", int, None, fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.LEFT = ABGAttribute.define("left", [int, float], None, fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.LOCKED = ABGAttribute.define("locked", bool, None)
ABGAttribute.MATERIAL_LANGUAGE = ABGAttribute.define("materialLanguage", str, ABGMaterialLanguage.validate)
ABGAttribute.MESSAGES = ABGAttribute.define("messages", list, None)
ABGAttribute.MOVING = ABGAttribute.define("moving", bool, None)
ABGAttribute.NAME = ABGAttribute.define("name", str, None)
ABGAttribute.NEVER_SAVED = ABGAttribute.define("neverSaved", bool, None)
ABGAttribute.OFFSET = ABGAttribute.define("offset", ABGLocation, ABGLocation.validate, fromJson = ABGLocation)
ABGAttribute.ON_ITEM = ABGAttribute.define("onItem", None, None) # Don't know yet.
ABGAttribute.OVERLAY = ABGAttribute.define("overlay", None, None) # Don't know yet
ABGAttribute.OWNED_BY = ABGAttribute.define("ownedBy", None, None) # Don't know yet.
ABGAttribute.PLAYER_COUNT = ABGAttribute.define("playerCount", list, ABGPlayerCount.validate, fromJson = ABGPlayerCount)
ABGAttribute.PUBLISHED = ABGAttribute.define("published", bool, None)
ABGAttribute.ROLL_ON_DBL_CLICK = ABGAttribute.define("rollOnDblClick", bool, None)
ABGAttribute.ROW_COUNT = ABGAttribute.define("rowCount", int, lambda x : (x > 0), fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.SCALE = ABGAttribute.define("scale", [int, float], lambda x : (x > 0), fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.SET_STATE = ABGAttribute.define("setState", None, None) # Don't know yet.
ABGAttribute.SIZE = ABGAttribute.define("size", [int, float], lambda x : (x > 0), fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.TEXT = ABGAttribute.define("text", str, None)
ABGAttribute.TEXT_COLOR = ABGAttribute.define("textColor", str, ABGColor.validate)
ABGAttribute.TIMESTAMP = ABGAttribute.define("timestamp", int, lambda x : (x >= 0), fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.TOP = ABGAttribute.define("top", [int, float], None, fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.TRANSLATIONS = ABGAttribute.define("translations", list, ABGTranslation.validateList, fromJson = ABGTranslation)
ABGAttribute.TYPE = ABGAttribute.define("type", str, None)
ABGAttribute.UNFLIPPED_FOR = ABGAttribute.define("unflippedFor", [list, None], None) # Don't know yet
ABGAttribute.VALUE = ABGAttribute.define("value", str, None)
ABGAttribute.VERTICAL = ABGAttribute.define("vertical", bool, None)
ABGAttribute.WIDTH = ABGAttribute.define("width", [int, float], lambda x : (x > 0), fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.X = ABGAttribute.define("x", [int, float], None, fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.Y = ABGAttribute.define("y", [int, float], None, fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.ROTATION = ABGAttribute.define("rotation", [int, float], None, fromJson = ABGAttribute.ensureNumeral)

if __name__ == '__main__':
	import sys

	testGame = ABGGame()
	testGame.fromFile(sys.argv[1])
	testGame.toFile(sys.argv[1] + ".out")
