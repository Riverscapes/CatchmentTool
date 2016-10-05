""" Module for writing Metadata XML files for SFR GIS tools.

    Author: kelly@southforkresearch.org
    Version: 0.1
    Date: 2016-Jul-2

    License:
"""

import xml.etree.ElementTree as ET
# from xml.dom import minidom
import datetime
from getpass import getuser
from socket import gethostname


class MetadataWriter():
    """Object to store tool run metadata and write output xml file"""

    Runs = []

    metadataVersion = "0.1"
    metadataType = "SFR Processing"

    def __init__(self, ToolName, ToolVersion, Operator="", GISVersion=""):
        """Create a new instance of a Metadata File Object

        MetadataFileName:

        ToolName:

        ToolVersion:
        """

        self.toolName = ToolName
        self.toolVersion = ToolVersion
        self.gisVersion = GISVersion
        self.computerID = gethostname()

        if Operator:
            self.operator = Operator
        else:
            try:
                self.operator = getuser()
            except:
                self.operator = "USERNAME not found"

    def createRun(self):
        """Create a new instance of a run"""
        self.currentRun = run()

    def finalizeRun(self):
        """Finish processing run and save to Metadata Runs"""

        self.currentRun.finalize()
        self.Runs.append(self.currentRun)

    def writeMetadataFile(self, metadataFile):
        """ save the final metadata xml file"""
        rootElement = ET.Element("Metadata", {"type": self.metadataType, "version": self.metadataVersion})

        nodeTool = ET.SubElement(rootElement, "Tool")
        ET.SubElement(nodeTool, "Name").text = self.toolName
        ET.SubElement(nodeTool, "Version").text = self.toolVersion

        nodeProcessing = ET.SubElement(rootElement, "Processing")
        ET.SubElement(nodeProcessing, "ComputerID").text = self.computerID
        ET.SubElement(nodeProcessing, "Operator").text = self.operator
        ET.SubElement(nodeProcessing, "GISVersion").text = self.gisVersion

        nodeRuns = ET.SubElement(nodeProcessing, "Runs")
        for run in self.Runs:
            nodeRun = ET.SubElement(nodeRuns, "Run", {"status": run.status})

            ET.SubElement(nodeRun, "TimeStart").text = run.timestampStart.strftime('%Y-%m-%d %H:%M:%S')
            ET.SubElement(nodeRun, "TimeStop").text = run.timestampStop.strftime('%Y-%m-%d %H:%M:%S')
            ET.SubElement(nodeRun, "TotalProcessingTime").text = str(run.timeProcessing.total_seconds())

            nodeParameters = ET.SubElement(nodeRun, "Parameters")
            for parameter in run.Parameters:
                nodeParameter = ET.SubElement(nodeParameters, "Parameter")
                ET.SubElement(nodeParameter, "Name").text = parameter.Name
                ET.SubElement(nodeParameter, "Value").text = parameter.Value

            nodeOutputs = ET.SubElement(nodeRun, "Outputs")
            for output in run.Outputs:
                nodeOutput = ET.SubElement(nodeOutputs, "Name").text = output.Name
                nodeOutput = ET.SubElement(nodeOutputs, "Value").text = output.Value

            nodeMesssages = ET.SubElement(nodeRun, "Messages")
            for message in run.Messages:
                nodeMessage = ET.SubElement(nodeOutputs, "Message", {"Level": message.Level}).text = message.Message

        tree = ET.ElementTree(rootElement)
        tree.write(metadataFile, 'utf-8', True)
        # writePrettyXML(metadataFile,rootElement)


class run():
    """ Class that represents a tool run. """

    Parameters = []
    Outputs = []
    Messages = []

    def __init__(self):
        """Get the start timestamp"""
        self.timestampStart = datetime.datetime.now()

    def addParameter(self, parameterName, parameterValue):
        """Add a parameter to the processing run"""
        newParameter = parameter(parameterName, parameterValue)
        self.Parameters.append(newParameter)

    def addOutput(self, outputName, outputValue):
        """Add an output to the processing run"""
        newOutput = output(outputName, outputValue)
        self.Outputs.append(newOutput)

    def addMessage(self, severityLevel, messageText):
        """Add a message to the processing run"""
        newMessage = message(severityLevel, messageText)
        self.Messages.append(newMessage)

    def finalize(self, status=""):
        """Sets the stop timestamp and total processing time"""
        self.timestampStop = datetime.datetime.now()
        self.timeProcessing = self.timestampStop - self.timestampStart

        self.status = status


class parameter():
    def __init__(self, Name, Value):
        self.Name = Name
        self.Value = Value


class output():
    def __init__(self, name, value):
        self.Name = name
        self.Value = value


class message():
    def __init__(self, level, message):
        self.Level = level
        self.Message = message