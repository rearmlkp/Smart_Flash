<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0">
    <xsl:output method="html"/>
    <xsl:template match="/root">
        <table>
            <thead>
                <tr>
                    <th>Cards</th>
                    <th>Deck name</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <xsl:for-each select="list-item">
                    <form action="deck/edform" method="post">
                        <input type="hidden" name="csrfmiddlewaretoken"
                               value="qZSp2nCdWg0un4ca9fTbrdCgNsXHEWNASYpOOMdJgYUwFjTLjzupJQ9Pq4AJCKuw"/>
                        <tr>
                            <td>
                                <a href="deck/{id}">Cards</a>
                            </td>
                            <td>
                                <input type="text" value="{name}" name="name"/>
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