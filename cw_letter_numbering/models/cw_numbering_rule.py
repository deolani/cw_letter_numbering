# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class CWNumberingRule(models.Model):
    _name = "cw.numbering.rule"
    _description = "Letter Numbering Rule"
    _order = "priority, id"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    priority = fields.Integer(default=10)
    letter_type_id = fields.Many2one(
        "cw.letter.type", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company, ondelete="cascade", index=True
    )
    department_id = fields.Many2one("hr.department", ondelete="set null", index=True)
    user_id = fields.Many2one("res.users", ondelete="set null", index=True)
    prefix = fields.Char()
    suffix = fields.Char()
    format_string = fields.Char(
        string="Format", required=True, default="{SEQ}/{YEAR}",
        help="Tokens: {SEQ}, {YEAR}, {MONTH}, {MONTH_ROMAN}, {DAY}, {USER}, "
             "{USER_CODE}, {DEPT}, {DEPT_CODE}, {COMPANY}, {COMPANY_CODE}, "
             "{TYPE}, {TYPE_CODE}."
    )
    padding = fields.Integer(default=4, required=True)
    reset_period = fields.Selection([
        ("never", "Never"),
        ("yearly", "Yearly"),
        ("monthly", "Monthly"),
    ], default="yearly", required=True)
    next_number = fields.Integer(default=1, required=True)
    preview = fields.Char(compute="_compute_preview")

    @api.constrains("padding", "next_number", "priority")
    def _check_values(self):
        for rec in self:
            if not 1 <= rec.padding <= 12:
                raise ValidationError(_("Padding must be between 1 and 12."))
            if rec.next_number < 1:
                raise ValidationError(_("Next number must be at least 1."))
            if rec.priority < 0:
                raise ValidationError(_("Priority cannot be negative."))

    @staticmethod
    def _roman_month(month):
        return ["I", "II", "III", "IV", "V", "VI",
                "VII", "VIII", "IX", "X", "XI", "XII"][month - 1]

    def _token_values(self, user, department, when):
        self.ensure_one()
        company = self.company_id or self.env.company
        letter_type = self.letter_type_id
        user = user or self.env.user
        department = department or user.employee_id.department_id
        user_code = user.login or user.name or ""
        dept_code = department.name if department else ""
        return {
            "{SEQ}": str(self.next_number).zfill(self.padding),
            "{YEAR}": str(when.year),
            "{MONTH}": f"{when.month:02d}",
            "{MONTH_ROMAN}": self._roman_month(when.month),
            "{DAY}": f"{when.day:02d}",
            "{USER}": user.name or "",
            "{USER_CODE}": user_code,
            "{DEPT}": department.name if department else "",
            "{DEPT_CODE}": dept_code,
            "{COMPANY}": company.name or "",
            "{COMPANY_CODE}": company.name or "",
            "{TYPE}": letter_type.name or "",
            "{TYPE_CODE}": letter_type.code or "",
        }

    def _render_number(self, sequence_number, user=None, department=None, when=None):
        self.ensure_one()
        when = when or fields.Date.context_today(self)
        values = self._token_values(user, department, when)
        values["{SEQ}"] = str(sequence_number).zfill(self.padding)
        result = self.format_string or "{SEQ}"
        for token, value in values.items():
            result = result.replace(token, value)
        return f"{self.prefix or ''}{result}{self.suffix or ''}"

    def _period_key(self, when):
        self.ensure_one()
        if self.reset_period == "never":
            return "ALL"
        if self.reset_period == "yearly":
            return str(when.year)
        return f"{when.year:04d}-{when.month:02d}"

    @api.depends("format_string", "padding", "prefix", "suffix",
                 "letter_type_id", "company_id", "department_id", "user_id")
    def _compute_preview(self):
        for rec in self:
            rec.preview = rec._render_number(
                rec.next_number, rec.user_id or self.env.user,
                rec.department_id, fields.Date.context_today(rec)
            ) if rec.letter_type_id else False

    def _find_matching_rule(self, letter_type, company, user, department):
        rules = self.search([
            ("active", "=", True),
            ("letter_type_id", "=", letter_type.id),
            ("company_id", "=", company.id),
        ], order="priority asc, id asc")
        matches = []
        for rule in rules:
            score = 0
            if rule.department_id:
                if rule.department_id != department:
                    continue
                score += 2
            if rule.user_id:
                if rule.user_id != user:
                    continue
                score += 4
            matches.append((score, rule))
        if not matches:
            return self.browse()
        matches.sort(key=lambda x: (-x[0], x[1].priority, x[1].id))
        return matches[0][1]

    @api.model
    def generate_number(self, letter_type, user=None, department=None, when=None):
        if isinstance(letter_type, int):
            letter_type = self.env["cw.letter.type"].browse(letter_type)
        if not letter_type.exists():
            raise UserError(_("Letter type was not found."))
        user = user or self.env.user
        company = self.env.company
        department = department or user.employee_id.department_id
        when = when or fields.Date.context_today(self)

        rule = self._find_matching_rule(letter_type, company, user, department)
        if not rule:
            raise UserError(
                _("No active numbering rule was found for letter type '%s'.")
                % letter_type.display_name
            )

        self.env.cr.execute(
            "SELECT next_number FROM cw_numbering_rule WHERE id = %s FOR UPDATE",
            (rule.id,)
        )
        row = self.env.cr.fetchone()
        if not row:
            raise UserError(_("The numbering rule no longer exists."))

        latest = self.env["cw.numbering.history"].search(
            [("rule_id", "=", rule.id)], order="id desc", limit=1
        )
        period_key = rule._period_key(when)
        current = 1 if (
            rule.reset_period != "never" and latest and latest.period_key != period_key
        ) else row[0]

        number = rule._render_number(current, user, department, when)
        rule.write({"next_number": current + 1})
        return number, rule
