<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:mml="http://morphml.org/morphml/schema"
    xmlns:meta="http://morphml.org/metadata/schema" 
    xmlns:nml="http://morphml.org/neuroml/schema"
    xmlns:bio="http://morphml.org/biophysics/schema" >

<!--

    This file is used to convert v1.5 MorphML files to a "neuroscientist friendly" view
    Note this doesn't by any means include all of the information present in the file, it just 
    summarises the notes, etc. embedded in the file and gives a summary of segment numbers, etc.
    
    This file has been developed as part of the neuroConstruct project
    
    Funding for this work has been received from the Medical Research Council
    
    Author: Padraig Gleeson
    Copyright 2007 Department of Physiology, UCL
    
-->

<xsl:output method="html" indent="yes" />


    <!-- Just imports the main NeuroML converter. Level 1 is handled there too... -->
    <xsl:import href="../Level2/NeuroML_Level2_v1.5_HTML.xsl"/>
    
</xsl:stylesheet>
