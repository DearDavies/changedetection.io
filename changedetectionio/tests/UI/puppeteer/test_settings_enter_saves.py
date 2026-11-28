#!/usr/bin/env python3
"""Enter in a field of the settings page saves the settings, in a real browser.

With a password set, "Remove password" was the first submit button of the settings form, which is the one a
browser presses for Enter: changing a number and pressing Enter removed the password and did not save."""

from .browser import click_and_wait_for_new_page, press_enter_and_wait_for_new_page, run_in_browser, screenshot, site_url

PASSWORD = 'enter-key-test-password'
# On the first tab, always shown
FIELD = '#application-filter_failure_notification_threshold_attempts'
REMOVE_PASSWORD = '[name="application-removepassword_button"]'
CONFIRM = '.modal-dialog[open] [data-action="confirm"]'


async def _path(page):
    return await page.evaluate("() => window.location.pathname")


def test_enter_in_settings_saves_and_keeps_password(client, live_server, measure_memory_usage, datastore_path, running_app):
    async def steps(page):
        await page.goto(site_url('settings.settings_page'))
        await page.type('input[name="application-password"]', PASSWORD)
        await click_and_wait_for_new_page(page, 'input[name="save_button"]')

        await page.goto(site_url('settings.settings_page'))
        assert await _path(page) == '/login', "The password is on"
        try:
            await page.type('input[name="password"]', PASSWORD)
            await press_enter_and_wait_for_new_page(page)

            await page.goto(site_url('settings.settings_page'))
            await page.waitForSelector(FIELD, visible=True)
            await page.evaluate("(selector) => { document.querySelector(selector).value = ''; }", FIELD)
            await page.type(FIELD, '9')
            await screenshot(page, 'settings-enter-saves')
            await press_enter_and_wait_for_new_page(page)

            await page.goto(site_url('settings.settings_page'))
            assert await _path(page) != '/login', "Still signed in"
            assert await page.querySelector(REMOVE_PASSWORD), "The password is still on"
            assert await page.evaluate("(selector) => document.querySelector(selector).value", FIELD) == '9', "Enter saved the setting"
        finally:
            # The application is shared with the other tests here, leave it without a password.
            # Also what the button is for: it still removes the password when it is the one pressed and confirmed.
            await page.goto(site_url('settings.settings_page'))
            if await _path(page) == '/login':
                await page.type('input[name="password"]', PASSWORD)
                await press_enter_and_wait_for_new_page(page)
                await page.goto(site_url('settings.settings_page'))
            if await page.querySelector(REMOVE_PASSWORD):
                # It asks first, and "Cancel" leaves the password on
                await page.click(REMOVE_PASSWORD)
                await page.waitForSelector(CONFIRM, visible=True)
                await screenshot(page, 'settings-remove-password-confirm')
                await page.click('.modal-dialog[open] [data-action="cancel"]')
                await page.goto(site_url('settings.settings_page'))
                assert await page.querySelector(REMOVE_PASSWORD), "Cancelled, the password is still on"

                await page.click(REMOVE_PASSWORD)
                await page.waitForSelector(CONFIRM, visible=True)
                await click_and_wait_for_new_page(page, CONFIRM)

        await page.goto(site_url('settings.settings_page'))
        assert await _path(page) != '/login'
        assert await page.querySelector('input[name="application-password"]'), "The button removed the password"

    run_in_browser(steps, 'settings-enter-saves')
