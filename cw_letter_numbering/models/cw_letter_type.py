# -*- coding: utf-8 -*-
from odoo import fields, models

class CWLetterType(models.Model):
    _name = "cw.letter.type"
    _description = "Letter Type"
    _order = "sequence, name"

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company, index=True
    )
    description = fields.Text()

    _sql_constraints = [
        ("code_company_unique", "unique(code, company_id)",
         "The letter type code must be unique per company."),
    ]
