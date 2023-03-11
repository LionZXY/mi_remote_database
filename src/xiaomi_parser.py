#!/usr/bin/env python3
# mi_remote_database a database retriever for IR codes
# Copyright (C) 2021  Ysard
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Parse data from Xiaomi API

TODO: make uniq patterns => option
TODO: get "others" section with an option
TODO: put the deviceid/vendorid in the Pattern object
"""
# Standard imports
import json
from pathlib import Path

from .commons import logger
# Custom imports
from .crypt_utils import process_xiaomi_shit
from .pattern import Pattern

LOGGER = logger()


def load_devices(filename):
    """Get devices from JSON dump

    TODO: what are providers ?
    """
    json_filedata = json.loads(Path(filename).read_text())
    devices = dict()

    for json_device in json_filedata["data"]:
        info = json_device["info"]
        device_name = [item["name"] for item in info if item["country"] == "EN"][0]
        device_id = json_device["deviceid"]
        devices[device_id] = {
            "name": device_name.replace("/", "_")  # Fix further errors with paths...
        }

    return devices


def load_brand_list(filename):
    """Get brands from JSON dump

    {
       "status":0,
       "data":[
          {
             "providers":[
                {
                   "id":"1973",
                   "type":"kk"
                }
             ],
             "brandid":1973,
             "deviceid":1,
             "info":[
                {
                   "name":"爱家乐",
                   "country":"CN"
                },
                {
                   "name":"Akira",
                   "country":"EN"
                }
             ],
             "name":"爱家乐",
             "yellow_id":-1,
             "category":"other"
          },
          {
             "brandid":4207,
             "providers":[
                {
                   "id":"4207",
                   "type":"kk"
                }
             ],
             "deviceid":1,
             "info":[
                {
                   "name":"Lloytron",
                   "country":"CN"
                },
                {
                   "name":"Lloytron",
                   "country":"EN"
                }
             ],
             "name":"Lloytron",
             "category":"other",
             "priority":999
          },
          {
             "category":"other",
             "deviceid":1,
             "providers":[
                {
                   "id":"64",
                   "type":"mx"
                },
                {
                   "id":"64",
                   "type":"kk"
                },
                {
                   "id":"64",
                   "type":"mi"
                }
             ],
             "logo":"http:\/\/image.box.xiaomi.com\/mfsv2\/download\/s010\/p01TX25H9u3v\/qjVx5KtQ66bvXj.jpg",
             "brandid":64,
             "name":"东芝",
             "priority":13,
             "info":[
                {
                   "name":"东芝",
                   "country":"CN"
                },
                {
                   "name":"Toshiba",
                   "country":"EN"
                }
             ],
             "yellow_id":14
          },
       ],
       "encoding":"UTF-8",
       "language":"ZH_CN"
    }

    Extract deviceid: 1 = TV, 10 = projectors, etc.

    :param filename: JSON file with the definitions of the available brands
    :type filename: <str>
    :return: Dictionary of brand ids as keys, dict of names and device ids as values.
        Used keys from JSON: brandid, deviceid, name
    :rtype: <dict <int>:<dict>>
    """
    json_filedata = json.loads(Path(filename).read_text())

    brands = dict()
    json_brands = json_filedata["data"]
    for brand in json_brands:
        # Get the occidental name of the brand
        # Assume EN language is always set
        info = brand["info"]
        brand_name = [item["name"] for item in info if item["country"] == "EN"][0]
        brand_id = brand["brandid"]
        device_id = brand["deviceid"]
        # print(brand_name, brand_id, type(brand_id))
        brands[brand_id] = {
            "name": brand_name,
            "deviceid": device_id,
        }
    return brands


def load_brand_codes(filename):
    """Extract IR encrypted codes for each model from a given JSON dump of a brand

    {
       "status":0,
       "data":{
          "tree":{
             "hasPower":1,
             "root_index":0,
             "spid":null,
             "seceret_key":null,
             "brand":64,
             "entrys":28,
             "nodes":[
                {
                   "children_index":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32],
                   "frequency":0,
                   "level":0,
                   "parent_index":-1,
                   "index":0
                },
                {
                   "ir_zip_key":"QJPmll3+SCgpSE73bTO9hni9upbSpKrS73cugR4FZSMT2VGtMTkEIsegm1kjFy3bCLQJsJZKAXxjDF7hGaYIolNzR+qo5f2H3C\/PqsSK2Q8kaQaJAycytxhqhVgnwnOUZ6gj0xXscdkPK3MBzr6HH5yEOGDtocCXKP8qEXZdvctnCmFZaZwubXf1Cscf\/rlVkAz53JacxfUkCiDqw8M27g==",
                   "keysetids":["xm_1_199", "xm_1_2425"],
                   "children_index":[7, 8],
                   "frequency":37990,
                   "level":1,
                   "parent_index":0,
                   "index":6,
                   "keyid":"power"
                },
                {
                   "ir_zip_key_r":"xxx",
                   "ir_zip_key":"xxx",
                   "keysetids":["xm_1_4410"],
                   "children_index":[],
                   "frequency":37000,
                   "level":1,
                   "parent_index":0,
                   "index":2,
                   "keyid":"power"
                },
                "status":true,
             "device":1,
             "version":1,
             "country":"IN"
          },
          "others":[
             {
                "_id":"kk_1_64_3445",
                "key":{
                   "vol+":"xxx",
                   "power":"xxx"
                },
                "frequency":38000,
                "seceret_key":null,
                "source":"kk",
                "kk_id":"3445",
                "brand":"64",
                "match_counts":{"ID":260, "UZ":1, "IN":27470, ...},
                "locales":{"MY":10, "ID":10, "IN":10},
                "order":10,
                "device":1
             },
             {
                "_id":"kk_1_64_6857",
                "key":{
                   "power_r":"xxx",
                   "vol+":"xxx",
                   "tv_av":"xxx",
                   "power":"xxx"
                },
                "frequency":36960,
                "seceret_key":null,
                "source":"kk",
                "kk_id":"6857",
                "brand":"64",
                "match_counts":{"SA":4, "ID":1687, "IN":2994, ...},
                "locales":{"MY":12, "ID":12, "IN":12},
                "order":12,
                "device":1
             }
          ]
       },
       "encoding":"UTF-8",
       "language":"ZH_CN"
    }

    TODO:
        filter on other keys than power/power_r for "other" field.
        If a device hasn't such keys, it will be skipped.

        TL;DR: Quickly, there is a filtering in this function which should not
        be done at this level.

        If we really wanted to retrieve all buttons, we would only use keysetids
        and _id/source fields.

    :param filename: JSON file with the definitions of the buttons available for 1 brand.
        1 model can have multiple codes including reverse codes.
        We asked power codes so, each code corresponds to this type.
    :type filename: <str>
    :return: List of dictionnaries corresponding to the definitions of the codes for each model.
        1 dict per model.
        Used keys from JSON: ir_zip_key, frequency, ir_zip_key, keysetids
        (internal model id linked to the codes in database), _id, source, power, power_r.
    :rtype: <list <dict>>
    """

    def parse_others_section(section):
        for json_model in section:
            buttons = [
                {
                    "id": name,
                    "ir_zip_key": ircode,
                    "frequency": json_model["frequency"]
                }
                for name, ircode in json_model["key"].items()
            ]

            yield buttons, json_model["source"]

    json_filedata = json.loads(Path(filename).read_text())
    models = list()

    if "others" in json_filedata["data"]:
        # "others" section is not considered for now
        for other_buttons, source in parse_others_section(json_filedata["data"]["others"]):
            models.append({
                'buttons': other_buttons,
                'source': source
            })

    ############################################################################

    tree = json_filedata["data"]["tree"]

    if "seceret_key" not in tree:
        # Empty tree
        return models

    assert tree["seceret_key"] is None  # TODO: To be identified correctly later
    json_models = tree["nodes"]
    for json_model in json_models:
        if "ir_zip_key" not in json_model:
            continue  # Skip the first element: "children_index"
        button = {
            "id": json_model["keyid"],
            "ir_zip_key": json_model["ir_zip_key"],
            "frequency": json_model["frequency"]
        }
        # Optional reverse code
        reverse_code = json_model.get("ir_zip_key_r")
        if reverse_code:
            button["ir_zip_key_r"] = reverse_code
        models.append({
            'buttons': [button],
            'keysetids': json_model['keysetids']
        })
    return models


def build_patterns(models):
    """Generate Pattern objects (clear IR codes) for the given models.

    IR codes are decrypted according to :meth:`process_xiaomi_shit`.

    :param models: Models returned by :meth:`load_brand_codes`.
    :return: List of Pattern objects: wrappers for one IR code.
    :rtype: <list <Pattern>>
    """
    patterns = list()

    for model in models:
        frequency = model["frequency"]

        if not frequency:
            # Some codes have a 0 frequency...
            LOGGER.error("Invalid frequency for the model:\n%s", model)
            continue

        # Decrypt IR code
        ir_code = process_xiaomi_shit(model["ir_zip_key"])
        pattern = Pattern(
            ir_code,
            frequency,
            model_id=model.get("_id", model.get("keysetids")),
            vendor_id=model.get("source", "mi"),
            id=model.get("id", None)
        )
        # print(pattern.to_pronto())
        patterns.append(pattern)

        # Optional reverse code = separated Pattern
        if "ir_zip_key_r" in model:
            # Decrypt IR code
            ir_code = process_xiaomi_shit(model["ir_zip_key_r"])
            button_name = model.get("id", None)
            if button_name is not None:
                button_name = button_name + '_r'
            pattern = Pattern(
                ir_code,
                frequency,
                model_id=model.get("_id", model.get("keysetids")),
                vendor_id=model.get("source", "mi"),
                id=button_name
            )
            # print(pattern.to_pronto())
            patterns.append(pattern)

    return patterns


def load_brand_codes_from_dir(directory):
    """Extract IR encrypted codes for models from all brands in the given directory

    .. seealso:: :meth:`load_brand_codes`

    :return: Dict with filenames as keys and list of dictionnaries corresponding
        to the definitions of the codes as values.
    :rtype: <dict <str>:<list <dict>>>
    """
    total = 0
    models = dict()
    for json_file in Path(directory).glob("*.json"):
        print(json_file, "...", end="")
        # Load codes from models in this brand file
        temp_models = load_brand_codes(json_file)
        models[json_file.stem] = temp_models
        print(len(temp_models))
        total += len(temp_models)

    print("TOTAL loaded", total)
    return models
