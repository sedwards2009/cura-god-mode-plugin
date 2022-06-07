# Copyright (c) 2016 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.SettingDefinition import SettingDefinition
from UM.Extension import Extension
from UM.Application import Application
from UM.Settings.ContainerRegistry import ContainerRegistry

try:
    from PyQt6.QtCore import QObject, QUrl
    from PyQt6.QtGui import QDesktopServices
except:
    from PyQt5.QtCore import QObject, QUrl
    from PyQt5.QtGui import QDesktopServices

import os.path
import tempfile
import html
import json

encode = html.escape

class GodMode(Extension, QObject):
    def __init__(self, parent = None):
        QObject.__init__(self, parent)
        Extension.__init__(self)

        self.addMenuItem("View Active Stack", viewAll)
        self.addMenuItem("View All Machines", viewAllMachines)
        self.addMenuItem("View All Materials", viewAllMaterials)
        self.addMenuItem("View All Qualities", viewAllQualities)
        self.addMenuItem("View All Quality Changes", viewAllQualityChanges)
        self.addMenuItem("View All User Containers", viewAllUserContainers)
        self.addMenuItem("View All Variants", viewAllVariants)
        self.addMenuItem("View All Stacks", viewAllStacks)

def viewAll():
    openHtmlPage("cura_settings.html", htmlPage())

def viewAllMaterials():
    openHtmlPage("cura_materials.html", containersOfTypeHtmlPage("Materials", "material"))

def viewAllUserContainers():
    openHtmlPage("cura_user_containers.html", containersOfTypeHtmlPage("User Containers", "user"))

def viewAllVariants():
    openHtmlPage("cura_variants.html", containersOfTypeHtmlPage("Variants", "variant"))

def viewAllQualities():
    openHtmlPage("cura_qualities.html", containersOfTypeHtmlPage("Quality", "quality"))

def viewAllQualityChanges():
    openHtmlPage("cura_quality_changes.html", containersOfTypeHtmlPage("Quality Changes", "quality_changes"))

def viewAllMachines():
    openHtmlPage("cura_machines.html", containersOfTypeHtmlPage("Machines", "machine"))

def viewAllStacks():
    openHtmlPage("cura_stacks.html", allStacksHtmlPage());

def openHtmlPage(page_name, html_contents):
    target = os.path.join(tempfile.gettempdir(), page_name)
    with open(target, "w", encoding="utf-8") as fhandle:
        fhandle.write(html_contents)
    QDesktopServices.openUrl(QUrl.fromLocalFile(target))

def getHtmlHeader(page_name="Cura Settings"):
    return """<!DOCTYPE html><html>
<head>
<meta charset="UTF-8">
<title>""" + encode(page_name) + """</title>
<script>
""" + keyFilterJS() + """
</script>
<style>
html {
  font-family: sans-serif;
  font-size: 11pt;
}

a, a:visited {
  color: #0000ff;
  text-decoration: none;
}

ul {
  padding-left: 1em;
}

div.menu {
  position: fixed;
  padding: 4px;
  left: 0px;
  width: 25em;
  top: 0px;
  height: 100%;
  box-sizing: border-box;
  overflow: auto;
}

div.contents {
  padding-left: 25em;
}

table.key_value_table {
  border-collapse: separate;
  border: 1px solid #e0e0e0;
  margin-top: 16px;
  border-top-left-radius: 5px;
  border-top-right-radius: 5px;
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  border-spacing: 0px;
}

table.key_value_table th, table.key_value_table td {
  padding: 4px;
}

table.key_value_table > thead th {
  width: 65em;
  text-align: left;
  background-color: #428bca;
  color: #ffffff;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}

table.key_value_table > tbody > tr:nth-child(even) {
  background-color: #e0e0e0;
}

table.key_value_table > tbody > tr.exception {
  background-color: #e08080;
}
table.key_value_table td.key {
  width: 25em;
  font-weight: bold;
  font-weight: bold;
}

table.key_value_table tr.preformat td.value {
  white-space: pre;
}

div.container_stack {
  padding: 8px;
  border: 2px solid black;
  border-radius: 8px;
}

div.container_stack > table.key_value_table > thead th {
  background-color: #18294D;
}

div.container_stack_containers {
  margin: 4px;
  padding: 4px;
  border: 1px dotted black;
  border-radius: 4px;
}

tr.key_hide {
  display: none;
}

body.hide_metadata tr.metadata {
  display: none;
}

ul.property_list {
  list-style: none;
  padding-left: 0;
  margin-left: 0;
}

span.prop_name {
  font-weight: bold;
}
</style>
</head>
<body onload='initKeyFilter();'>
"""

def htmlPage():
    html = getHtmlHeader()

    html += "<div class='menu'>\n"
    html += "<ul>"
    html += "<li><a href='#global_stack'>Global Stack</a>"
    html += formatContainerStackMenu(Application.getInstance().getGlobalContainerStack())
    html += "</li>\n"

    html += "<li><a href='#extruder_stacks'>Extruder Stacks</a>\n"
    html += formatExtruderStacksMenu()
    html += "</li>\n"

    html += "</ul>\n"
    html += keyFilterWidget()
    html += "</div>"

    html += "<div class='contents'>"
    html += "<h2 id='global_stack'>Global Stack</h2>"
    html += formatContainerStack(Application.getInstance().getGlobalContainerStack())

    html += formatExtruderStacks()

    html += "</div>"

    html += htmlFooter
    return html

def containersOfTypeHtmlPage(name, type_):
    html = getHtmlHeader(name)

    html += "<div class='menu'>\n"
    html += "<ul>"
    if type_ == "machine":
        containers = ContainerRegistry.getInstance().findDefinitionContainers()
    else:
        containers = ContainerRegistry.getInstance().findInstanceContainers(type=type_)
    containers.sort(key=lambda x: x.getId())
    for container in containers:
        html += "<li><a href='#"+ str(id(container)) + "'>"+encode(container.getId())+"</a></li>\n"
    html += "</ul>"

    html += keyFilterWidget()
    html += "</div>"

    html += "<div class='contents'>"
    html += formatAllContainersOfType(name, type_)
    html += "</div>"

    html += htmlFooter
    return html

def allStacksHtmlPage():
    html = getHtmlHeader("All Stacks")

    html += "<div class='menu'>\n"
    html += "<ul>"
    stacks = ContainerRegistry.getInstance().findContainerStacks()
    stacks.sort(key=lambda x: x.getId())
    for container in stacks:
        html += "<li><a href='#"+ str(id(container)) + "'>"+encode(container.getId())+"</a></li>\n"
    html += "</ul>"
    html += keyFilterWidget()
    html += "</div>"

    html += "<div class='contents'>"
    for stack in stacks:
        html += formatContainerStack(stack, show_stack_keys=False)
    html += "</div>"

    html += htmlFooter
    return html

def formatExtruderStacks():
    html = ""
    html += "<h2 id='extruder_stacks'>Extruder Stacks</h2>"
    machine = Application.getInstance().getMachineManager().activeMachine
    for position, extruder_stack in sorted([(int(p + 1), es) for p, es in enumerate(machine.extruderList)]):
        position = str(position)
        html += "<h3 id='extruder_index_" + position + "'>Index " + position + "</h3>"
        html += formatContainerStack(extruder_stack)
    return html

def formatExtruderStacksMenu():
    html = ""
    html += "<ul>"
    machine = Application.getInstance().getMachineManager().activeMachine
    for position, extruder_stack in sorted([(int(p + 1), es) for p, es in enumerate(machine.extruderList)]):
        html += "<li>"
        html += "<a href='#extruder_index_" + str(position) + "'>Index " + str(position) + "</a>\n"
        html += formatContainerStackMenu(extruder_stack)
        html += "</li>"
    html += "</ul>"
    return html

def formatAllContainersOfType(name, type_):
    html = "<h2>" + name + "</h2>\n"

    if type_ == "machine":
        containers = ContainerRegistry.getInstance().findDefinitionContainers()
    else:
        containers = ContainerRegistry.getInstance().findInstanceContainers(type=type_)

    containers.sort(key=lambda x: x.getId())
    for container in containers:
        html += formatContainer(container)
    return html

def formatContainerStack(stack, show_stack_keys=True):
    html = "<div class='container_stack'>\n"
    html += formatContainer(stack, name="Container Stack", short_value_properties=True)
    html += "<div class='container_stack_containers'>\n"
    html += "<h3>Containers</h3>\n"
    for container in stack.getContainers():
        html += formatContainer(container, show_keys=show_stack_keys)
    html += "</div>\n"
    html += "</div>\n"
    return html

def formatContainerStackMenu(stack):
    html = ""
    html += "<a href='#" + str(id(stack)) + "'></a><br />\n"
    html += "<ul>\n"
    for container in stack.getContainers():
        html += "<li><a href='#" + str(id(container)) + "'>" + encode(container.getId()) + "</a></li>"
    html += "</ul>\n"
    return html

def formatContainerMetaDataOnly(container):
    html = tableHeader("Container: " + safeCall(container.getId))
    html += formatContainerMetaDataRows(container)
    html += tableFooter()
    return html

def formatContainer(container, name="Container", short_value_properties=False, show_keys=True):
    html = ""
    html += "<a id='" + str(id(container)) + "' ></a>"
    html += tableHeader(name + ": " + safeCall(container.getId))
    html += formatContainerMetaDataRows(container)

    if show_keys:
        key_properties = ["value", "resolve"] if short_value_properties else setting_prop_names
        key_properties.sort()

        if hasattr(container, "getAllKeys"):
            keys = list(container.getAllKeys())
            keys.sort()
            for key in keys:
                html += formatSettingsKeyTableRow(key, formatSettingValue(container, key, key_properties))

    html += tableFooter()
    return html

def formatContainerMetaDataRows(def_container):
    html = ""
    try:
        html += formatKeyValueTableRow("<type>", type(def_container), extra_class="metadata")
        html += formatKeyValueTableRow("<id>", def_container, extra_class="metadata")
        html += formatKeyValueTableRow("id", safeCall(def_container.getId), extra_class="metadata")
        html += formatKeyValueTableRow("name", safeCall(def_container.getName), extra_class="metadata")
        if hasattr(def_container, "_getDefinition"):
            html += formatKeyValueTableRow("definition", safeCall(def_container._getDefinition), extra_class="metadata")
        html += formatKeyValueTableRow("read only", safeCall(def_container.isReadOnly), extra_class="metadata")
        html += formatKeyValueTableRow("path", safeCall(def_container.getPath), extra_class="metadata")
        html += formatKeyValueTableRow("metadata", safeCall(def_container.getMetaData), extra_class="metadata")
    except:
        pass

    return html

setting_prop_names = SettingDefinition.getPropertyNames()
def formatSettingValue(container, key, properties=None):
    if properties is None:
        properties = setting_prop_names

    value = "<ul class=\"property_list\">\n"
    comma = ""
    properties.sort()
    for prop_name in properties:
        prop_value = container.getProperty(key, prop_name)
        if prop_value is not None:
            value += "  <li>\n"
            value += "    <span class='prop_name'>" + encode(prop_name) + ":</span> " + encode(repr(prop_value))
            value += "  </li>\n"
    value += "</ul>\n"

    return RawHtml(value)

def safeCall(callable):
    try:
        result = callable()
        return result
    except Exception as ex:
        return ex

def tableHeader(title):
    return """<table class="key_value_table">
    <thead><tr><th colspan="2">""" + encode(title) + """</th></tr></thead>
    <tbody>
"""

def tableFooter():
    return "</tbody></table>"

def formatKeyValueTableRow(key, value, extra_class=""):
    clazz = ""
    if isinstance(value, Exception):
        clazz = "exception"

    if isinstance(value, RawHtml):
        formatted_value = value.value
    elif isinstance(value, dict):
        formatted_value = encode(json.dumps(value, sort_keys=True, indent=4))
        clazz += " preformat"
    elif isinstance(value, DefinitionContainer):
        formatted_value = encode(value.getId() + " " + str(value))
    else:
        formatted_value = encode(str(value))

    if isinstance(key, RawHtml):
        formatted_key = key.value
    else:
        formatted_key = encode(str(key))

    return "<tr class='" + extra_class + " " + clazz + "'><td class='key'>" + formatted_key + "</td><td class='value'>" + formatted_value + "</td></tr>\n"

def formatSettingsKeyTableRow(key, value):
    clazz = ""
    if isinstance(value, Exception):
        clazz = "exception"

    if isinstance(value, RawHtml):
        formatted_value = value.value
    else:
        formatted_value = encode(str(value))

    formatted_key = encode(str(key))
    return "<tr class='" + clazz + "' --data-key='" + formatted_key + "'><td class='key'>&#x1f511; " + formatted_key + "</td><td class='value'>" + formatted_value + "</td></tr>\n"

def keyFilterJS():
    return """
    function initKeyFilter() {
      var filter = document.getElementById('key_filter');
      filter.addEventListener('change', function() {
        var filterValue = filter.value;

        if (filterValue === "") {
          document.body.classList.add('show_metadata');
          document.body.classList.remove('hide_metadata');
        } else {
          document.body.classList.remove('show_metadata');
          document.body.classList.add('hide_metadata');
        }

        var filterRegexp = new RegExp(filterValue, 'i');

        var allKeys = document.querySelectorAll('[--data-key]');
        var i;
        for (i=0; i<allKeys.length; i++) {
          var keyTr = allKeys[i];
          var key = keyTr.getAttribute('--data-key');
          if (filterRegexp.test(key)) {
            keyTr.classList.remove('key_hide');
          } else {
            keyTr.classList.add('key_hide');
          }
        }
      });
    }
    """

def keyFilterWidget():
    html = """
    <div class='key_filter'>
    &#x1f511; filter regex: <input type='text' id='key_filter' />
    </div>
    """
    return html

# def formatContainerInstance(container_instance):
#     return """
#
# """


htmlFooter = """</body>
</html>
"""
class RawHtml:
    def __init__(self, value):
        self.value = value
