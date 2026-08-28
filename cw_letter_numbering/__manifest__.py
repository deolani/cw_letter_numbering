# -*- coding: utf-8 -*-
{
    "name": "CW Letter Numbering",
    "version": "17.0.1.0.1",
    "summary": "Automatic and configurable letter numbering for Odoo",
    "description": """
CW Letter Numbering
===================
Configurable letter numbering with company, department and user rules.
Supports custom tokens, reset periods and numbering history.

Features:
- Custom letter numbering
- Company-based numbering
- Department-based numbering
- User-based numbering
- Custom numbering tokens
- Configurable reset periods
- Numbering history

""",
    "category": "Productivity",
    "author": "CORE Warehouse Technology",
    "license": "LGPL-3",
    "depends": ["base", "hr"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/cw_letter_type_views.xml",
        "views/cw_numbering_rule_views.xml",
        "views/cw_numbering_history_views.xml",
        "views/cw_letter_views.xml",
        "views/menus.xml",
    ],
    "images": [
    "static/description/icon.png",
    ],
    "installable": True,
    "application": True,
    "price": 21.99,
    "currency": "USD",
}
