#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2018 Paul Ashton
# Sponsored by Rusty Brown's Ring Donuts

# v4
# - Tidy up
# - Add test afp file and example usage

# v3
# - Added support for text overlays - these are now automagically added to
#   page text-element list so will just show up as regular text elements.
#   You can disable this by setting incorporateOverlays to False
# - Fixed bug in resource names
#
# v2
# - Added support for color filtering.
#
# v1
# - Initial release.

import codecs
import os
import re
import struct
import time

# Contants..

# Field types..
SF_NOP = 0xd3eeee
SF_BRG = 0xd3a8c6
SF_ERG = 0xd3a9c6
SF_BRS = 0xd3a8ce
SF_ERS = 0xd3a9ce
SF_BCP = 0xd3a887
SF_ECP = 0xd3a987
SF_CPD = 0xd3a687
SF_CPC = 0xd3a787
SF_CPI = 0xd38c87
SF_BFN = 0xd3a889
SF_EFN = 0xd3a989
SF_FND = 0xd3a689
SF_FNC = 0xd3a789
SF_FNM = 0xd3a289
SF_FNN = 0xd3ab89
SF_FNO = 0xd3ae89
SF_FNP = 0xd3ac89
SF_FNI = 0xd38c89
SF_FNG = 0xd3ee89
SF_BFM = 0xd3a8cd
SF_EFM = 0xd3a9cd
SF_BMM = 0xd3a8cc
SF_EMM = 0xd3a9cc
SF_PGP = 0xd3b1af
SF_MDD = 0xd3a688
SF_MCC = 0xd3a288
SF_MMC = 0xd3a788
SF_BPS = 0xd3a85f
SF_EPS = 0xd3a95f
SF_BIM = 0xd3a8fb
SF_EIM = 0xd3a9fb
SF_BOG = 0xd3a8c7
SF_EOG = 0xd3a9c7
SF_OBD = 0xd3a66b
SF_OBP = 0xd3ac6b
SF_MIO = 0xd3abfb
SF_IDD = 0xd3a6fb
SF_IPD = 0xd3eefb
SF_BDT = 0xd3a8a8
SF_EDT = 0xd3a9a8
SF_BNG = 0xd3a8ad
SF_ENG = 0xd3a9ad
SF_TLE = 0xd3a090
SF_IMM = 0xd3abcc
SF_BPG = 0xd3a8af
SF_EPG = 0xd3a9af
SF_BAG = 0xd3a8c9
SF_EAG = 0xd3a9c9
SF_MCF1 = 0xd3b18a # format 1
SF_MCF = 0xd3ab8a # format 2
SF_MPS = 0xd3b15f
SF_PGD = 0xd3a6af
SF_PTD = 0xd3b19b
SF_BPT = 0xd3a89b
SF_EPT = 0xd3a99b
SF_PTX = 0xd3ee9b
SF_IPS = 0xd3af5f
SF_BGO = 0xd3a8bb
SF_EGR = 0xd3a9bb
SF_MGO = 0xd3abbb
SF_GDD = 0xd3a6bb
SF_GAD = 0xd3eebb
SF_BOC = 0xd3a892
SF_EOC = 0xd3a992
SF_CDD = 0xd3a692
SF_OCD = 0xd3ee92
SF_BMO = 0xd3a8df
SF_EMO = 0xd3a9df
SF_MDR = 0xd3abc3
SF_IOB = 0xd3afc3
SF_BSG = 0xd3a8d9
SF_ESG = 0xd3a9d9
SF_MPO = 0xd3abd8
SF_IPO = 0xd3afd8
SF_BCF = 0xd3a88a
SF_ECF = 0xd3a98a
SF_CFC = 0xd3a78a
SF_CFI = 0xd38c8a
SF_BII = 0xd3a87b
SF_EII = 0xd3a97b
SF_IOC = 0xd3a77b
SF_IID = 0xd3a67b
SF_IRD = 0xd3ee7b
SF_ICP = 0xd3ac7b
SF_CTC = 0xd3a79b
SF_PTD1 = 0xd3a69b

# Field descriptions..
afp_fields = {
    SF_BAG: "Begin Active Environment Group",
    SF_BCF: "Begin Coded Font",
    SF_BCP: "Begin Code Page",
    SF_BDT: "Begin Document",
    SF_BFM: "Begin Form Map",
    SF_BFN: "Begin Font",
    SF_BGO: "Begin Graphics Object",
    SF_BII: "Begin IM Image Object",
    SF_BIM: "Begin Image Object",
    SF_BMM: "Begin Medium Map",
    SF_BMO: "Begin Overlay",
    SF_BNG: "Begin Named Page Group",
    SF_BOC: "Begin Object Container",
    SF_BOG: "Begin Object Environment Group",
    SF_BPG: "Begin Page",
    SF_BPS: "Begin Page Segment",
    SF_BPT: "Begin Presentation Text Object",
    SF_BRG: "Begin Resource Group",
    SF_BRS: "Begin Resource",
    SF_CDD: "Container Data Description",
    SF_CFC: "Coded Font Control",
    SF_CFI: "Coded Font Index",
    SF_CPC: "Code Page Control",
    SF_CPD: "Code Page Description",
    SF_CPI: "Code Page Index",
    SF_EAG: "End Active Environment Group",
    SF_ECF: "End Coded Font",
    SF_ECP: "End Code Page",
    SF_EDT: "End Document",
    SF_EFM: "End Form Map",
    SF_EFN: "End Font",
    SF_EGR: "End Graphics Object",
    SF_EII: "End IM Image Object",
    SF_EIM: "End Image Object",
    SF_EMM: "End Medium Map",
    SF_EMO: "End Overlay",
    SF_ENG: "End Named Page Group",
    SF_EOC: "End Object Container",
    SF_EOG: "End Object Environment Group",
    SF_EPG: "End Page",
    SF_EPS: "End Page Segment",
    SF_EPT: "End Presentation Text Object",
    SF_ERG: "End Resource Group",
    SF_ERS: "End Resource",
    SF_FNC: "Font Control",
    SF_FND: "Font Description",
    SF_FNG: "Font Patterns",
    SF_FNI: "Font Index",
    SF_FNM: "Font Patterns Map",
    SF_FNN: "Font Name Map",
    SF_FNO: "Font Orientation",
    SF_FNP: "Font Position",
    SF_GAD: "Graphics Data",
    SF_GDD: "Graphics Data Descriptor",
    SF_ICP: "IM Image Cell Position",
    SF_IDD: "Image Data Descriptor",
    SF_IID: "IM Image Input Description",
    SF_IMM: "Invoke Medium Map",
    SF_IOC: "IM Image Output Control",
    SF_IPD: "Image Picture Data",
    SF_IPS: "Include Page Segment",
    SF_IRD: "IM Image Raster Data",
    SF_MCC: "Medium Copy Count",
    SF_MCF1: "Map Coded Font - Format 1",
    SF_MCF: "Map Coded Font - Format 2",
    SF_MDD: "Medium Description",
    SF_MGO: "Map Graphics Object",
    SF_MIO: "Map Image Object",
    SF_MMC: "Medium Modification Control",
    SF_MPS: "Map Page Segment",
    SF_NOP: "NOP",
    SF_OBD: "Object Area Descriptor",
    SF_OBP: "Object Area Position",
    SF_OCD: "Object Container Data",
    SF_PGD: "Page Descriptor",
    SF_PGP: "Page Position",
    SF_PTD: "Presentation Text Data Descriptor - Format 2",
    SF_PTD1: "Presentation Text Data Description",
    SF_PTX: "Presentation Text Data",
    SF_TLE: "Tag Logical Element",

    SF_MDR: "Map Data Resource",
    SF_IOB: "Include Object",
    SF_BSG: "Begin Resource Environment Group",
    SF_ESG: "End Resource Environment Group",
    SF_MPO: "Map Page Overlay",
    SF_IPO: "Include Page Overlay",
    SF_CTC: "Composed Text Control",
    }


afp_functions = {
    # Functions
    #    (Unchained, Chained)
    "AMB": (0xd2, 0xd3),
    "AMI": (0xc6, 0xc7),
    "BSU": (0xf2, 0xf3),
    "DBR": (0xe6, 0xe7),
    "DIR": (0xe4, 0xe5),
    "ESU": (0xf4, 0xf5),
    "RMB": (0xd4, 0xd5),
    "RMI": (0xc8, 0xc9),
    "RPS": (0xee, 0xef),
    "SCFL": (0xf0, 0xf1),
    "SEC": (0x80, 0x81),
    "SIA": (0xc2, 0xc3),
    "STC": (0x74, 0x75),
    "STO": (0xf6, 0xf7),
    "SVI": (0xc4, 0xc5),
    "TRN": (0xda, 0xdb),
    "NOP": (0xf8, 0xf9),
    }

afp_functions_desc = {
    # Descriptions of functions
    # Unchained
    afp_functions["AMB"][0]: "Absolute Move Baseline U",
    afp_functions["AMI"][0]: "Absolute Move Inline U",
    afp_functions["BSU"][0]: "Begin Suppression",
    afp_functions["DBR"][0]: "Draw B-Axis Rule U",
    afp_functions["DIR"][0]: "Draw I-Axis Rule U",
    afp_functions["ESU"][0]: "End Suppression U",
    afp_functions["RMB"][0]: "Relative Move Baseline U",
    afp_functions["RMI"][0]: "Relative Move Inline U",
    afp_functions["RPS"][0]: "Repeat String U",
    afp_functions["SCFL"][0]: "Set Coded Font Local U",
    afp_functions["SEC"][0]: "Set Extended Text Color U",
    afp_functions["SIA"][0]: "Set Intercharacter Adjustment U",
    afp_functions["STC"][0]: "Set Text Color U",
    afp_functions["STO"][0]: "Set Text Orientation U",
    afp_functions["SVI"][0]: "Set Variable Space Character Increment U",
    afp_functions["TRN"][0]: "Transparent Data U",
    afp_functions["NOP"][0]: "No Operation U",
    # Chained
    afp_functions["AMB"][1]: "Absolute Move Baseline C",
    afp_functions["AMI"][1]: "Absolute Move Inline C",
    afp_functions["BSU"][1]: "Begin Suppression C",
    afp_functions["DBR"][1]: "Draw B-Axis Rule C",
    afp_functions["DIR"][1]: "Draw I-Axis Rule C",
    afp_functions["ESU"][1]: "End Suppression C",
    afp_functions["RMB"][1]: "Relative Move Baseline C",
    afp_functions["RMI"][1]: "Relative Move Inline C",
    afp_functions["RPS"][1]: "Repeat String C",
    afp_functions["SCFL"][1]: "Set Coded Font Local C",
    afp_functions["SEC"][1]: "Set Extended Text Color C",
    afp_functions["SIA"][1]: "Set Intercharacter Adjustment C",
    afp_functions["STC"][1]: "Set Text Color C",
    afp_functions["STO"][1]: "Set Text Orientation C",
    afp_functions["SVI"][1]: "Set Variable Space Character Increment C",
    afp_functions["TRN"][1]: "Transparent Data C",
    afp_functions["NOP"][1]: "No Operation C",
    }

afp_clut = {
    # Color look-up table for STC fields
    0x0000: 0x000000, # Device Default
    0x0001: 0x0000ff, # Blue
    0x0002: 0xff0000, # Red
    0x0003: 0xff00ff, # Pink/Magenta
    0x0004: 0x00ff00, # Green
    0x0005: 0x00ffff, # Turquoice/Cyan
    0x0006: 0xffff00, # Yellow

    0xff00: 0x000000, # Device Default
    0xff01: 0x0000ff, # Blue
    0xff02: 0xff0000, # Red
    0xff03: 0xff00ff, # Pink/Magenta
    0xff04: 0x00ff00, # Green
    0xff05: 0x00ffff, # Turquoice/Cyan
    0xff06: 0xffff00, # Yellow

    0x0008: 0x000000, # Black
    0x0010: 0xa52a2a, # Brown
    0xff07: 0x000000, # Device Default
    0xff08: 0x000000, # Reset Color ?????
    0xffff: 0x000000, # Default Indicator
    }

class Document(object):
    def __init__(self, pages=[], tle={}):
        self.pages = pages
        self.tle = tle

    def getText(self):
        """
        Return all pages text separated by a pagebreak
        """
        return '\x0c'.join(i.getText() for i in self.pages)

    def findText(self, text, rx=True, exactMatch=False):
        """
        Return all instances of text on all pages
        """
        assert self.pages, "No pages!"

        results = []
        for page_num, page in enumerate(self.pages):
            result = page.findText(text, rx=rx, exactMatch=exactMatch)
            if result:
                for i in result:
                    results.append((page_num,) + i) # Include the page number

        return results

    def addPage(self, page):
        self.pages.append(page)


class Page(object):
    def __init__(self, elements=None):
        self.elements = tuple(elements) if elements != None else None

    def getText(self, area=None, delimiter="\n", sort=True, strip=True, color=None):
        """
        Return all text on page or in given area
        Separated by delimiter

        Area should be a tuple of (x1, y1, x2, y2)

        We ignore anything with an orientation of -1 as this is an
        I or B-Rule and those can be retrieved using getRules()

        sort will sort elements by their position on the page so we
        get text out in the correct(ish) order.
        """
        if not self.elements:
            return ""

        if sort:
            items = sorted(self.elements, key=lambda x: (x[1], x[0]))
        else:
            items = self.elements

        if area != None:
            items = (i[4] for i in items if i[3] != -1 and i[0] >= area[0] and i[0] <= area[2] and i[1] >= area[1] and i[1] <= area[3])
        else:
            items = (i[4] for i in items if i[3] != -1)

        # Check for strippable items (remove them if empty)..
        if strip:
            items = (i.strip() for i in tuple(items) if i.strip())

        if color != None:
            items = (i for i in items if i[2]==color)

        return delimiter.join(items)

    def getTextElements(self, area=None, sort=True, color=None):
        """
        Return all text elements on page or in given area

        Area should be a tuple of (x1, y1, x2, y2)

        We ignore anything with an orientation of -1 as this is an
        I or B-Rule and those can be retrieved using getRules()

        sort will sort elements by their position on the page so we
        get text out in the correct(ish) order.
        """
        if not self.elements:
            return ()

        if sort:
            items = sorted(self.elements, key=lambda x: (x[1], x[0]))
        else:
            items = self.elements

        if area != None:
            items = (i for i in items if i[3] != -1 and i[0] >= area[0] and i[0] <= area[2] and i[1] >= area[1] and i[1] <= area[3])
        else:
            items = (i for i in items if i[3] != -1)

        if color != None:
            items = (i for i in items if i[2]==color)

        return tuple(items)

    def getRules(self, area=None, color=None):
        """
        Return all rules on page or in given area
        Area should be a tuple of (x1, y1, x2, y2)

        We want orientation of -1 as I or B-Rule will be set to that

        Returned elements will contain a tuple instead of text value at
        position 4 like:
            ("I-Rule", length, width)
        """
        assert self.elements, "No elements!"
        assert area == None or isinstance(area, tuple), "specified area is not a tuple in the form: (x1, y1, x2, y2)"

        if area != None:
            items = (i for i in self.elements if i[3] == -1 and i[0] >= area[0] and i[0] <= area[2] and i[1] >= area[1] and i[1] <= area[3])
        else:
            items = (i for i in self.elements if i[3] == -1)

        if color != None:
            items = (i for i in items if i[2]==color)

        return tuple(items)

    def findTextPos(self, text, rx=True, exactMatch=False, color=None):
        """
        Return the position of the first match
        """
        results = self.findText(text, rx=rx, exactMatch=exactMatch, color=color)
        if results:
            return results[0][0:2]
        return None

    def findText(self, text, rx=True, exactMatch=False, color=None):
        """
        Return the element containing given text
        If color is specified then only text with that color will be returned.
        """
        items = []
        for i in self.elements:
            if i[3] == -1: # Ignore rules
                continue

            if rx == True:
                result = re.search(text, i[4])
                if result:
                    if not exactMatch or (exactMatch and result.group()==i[4]):
                        items.append(i)
            else:
                if (exactMatch and i[4] == text) or (not exactMatch and text in i[4]):
                    items.append(i)

        if color != None:
            items = (i for i in items if i[2]==color)

        return tuple(items)

class AshyAFP(object):
    """
    Ashy's attempt to read AFP data without some shitty library
    """
    def __init__(self, filename=None, allow_unknown_fields=False, keep_all_resources=True, incorporateOverlays=True):
        self.debug = False

        self.data = None # Holds whole AFP file
        self.pages = None
        self.documents = None
        self.resources = None

        self.page_count = 0
        self.document_count = 0
        self.resource_count = 0

        self.unknown_field_count = 0

        self.filename = None

        self.keep_all_resources = keep_all_resources
        self.allow_unknown_fields = allow_unknown_fields

        self.incorporateOverlays = incorporateOverlays

        if filename != None:
            self.load(filename)

    def saveImageResources(self, output_folder):
        """
        Save all image resources to the output_folder
        """
        if not self.resources:
            return 0

        os.makedirs(output_folder, exist_ok=True)

        for res in self.resources:
            if isinstance(self.resources[res], bytes):
                with open(os.path.join(output_folder, f"{res}.jpg"), "wb") as fp:
                    fp.write(self.resources[res])

        return len(self.resources)

    def _getResources(self):
        """
        Parse resource fields to find jpg images.
        Returns a dict of binary jpg-image data with resource name as the key
        """
        assert self.data, "No data loaded"

        self.resources = {}

        for res in self._getFieldsBetween(SF_BRS, SF_ERS):
            # Get the resource name from the first entry (which is the BRS field)..
            res_name = self.toASCII(res[0][1][0:8])

            # Overlay Objects with Text element..
            result = [t_dat for t_id, t_dat in res if t_id == SF_PTX]
            if result:
                self.resources[res_name] = self._parsePTOCAdat(result[0])

            # Image objects..
            result = [t_dat for t_id, t_dat in res if t_id == SF_IPD]
            if result:
                img_data = b''
                for ipd in result:
                    i_id, i_len = struct.unpack_from(">HH", ipd)
                    if i_id == 0xFE92: # Image Data header
                        img_data += ipd[4:4+i_len]

                if len(img_data):
                    self.resources[res_name] = img_data
            else:
                self.resources[res_name] = res

        return len(self.resources)

    def countFields(self, field_type, data=None):
        """
        Return how many of this field_type there is in data
        """
        if not data and self.data:
            data = self.data
        assert data, "No data loaded"
        return len([1 for t_id, t_dat in data if t_id == field_type])

    def toASCII(self, ebcdic_text):
        """
        Convert EBCDIC encoded text to ASCII

        Example:
        >>> text = b'\xc3\xa4\xa2\xa3\x96\x94\x85\x99\xc9\x95\xd9\xa4\x95'
        >>> self.toASCII(text)
        'CustomerInRun'

        """
        return codecs.decode(ebcdic_text, "EBCDIC-CP-BE")

    def _parseTLEs(self, tle_data):
        """
        Parse the TLE information and create a dict

        Example:
        >>> testdata = (35, 13869200, b'\x11\x02\x0b\x00\xc3\xa4\xa2\xa3\x96\x94\x85\x99\xc9\x95\xd9\xa4\x95\t6\x00\x00\xf0\xf0\xf1\xf2\xf2')
        >>> self._parseTLEs(testdata)
        {"CustomerInRun": "00122"}

        """
        assert tle_data, "No data"

        TLEs = {}

        for t_id, t_dat in tle_data:
            offset = 0
            key = None
            value = None
            while offset < len(t_dat):
                # get triplet..
                # t_len, t_id, t_dat = struct.unpack_from(f"BB{t_dat[0]-2}s", t_dat, offset=offset)
                tle_length = t_dat[offset]
                tle_code = t_dat[offset+1]
                data = t_dat[offset+2:offset+tle_length]
                offset += tle_length

                if tle_code == 0x02: # Fully Qualified Name
                    key = self.toASCII(data[2:2+tle_length])

                elif tle_code == 0x36: # Attribute Value
                    value = codecs.decode(data[2:2+tle_length], "EBCDIC-CP-BE")

                # Add to dict..
                if key and value:
                    TLEs[key] = value

        return TLEs

    def _getDocuments(self):
        """
        Get all documents (Named Page Groups)
        """
        assert self.data, "No data loaded"

        # Init documents..
        self.documents = []

        # Get Named-Page groups..
        result = self._getFieldsBetween(SF_BNG, SF_ENG)

        # Loop through groups..
        for doc_num, doc in enumerate(result):
            tles = self._parseTLEs([i for i in doc if i[0] == SF_TLE])
            rawpages = self._getFieldsBetween(SF_BPG, SF_EPG, data=doc)
            pages = [self.parsePage(i) for i in rawpages]

            self.documents.append(Document(pages=pages, tle=tles))

        return len(self.documents)

    def _getFieldsBetween(self, start, end, data=None):
        if not data and self.data:
            data = self.data
        assert data, "No data loaded"

        # Init..
        collections = []
        collection = None

        # Loop through every field in data lookinf for start and end fields..
        for field in data:
            if field[0] == start:
                # Begin field
                collection = [field]

            elif field[0] == end:
                # End field
                collection.append(field)
                collections.append(collection)
                collection = None

            else:
                # Some other field
                if collection != None:
                    # It is between start and end so add it to collection..
                    collection.append(field)

        # Ensure we have not finished in the middle of a block..
        assert collection == None, f"{hex(start)} but no {hex(end)}"

        return tuple(collections)

    def _getPages(self):
        """
        Get all pages from afp data
        """
        assert self.data, "No data loaded"
        self.pages = self._getFieldsBetween(SF_BPG, SF_EPG)
        return len(self.pages)

    def _parsePTOCAdat(self, data):
        """
        Parse the PTOCAdat
        """
        # Init states..
        orientation = 0
        color = 0
        ami = 0
        amb = 0

        PTOCA = []

        offset = 0
        chained = False
        while offset < len(data):
            if not chained:
                # Check ESC SEQ..
                esc_seq = int.from_bytes(data[offset:offset+2], byteorder="big")
                assert esc_seq == 0x2bd3, f"Escape sequence not correct! ({hex(esc_seq)} should be 0x2bd3)"
                offset += 2

            # Get length..
            length = data[offset:offset+1][0]
            offset += 1

            # Get function..
            function = data[offset:offset+1][0]
            offset += 1
            assert function in afp_functions_desc, f"Function {hex(function)} not defined"

            # Get function data..
            function_data = data[offset:offset+(length-2)]
            offset += length-2

            # Handle functions..
            if function in afp_functions["STO"]:
                # Set Text Orientation
                result = struct.unpack(">HH", function_data)

                if result[0] and not result[1]:
                    orientation = 1 # Landscape
                elif result[1] and not result[0]:
                    orientation = 0 # Portrait
                else:
                    assert 0, "bad orientation?!"

            elif function in afp_functions["AMB"]:
                # Absolute Move Baseline
                amb = int.from_bytes(function_data, byteorder="big") # The range for this parameter assumes a measurement unit of 1/1440 inch

            elif function in afp_functions["AMI"]:
                # Absolute Move Inline
                ami = int.from_bytes(function_data, byteorder="big") # The range for this parameter assumes a measurement unit of 1/1440 inch

            elif function in afp_functions["STC"]:
                # Set Text Color
                color = afp_clut[int.from_bytes(function_data, byteorder="big")]

            elif function in afp_functions["SEC"]:
                # Set Extended Text Color
                assert function_data[0] == 0, f"reserved, must be zero ({function_data[0]})"
                assert function_data[1] == 1, f"color space not supported ({function_data[1]})" # must be 1 - RGB
                color = int.from_bytes(function_data[10:13], byteorder="big")

            elif function in afp_functions["TRN"]:
                # Transparent Data
                # Decode this data from EBCDIC to ASCII
                text = codecs.decode(function_data, "EBCDIC-CP-BE")
                text = re.sub(r"\x16|\x91", r"'", text) # Fix quotes

                # Add to PTOCA list..
                PTOCA.append((ami, amb, color, orientation, text))

            elif function in afp_functions["RMI"]:
                # Relative Move Inline
                pass

            elif function in afp_functions["RMB"]:
                # Relative Move Baseline
                pass

            elif function in afp_functions["DBR"]:
                # Draw B-Axis Rule
                # Orientation is not used so -1
                r_len = int.from_bytes(function_data[0:2], byteorder="big") # length of rule in B direction
                r_wid = int.from_bytes(function_data[2:4], byteorder="big") # width of rule in I direction (-32765 to +32767)
                r_fra = function_data[4] # fraction (bit 0 denotes 1/2 measurement unit, bit 1 denotes 1/4 measurement unit etc..)
                PTOCA.append((ami, amb, color, -1, ("B-Rule", r_len, r_wid, r_fra)))

            elif function in afp_functions["DIR"]:
                # Draw I-Axis Rule
                # Orientation is not used so -1
                r_len = int.from_bytes(function_data[0:2], byteorder="big") # length of rule in B direction
                r_wid = int.from_bytes(function_data[2:4], byteorder="big") # width of rule in I direction (-32765 to +32767)
                r_fra = function_data[4] # fraction (bit 0 denotes 1/2 measurement unit, bit 1 denotes 1/4 measurement unit etc..)
                PTOCA.append((ami, amb, color, -1, ("I-Rule", r_len, r_wid, r_fra)))

            elif function in afp_functions["NOP"] + afp_functions["SCFL"] + afp_functions["SIA"] + afp_functions["SVI"]:
                # Ignore these functions
                pass

            else:
                print(f"Warning: Unhandled function {hex(function)} ({afp_functions.get(function)})")

            # chained or unchained function?
            chained = True if function % 2 else False

        assert not chained, "Final function is chained!"

        return PTOCA

    def parsePage(self, page_data, area=None):
        """
        Return a list of tuples with every text object on the given page
        A single tuple will contain 5 items:

        A 5 item tuple will contain a text field as follows:
            (ami, amb, color, orientation, text)

        If area is defined then we will only return items that fall within it.
        Area should be a tuple of points: (x1, y1, x2, y2)
        """
        assert page_data, "No data"

        allTexts = []

        # Get all objects
        for f_id, f_dat in page_data:
            if f_id == SF_PTX:
                # Text object
                allTexts.extend(self._parsePTOCAdat(f_dat))

            elif f_id == SF_IPO:
                # Overlay
                name = self.toASCII(f_dat[0:8])
                xorigin = int.from_bytes(f_dat[8:11], byteorder="big")
                yorigin = int.from_bytes(f_dat[11:14], byteorder="big")
                orient = int.from_bytes(f_dat[14:16], byteorder="big") if len(f_dat) >= 16 else None # orientation is an optional entry

                for g_id, g_dat in self.resources.get(name):
                    if g_id == SF_PTX: # Text object in overlay
                        newTexts = self._parsePTOCAdat(g_dat)
                        # Add text elements to allTexts with modified position
                        # based on x and y offsets defined in the overlay..
                        for t in newTexts:
                            allTexts.append((t[0]+xorigin, t[1]+yorigin) + t[2:])

        return Page(elements=allTexts)

    def printStats(self):
        assert self.data, "No data loaded."

        print(f"-- AFP Stats for {self.filename!r} --")
        print(f"   Load time:    {self.loadtime:.2f}s")
        print(f"   Total fields: {len(self.data)}" + (f" ({self.unknown_field_count} UNKNOWN)" if self.unknown_field_count else ""))
        print(f"   Resources:    {self.resource_count}")
        print(f"   Documents:    {self.document_count}")
        print(f"   Pages:        {self.page_count}")
        print(f"-- End Stats --")

    def load(self, filename):
        """
        Load the AFP data into ram and parse docs/pages/resources
        """
        self.filename = filename
        start_time = time.time()
        print(f"Loading AFP {filename!r}..")

        self.data = [] # Will contain list of tuples (id, data)

        start_time = time.time()
        with open(filename, "rb") as fp:
            while fp:
                data = fp.read(9)
                if not data:
                    break # End of file

                sf_ccc, sf_len, sf_id = struct.unpack(">BH3s3x", data)
                assert sf_ccc == 0x5A, "Carriage control char missing"

                sf_len += 1 # length does not take into account the CARRIAGE_CONTROL_CHAR so add one
                sf_id = int.from_bytes(sf_id, byteorder="big")

                if self.debug:
                    print(f"{fp.tell()-9} {hex(sf_id)} {afp_fields.get(sf_id, '-Unknown-')}")

                if not self.allow_unknown_fields:
                    assert sf_id in afp_fields, f"Unknown field id {hex(sf_id)}"

                if sf_id not in afp_fields:
                    self.unknown_field_count += 1

                # Read this records data..
                sf_data = fp.read(sf_len-9) # Minus 9 as we have already read 9 bytes

                # add to data dict..
                self.data.append((sf_id, sf_data))

        # Do resources..
        self.resource_count = self._getResources()

        # Do we have documents or pages?
        if self.countFields(SF_BNG) > 1:
            self.document_count = self._getDocuments()
        else:
            self.page_count = self._getPages()

        self.loadtime = time.time()-start_time
        return True # Huge Success


if __name__ == "__main__":
    a = AshyAFP(r"test.afp")
    a.printStats()
    page = a.parsePage(a.pages[0])

    # Find text pos..
    pos = page.findTextPos("README")
    print(f"\nThe text 'README' was found at position {pos}.")

    # Find text element..
    elem = page.findText("README")[0]
    print(f"The text element for 'README' looks like {elem}")

    # Get area text..
    area = (0, 4583, 10000, 5300)
    text = page.getText(area=area, delimiter="")
    print(f"The area {area}, contains this text: {text}")

    # Find text with color..
    text = page.findText("", color=0x197f33)
    print(f"Find texts with color 0x197f33: {text}")

    # List resources..
    res = a.resources.keys()
    print(f"List of resources: {tuple(res)}")

    print("\nFinished!")
    assert 0