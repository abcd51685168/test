#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET

if __name__ == "__main__":
    xml_file = r"C:\tmp\winxpl_0.xml"
    ET.register_namespace("qemu", "http://libvirt.org/schemas/domain/qemu/1.0")
    tree = ET.parse(xml_file)
    root = tree.getroot()

    root.find("name").text = "234"
    root.find("uuid").text = "234"
    root.find("memory").text = "234"
    root.find("currentMemory").text = "234"
    root.find("devices").find("disk").find("source").set("file", "234")
    root.find("devices").find("interface").find("mac").set("address", "234")
    tree.write(r"c:\tmp\234.xml")
