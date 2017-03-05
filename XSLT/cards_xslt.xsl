<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0">
    <xsl:output method="html"/>
    <xsl:template match="/root">
        <table>
            <thead>
                <tr>
                    <th>Front</th>
                    <th>Back</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <xsl:for-each select="list-item">
                    <form action="edform" method="post">
                        <tr>
                            <td>
                                <input type="text" value="{front}" name="front"/>
                            </td>
                            <td>
                                <input type="text" value="{back}" name="back"/>
                            </td>
                            <input type="hidden" value="{id}" name="id"/>
                            <td>
                                <input type="submit" name="edit" value="edit"/>
                                <input type="submit" name="delete" value="delete"/>
                            </td>
                        </tr>
                    </form>
                </xsl:for-each>
            </tbody>
        </table>
    </xsl:template>
</xsl:stylesheet>