# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    @api.model
    def _get_selection_invoice_note_place(self):
        """
        Get all possible selection choice (for invoice_note_place field)
        This list depends on values set on res.company.
        Returns: list of tuple (str, str)
        """
        fields_get = self.env['res.company'].fields_get(
            allfields=['invoice_note_place'])
        values = [
            (v[0], _(v[1])) for v in fields_get.get(
                'invoice_note_place', {}).get('selection', '')
        ]
        return values

    invoice_note_place = fields.Selection(
        selection=_get_selection_invoice_note_place,
        default="no",
        required=True,
        help="Define on where to place the additional invoice note on the "
             "invoice report",
        related="company_id.invoice_note_place",
    )
    # In a perfect world, this field should be related and translatable.
    # Unfortunately these 2 parameters are not compatible.
    # So the default_get fill the invoice_note (in current lang).
    # Then the following onchange update it when the company_id change.
    # Finally, the set_default will write on the company (with correct lang)
    invoice_note = fields.Html(
        help="Note who'll be printed on every invoice related to this company",
    )

    @api.model
    def default_get(self, fields_list):
        """
        Inherit to add the invoice_note depending on company
        :param fields_list: list of str
        :return: dict
        """
        result = super(AccountConfigSettings, self).default_get(fields_list)
        company_id = result.get('company_id')
        company = self.env.user.company_id
        if company_id:
            company = self.env['res.company'].browse(company_id)
        result.update({
            'invoice_note': company.invoice_note,
        })
        return result

    @api.multi
    def set_default_invoice_note(self):
        """
        Write the invoice_note on the company
        :return:
        """
        for record in self:
            record.company_id.write({
                'invoice_note': record.invoice_note,
            })

    @api.multi
    @api.onchange('company_id')
    def _onchange_company_id(self):
        """
        Onchange for company_id.
        When the company_id is updated, we have to update also the invoice_note
        :return:
        """
        self.invoice_note = self.company_id.invoice_note
