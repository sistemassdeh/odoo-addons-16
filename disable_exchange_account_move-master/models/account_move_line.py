# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, _, api


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"


    def _create_reconciliation_partials(self):
        '''create the partial reconciliation between all the records in self
         :return: A recordset of account.partial.reconcile.
        '''
        partials_vals_list, exchange_data = self._prepare_reconciliation_partials([
            {
                'record': line,
                'balance': line.balance,
                'amount_currency': line.amount_currency,
                'amount_residual': line.amount_residual,
                'amount_residual_currency': line.amount_residual_currency,
                'company': line.company_id,
                'currency': line.currency_id,
                'date': line.date,
            }
            for line in self
        ])
        partials = self.env['account.partial.reconcile'].create(partials_vals_list)

        # ==== Create exchange difference moves ====
        if self.env['ir.config_parameter'].sudo().get_param('disable_exchange_differente',False) != '1':
            for index, exchange_vals in exchange_data.items():
                partials[index].exchange_move_id = self._create_exchange_difference_move(exchange_vals)

        return partials
