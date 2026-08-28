# CW Letter Numbering - Odoo 17 MVP

Configurable letter numbering for Odoo 17.

Features:
- Letter types
- Numbering rules
- Company / department / user matching
- Custom format tokens
- Yearly, monthly or no reset
- Number history
- Basic concurrency locking

Supported tokens:
{SEQ}, {YEAR}, {MONTH}, {MONTH_ROMAN}, {DAY}, {USER}, {USER_CODE},
{DEPT}, {DEPT_CODE}, {COMPANY}, {COMPANY_CODE}, {TYPE}, {TYPE_CODE}

This is a development MVP. Test thoroughly on a clean Odoo 17 database
before publishing to Odoo Apps.
