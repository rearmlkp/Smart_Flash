<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xs="http://www.w3.org/2001/XMLSchema"
                exclude-result-prefixes="xs"
                version="2.0">
    <xsl:output method="html"></xsl:output>
    <xsl:template match="/root">
        <table>
            <thead>
                <tr>
                    <th>Deck name</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <xsl:for-each select="list-item">
                    <tr>
                        <td>
                            <xsl:value-of select="name">
                            </xsl:value-of>
                        </td>
                        <td>
                            <a href="/web/deck/edit/{id}">Edit</a>
                            <a href="/web/deck/delete/{id}">Delete</a>
                        </td>
                    </tr>
                </xsl:for-each>
            </tbody>
        </table>
    </xsl:template>
</xsl:stylesheet>