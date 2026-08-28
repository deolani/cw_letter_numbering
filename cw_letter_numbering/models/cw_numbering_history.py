# -*- coding: utf-8 -*-
from odoo import fields, models

class CWNumberingHistory(models.Model):
    _name = "cw.numbering.history"
    _description = "Numbering History"
    _order = "generated_at desc, id desc"

    name = fields.Char(string="Number", required=True, index=True)
    rule_id = fields.Many2one("cw.numbering.rule", required=True, ondelete="restrict", index=True)
    letter_type_id = fields.Many2one("cw.letter.type", required=True, ondelete="restrict", index=True)
    user_id = fields.Many2one("res.users", index=True)
    department_id = fields.Many2one("hr.department", index=True)
    company_id = fields.Many2one("res.company", required=True, index=True)
    generated_at = fields.Datetime(default=fields.Datetime.now, required=True, index=True)
    period_key = fields.Char(required=True, index=True)
    document_model = fields.Char()
    document_id = fields.Integer()
    document_name = fields.Char()

    _sql_constraints = [
        ("number_rule_unique", "unique(name, rule_id)",
         "The generated number must be unique for the numbering rule."),
    ]
