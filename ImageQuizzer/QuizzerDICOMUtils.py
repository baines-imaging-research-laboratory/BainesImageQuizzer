import os
import vtk, qt, ctk, slicer
import sys
from DICOMLib.DICOMUtils import *

##########################################################################
# Class QuizzerDICOMUtils
##########################################################################
class QuizzerDICOMUtils:
    ''' class QuizzerDICOMUtils
        stub set up to remove error message when loading scripted modules during Slicer startup
    '''
    
    def __init__(self, parent=None):
        self.parent = parent

##########################################################################
# Slicer override of the DicomUtils>loadSeriesByUID function
##########################################################################


''' These functions were taken from the DicomLib.DicomUtils.py in the nightly 
    release of Slicer v. 4.13 (Feb. 27/2022).
    
    The stable version of v4.11.20220226 does not take into consideration the 
    confidence assigned to the potential loadable plugins resulting in the series
    being loaded twice.
    
    This came about when the DICOMImageSequencePlugin now specifically supports
    MRI's with the SOPClassUID of '1.2.840.10008.5.1.4.1.1.4' (a possible cineMR).
    
    This issue is fixed in Slicer's v 4.13 but because it is a nightly release at this
    time, it has other issues. Once an updated stable release is available,
    these functions can be deleted and the ImageView function can call the 
    loadSeriesByUID function directly from DICOMLib.DicomUtils.py

'''

#------------------------------------------------------------------------------
def loadSeriesByUID(seriesUIDs):
  """ Load multiple series by UID from DICOM database.
  Returns list of loaded node ids.
  """
  if not isinstance(seriesUIDs, list):
    raise ValueError('SeriesUIDs must contain a list')
  if seriesUIDs is None or len(seriesUIDs) == 0:
    raise ValueError('No series UIDs given')

  if not slicer.dicomDatabase.isOpen:
    raise OSError('DICOM module or database cannot be accessed')

  fileLists = []
  for seriesUID in seriesUIDs:
    fileLists.append(slicer.dicomDatabase.filesForSeries(seriesUID))
  if len(fileLists) == 0:
    # No files found for DICOM series list
    return []

  loadablesByPlugin, loadEnabled = getLoadablesFromFileLists(fileLists)
  selectHighestConfidenceLoadables(loadablesByPlugin)
  return loadLoadables(loadablesByPlugin)

def selectHighestConfidenceLoadables(loadablesByPlugin):
  """Review the selected state and confidence of the loadables
  across plugins so that the options the user is most likely
  to want are listed at the top of the table and are selected
  by default. Only offer one pre-selected loadable per series
  unless both plugins mark it as selected and they have equal
  confidence."""

  # first, get all loadables corresponding to a series
  seriesUIDTag = "0020,000E"
  loadablesBySeries = {}
  for plugin in loadablesByPlugin:
    for loadable in loadablesByPlugin[plugin]:
      seriesUID = slicer.dicomDatabase.fileValue(loadable.files[0], seriesUIDTag)
      if seriesUID not in loadablesBySeries:
        loadablesBySeries[seriesUID] = [loadable]
      else:
        loadablesBySeries[seriesUID].append(loadable)

  # now for each series, find the highest confidence selected loadables
  # and set all others to be unselected.
  # If there are several loadables that tie for the
  # highest confidence value, select them all
  # on the assumption that they represent alternate interpretations
  # of the data or subparts of it.  The user can either use
  # advanced mode to deselect, or simply delete the
  # unwanted interpretations.
  for series in loadablesBySeries:
    highestConfidenceValue = -1
    for loadable in loadablesBySeries[series]:
      if loadable.confidence > highestConfidenceValue:
        highestConfidenceValue = loadable.confidence
    for loadable in loadablesBySeries[series]:
      loadable.selected = loadable.confidence == highestConfidenceValue

