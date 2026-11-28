#!/usr/bin/env python3
"""Enter in a field of the settings page saves the settings.

A browser sends a form with its first submit button when Enter is pressed in one of its fields. On the
settings page that was "Remove password", so Enter removed the password instead of saving."""

from bs4 import BeautifulSoup
from flask import url_for

from .test_password_change_signs_out_sessions import SETTINGS_FORM, _forget_cached_user, _login, _set_password


def test_enter_in_settings_form_is_save_not_remove_password(app, client, live_server, measure_memory_usage, datastore_path):
    browser = app.test_client(use_cookies=True)
    _set_password(browser, "some-password")
    _login(browser, "some-password")

    _forget_cached_user()
    soup = BeautifulSoup(browser.get(url_for("settings.settings_page")).data, 'html.parser')
    settings_form = soup.select_one('form.settings')
    # A button with form="..." belongs to that other form, Enter in this one never presses it
    own_submit_buttons = [b for b in settings_form.select('input[type=submit], button[type=submit], button:not([type])')
                          if not b.get('form')]
    assert own_submit_buttons[0].get('name') == 'save_button', "The first submit button is the one Enter presses"

    # "Remove password" is still there, and still works from the form it now belongs to
    remove = soup.select_one('[name="application-removepassword_button"]')
    remove_form = soup.find('form', id=remove.get('form'))
    assert remove_form and remove_form is not settings_form
    assert remove_form.get('action') == settings_form.get('action')
    data = {i.get('name'): i.get('value') for i in remove_form.select('input[name]')}
    data[remove.get('name')] = remove.get('value')

    # What Enter sends: every field and the Save button, the password stays
    _forget_cached_user()
    res = browser.post(url_for("settings.settings_page"), data=dict(SETTINGS_FORM, save_button="Save"), follow_redirects=True)
    assert b"Password protection removed." not in res.data
    assert b"/logout" in res.data

    _forget_cached_user()
    res = browser.post(remove_form.get('action'), data=data, follow_redirects=True)
    assert b"Password protection removed." in res.data
