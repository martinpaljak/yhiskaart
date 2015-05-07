<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns="http://www.w3.org/1999/xhtml">
<xsl:output method="text"/>
<xsl:strip-space elements="*"/> 
<xsl:template match="Sector/Block"> 
<xsl:value-of select="normalize-space(text())"/>
</xsl:template>
<xsl:template match="/"> 
<xsl:apply-templates select="InfoDump/Tag/MemoryTag/Data"/>
</xsl:template>
</xsl:stylesheet>