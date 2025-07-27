# Django script for diagnosing and resolving common issues

import logging

from django.conf import settings
from django.core.management import call_command
from django.template.loader import get_template
from django.urls import Resolver404, get_resolver

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def check_urls():
    """
    Check for missing URL patterns or misconfigurations.
    """
    logger.info("Checking URL configuration for issues...")
    resolver = get_resolver()
    missing_urls = []

    # List of URLs to verify
    urls_to_check = [
        "favicon.ico",
        "client/",
        "projektiranje/",
        "financije/",
        "ljudski_resursi/",
        "nabava/",
        "prodaja/",
        "proizvodnja/",
        "skladiste/",
    ]

    for url in urls_to_check:
        try:
            resolver.resolve(url)
        except Resolver404:
            logger.error(f"URL pattern missing for path: {url}")
            missing_urls.append(url)

    if not missing_urls:
        logger.info("All URL patterns are properly configured.")
    else:
        logger.warning(f"Missing URL patterns: {missing_urls}")


def check_templates():
    """
    Check for issues with templates, such as missing variables.
    """
    logger.info("Checking template files for potential issues...")
    templates = settings.TEMPLATES[0]["DIRS"]
    missing_variables = []

    for template_dir in templates:
        try:
            template = get_template(template_dir)
            context = {}  # Ideally, we need sample context data here
            template.render(context)
        except Exception as e:
            logger.error(f"Error in template {template_dir}: {e}")
            missing_variables.append((template_dir, str(e)))

    if not missing_variables:
        logger.info("No missing variables found in templates.")
    else:
        logger.warning(f"Issues found in templates: {missing_variables}")


def check_static_files():
    """
    Ensure static files are properly collected and accessible.
    """
    logger.info("Checking static files configuration...")
    try:
        call_command("collectstatic", interactive=False, verbosity=0)
        logger.info("Static files collected successfully.")
    except Exception as e:
        logger.error(f"Error during static file collection: {e}")


def add_favicon_to_template():
    """
    Add favicon link to HTML templates if missing.
    """
    logger.info("Checking if favicon is added to templates...")
    templates = settings.TEMPLATES[0]["DIRS"]
    favicon_link = '<link rel="icon" type="image/x-icon" href="{% static \'favicon.ico\' %}">'

    for template_dir in templates:
        try:
            with open(template_dir, "r+") as file:
                content = file.read()
                if "favicon.ico" not in content:
                    logger.info(f"Adding favicon link to template {template_dir}")
                    file.seek(0, 0)
                    file.write(favicon_link + "\n" + content)
        except Exception as e:
            logger.error(f"Error while adding favicon to template {template_dir}: {e}")


def run_diagnostics():
    """
    Run all diagnostics to identify and resolve common issues.
    """
    logger.info("Starting Django diagnostics script...")
    check_urls()
    check_templates()
    check_static_files()
    add_favicon_to_template()
    logger.info("Diagnostics completed.")


if __name__ == "__main__":
    run_diagnostics()
