#!/usr/bin/python3
import argostranslate.package

# Source and target language codes
SOURCE_LANGUAGE="de"  # German
TARGET_LANGUAGE="en"  # ENglish

print("Fetching available translation models....")

# Download the online list of available models
argostranslate.package.update_package_index()

# Get all available models
available_packages=argostranslate.package.get_available_packages()

# Find a direct German-to-English Model
package=next(
    (
        p for p in available_packages
        if p.from_code==SOURCE_LANGUAGE
        and p.to_code==TARGET_LANGUAGE
    ),
    None 
)


if package is None:
    print("German-to-English model was not found.")
else:
    print(f"Selected: {package.from_name}->{package.to_name}")
    print("Downloading model. Please wait")

    # Download the model package
    downloaded_package=package.download()

    # Install it on this computer
    argostranslate.package.install_from_path(downloaded_package)

    print("Installation complete")
