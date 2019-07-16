cmake_minimum_required(VERSION 3.5)

project(ImageQuizzerProject)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/ImageQuizzerProject")
set(EXTENSION_CATEGORY "Baines Custom Modules")
set(EXTENSION_CONTRIBUTORS "Carol Johnson (Baines Imaging Research Laboratory)")
set(EXTENSION_DESCRIPTION "Teaching tool - present images with associated quiz")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/ImageQuizzerProject.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/ImageQuizzerProject/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(ImageQuizzer)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
