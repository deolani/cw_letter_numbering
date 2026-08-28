# -*- coding: utf-8 -*-
from odoo import api, fields, models

class CWLetter(models.Model):
    _name = "cw.letter"
    _description = "Letter"
    _order = "date desc, id desc"

    name = fields.Char(string="Letter Number", readonly=True, copy=False, index=True)
    letter_type_id = fields.Many2one("cw.letter.type", required=True, ondelete="restrict")
    date = fields.Date(default=fields.Date.context_today, required=True)
    subject = fields.Char(required=True)
    user_id = fields.Many2one("res.users", string="Responsible User",default=lambda self: self.env.user, required=True)
    department_id = fields.Many2one("hr.department", string="Department")
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    state = fields.Selection([
        ("draft", "Draft"), 
        ("done", "Numbered"), 
        ("cancel", "Cancelled")
    ], default="draft", required=True, copy=False)
    note = fields.Text()

    def action_generate_number(self):
        for record in self:
            if record.name:
                continue
            number, rule = self.env["cw.numbering.rule"].generate_number(
                record.letter_type_id, record.user_id, record.department_id, record.date
            )
            record.write({"name": number, "state": "done"})
            self.env["cw.numbering.history"].create({
                "name": number,
                "rule_id": rule.id,
                "letter_type_id": record.letter_type_id.id,
                "user_id": record.user_id.id,
                "department_id": record.department_id.id,
                "company_id": record.company_id.id,
                "period_key": rule._period_key(record.date),
                "document_model": record._name,
                "document_id": record.id,
                "document_name": record.subject,
            })
        return True

    def action_cancel(self):
        self.write({"state": "cancel"})

    def action_reset_to_draft(self):
        self.write({"state": "draft"})

    @api.onchange("user_id")
    def _onchange_user_id(self):
        if self.user_id and self.user_id.employee_id.department_id:
            self.department_id = self.user_id.employee_id.department_id
