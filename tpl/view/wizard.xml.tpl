<?xml version="1.0" encoding="utf-8"?>
<openerp>
    <data>

        <record id="wizard_cenit_{name}_install" model="ir.ui.view">
            <field name="name">{summary} settings</field>
            <field name="model">cenit.{name}.settings</field>
            <field name="inherit_id" ref="base.res_config_installer" />
            <field name="arch" type="xml">
                <form position="attributes">
                    <attribute name="string">{summary} settings</attribute>
                </form>
                <footer position="replace">
                    <footer>
                        <button string="Apply" type="object" name="execute"
                                class="oe_highlight" context="{{'install': True}}"/>
                    </footer>
                </footer>
                <separator string="title" position="replace">
                    <p class="oe_grey">
                        Configure {summary} data
                    </p>
                    <group>
{view_fields}
                    </group>
                </separator>
            </field>
        </record>

        <record id="action_wizard_cenit_{name}_install" model="ir.actions.act_window">
            <field name="name">Configure {summary} data</field>
            <field name="type">ir.actions.act_window</field>
            <field name="res_model">cenit.{name}.settings</field>
            <field name="view_id" ref="wizard_cenit_{name}_install" />
            <field name="view_type">form</field>
            <field name="view_mode">form</field>
            <field name="target">new</field>
        </record>

        <record id="todo_wizard_cenit_{name}_install" model="ir.actions.todo">
            <field name="action_id" ref="action_wizard_cenit_{name}_install"/>
            <field name="sequence">1</field>
            <field name="type">automatic</field>
        </record>

    </data>
</openerp>
