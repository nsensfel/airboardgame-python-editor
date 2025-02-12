#!/bin/env python3

import json
import inspect
import copy
import math

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

	def validate (value, parent = ""):
		if len(parent) > 0:
			parent = " from " + parent

		ABGAssert.ensure(
			isinstance(value, str),
			"Border Style must be strings. " + str(value) + parent +" is not."
		)
		ABGAssert.ensure(
			value in ABGBorderStyle.COLLECTION,
			"Unknown Border Style: " + value + parent + "."
		)

		return True

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

	def validate (value, parent = ""):
		if len(parent) > 0:
			parent = " from " + parent

		ABGAssert.ensure(
			isinstance(value, str),
			"Label Position must be strings. " + str(value) + parent + " is not."
		)
		ABGAssert.ensure(
			value in ABGLabelPosition.COLLECTION,
			"Unknown Label Position: " + value + parent + "."
		)

		return True

class ABGSide:
	COLLECTION = set()

	def define (key):
		ABGAssert.ensure(
			isinstance(key, str),
			"ABGSide keys must be strings. " + str(key) + " is not."
		)

		key = key.lower()

		ABGAssert.ensure(
			(key not in ABGSide.COLLECTION),
			"Duplicate definition of Side " + key + "."
		)

		ABGSide.COLLECTION.add(key)

		return key

	def validate (value, parent = ""):
		if len(parent) > 0:
			parent = " from " + parent

		ABGAssert.ensure(
			isinstance(value, str),
			"Sides must be strings. " + str(value) + parent + " is not."
		)
		ABGAssert.ensure(
			value in ABGSide.COLLECTION,
			"Unknown Side: " + value + parent + "."
		)

		return True

class ABGColor:

	def define (value):
		ABGColor.validate(value)

		return value

	def validate (value, parent = ""):
		if len(parent) > 0:
			parent = " from " + parent

		ABGAssert.ensure(
			isinstance(value, str),
			"Colors must be strings. " + str(value) + parent + " is not."
		)

		# TODO

		return True

class ABGFamilies:
	def validate (value, parent = ""):
		if len(parent) > 0:
			parent = " from " + parent

		ABGAssert.ensure(
			isinstance(value, list),
			"Families must be lists. " + str(value) + parent + " is not."
		)

		for e in value:
			ABGAssert.ensure(
				isinstance(e, str),
				"Families must be lists of strings. " + str(value) + parent + " is not."
			)

		return True

class ABGId:
	def validate (value, parent = ""):
		if len(parent) > 0:
			parent = " from " + parent

		ABGAssert.ensure(
			isinstance(value, str),
			"IDs must be strings. " + str(value) + parent + " is not."
		)

		return True

	def validateList (l, parent = ""):
		for i in l:
			if not ABGId.validate(i, parent):
				return False

		return True

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

	def validate (this, value, parent = ""):
		true_parent = parent

		if len(parent) > 0:
			parent = " of " + parent

		if isinstance(this.assertedClass, list):
			matched = False

			for i in this.assertedClass:
				if i is None and value is None:
					matched = True
					break

				if i is not None and isinstance(value, i):
					matched = True
					break

			ABGAssert.ensure(
				matched,
				(
					"The "
					+ this.key
					+ " attribute"
					+ parent
					+ " accepts values of the following types: "
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
					+ " attribute"
					+ parent
					+ " accepts values of the type: "
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
					+ " attribute"
					+ parent
					+ " accepts no values other than None."
					+ ". The value "
					+ str(value)
					+ " is not compatible."
				)
			)

		if this.specialCheck is not None:
			ABGAssert.ensure(
				this.specialCheck(value, true_parent),
				(
					"The "
					+ this.key
					+ " attribute"
					+ parent
					+ " does not accept the value "
					+ str(value)
					+ "."
				)
			)

		return True

	def getKey (this):
		return this.key

class ABGAttributesHaver:
	def __init__ (this, name, attributes, hijackedAttributes = dict()):
		this.name = name
		this.hijackedAttributes = hijackedAttributes

		for (key, value) in attributes.items():
			attribute = this.getAttribute(key)
			attribute.validate(value, name)

		this.attributes = attributes

	def getAttribute (this, keyOrAttribute):
		key = keyOrAttribute

		if isinstance(key, ABGAttribute):
			key = key.getKey()
		else:
			ABGAssert.ensure(
				key in ABGAttribute.COLLECTION,
				this.name + " has unknown attribute " + key + "."
			)

		if key in this.hijackedAttributes:
			return this.hijackedAttributes[key]
		else:
			return ABGAttribute.COLLECTION[key]

	def hasAttribute (this, keyOrAttribute):
		key = keyOrAttribute

		if isinstance(key, ABGAttribute):
			key = key.getKey()

		return key in this.attributes

	def setAttributeValue (this, attribute, value):
		attribute = this.getAttribute(attribute)
		key = attribute.getKey()

		ABGAssert.ensure(
			key in this.attributes,
			"There is no " + key + " attribute for " + this.name + " objects."
		)

		attribute.validate(value, this.name)

		this.attributes[key] = value

		return this

	def getAttributeValue (this, attribute):
		attribute = this.getAttribute(attribute)
		key = attribute.getKey()

		ABGAssert.ensure(
			key in this.attributes,
			"There is no " + key + " attribute for " + this.name + " objects."
		)

		return this.attributes[key]

	def pullAttributesFromJson (this, attributes: dict):
		for (key, value) in attributes.items():
			attribute = this.getAttribute(key)

			if (isinstance(value, list)):
				l = []

				for i in value:
					if (isinstance(i, dict)):
						ABGAssert.ensure(
							(attribute.fromJson is not None),
							(
								"Missing Python class to parse a "
								+ this.name
								+ " object's "
								+ key
								+ " attribute from a list containing: "
								+ str(i)
							)
						)

						v = None

						if (inspect.isclass(attribute.fromJson)):
							v = attribute.fromJson()
							v.pullAttributesFromJson(i)
						else:
							v = attribute.fromJson(i)

						l.append(v)
					else:
						l.append(i)

				this.setAttributeValue(key, l)

			elif (isinstance(value, dict)):
				ABGAssert.ensure(
					(attribute.fromJson is not None),
					(
						"Missing Python class to parse a "
						+ this.name
						+ " object's "
						+ key
						+ " attribute from: "
						+ str(value)
					)
				)

				v = None

				if (inspect.isclass(attribute.fromJson)):
					v = attribute.fromJson()
					v.pullAttributesFromJson(value)
				else:
					v = attribute.fromJson(value)

				this.setAttributeValue(key, v)
			else:
				if attribute.fromJson is not None:
					this.setAttributeValue(key, attribute.fromJson(value))
				else:
					this.setAttributeValue(key, value)

	def pushAttributesToJson (this, attributes: dict):
		for (key, value) in this.attributes.items():
			attribute = this.getAttribute(key)

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
			elif (value is not None):
				attributes[key] = value

		return this

	def asDict (this):
		return this.attributes

	def validate (this, parent = ""):
		if len(parent) > 0:
			parent = parent + "::"

		if this is None:
			return True

		for (key, value) in this.attributes.items():
			attribute = this.getAttribute(key)
			attribute.validate(value, parent + this.name)

		# TODO: we're currently not checking which attributes are there or not.

		return True

	def clone (this):
		return copy.deepcopy(this)

################################################################################
#### ADVANCED VALUES FOR ATTRIBUTES ############################################
################################################################################
class ABGContent (ABGAttributesHaver):
	# Content objects have "content" that are strings...
	CONTENT_ATTRIBUTE = ABGAttribute("content", str, None, None, None)

	def __init__ (this):
		ABGAttributesHaver.__init__(
			this,
			"Content",
			{
				'id': "",
				'type': "external",
				'content': "",
				'file': ""
			},
			hijackedAttributes = {'content': ABGContent.CONTENT_ATTRIBUTE}
		)

	def fromJson (val):
		if isinstance(val, str):
			return val

		result = ABGContent()

		result.pullAttributesFromJson(val)

		return result

	def validate (this, parent = ""):
		if isinstance(this, str):
			return True

		if this is not None:
			return ABGAttributesHaver.validate(this, parent)

	def validateList (l, parent = ""):
		source = "" if len(parent) == 0 else ("Found in " + parent + "'s attributes: ")

		for i in l:
			ABGAssert.ensure(
				isinstance(i, ABGContent),
				source + "This is not a ABGContent: " + str(i) + "."
			)
			i.validate(parent)

		return True

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
		'label': "",
		'name': "",
		'groupId': "",
		'editable': None,
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

	def __init__ (this, type_name: str, attributes, hijackedAttributes = dict()):
		attributes['type'] = type_name

		for (key, value) in ABGItem.INSTANCE_DEFAULT_ATTRIBUTES.items():
			if key not in attributes:
				attributes[key] = value

		ABGAttributesHaver.__init__(
			this,
			"Item::" + type_name,
			attributes,
			hijackedAttributes = hijackedAttributes
		)

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

	def validateList (l, parent = ""):
		source = "" if len(parent) == 0 else ("Found in " + parent + "'s attributes: ")

		for i in l:
			ABGAssert.ensure(
				isinstance(i, ABGItem),
				source + "This is not an Item: " + str(i) + "."
			)
			i.validate(parent)

		return True

	def fromJson (value):
		if value is None:
			return None

		ABGAssert.ensure(
			("type" in value),
			(
				"An object's attribute was fed a list with a Item that has no"
				+ " type field: "
				+ str(value)
			)
		)

		result = ABGItem.createInstanceOf(value["type"])
		result.pullAttributesFromJson(value)

		return result

	def getLocation (this):
		return (this.getAttributeValue("x"), this.getAttributeValue("y"))

	def getCenterLocation (this):
		(x, y) = this.getLocation()

		if this.hasAttribute("width") and this.hasAttribute("height"):
			return (
				(x + this.getAttributeValue("width") / 2.0),
				(y + this.getAttributeValue("height") / 2.0)
			)
		elif this.hasAttribute("radius"):
			radius = this.getAttributeValue("radius")
			return (
				(x + radius),
				(y + radius)
			)
		elif this.hasAttribute("size"):
			half_size = this.getAttributeValue("size") / 2.0
			return (
				(x + half_size),
				(y + half_size)
			)
		else:
			return (x, y)

	def setLocation (this, x, y, useCenter = False):
		if useCenter:
			(center_x, center_y) = this.getCenterLocation()
			x -= (this.getAttributeValue("x") - center_x)
			y -= (this.getAttributeValue("y") - center_y)

		this.setAttributeValue("x", x)
		this.setAttributeValue("y", y)

		return this

	def setLocationRelativeTo (this, otherItem, offsetX, offsetY, useCenters = False):
		other_x = 0
		other_y = 0

		if useCenters:
			(other_x, other_y) = otherItem.getCenterLocation()
		else:
			(other_x, other_y) = otherItem.getLocation()

		this.setLocation(other_x + offsetX, other_y + offsetY, useCenters)

	def getDistanceTo (this, otherItem, useCenters = False):
		other_x = 0
		other_y = 0
		this_x = 0
		this_y = 0

		if useCenters:
			(other_x, other_y) = otherItem.getCenterLocation()
			(this_x, this_y) = this.getCenterLocation()
		else:
			(other_x, other_y) = otherItem.getLocation()
			(this_x, this_y) = this.getLocation()

		return math.dist([this_x, this_y], [other_x, other_y])

class ABGZone (ABGItem):
	KEY = "zone"

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGZone.KEY,
			{
				'width': 200,
				'height': 200,
				'borderColor': ABGColor.define("#cccccc33"),
				'borderStyle': ABGBorderStyle.DOTTED,
				'backgroundColor': ABGColor.TRANSPARENT,
				'labelPosition': ABGLabelPosition.LEFT,
				'holdItems': False,
				'linkedItems': [],
				#'setState': None,
				'onItem': [],
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
				'color': ABGColor.define("#b3b3b3"),
				'flippedColor': ABGColor.define("#b3b3b3"),
				'flipped': False,
				'text': "",
				'textColor': ABGColor.define("#000"),
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
				'radius': 50,
				'color': ABGColor.define("#ccc"),
				'flippedColor': ABGColor.define("#ccc"),
				'flipped': False,
				'text': "",
				'textColor': ABGColor.define("#000"),
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
				'color': ABGColor.define("#ccc"),
				'flippedColor': ABGColor.define("#ccc"),
				'flipped': False,
				'text': "",
				'textColor': ABGColor.define("#000"),
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
				'color': ABGColor.define("#b3b3b3"),
			}
		)

class ABGAnchor (ABGItem):
	KEY = "anchor"

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGAnchor.KEY,
			{
				'families': [],
				'color': ABGColor.define("#b3b3b3"),
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
				'color': ABGColor.define("#FFEC27"),
				'textColor': ABGColor.define("#000"),
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
				'color': ABGColor.define("#b3b3b3"),
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
				'color': ABGColor.define("#b3b3b3"),
			}
		)

# FIXME: Image vs AdvancedImage

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
				'holdItems': False,
				'backText': "",
				'overlay': ABGContent(),
				'rotation': 0
				#'setState': None,
			}
		)

class ABGAdvancedImage (ABGItem):
	KEY = "advancedImage"

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGImage.KEY,
			{
				'width': 1,
				'height': 1,
				'front': ABGContent(),
				'back': ABGContent(),
				'flipped': False,
				'unflippedFor': [],
				'text': "",
				'backText': "",
				'layers': [],
				'holdItems': False,
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
				'color': "#ccc",
				'item': None,
				'currentItemId': "",
				'linkedItems': []
			}
		)

class ABGDiceImage (ABGItem):
	KEY = "diceImage" # TODO: check.
	IMAGES_ATTRIBUTE = ABGAttribute("images", list, ABGContent.validateList, ABGContent, None)

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGDiceImage.KEY,
			{
				'value': 0,
				'side': 6,
				'images': [],
				'width': 50,
				'height': 50,
				'rollOnDblClick': False,
		#		'rollOnMove': !rollOnDblClick,
			},
			hijackedAttributes = {
				'value': ABGDice.VALUE_ATTRIBUTE,
				'side': ABGDice.SIDE_ATTRIBUTE,
				'images': ABGDiceImage.IMAGES_ATTRIBUTE
			}
		)

class ABGDice (ABGItem):
	KEY = "dice" # TODO: check.
	VALUE_ATTRIBUTE = ABGAttribute("value", int, lambda x, y : x >= 0, None, None)
	SIDE_ATTRIBUTE = ABGAttribute("side", int, lambda x, y : x >= 1, ABGAttribute.ensureNumeral, None)

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGDice.KEY,
			{
				'value': 0,
				'side': 6,
				'color': ABGColor.define("#CCC"),
				'textColor': ABGColor.define("#fff"),
				'fontSize': 35,
			},
			hijackedAttributes = {
				'value': ABGDice.VALUE_ATTRIBUTE,
				'side': ABGDice.SIDE_ATTRIBUTE
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
				'color': ABGColor.define("#b3b3b3"),
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
				'color': ABGColor.define("#b3b3b3"),
			}
		)

class ABGCounter (ABGItem):
	KEY = "counter"

	VALUE_ATTRIBUTE = ABGAttribute("value", int, None, None, None)
	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGCounter.KEY,
			{
				'value': 0,
				'color': ABGColor.define("#CCC"),
				'textColor': ABGColor.define("#000"),
				'fontSize': 22,
				#'setState': None,
			},
			hijackedAttributes = {'value': ABGCounter.VALUE_ATTRIBUTE}
		)

class ABGCheckerBoard (ABGItem):
	KEY = "checkerboard"

	def __init__ (this):
		ABGItem.__init__(
			this,
			ABGCheckerBoard.KEY,
			{
				'width': 50,
				'height': 50,
				'color': ABGColor.define("#CCC"),
				'alternateColor': ABGColor.define("#888"),
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

	def validate (value, parent = ""):
		if len(parent) > 0:
			parent = " used in " + parent

		ABGAssert.ensure(
			value in ABGLanguage.COLLECTION,
			"Unknown language" + parent + ": " + value + "."
		)

		return True

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

	def validate (value, parent = ""):
		if len(parent) > 0:
			parent = " used in " + parent

		ABGAssert.ensure(
			value in ABGMaterialLanguage.COLLECTION,
			"Unknown material language" + parent + ": " + value + "."
		)

		return True

class ABGTranslation (ABGAttributesHaver):
	def __init__ (this):
		ABGAttributesHaver.__init__(
			this,
			"Translation",
			{
				'language': "en",
				'name': "",
				'baseline': "",
				'description': ""
			}
		)

	def validateList (l, parent = ""):
		source = "" if len(parent) == 0 else ("Found in " + parent + "'s attributes: ")

		for i in l:
			ABGAssert.ensure(
				isinstance(i, ABGTranslation),
				source + "This is not a translation: " + str(i) + "."
			)

			i.validate(parent)

		return True

class ABGActionArgs (ABGAttributesHaver):
	def __init__ (this):
		ABGAttributesHaver.__init__(
			this,
			"ActionArgs",
			{
				'customLabel': None,
				'customShortcut': None,
				'angle': None,
			}
		)

	def validateList (l, parent = ""):
		source = "" if len(parent) == 0 else ("Found in " + parent + "'s attributes: ")

		for i in l:
			ABGAssert.ensure(
				isinstance(i, ABGActionArgs),
				source + "This is not an ActionArgs: " + str(i) + "."
			)

			if not i.validate(parent):
				return False

		return True

class ABGAction (ABGAttributesHaver):
	def __init__ (this):
		ABGAttributesHaver.__init__(
			this,
			"Action",
			{
				'name': "",
				'uid': "",
				'args': None,
			}
		)

	def validateList (l, parent = ""):
		source = "" if len(parent) == 0 else ("Found in " + parent + "'s attributes: ")

		for i in l:
			ABGAssert.ensure(
				isinstance(i, ABGAction),
				source + "This is not an action: " + str(i) + "."
			)

			if not i.validate(parent):
				return False

		return True

class ABGLayerImage (ABGAttributesHaver):
	def __init__ (this):
		ABGAttributesHaver.__init__(
			this,
			"LayerImage",
			{
				'uid': "",
				'type': "external",
				'content': ""
			},
			hijackedAttributes = {'content': ABGContent.CONTENT_ATTRIBUTE}
		)

	def validate (this, parent = ""):
		if isinstance(this, str):
			return True

		if this is not None:
			return ABGAttributesHaver.validate(this, parent)

	def validateList (l, parent = ""):
		source = "" if len(parent) == 0 else ("Found in " + parent + "'s attributes: ")

		for i in l:
			ABGAssert.ensure(
				isinstance(i, ABGLayerImage),
				source + "This is not an LayerImage: " + str(i) + "."
			)

			if not i.validate(parent):
				return False

		return True

class ABGImageLayer (ABGAttributesHaver):
	def __init__ (this):
		ABGAttributesHaver.__init__(
			this,
			"ImageLayer",
			{
				'uid': "",
				'offset': ABGLocation(),
				'images': [],
				'side': "front",
				'offsetX': 0,
				'offsetY': 0
			}
		)

	def validateList (l, parent = ""):
		source = "" if len(parent) == 0 else ("Found in " + parent + "'s attributes: ")

		for i in l:
			ABGAssert.ensure(
				isinstance(i, ABGImageLayer),
				source + "This is not an ImageLayer: " + str(i) + "."
			)

			if not i.validate(parent):
				return False

		return True

################################################################################
#### ABG GAME CLASSES ##########################################################
################################################################################
class ABGDuration:
	def validate (value, parent = ""):
		if len(parent) > 0:
			parent = parent + "'s "

		ABGAssert.ensure(
			isinstance(value, list),
			parent + "Duration should be a list. " + str(value) + " is not."
		)

		return True

class ABGPlayerCount:
	def validate (value, parent = ""):
		if len(parent) > 0:
			parent = parent + "'s "

		ABGAssert.ensure(
			isinstance(value, list),
			parent + "Player count should be a list. " + str(value) + " is not."
		)
		ABGAssert.ensure(
			(len(value) == 0) or len(value) == 2,
			parent + "Player count should have two values or none. " + str(value) + " does not."
		)

		if (len(value) == 0):
			return True

		ABGAssert.ensure(
			(isinstance(value[0], int) and isinstance(value[1], int)),
			parent + "Player count should be two integers. " + str(value) + " is not."
		)
		ABGAssert.ensure(
			value[0] >= 1,
			parent + "Minimal player count should be 1 or more. " + str(value) + " is illegal."
		)
		ABGAssert.ensure(
			value[1] <= 9,
			parent + "Maximal player count should be 9 or less. " + str(value) + " is illegal."
		)
		ABGAssert.ensure(
			value[0] <= value[1],
			parent + "Maximal player count should be less or equal to minimum player count. " + str(value) + " is illegal."
		)

		return True

class ABGBoardPosition (ABGAttributesHaver):
	def __init__ (this):
		ABGAttributesHaver.__init__(
			this,
			"BoardPosition",
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
			"Location",
			{
				'x': 0,
				'y': 0,
			}
		)

class ABGGrid (ABGAttributesHaver):
	def __init__ (this):
		ABGAttributesHaver.__init__(
			this,
			"Grid",
			{
				'type': "grid",
				'size': 0,
				'offset': ABGLocation()
			}
		)

	def validate (this, parent):
		if this is not None:
			return ABGAttributesHaver.validate(this, parent)
		else:
			return True

class ABGBoard (ABGAttributesHaver):
	def __init__ (this):
		ABGAttributesHaver.__init__(
			this,
			"Board",
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
			"Game",
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

	def findItemsMatching (this, criteria):
		result = list()

		for e in this.getAttributeValue('items'):
			matched = True

			for (key, value) in criteria.items():
				if not e.hasAttribute(key):
					matched = False
					break

				if not e.getAttributeValue(key) == value:
					matched = False
					break

			if matched:
				result.append(e)

		return result

	def addItem (this, item):
		ABGAssert.ensure(isinstance(item, ABGItem), "This is not an item.")
		this.getAttributeValue('items').append(item)

################################################################################
#### ENUM CREATION #############################################################
################################################################################
ABGColor.TRANSPARENT = ABGColor.define("transparent")

ABGItem.registerSubclass(ABGAdvancedImage.KEY, ABGAdvancedImage)
ABGItem.registerSubclass(ABGAnchor.KEY, ABGAnchor)
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

ABGSide.FRONT = ABGSide.define("front")
ABGSide.BACK = ABGSide.define("back")

ABGBorderStyle.DOTTED = ABGBorderStyle.define("DOTTED")
ABGBorderStyle.SOLID = ABGBorderStyle.define("SOLID")
ABGBorderStyle.DASHED = ABGBorderStyle.define("DASHED")

ABGLanguage.EN = ABGLanguage.define("en")
ABGLanguage.FR = ABGLanguage.define("fr")

ABGMaterialLanguage.MULTI_LANG = ABGMaterialLanguage.define("Multi-lang")
ABGMaterialLanguage.EN = ABGMaterialLanguage.define("en")
ABGMaterialLanguage.FR = ABGMaterialLanguage.define("fr")

ABGAttribute.ACTIONS = ABGAttribute.define("actions", list, ABGAction.validateList, fromJson = ABGAction)
ABGAttribute.ON_ITEM = ABGAttribute.define("onItem", list, ABGAction.validateList, fromJson = ABGAction)
ABGAttribute.ARGS = ABGAttribute.define("args", [None, ABGActionArgs], ABGActionArgs.validate, fromJson = ABGActionArgs)
ABGAttribute.ALTERNATE_COLOR = ABGAttribute.define("alternateColor", str, ABGColor.validate)
ABGAttribute.AVAILABLE_ITEMS = ABGAttribute.define("availableItems", list, None, fromJson = ABGItem.fromJson)
ABGAttribute.BACK = ABGAttribute.define("back", [ABGContent, str], ABGContent.validate, fromJson = ABGContent.fromJson)
ABGAttribute.BACKGROUND_COLOR = ABGAttribute.define("backgroundColor", str, ABGColor.validate)
ABGAttribute.BACK_CONTENT = ABGAttribute.define("backContent", [ABGContent, None, str], ABGContent.validate, fromJson = ABGContent)
ABGAttribute.BACK_TEXT = ABGAttribute.define("backText", str, None)
ABGAttribute.BASELINE = ABGAttribute.define("baseline", str, None)
ABGAttribute.BG_TYPE = ABGAttribute.define("bgType", str, None)
ABGAttribute.BOARD = ABGAttribute.define("board", ABGBoard, None, fromJson = ABGBoard)
ABGAttribute.BORDER_COLOR = ABGAttribute.define("borderColor", str, ABGColor.validate)
ABGAttribute.BORDER_STYLE = ABGAttribute.define("borderStyle", str, ABGBorderStyle.validate)
ABGAttribute.COLOR = ABGAttribute.define("color", str, ABGColor.validate)
ABGAttribute.COL_COUNT = ABGAttribute.define("colCount", int, lambda x, y : (x > 0), fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.CONTENT = ABGAttribute.define("content", [ABGContent, str], ABGContent.validate, fromJson = ABGContent.fromJson)
ABGAttribute.CURRENT_ITEM_ID = ABGAttribute.define("currentItemId", str, None) # Don't know yet.
ABGAttribute.DEFAULT_BASELINE = ABGAttribute.define("defaultBaseline", str, None)
ABGAttribute.DEFAULT_DESCRIPTION = ABGAttribute.define("defaultDescription", str, None)
ABGAttribute.DEFAULT_LANGUAGE = ABGAttribute.define("defaultLanguage", str, ABGLanguage.validate)
ABGAttribute.DEFAULT_NAME = ABGAttribute.define("defaultName", str, None)
ABGAttribute.DESCRIPTION = ABGAttribute.define("description", str, None)
ABGAttribute.DURATION = ABGAttribute.define("duration", list, ABGDuration.validate)
ABGAttribute.EDITABLE = ABGAttribute.define("editable", [None, bool], lambda x, y: x is None or x is False)
ABGAttribute.FAMILIES = ABGAttribute.define("families", list, ABGFamilies.validate)
ABGAttribute.FILE = ABGAttribute.define("file", str, None)
ABGAttribute.FLIPPED = ABGAttribute.define("flipped", bool, None)
ABGAttribute.FLIPPED_COLOR = ABGAttribute.define("flippedColor", str, ABGColor.validate)
ABGAttribute.FONT_FAMILY = ABGAttribute.define("fontFamily", str, None)
ABGAttribute.FONT_SIZE = ABGAttribute.define("fontSize", [int, float], lambda x, y : (x >= 0), fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.FRONT = ABGAttribute.define("front", [ABGContent, str], ABGContent.validate, fromJson = ABGContent.fromJson)
ABGAttribute.GAME_ID = ABGAttribute.define("gameId", str, None)
ABGAttribute.GRID = ABGAttribute.define("grid", [ABGGrid, None], ABGGrid.validate, fromJson = ABGGrid)
ABGAttribute.GRID_SIZE = ABGAttribute.define("gridSize", int, lambda x, y : (x > 0), fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.GROUP_ID = ABGAttribute.define("groupId", str, None)
ABGAttribute.HEIGHT = ABGAttribute.define("height", [int, float], lambda x, y : (x > 0), fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.HOLD_ITEMS = ABGAttribute.define("holdItems", bool, None)
ABGAttribute.ID = ABGAttribute.define("id", str, None) # Don't know yet.
ABGAttribute.IMAGES = ABGAttribute.define("images", list, ABGLayerImage.validateList, ABGLayerImage)
ABGAttribute.IMAGE_URL = ABGAttribute.define("imageUrl", [ABGContent, str, None], ABGContent.validate, fromJson = ABGContent.fromJson)
ABGAttribute.INITIAL_BOARD_POSITION = ABGAttribute.define("initialBoardPosition", ABGBoardPosition, ABGBoardPosition.validate, fromJson = ABGBoardPosition)
ABGAttribute.ITEM = ABGAttribute.define("item", [None, ABGItem], ABGItem.validate, fromJson = ABGItem.fromJson)
ABGAttribute.ITEMS = ABGAttribute.define("items", list, ABGItem.validateList, fromJson = ABGItem.fromJson)
ABGAttribute.KEEP_TITLE = ABGAttribute.define("keepTitle", bool, None)
ABGAttribute.LABEL = ABGAttribute.define("label", [str, None], None)
ABGAttribute.CUSTOM_SHORTCUT = ABGAttribute.define("customShortcut", [str, None], None)
ABGAttribute.CUSTOM_LABEL = ABGAttribute.define("customLabel", [str, None], None)
ABGAttribute.ANGLE = ABGAttribute.define("angle", [int, None], None)
ABGAttribute.LABEL_POSITION = ABGAttribute.define("labelPosition", str, ABGLabelPosition.validate)
ABGAttribute.LANGUAGE = ABGAttribute.define("language", str, ABGLanguage.validate)
ABGAttribute.LAYER = ABGAttribute.define("layer", int, None, fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.LAYERS = ABGAttribute.define("layers", list, ABGImageLayer.validateList, ABGImageLayer)
ABGAttribute.LEFT = ABGAttribute.define("left", [int, float], None, fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.LINKED_ITEMS = ABGAttribute.define("linkedItems", list, ABGId.validateList)
ABGAttribute.LOCKED = ABGAttribute.define("locked", bool, None)
ABGAttribute.MATERIAL_LANGUAGE = ABGAttribute.define("materialLanguage", str, ABGMaterialLanguage.validate)
ABGAttribute.MESSAGES = ABGAttribute.define("messages", list, None)
ABGAttribute.MOVING = ABGAttribute.define("moving", bool, None)
ABGAttribute.NAME = ABGAttribute.define("name", str, None)
ABGAttribute.NEVER_SAVED = ABGAttribute.define("neverSaved", bool, None)
ABGAttribute.OFFSET = ABGAttribute.define("offset", ABGLocation, ABGLocation.validate, fromJson = ABGLocation)
ABGAttribute.OFFSET_X = ABGAttribute.define("offsetX", [int, float], None, fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.OFFSET_Y = ABGAttribute.define("offsetY", [int, float], None, fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.OVERLAY = ABGAttribute.define("overlay", [ABGContent, str, None], ABGContent.validate, fromJson = ABGContent.fromJson)
ABGAttribute.OWNED_BY = ABGAttribute.define("ownedBy", None, None) # Don't know yet.
ABGAttribute.PLAYER_COUNT = ABGAttribute.define("playerCount", list, ABGPlayerCount.validate, fromJson = ABGPlayerCount)
ABGAttribute.PUBLISHED = ABGAttribute.define("published", bool, None)
ABGAttribute.RADIUS = ABGAttribute.define("radius", [int, float], lambda x, y : (x > 0), fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.ROLL_ON_DBL_CLICK = ABGAttribute.define("rollOnDblClick", bool, None)
ABGAttribute.ROTATION = ABGAttribute.define("rotation", [int, float], None, fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.ROW_COUNT = ABGAttribute.define("rowCount", int, lambda x, y : (x > 0), fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.SCALE = ABGAttribute.define("scale", [int, float], lambda x, y : (x > 0), fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.SET_STATE = ABGAttribute.define("setState", None, None) # Don't know yet.
ABGAttribute.SIDE = ABGAttribute.define("side", str, ABGSide.validate)
ABGAttribute.SIZE = ABGAttribute.define("size", [int, float], lambda x, y : (x >= 0), fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.TEXT = ABGAttribute.define("text", str, None)
ABGAttribute.TEXT_COLOR = ABGAttribute.define("textColor", str, ABGColor.validate)
ABGAttribute.TIMESTAMP = ABGAttribute.define("timestamp", int, lambda x, y : (x >= 0), fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.TOP = ABGAttribute.define("top", [int, float], None, fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.TRANSLATIONS = ABGAttribute.define("translations", list, ABGTranslation.validateList, fromJson = ABGTranslation)
ABGAttribute.TYPE = ABGAttribute.define("type", str, None)
ABGAttribute.UID = ABGAttribute.define("uid", str, None) # Don't know yet.
ABGAttribute.UNFLIPPED_FOR = ABGAttribute.define("unflippedFor", [list, None], None) # Don't know yet
ABGAttribute.VALUE = ABGAttribute.define("value", str, None)
ABGAttribute.VERTICAL = ABGAttribute.define("vertical", bool, None)
ABGAttribute.WIDTH = ABGAttribute.define("width", [int, float], lambda x, y : (x > 0), fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.X = ABGAttribute.define("x", [int, float], None, fromJson = ABGAttribute.ensureNumeral)
ABGAttribute.Y = ABGAttribute.define("y", [int, float], None, fromJson = ABGAttribute.ensureNumeral)

## TODO: utility functions.
# - Return anchor families' members that match no "family" attribute.
# - Return objects that have no anchor to match their family.

if __name__ == '__main__':
	import sys

	ABGAssert.ensure(len(sys.argv) == 2, "Call with a content.json file as argument to test parsing.")
	testGame = ABGGame()
	print("Parsing: " + sys.argv[1] + "...")
	testGame.fromFile(sys.argv[1])
	print("Parsing completed.")
